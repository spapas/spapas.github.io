Title: Multiple storages for the same FileField in Django
Date: 2023-04-11 14:20
Tags: python, django, media, storage
Category: django
Slug: django-multiple-file-storages
Author: Serafeim Papastefanos
Summary: Using multiple file storages from the same FileField in Django

When you need to support user-uploaded files from Django (usually called *media*)
you will probably use a [FileField](https://docs.djangoproject.com/en/4.2/topics/files/)
in your models. This is translated to a simple varchar (text) field in the database that
contains a unique identifier for the file. This usually would be the path to the file,
however this is not always the case!

What really happens is that Django has an underlying concept called a 
[File Storage](https://docs.djangoproject.com/en/4.2/topics/files/#file-storage)
which is a class that has information on how to talk to the actual storage backend,
and particularly how to translate the unique identifier stored on the db to an actual file object. 
By default
Django stores files in the file system using the 
[FileSystemStorage](https://docs.djangoproject.com/en/4.2/ref/files/storage/#django.core.files.storage.FileSystemStorage) 
however it is possible to use different backends through an add-on 
(for example [Amazon S3](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html))
or even write your own.

Each FileField can be configured to use a different storage backend by passing the `storage` parameter;
if you don't use this parameter then the default storage backend is used. So you can easily configure a `FileField`
that would upload files to your filesystem and another one that would upload files to S3.

However, one thing that is not
supported though is to use multiple storages for *the same* FileField depending on some parameter of the model instance.
Unfortunately, in a recent project I had to do exactly that: We had a `FileField` on a model that contained 
hundreds of GBs of files stored on the filesystem; we wanted to be able to upload the files of new
instances of that model on S3 but also wanted to keep the old files on the filesystem to avoid moving all these
to S3 (which would result to a lot of downtime). I also wanted a way to be "flexible" on this i.e to be able 
to change again the storage backend for some instances if needed and definitely not move/copy all these files!

If you take a peek
at the FileField options you'll see that there's a `storage` parameter that can be a 
[callable](https://docs.djangoproject.com/en/4.2/topics/files/#using-a-callable). However this
callable is initialized with the models and is not evaluated again until the app is restarted so it can't be used
to decide on the storage for each model instance. 

The only thing that is evaluated each time a file is uploaded through the FileField is when `upload_to` 
is a function. This function receives the model instance and returns the path that the file will be uploaded to.

The idea is to use this `upload_to` function to return a different path depending on the model instance
and then use a custom storage backend that will use the path to decide on the actual storage backend to use.

This is the code I ended up with for the `upload_to` function:

```python

def file_upload_path(instance, filename):
    dt_str = app.created_on.strftime("%Y/%m/%d")
    file_storage = ""

    if instance.id >= settings.STORAGE_CHANGE_ID: 
        file_storage = settings.STORAGE_SELECTION_STR + "/"
    
    return "protected/{0}{1}/{2}/{3}".format(file_storage, dt_str, instance.id, filename)

class Model(models.Model):
    file = models.FileField(upload_to=file_upload_path)
```

What happens here is that I have a setting `STORAGE_CHANGE_ID` that is the `id` of the instance
after which all instances will use the different storage backend. You can use whatever method
you want here to decide on the storage that would be used; the only thing to keep in mind is to 
put the storage *somewhere on the returned path*.

I also have a setting
`STORAGE_SELECTION_STR` that is the string that will be used in the path to differentiate the storage backend.
The `STORAGE_SELECTION_STR` has the value of `minios3` for this project.

Using this function the paths of the instances that are >= `STORAGE_CHANGE_ID` will be of the form `protected/minios3/2021/04/11/1234/filename.ext` while for the old files these will be of the form `protected/2021/04/11/1234/filename.ext`. Notice the `minios3` string in between. 

Of course this is not enough. We also need to tell Django to use the different storage backend for the new files. In order 
to do this we have to implement a [custom storage class](https://docs.djangoproject.com/en/4.2/howto/custom-file-storage/) like this:

```python

from django.core.files.storage import FileSystemStorage, Storage
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class FilenameBasedStorage(Storage):
    minio_choice = settings.STORAGE_SELECTION_STR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _open(self, name, mode="rb"):
        if self.minio_choice in name:
            return S3Boto3Storage().open(name, mode)
        else:
            return FileSystemStorage().open(name, mode)

    def _save(self, name, content):
        if self.minio_choice in name:
            return S3Boto3Storage().save(name, content)
        else:
            return FileSystemStorage().save(name, content)

    def delete(self, name):
        if self.minio_choice in name:
            return S3Boto3Storage().delete(name)
        else:
            return FileSystemStorage().delete(name)

    def exists(self, name):
        if self.minio_choice in name:
            return S3Boto3Storage().exists(name)
        else:
            return FileSystemStorage().exists(name)

    def size(self, name):
        if self.minio_choice in name:
            return S3Boto3Storage().size(name)
        else:
            return FileSystemStorage().size(name)

    def url(self, name):
        if self.minio_choice in name:
            return S3Boto3Storage().url(name)
        else:
            return FileSystemStorage().url(name)

    def path(self, name):
        if self.minio_choice in name:
            return S3Boto3Storage().path(name)
        else:
            return FileSystemStorage().path(name)

```

This class should be self explainable: It uses the `settings.STORAGE_SELECTION_STR`
we mentioned above to decide which storage backend to use and then it forwards each
method to the corresponding backend (either the filesystem storage or the S3 storage).

One thing to notice is that the `django.core.files.storage.Storage` class this class
inherits from has more methods that can be implemented (and would raise if called without implementing them)
however this implementation works fine for my needs.

One question some readers may have is what happens if the user uploads a file named `test-minios3.pdf` (i.e a file containing the 
`STORAGE_SELECTION_STR`). Well you may just as well ignore it; it will just be saved always on the minio-s3
storage backend. Or you can make sure to *remove* that string from the filename before saving it on the `file_upload_path`.
I chose to ignore it since it doesn't matter for my use case.

Finally, we need to tell Django to use this storage class for the `file` field. We can do this by
adding it to the `FileField` like:

```python
file = models.FileField(upload_to=file_upload_path, storage=FilenameBasedStorage)
```

or we can configure it on the `DEFAULT_FILE_STORAGE` setting 
([for Django < 4.2](https://docs.djangoproject.com/en/4.2/ref/settings/#default-file-storage)) 
or on the 
`STORAGES` dict ([for Django >= 4.2](https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-STORAGES)).

I hope this helps someone else that needs to do something similar!
How to download all images of an imgur album
############################################

:date: 2016-06-27 14:20
:tags: imgur, python, react, javascript, console, research
:category: python
:slug: download-imgur-album-images
:author: Serafeim Papastefanos
:summary: How to download all images of an imgur album


Recently I stubmled upon a great imgur_ album that contained 
`379 movie stills that could be used for desktop background`_. I
really liked the idea and wanted to download all the images in order
to put them in a folder and use them as a slideshow for my Windows
desktop background. 

Downloading them one by one would be considered penal
labour so I tried to find out an automatic way to get them all. With some
research in google, I found out an old post with the hint that by appending ``/zip``
to the URL  you could get a zip with all the images -- this didn't work for me. I 
also tried various browser tools for scrapping or downloading all images from a page but they
didn't work also (they could only download a small number of the images and not all).

This seemed strange to me until I understood how imgur loads its images by "inspecting"
an image and taking a look at the page's DOM structure through the console: 

.. image:: /images/imgur.gif
  :alt: How imgur loads images
  :width: 700 px

As we can see, the imgur client-side code has a component with a ``post-images`` class
that contains the visible images (and thoese that are above/below the visible images). When
the user scrolls up/down the contents of ``post-images`` will be changed accordingly 
(notice how the component with ``id=EKMGEPc`` moves down when I scroll up).
What this means is that each time there are 3-4 images (this actually depends on your window size)
under ``post-images`` that are changed when you scroll -- that's why downloaders / scrappers are not working (since these 
tools just inspect the DOM they only see these 3-4 images to download). 

Another interesting observation is that if you take a look at the network tab when you
scroll app down you won't see any ajax calls (the only network calls are the images that
are downloaded when they are appended to the DOM). So this means that somewhere there's
an array that is loaded when the page is loaded and contains all the images of the album.
If we can access this array then we'd be able to get all the URLs of the images...

From a quick look at the DOM structure we can understand that this is a React application 
(components have a ``data-reactid`` attribute). So I tried the `React Developer Tools`_
extension to see if I could find anything insteresting. Here's the output:


.. image:: /images/imgur-react.png
  :alt: Imgur - react dev tools
  :width: 1000 px

As you can see, there seem to be 4 top-level react elements -- the interesting one is ``GalleryPost``.
If you take a look at its props (in the right hand side of the react-devtools) you'll see that it has
an ``album_image_store`` property which also seems interesting (it should be the image store for this
album). After searching a bit its attributes
you'll see that it has a ``_`` child attribute, which has a ``posts`` child attribute which has an ``aoi3T``
attribute (notice that this is similar to the URL id of the album) and, finally this has an ``images``
attribute with objects describing all the images of that album \\o/! 

Now we need to get our hands on that ``images`` array contents. Unfortunately, right clicking doesn't seem
to do anything from react-dev-tools and there doesn't seem a way to copy data from that panel... However, in
the upper right position of that window you'll see the hint ``($r in the console)`` which means that
the selected react component is available as $r in the normal javascript console - so by entering 

.. code::

    copy($r.props.album_image_store._.posts.aoi3T)

I was able to copy the images of the album to my clipboard (please notice that ``$r`` will have the
value of the selected react component so, before trying it you must select the ``GalleryPost`` 
component in the react-dev-tools tab)!

I dumped this to a file to take a look at it - it is really easy to interpret it:

.. code::

    [
      {
        "hash": "MQplfkV",
        "title": "2001: A Space Odyssey",
        "description": "Cinematographer: Geoffrey Unsworth\n\nsource:\nhttp://www.filmcaptures.com/2001-a-space-odyssey/",
        "width": 1920,
        "height": 864,
        "size": 2262862,
        "ext": ".png",
        "animated": false,
        "prefer_video": false,
        "looping": false,
        "datetime": "2014-10-25 04:02:58",
        "thumbsize": "g",
        "minHeight": 306,
        "shown": true,
        "containerHeight": 501
      },
    ..

The imgur images have a URL of http//i.imgur.com/{hash}{ext} so, we 
can use the following small python 2 program to download all images from that album:

.. code::

    import requests
    import json
    from slugify import slugify

    # Modified from http://stackoverflow.com/a/16696317/119071
    def download_file(url, local_filename):
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from J.F.Sebastian
        return local_filename

        
    if __name__ == '__main__':
        for i, jo in enumerate(json.loads(open("album.txt").read())):
            filename = '{0}-{1}{2}'.format(slugify(jo['title']), i+1, jo['ext'])
            url = 'http://i.imgur.com/{0}{1}'.format(jo['hash'].strip(), jo['ext'])
            print filename, url
            download_file(url, filename)


Notice that the above uses the ``requests`` library to retrieve the files and the 
``python-slugify`` library to generate a filename using the image title so these
libraries must be installed by using ``pip install requests python-slugify``. This 
will read a file named ``album.txt`` that should contain the copied imgur album images
in the same directory and download all the images.

**Disclaimer** The above methodology works today (27-06-2016) - probably it will
stop working sometime in the future, when imgur changes its image loading algorithm
or its image object representation.
Also, I haven't been able to find a way to quickly access the ``GalleryPost`` react
component from the javascript console - you need to install the react dev tools and 
select that component from there so that you'll have the ``$r`` reference to it in
the javascript console. Finally, don't forget to change the 
``copy($r.props.album_image_store._.posts.aoi3T)``
depending on your album id (also if the id is not a valid identifier, for example it
starts with number, use ``copy($r.props.album_image_store._.posts['aoi3T']``).

.. _imgur: http://imgur.com/
.. _`379 movie stills that could be used for desktop background`: http://imgur.com/a/aoi3T
.. _`at his article`: http://www.barfuhok.com/how-to-download-a-file-with-anti-virus-warning-on-gmail/ 
.. _`React Developer Tools`: https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi

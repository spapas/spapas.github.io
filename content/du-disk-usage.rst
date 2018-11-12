Use du to find out the disk usage of each directory in unix
###########################################################

:date: 2018-11-12 14:20
:tags: du, unix, linux, disk-usage
:category: unix
:slug: du-disk-usage
:author: Serafeim Papastefanos
:summary: How to use the du utility to find out the disk usage of each directory in unix


One usual problem I have when dealing with production servers is that their
disks are filled.  This results in various errors and should be fixed
immediately. The first step to resolve this issue is to find out where is that 
user space wasted.

For this you can use the `du` unix tool with some parameters. However `du`
has various parameters (not needed for the task at hand) and the various
places I search for contain other info not related to this specific task.

Thus I've decided to write this small blog post to help people struggling with
this and also to help *me* avoid googling for it and searching in pages that
also contain other ``du`` recipies and also avoid the try and error that this
would require.

So to print out the disk usage summary for a directory go to that directory
and run ``du -h -s *``; you need to have access to the child subdirectories
so probably it's better to try this as root (unless you go to your home dir
for example).

Here's a sample usage

.. code-block:: sh

    [root@server1 /]# cd /
    [root@server1 /]# du -h -s *
    7.2M    bin
    55M     boot
    164K    dev
    35M     etc
    41G     home
    236M    lib
    25M     lib64
    20K     lost+found
    8.0K    media
    155G    mnt
    0       proc
    1.6G    root
    12M     sbin
    8.0K    srv
    427M    tmp
    3.2G    usr
    8.9G    var

The parameters are -h to print human readable sizes (G, M etc) and -s to
print a summary usage of *each* parameter. Since this will output the
summary for each parameter I finally pass ``*`` to be changed to all files/dirs
in that directory. If I used ``du -h -s /tmp`` I'd get the total usage only for
the ``/tmp`` directory.

Another tricck that may help you quickly find out the offending directories is to
append the ``| grep G`` pipe command (i.e run ``du -h -s * | grep G``) which will
filter out only the entries containing a ``G`` (i.e only print the folders having
more than 1 GB size). Yeh I know that this will also print entries that have
also a G in their name but since there aren't many directores that have
G in their name you should be ok.

Finally, if you run the above from ``/`` so that ``/proc`` is included you may
get a bunch of ``du: cannot access 'proc/nnn/task/nnn/fd/4': No such file or directory``
errors; just add the ``2> /dev/null`` pipe redirect to redirect the stderr output
to ``/dev/null``, i.e run ``du -h -s * 2> /dev/null``.




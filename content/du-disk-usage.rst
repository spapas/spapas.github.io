Use du to find out the disk usage of each directory in unix
###########################################################

:date: 2018-11-12 14:20
:tags: du, unix, linux, disk-usage
:category: unix
:slug: du-disk-usage
:author: Serafeim Papastefanos
:summary: How to use the du utility to find out the disk usage of each directory in unix


One usual problem I have when dealing with production servers is that their
disks get filled.  This results in various warnings and errors and should be fixed
immediately. The first step to resolve this issue is to actually find out where is that 
hard disk space is used!

For this you can use the `du` unix tool with some parameters. The problem is that `du`
has various parameters (not needed for the task at hand) and the various
places I search for contain other info not related to this specific task.

Thus I've decided to write this small blog post to help people struggling with
this and also to help *me* avoid googling for it by searching in pages that
also contain other ``du`` recipies and also avoid the trial and error that this
would require.

So to print out the disk usage summary for a directory go to that directory
and run ``du -h -s *``; you need to have access to the child subdirectories
so probably it's better to try this as root (unless you go to your home dir
for example).

Here's a sample usage:

.. code::

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
in that directory. If I used ``du -h -s /tmp`` instead I'd get the total usage only for
the ``/tmp`` directory.

Another trick that may help you quickly find out the offending directories is to
append the ``| grep G`` pipe command (i.e run ``du -h -s * | grep G``) which will
filter out only the entries containing a ``G`` (i.e only print the folders having
more than 1 GB size). Yeh I know that this will also print entries that have
also a G in their name but since there aren't many directores that have
G in their name you should be ok.

If you run the above from ``/`` so that ``/proc`` is included you may
get a bunch of ``du: cannot access 'proc/nnn/task/nnn/fd/4': No such file or directory``
errors; just add the ``2> /dev/null`` pipe redirect to redirect the stderr output
to ``/dev/null``, i.e run ``du -h -s * 2> /dev/null``.

Finally, please notice that if there are *lots* of files in your directory you'll get 
a lot of output entries (since the `*` will match both files and directories).
In this case you can use ``echo */`` or ``ls -d */`` to list only the directories;
append that command inside a \` pair or ``$()`` (to substitute for the command
output) instead of the ``*`` to only get the sizes of the
directories, i.e run ``du -h -s $(echo */)`` or ``du -h -s `echo */```.

One thing that you must be aware of is that this command may take *a long time*
especially if you have lots of small files somewhere. Just let it run and it
should finish after some time. If it takes too long time try to exclude any 
mounted network
directories (either with SMB or NFS) since these will take extra long time.

Also, if you awant a nice interactive output
using ncurses you can download and compile the `ncdu tool`_ (NCurses Disk Usage).

.. _`ncdu tool`: https://dev.yorhel.nl/ncdu


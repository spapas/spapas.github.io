Easy downloading youtube videos and mp3s using python
#####################################################

:date: 2018-03-05 10:20
:tags: youtube, youtube-dl, ffmpeg, python
:category: python
:slug: easy-youtube-mp3-downloading
:author: Serafeim Papastefanos
:summary: Download videos (and convert them to mp3s) from youtube using python youtube-dl and ffmpeg!

In this article I am going to present you with an easy (and advertisement/malware free) way to download
videos from youtube, converting them to mp3 if needed. Also, I will give some more useful hints, for
example how to download multiple mp3s using a script, how to break a long mp3 to same-length parts 
so you could quickly skip tracks when you play it in your stereo etc.

I am going to give specific instructions for Windows users - however everything I'll propose should also be applicable
to OSX or Linux users with minor modifications.

The tools we are going to use are:

* youtube-dl_ which is a python library for downloading videos from youtube (and some other sites)
* ffmpeg_ which is a passepartout video/audio editing library 

Installation
------------

To install youtube-dl I recommend installing it in your global python (2 or 3) package list using pip. Please read my
`previous1 <{filename}python-2-3-windows.rst>`_ article

to see how you should install and use Python 2 or 3
on Windows. Following the instructions from there, you can do the following to install youtube-dl in your global 
Python 3 packages:

.. code::

    py -3 -m pip install youtube-dl
    
To run youtube-dl you'll write something like ``py -3 -m youtube_dl url_or_video_id`` (notice the underscore instead of dash since
dashes are not supported in module names in python). For example try something like this ``py -3 -m youtube_dl YgtL4S7Hrwo`` and you'll
be rewarded with the 2016 Pycon talk from Guido van Rossum! If you find this a little too much too type don't be afraid, I will give 
some hints later about how to improve this.

To upgrade your youtube-dl installation you should do something like this:   

.. code::

    py -3 -m pip install -U youtube-dl
    
Notice that you must frequently upgrade your youtube-dl installation because sometimes youtube changes the requirements
for viewing / downloading videos and your old version will not work. So if for some reason something is not correct when
you use youtube-dl always try updating first. 
    
If you wanted you could also create a virtual environment (see instructions on previously mentioned article) and install youtube-dl locally there using ``pip install youtube-dl``
however I prefer to install it on the global packages to be really easy for me to call it from a command prompt I open. Notice
that if you install youtube-dl in a virtualenv, after you activate that virtualenv you'll be able to run it just by typing ``youtube-dl``.

Finally, If for some reason you don't want want to mess with python and all this (or it just seems greek to you) then you
may go on and directly download a `youtube-dl windows executable`_. Just put it in your path and you should be good to go. 

To install ffmpeg, I recommend `downloading the Windows build from here`_ (select the correct Windows architecture of your system and
always static linking - the version doesn't matter). This will get you a zip - we are mainly interested to the three files under the
``bin`` folder of that zip which should be copied to a directory under your path: 

* ffmpeg is the passepartout video converting toot that we are going to use
* ffprobe will print some information about a file (about its container and video/audio streams)
* ffplay will play the file -- not really recommended there are better tools but it is invaluable 
  for testing; if it can be played be ffplay then ffmpeg will be able to properly read your file

Notice I recommend copying things to a directory in your path. This is recommended and will save you from repeatedly typing the same things
over and over. Also, later I will propose a bunch of DOS batch (.bat) files that can also be copied to that directory and help you even
more in you youtube video downloading. To add a directory to the PATH, just press Windows+Pause Break, Advanced System Settings, Advanced,
Environment Variables, edit the "Path" User variable (for your user) and append the directory there.

Using youtube-dl
----------------

As I've already explained before, to run youtube-dl you'll either write something like ``py -3 -m youtube_dl`` (if you've installed it
to your global python packages) or run youtube-dl if you've downloaded the pre-built exe or have installed it in a virtualenv. To save
you from some keystrokes, you can create a batch file that will run and pass any more parameters to it, something like this:

.. code::
    
    py -3 -m youtube_dl %*
    
(the %* will capture the remaining command line) so to get the previous video just run ``getvideo YgtL4S7Hrwo`` 
(or getvideo https://www.youtube.com/watch?v=YgtL4S7Hrwo - works the same with the video id or the complete url).

One thing I'd like to mention here is that youtube-dl works fine with playlists and even channels. For example,
to download all videos from PyCon 2017 just do this:

``getvideo https://www.youtube.com/channel/UCrJhliKNQ8g0qoE_zvL8eVg/feed`` and you should see something like:

.. code::
    
    E:\>py -3 -m youtube_dl https://www.youtube.com/channel/UCrJhliKNQ8g0qoE_zvL8eVg/feed
    [youtube:channel] UCrJhliKNQ8g0qoE_zvL8eVg: Downloading channel page
    [youtube:playlist] UUrJhliKNQ8g0qoE_zvL8eVg: Downloading webpage
    [download] Downloading playlist: Uploads from PyCon 2017
    [youtube:playlist] UUrJhliKNQ8g0qoE_zvL8eVg: Downloading page #1
    [youtube:playlist] playlist Uploads from PyCon 2017: Downloading 143 videos
    [download] Downloading video 1 of 143
    [youtube] AjFfsOA7AQI: Downloading webpage
    [youtube] AjFfsOA7AQI: Downloading video info webpage
    [youtube] AjFfsOA7AQI: Extracting video information
    WARNING: Requested formats are incompatible for merge and will be merged into mkv.
    [download] Destination: Final remarks and conference close  - Pycon 2017-AjFfsOA7AQI.f137.mp4
    [download]   2.9% of 34.49MiB at 940.52KiB/s ETA 00:36
    

This is gonna take some time ... 

Now, youtube-dl has `many options`_ and can be configured with `default values`_ depending on your
requirements. I won't go into detail about these except on some things I usually use, if you
need some help feel free to ask me.

When you download a video, youtube-dl will try to download the best quality possible for that video,
however a video may have various different formats that can be queries by passing the option ``--list-formats``
to ffmpeg, for example here's the output from the previously mentioned video:

.. code::

    E:\>getvideo YgtL4S7Hrwo --list-formats
    [youtube] YgtL4S7Hrwo: Downloading webpage
    [youtube] YgtL4S7Hrwo: Downloading video info webpage
    [youtube] YgtL4S7Hrwo: Extracting video information
    [info] Available formats for YgtL4S7Hrwo:
    format code  extension  resolution note
    249          webm       audio only DASH audio   53k , opus @ 50k, 15.14MiB
    250          webm       audio only DASH audio   72k , opus @ 70k, 20.29MiB
    171          webm       audio only DASH audio  111k , vorbis@128k, 29.42MiB
    140          m4a        audio only DASH audio  130k , m4a_dash container, mp4a.40.2@128k, 38.38MiB
    251          webm       audio only DASH audio  130k , opus @160k, 36.94MiB
    278          webm       256x144    144p   58k , webm container, vp9, 30fps, video only, 11.01MiB
    242          webm       426x240    240p   88k , vp9, 30fps, video only, 12.40MiB
    160          mp4        256x144    144p  120k , avc1.4d400c, 30fps, video only, 33.64MiB
    243          webm       640x360    360p  153k , vp9, 30fps, video only, 23.48MiB
    134          mp4        640x360    360p  230k , avc1.4d401e, 30fps, video only, 28.91MiB
    133          mp4        426x240    240p  260k , avc1.4d4015, 30fps, video only, 74.75MiB
    244          webm       854x480    480p  289k , vp9, 30fps, video only, 39.31MiB
    135          mp4        854x480    480p  488k , avc1.4d401f, 30fps, video only, 56.43MiB
    247          webm       1280x720   720p  945k , vp9, 30fps, video only, 102.45MiB
    136          mp4        1280x720   720p 1074k , avc1.4d401f, 30fps, video only, 116.72MiB
    17           3gp        176x144    small , mp4v.20.3, mp4a.40.2@ 24k
    36           3gp        320x180    small , mp4v.20.3, mp4a.40.2
    43           webm       640x360    medium , vp8.0, vorbis@128k
    18           mp4        640x360    medium , avc1.42001E, mp4a.40.2@ 96k
    22           mp4        1280x720   hd720 , avc1.64001F, mp4a.40.2@192k (best)

As you can see, each has an id and defines an extension (container)  and info about its video and audio stream.
You can download a *specific* format by using the -f command line otpion. For example , to download the audio-only
format with the worst audio quality use ``C:\Users\serafeim>getvideo YgtL4S7Hrwo -f 249``. Notice that there are
formats with audio ony and other formats with vide only. To download the worst format possible (resulting in the
smallest file size of course ) you can pass the ``-f worst`` command line (there's also a ``-f best`` command line
which is used by default).

Another thing I'd like to point out here is that you can define an `output template`_ using the ``-o`` option that
will format the name of the output file of your video using the provided options. There are  `many examples in the docs`_
so I won't go into any more details here.

Another cool option is the -a that will help you download all videos from a file. For example, if you have a file 
named ``videos.txt`` with the following contsnts:

.. code::

    AjFfsOA7AQI
    3dDtACSYVx0
    G17E4Muylis

running ``getvideo -a videos.txt -f worst``

will get you all three videos in their worst quality. If you don't want to create files then you can use something
like this:

.. code::

    for %i in (AjFfsOA7AQI 3dDtACSYVx0 G17E4Muylis) do getvideo %i -f worst

and it will run  getvideo for all three files.

Some more options I'd like to recommend using are:

* ``--restrict-filenames`` to avoid strange filenames 
* ``--ignore-errors`` to ignore errors when download multiple files (from a playlist or a channel) - this is really 
  useful because if you have a play with missing items youtube-dl will stop downloading the remaining files when it
  encounters the missing one
  
If you want to always use these options you may add them to your configuration file (``C:\Users\<user name>\youtube-dl.conf``)
or to the getvideo.bat defined above i.e getvideo.bat will be:

.. code::
    
    py -3 -m youtube_dl --restrict-filenames --ignore-errors %*

Extracting mp3s
---------------




.. _youtube-dl: https://rg3.github.io/youtube-dl/
.. _ffmpeg: https://www.ffmpeg.org
.. _`youtube-dl windows executable`: https://yt-dl.org/latest/youtube-dl.exe
.. _`downloading the Windows build from here`: https://ffmpeg.zeranoe.com/builds/
.. _`many options`: https://github.com/rg3/youtube-dl/blob/master/README.md#options
.. _`default values`: https://github.com/rg3/youtube-dl/blob/master/README.md#configuration
.. _`output template`: https://github.com/rg3/youtube-dl/blob/master/README.md#output-template
.. _`many examples in the docs`: https://github.com/rg3/youtube-dl/blob/master/README.md#output-template-examples
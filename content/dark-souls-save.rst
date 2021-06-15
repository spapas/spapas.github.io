Saving in Dark Souls
####################

:date: 2021-06-15 14:20
:tags: dark-souls, dark-souls-2, dark-souls-3, autohotkey
:category: gaming
:slug: dark-souls-saves
:author: Serafeim Papastefanos
:summary: How to properly save your game in the Dark Souls trilogy

Introduction
------------

The Dark Souls Trilogy (1-2-3) from FromSoftware is one of the modern gaming classics. The games should 
be experienced by everybody because of their excellent gameplay, combat mechanics, atmosphere and 
character development. The defining characteristic of the Dark Souls Trilogy and what scares most gamers 
is their over the top difficulty. 

This great difficulty is increased even more because of the saving mechanism of these games: There's a 
single save game in the game, if you die you'll return to a previous checkpoint (called bonfire). These
checkpoint are sparcely located within the gaming world and they are not always near boss fights, so 
if you die in a boss fight you may need to kill enemies for sometime before you reach the boss again to 
retry. Also, everything is permanent so if you 
screw up somehow (i.e you kill an important NPC) there's no way to "restore" your game; you'll lose him
(and his items if he's a merchant) for the rest of your current game!

If the above seems too difficult for you to even try, fear not! There a particular way to have "real" saves in all three 
Dark Souls games, even if it is a little cumbersome. It will be much less cumbersome than having to restart
the game because you killed an important NPC.

Disclaimer 
----------

Before describing the technique I'd like to provide some disclaimer points:

* The Dark Souls Trilogy should be experienced as-is. You shouldn't use this method because you'll make the games easier and not as difficult as it was intented by their publisher. Use it only as a last resort when you are going to abandon the game.
* Most other Dark Souls players will mock you and hate you for using these techniques.
* You may break your save if you do something wrong so I won't be held responsible for losing your progress.

How Dark Souls saves your game 
------------------------------

All three Dark Souls games have a particular directory in your hard disk where they place their save game. There's a single file with your save game that has an extension endingg in .sl2. 

From my PC, the folders and names of each of these games are the following:

* Dark Souls Remastered: Folder ``C:\Users\username\Documents\NBGI\DARK SOULS REMASTERED\1638``, filename: ``DRAKS0005.sl2``
* Dark Souls 2: Scholar of the First Sin: ``C:\Users\username\AppData\Roaming\DarkSoulsII\0110000100000666\``, filename: ``DS2SOFS0000.sl2``
* Dark Souls 3: ``C:\Users\username\AppData\Roaming\DarkSoulsIII\0110000100000666\``, filename: ``DS3000.sl2``

Notice that the username will be your user's username while the numbers you see will probably be different.

Now, when some particular action occurs (i.e when you kill an enemy) the game will overwrite the file in the folder with a new one 
with the changes. You will see a flame in the top right of your screen when this happens. Notice that this happens on particular moments,
for example if you are just moving without encountering enemies your game won't be saved (so if for example you make a difficult jump 
the game won't be saved right after the jump). Also, Dark Souls will save your game when you quit (so if you do a difficult jump, quit the game
and restart you will be after the jump). 

The above description enables you to actually have proper saves: Quit the game (not completely, just display the title screen), 
backup the save file in a different location, start the game. 
If you die, quit the game (again just display the title screen), copy over from the backup to the save location and start the game again. 
Notice that you should always quit the 
game before restoring from a save file because Dark Souls reads the saves only then. 
If you copy over a backup save while playing the game the 
backup will be just overwritten with the new save data. 

However you can backup your game without actually quitting: When you've reach a point you feel it needs saving, just alt+tab outside of your game
copy over the save to a backup location (you can even give it a proper name) and continue playing. When you want to load that save you'll need to
quit, restore the backup and start the game again. Notice that when you do this the game will show you a warning that you "did not properly quit
the game". From what I can understand, when you quit the game Dark Souls writes some flag to your save game. If you shut down your PC while 
playing (or copy over the save game) then Dark Souls won't write that flag to your save game. However from my experience in all three Dark Souls
games this warning doesn't mean anything, the game will continue normally without any problems.

Making it simpler
-----------------

Copying over the save game in a different location is cumbersome and makes it easy to do mistakes (i.e copy instead of restoring your backup
save, copy over the current save to your backup). To make this process easier I will give you here a simple autohotkey script that will do 
this for you using F7 to backup your save and F8 to restore it (don't forget that you can only restore when you have quit the game and see the 
title screen).

To use this script you need the excellent autohotkey_ utility. Download and install it and then execute the script by double clicking it (it needs to have an .ahk extension):

.. code::

  #SingleInstance Force
  #MaxHotkeysPerInterval 99999
  SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
  SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.


  SAVE_FOLDER_DS := "C:\Users\serafeim\AppData\Roaming\DarkSoulsII\0110000100000666\"
  SAVE_FILENAME_DS := "DS2SOFS0000.sl2"
  BACKUP_FOLDER_DS := "C:\Users\serafeim\Documents\ds2\"


  GetFolderMax(f) 
  {
    MAX := 0
    Loop, Files, %f%\*.* 
    {
      NUM_EXT := 1 * A_LoopFileExt

      if (NUM_EXT> MAX) 
      {
        MAX := NUM_EXT
      }
    }
    
    return MAX
  }

  F7::
  {
    ;MsgBox % "F7"
    ;MsgBox % "Will copy " . SAVE_FILENAME_DS . " to " . BACKUP_FOLDER_DS
      
    MAX_P1 := GetFolderMax(BACKUP_FOLDER_DS) + 1
    ;MsgBox % "Max + 1 is " . MAX_P1
    
    SOURCE := SAVE_FOLDER_DS . SAVE_FILENAME_DS
    DEST := BACKUP_FOLDER_DS . SAVE_FILENAME_DS . "." . MAX_P1
    
    ;MsgBox % "Will copy " . SOURCE . " to " . DEST
    FileCopy, %SOURCE%, %DEST%
    return
  }

  F8::
  {
    ;MsgBox % "F8"
    MAX := GetFolderMax(BACKUP_FOLDER_DS)
    MAX_FILE := BACKUP_FOLDER_DS . SAVE_FILENAME_DS . "." . MAX
    ;MsgBox % "Maxfile is " . MAX_FILE
    
    SOURCE := MAX_FILE 
    DEST := SAVE_FOLDER_DS . SAVE_FILENAME_DS
    
    ;MsgBox % "Will copy " . SOURCE . " to " . DEST
    FileCopy, %SOURCE%, %DEST%, 1
    return
  }

The script is very easy to understand but I'll explain it a bit here: First of all you need to define the 
``SAVE_FOLDER_DS, SAVE_FILENAME_DS`` and ``BACKUP_FOLDER_DS`` variables. The first two are the folder and 
filename of your game (in my example I'm using it for DS2). The ``BACKUP_FOLDER_DS`` is where you want your 
backups to be placed. This script will backup your save file in that folder when you press F7. To keep better
backups it will append an increasing number in the end of your filename so when you press F7 you will see
that it will create a file named ``DS2SOFS0000.sl2.0``, then ``DS2SOFS0000.sl2.1`` etc in the ``BACKUP_FOLDER_DS``.
When you press F8 it will get the file with the biggest number in the end, strip that number and copy it over your 
Dark Souls save file.

As you can see there's a ``GetFolderMax`` function that retrieves the max number from your backup folder. Then,
F7 and F8 will use that function to either copy over your Dark Souls save file in the backup with an increased 
number or retrieve the latest one and restore it in your save folder.

The script works independently of the game so if you configure it and press F7 you should see that the backup file 
will be created. Also if you delete (or rename) your Dark Souls save file and press F8 you should see that it will 
be restore by the backup. 

So using the above script, my play workflow is like this: Start Dark Souls, kill an enemy, press F7, kill another
enemy, press F7 (depending on how difficult the enemies are of course). Die from an enemy,
quit the game, press F8, continue my game. 

One thing to notice is that in Windows 10 it seems that the hotkeys are not captured from autohotkey when the game 
runs in full screen. When I run the games in a window it works fine. Some people say that if you run autohotkey 
as administrator it will capture the key-presses but it didn't work fine for me.



.. _autohotkey: https://www.autohotkey.com/
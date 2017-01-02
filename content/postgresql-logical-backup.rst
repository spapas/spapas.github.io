Getting a logical backup of all databases of your Postgresql server
###################################################################

:date: 2016-11-02 15:10
:tags: bash, cron, postgresql
:category: postgresql
:slug: postgresql-backup
:author: Serafeim Papastefanos
:summary: A script to help you backup your postgresql databases

In this small post I will present a small bash script that could be used to create logical backups of all the databases in a Postgresql server along
with some other goodies. More specifically, the script will:

- Create two files at /tmp to output information (one for debugging and one with info for sending it through email at the end)
- Create a backup directory with the current date
- Create a list of all databases found on the server
- For each database, vacuum and analyze it, backup it, gzip it and put it in the backup directory
- Write info about the backup in the info log file
- Do the same for global objects
- Send an email when the backup is finished with the info log

Now, in my system I'm using an external folder at ``/mnt/backupdb`` to put my backups. You may either use the same technique or connect remotely to a 
postgresql database (so you need to change the parameters of ``vacuumdb``, ``pg_dump`` and ``pg_dumpall`` to define the server and credentials to connect to) 
and put the backups to a local disc. 

.. code-block:: bash

    #!/bin/sh
    echo "" > /tmp/db_backup.log
    echo "" > /tmp/db_backup_info.log
    date_str=$(date +"%Y%m%d_%H%M%S")
    backup_dir=/mnt/backupdb/pg_backup.$date_str
     
    mkdir $backup_dir
    pushd $backup_dir > /dev/null
    
    dbs=`sudo -u postgres psql -Upostgres -lt | grep -v : | cut -d \| -f 1 | grep -v template | grep -v -e '^\s*$' | sed -e 's/  *$//'|  tr '\n' ' '`
    echo "Will backup: $dbs to $backup_dir" >> /tmp/db_backup_info.log
    for db in $dbs; do
      echo "Starting backup for $db" >> /tmp/db_backup_info.log
      filename=$db.$date_str.sql.gz
      sudo -u postgres vacuumdb --analyze -Upostgres $db >> /tmp/db_backup.log
      sudo -u postgres pg_dump -Upostgres -v $db -F p 2>> /tmp/db_backup.log | gzip > $filename
      size=`stat $filename --printf="%s"`
      kb_size=`echo "scale=2; $size / 1024.0" | bc`
      echo "Finished backup for $db - size is $kb_size KB" >> /tmp/db_backup_info.log
    done
    
    echo "Backing up global objects" >> /tmp/db_backup_info.log
    filename=global.$date_str.sql.gz
    sudo -u postgres pg_dumpall -Upostgres -v -g 2>> /tmp/db_backup.log | gzip > $filename
    size=`stat $filename --printf="%s"`
    kb_size=`echo "scale=2; $size / 1024.0" | bc`
    echo "Finished backup for global - size is $kb_size KB" >> /tmp/db_backup_info.log
    
    echo "Ok!" >> /tmp/db_backup_info.log
    mail -s "Backup results" spapas@mymail.foo.bar  < /tmp/db_backup_info.log
    popd > /dev/null

Let's explain a bit the above script: The two first lines (echo ...)  will just clear out the two files ``/tmp/db_backup.log`` and ``/tmp/db_backup_info.log``. The first
will contain debug info from the commands and the second one will contain our info that will be sent through an email at the end of the backup. After that, we initialize
``date_str`` with the current date in the form ``20161102_145011`` and the backup_dir with the correct directory to save the backups to. We then create the backup directory
and switch to it with ``pushd``.

The following, rather long command will assign the names of the databases to the ``dbs`` variable. So how is it working? ``psql -lt`` lists the names of the databases, but lists
also more non-needed information which we remove with the following commands (grep, cut etc). The sed removes whitespace and the tr concatenates individual lines to a single line
so dbs will have a value like 'db1 db2 ...'. For each one of these files then we assign its name and date to a filename and then, after we execute vacuumdb we use pg_dump with gzip to actually
create the backup and output it to the file. The other two lines (size and kb_size) are used to calculate the size of the backup file (to be sure that something is actually created) - you'll
need to install bc for that. The same process is followed the to backup global objects (usernames etc) using ``pg_dumpall -g``. Finally, we send a mail with a subject of "Backup results"
and body the contents of ``/tmp/db_backup_info.log``.
    
I've saved this file to ``/var/lib/pgsql/db_backup_all.sh``. To run I propose using cron -- just edit your crontab (through ``vi /etc/crontab``) and add the line 

.. code::

   15 2  *  *  * root       /usr/bin/bash /var/lib/pgsql/db_backup_all.sh
   
This will run the backup every night at 2.15. Uses the root user to have access rights to the backup folder. One thing to be careful about is that on Redhat/Centos distributions, 
the above won't work because sudo requires a tty to work and cron doesn't have one. To fix this, comment out the line

.. code::

    Defaults    requiretty

of your /etc/sudoers file.

**Update 02/12/2016:** Here's a little better version of the above script that

1. Create two files for each database, one with SQL script backup, one with binary backup. Although with SQL backup you can check out the backup and maybe do changes before applying it, the binary backup is a more foolproof method of restoring everything to your database! Also, instead of restoring the database through ``psql`` (as required by the SQL script backup), using the binary backup you can restore through the ``pg_restore`` tool.
2. Adds a function to output the file size (so the script is more DRY)

.. code-block:: bash

    #!/bin/sh
     
    function output_file_size {
      size=`stat $1 --printf="%s"`
      kb_size=`echo "scale=2; $size / 1024.0" | bc`
      echo "Finished backup for $2 - size is $kb_size KB" >> /tmp/db_backup_info.log
    }
     
    echo "" > /tmp/db_backup.log
    echo "" > /tmp/db_backup_info.log
    date_str=$(date +"%Y%m%d_%H%M%S")
    backup_dir=/mnt/backupdb/dbpg/pg_backup.$date_str
     
    mkdir $backup_dir
    pushd $backup_dir > /dev/null
    dbs=`sudo -u postgres psql -Upostgres -lt | cut -d \| -f 1 | grep -v template | grep -v -e '^\s*$' | sed -e 's/  *$//'|  tr '\n' ' '`
    #dbs='dgul  hrms  mailer_server  missions  postgres'
    echo "Will backup: $dbs to $backup_dir" >> /tmp/db_backup_info.log
    for db in $dbs; do
      echo "Starting backup for $db" >> /tmp/db_backup_info.log
      filename=$db.$date_str.sql.gz
      filename_binary=$db.$date_str.bak.gz
      sudo -u postgres vacuumdb --analyze -Upostgres $db >> /tmp/db_backup.log
      sudo -u postgres pg_dump -Upostgres -v $db -F p 2>> /tmp/db_backup.log | gzip > $filename
      sudo -u postgres pg_dump -Upostgres -v $db -F c 2>> /tmp/db_backup.log | gzip > $filename_binary
      output_file_size $filename "$db sql"
      output_file_size $filename_binary "$db bin"
    done
    echo "Backing up global objects" >> /tmp/db_backup_info.log
    filename=global.$date_str.sql.gz
    sudo -u postgres pg_dumpall -Upostgres -v -g 2>> /tmp/db_backup.log | gzip > $filename
    output_file_size $filename global
    echo "Ok!" >> /tmp/db_backup_info.log
    mail -s "Backup results" spapas@hcg.gr  < /tmp/db_backup_info.log
    popd > /dev/null

.. _Werkzeug: http://werkzeug.pocoo.org/
.. _django-extensions: https://github.com/django-extensions/django-extensions

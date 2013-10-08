git branches
############

:date: 2013-10-08 13:20
:tags: git, github, branching
:category: git
:slug: git-branches
:author: Serafeim Papastefanos
:summary: Experiments and answers for git branching

.. contents::

Introduction
------------

A branch_ is a very interesting git feature. With this you may have more than one *branches* in the same repository. The main
usage of this feature would be to create different versions of your source code to parallel test development of different features.
When the development of each of these features has been finished then the different versions would need to be combined (or merged) to a
single version. Of course, merging is not always the result of branching - some branches may exist indefinitely or other may just  be
deleted without merging. 

I will try to experiment with it and comment on the results.

Creating a new git repository
-----------------------------

Let's start by creating a new git repository:

.. code::

 D:\>mkdir testgit
 D:\>cd testgit
 D:\testgit>echo contents 11 > file1.txt
 D:\testgit>echo contents 222 > file2.txt
 D:\testgit>echo 3333 > file2.txt
 D:\testgit>copy con file3.txt
 line 1 of file 3

 line 3 of file 3

 test

 line 7 of file 3
 ^Z
        1 files copied.

 D:\testgit>git init
 Initialized empty Git repository in D:/testgit/.git/
 D:\testgit>git add .
 D:\testgit>git commit -m Initial
 [master (root-commit) 96ca9af] Initial
  3 files changed, 9 insertions(+)
  create mode 100644 file1.txt
  create mode 100644 file2.txt
  create mode 100644 file3.txt

To see the branch we are in we can use the ``git branch`` command. Also ``git status`` outputs the current branch:

.. code::

 D:\testgit>git status
 # On branch master
 nothing to commit, working directory clean
 D:\testgit>git branch
 * master

So, it seems that when we create a new repository, a "master" branch is created. 
        
Branching
---------
Lets create a new branch and change our working branch to it:

.. code::

 D:\testgit>git branch slave
 D:\testgit>git branch
 * master
   slave
 D:\testgit>git checkout slave
 Switched to branch 'slave'
 D:\testgit>git branch
   master
 * slave

We can see that now the slave branch is the current one. Let's do some changes and add commit them to the slave branch:

.. code::
 
 D:\testgit>git branch
   master
 * slave
 D:\testgit>echo new file1 contents > file1.txt
 D:\testgit>git commit -m "Slave modification"
 [slave b6083ad] Slave modification
  1 file changed, 1 insertion(+), 1 deletion(-)
 D:\testgit>git checkout master
 Switched to branch 'master'
 D:\testgit>more file1.txt
 contents 11
 D:\testgit>git checkout slave
 Switched to branch 'slave'
 D:\testgit>more file1.txt
 new file1 contents

So the contents of file1.txt in the branch master is ``contents 11`` while the contents of the same file
in the branch slave is ``new file1 contents``.  

An interested behaviour is what happens with uncommit changes when changing branches. Let's try deleting a file:

.. code::

 D:\testgit>del file2.txt
 D:\testgit>git status
 # On branch master
 # Changes not staged for commit:
 #   (use "git add/rm <file>..." to update what will be committed)
 #   (use "git checkout -- <file>..." to discard changes in working directory)
 #
 #       deleted:    file2.txt
 #
 no changes added to commit (use "git add" and/or "git commit -a")
 D:\testgit>git checkout slave
 D       file2.txt
 Switched to branch 'slave'
 D:\testgit>git status
 # On branch slave
 # Changes not staged for commit:
 #   (use "git add/rm <file>..." to update what will be committed)
 #   (use "git checkout -- <file>..." to discard changes in working directory)
 #
 #       deleted:    file2.txt
 #
 no changes added to commit (use "git add" and/or "git commit -a")
 D:\testgit>git add -A
 D:\testgit>git status
 # On branch slave
 # Changes to be committed:
 #   (use "git reset HEAD <file>..." to unstage)
 #
 #       deleted:    file2.txt
 #
 D:\testgit>git checkout master
 D       file2.txt
 Switched to branch 'master'
 D:\testgit>git status
 # On branch master
 # Changes to be committed:
 #   (use "git reset HEAD <file>..." to unstage)
 #
 #       deleted:    file2.txt
 #

So, our changes are not correlated with a branch until we commit them! Let's commit them to the master repository and confirm that:

.. code::

 D:\testgit>git commit -m "Deleted file2.txt"
 [master 6f8749d] Deleted file2.txt
  1 file changed, 1 deletion(-)
  delete mode 100644 file2.txt
 D:\testgit>git status
 # On branch master
 nothing to commit, working directory clean
 D:\testgit>dir file2.txt
 [...]
 File not found
 D:\testgit>git checkout slave
 Switched to branch 'slave'
 D:\testgit>git status
 # On branch slave
 nothing to commit, working directory clean
 D:\testgit>dir file2.txt
 [...]
 08/10/2013  05:59 pm                15 file2.txt

This is interesting... Let's try modifying the file2.txt (which does not exist to the master branch): 

.. code::

 D:\testgit>git branch
   master
 * slave
 D:\testgit>echo new file2 contents > file2.txt
 D:\testgit>git add .
 D:\testgit>git status
 # On branch slave
 # Changes to be committed:
 #   (use "git reset HEAD <file>..." to unstage)
 #
 #       modified:   file2.txt
 #
 D:\testgit>git checkout master
 error: Your local changes to the following files would be overwritten by checkout:
        file2.txt
 Please, commit your changes or stash them before you can switch branches.
 Aborting
 
We won't be able to change the current branch until we commit the conflicting change:
 
.. code::

 D:\testgit>git commit -m "Modified file2"
 [slave b5af832] Modified file2
  1 file changed, 1 insertion(+), 1 deletion(-)
 D:\testgit>git checkout master
 Switched to branch 'master'
 
Remote branches
---------------

For each local repository you can define a number of remote repositories, or remotes_ as git calls them.
When you clone a repository from github.com, your local repository will have one remote, named origin. We will
try to add the same remote by hand. Let's suppose that we have created a repository in github.com named
testgit. After that we wil issue:

.. code::

 D:\testgit>git remote
 D:\testgit>git remote add origin https://github.com/spapas/testgit.git
 D:\testgit>git remote
 origin
 
So no we have one remote named origin that is linked with https://github.com/spapas/testgit.git. Let's try to push our master
branch to the origin remote:

.. code::

 D:\testgit>git push origin master
 Username for 'https://github.com': spapas
 Password for 'https://spapas@github.com':
 Counting objects: 7, done.
 Delta compression using up to 4 threads.
 Compressing objects: 100% (5/5), done.
 Writing objects: 100% (7/7), 531 bytes, done.
 Total 7 (delta 1), reused 0 (delta 0)
 To https://github.com/spapas/testgit.git
  * [new branch]      master -> master  
 D:\testgit>git branch -r
   master
 * slave  
   remote/origin/master
   
We see now that we have *three* branches. Two local (master slave) and one remote (origin/master).  We will also add the slave remote (origin/slave):

.. code::

 D:\testgit>git branch -r
   origin/master
   origin/slave

Let's do a change to our local repository and then push them to the remote:

.. code::

 D:\testgit>notepad file3.txt
 D:\testgit>git add .
 D:\testgit>git status
 # On branch slave
 # Changes to be committed:
 #   (use "git reset HEAD <file>..." to unstage)
 #
 #       modified:   file3.txt
 #
 D:\testgit>git commit -m "Changed file3.txt"
 [slave ce3b7b9] Changed file3.txt
  1 file changed, 1 insertion(+), 1 deletion(-)
 D:\testgit>git push origin slave
 Username for 'https://github.com': spapas
 Password for 'https://spapas@github.com':
 Counting objects: 5, done.
 Delta compression using up to 4 threads.
 Compressing objects: 100% (3/3), done.
 Writing objects: 100% (3/3), 299 bytes, done.
 Total 3 (delta 1), reused 0 (delta 0)
 To https://github.com/spapas/testgit.git
    b5af832..ce3b7b9  slave -> slave  

Everything works as expected. The final thing to test is to try checking out a remote branch:

.. code::

 D:\testgit>git checkout master
 Switched to branch 'master'
 D:\testgit>echo new new file1 > file1.txt   
 D:\testgit>more file1.txt
  new new file1
 D:\testgit>git checkout origin/master
 M       file1.txt
 Note: checking out 'origin/master'.
 
 You are in 'detached HEAD' state. You can look around, make experimental
 changes and commit them, and you can discard any commits you make in this
 state without impacting any branches by performing another checkout.

 If you want to create a new branch to retain commits you create, you may
 do so (now or later) by using -b with the checkout command again. Example:

   git checkout -b new_branch_name

 HEAD is now at 6f8749d... Deleted file2.txt
 D:\testgit>git status
 # Not currently on any branch.
 # Changes not staged for commit:
 #   (use "git add <file>..." to update what will be committed)
 #   (use "git checkout -- <file>..." to discard changes in working directory)
 #
 #       modified:   file1.txt
 #
 no changes added to commit (use "git add" and/or "git commit -a")
 D:\testgit>more file1.txt
 new new file1
 
So, it seems that  when we check out the remote branch, we won't have any local branches, however the change we did to the file1.txt
is transfered just like when switching from one local repository to another. We can then add the changes and commit:

.. code::
 
 D:\testgit>git add .
 D:\testgit>git commit
 [detached HEAD 506674c] foo
  1 file changed, 1 insertion(+), 1 deletion(-)
  D:\testgit>git status
 # Not currently on any branch.
 nothing to commit, working directory clean
 D:\testgit>git branch
 * (no branch)
   master
   slave

So we are working with an unnamed branch! We have to name it to be able to work without problems:

.. code::

 D:\testgit>git checkout -b named_branch
 Switched to a new branch 'named_branch'
 D:\testgit>git branch
   master
 * named_branch
   slave

Finally we may push again the named_branch to our remote origin.   
   


.. _`github pages`: http://pages.github.com/
.. _remotes: http://git-scm.com/book/en/Git-Basics-Working-with-Remotes
.. _branch: http://git-scm.com/book/en/Git-Branching-What-a-Branch-Is

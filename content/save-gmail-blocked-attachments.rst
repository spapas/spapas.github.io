Retrieving Gmail blocked attachments
####################################

:date: 2014-10-23 14:20
:tags: gmail, python, security, google
:category: python
:slug: retrieve-gmail-blocked-attachments
:author: Serafeim Papastefanos
:summary: A method to retrieve blocked attachments from your Gmail


Before services like Dropbox were widely available, some people (including me) were using
their Gmail account as a primitive backup solution: Compress your directory and send it to
your gmail. There. Backup complete.

However, nothing is so easy...

Recently, I wanted to retrieve one of these backups, a .rar containing the complete
source code (since it was written in TeX) of my PhD thesis. The problem was that Gmail blocked the access to these attachments
saying 

 Anti-virus warning - 1 attachment contains a virus or blocked file. Downloading this attachment is disabled.

probably because I had a number of .bat files inside that .rar archive to automate my work :(

Now what ? 

After searching the internet and not founding any solutions, I tried the options that gmail gives for each email. One
particular one cought my interest: *Show original*

.. image:: /images/show_original.png
  :alt: Here it is!
  :width: 780 px

Clicking this option opened a text file with the original, MIME encoded message. The interesting thing of course was

.. code:: 

  ------=_NextPart_000_004F_01CA0AED.E63C2A30
  Content-Type: application/octet-stream;
        name="phdstuff.rar"
  Content-Transfer-Encoding: base64
  Content-Disposition: attachment;
        filename="phdstuff.rar"
  
  UmFyIRoHAM+QcwAADQAAAAAAAAB0f3TAgCwANAMAAFQEAAACRbXCx8lr9TodMwwAIAAAAG5ld2Zp
  bmFsLnR4dA3dEQzM082BF7sB+D3q6QPUNEfwG7vHQgNkiQDTkGvfhOE4mNltIJJlBFMOCQPzPeKD
  ...
  
  
So the whole attachment was contained in that text file, encoded in base64! Now I just
needed to extract it from the email and convert it back to binary. 

This was very easy to do using Python - some people `had already asked the same thing on SO`_.
So here's a simple program that gets an email in text/mime format as input and dumps all
attachments: 

.. code-block:: python

  import email
  import sys

  if __name__=='__main__':
      if len(sys.argv)<2:
          print "Please enter a file to extract attachments from"
          sys.exit(1)

      msg = email.message_from_file(open(sys.argv[1]))
      for pl in msg.get_payload():
          if pl.get_filename(): # if it is an attachment
              open(pl.get_filename(), 'wb').write(pl.get_payload(decode=True))
  
  
.. _`had already asked the same thing on SO`: http://stackoverflow.com/questions/4067937/getting-mail-attachment-to-python-file-object


Save this to a file named ``get_attachments.py`` and, after saving the original message to a file 
named ``0.txt`` run ``python get_attachments.py 0.txt`` and you'll see the attachments of your email in the same folder!

 Disclaimer: I have to warn you that since Gmail claims that an attachment is *not safe* it may be **actually not safe**. So 
 you must be 100% sure that you know what you are doing before retrievening your email attachments like this.
 
 
 
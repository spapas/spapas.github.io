Title: Multiple Erlang/Elixir versions in Windows
Date: 2024-08-22 15:20
Tags: erlang, elixir, windows
Category: elixir
Slug: multiple-erl-elixir-windows
Author: Serafeim Papastefanos
Summary: How to use multiple Erlang/Elixir versions in Windows

If you work in multiple projects that use different Erlang/Elixir versions, you may need to switch between them. Using the latest versions of Erlang and Elixir is definitely recommended, as they include many improvements and bug fixes, however this is not always possible. So one project may need Erlang/otp 25 with Elixir 1.14 and the other Erlang/otp 27 with Elixir 1.17. 

In Unix-like systems, this problem is easily solved with asdf, a version manager that handles multiple programming languages. However, asdf does not support Windows natively. While using Windows Subsystem for Linux (WSL) could be a solution, I personally prefer sticking to the traditional command prompt (cmd) for my workflow.




Fortunately, there is a solution for Windows users as well. It involves some manual path wrangling but shouldn't be too complicated if you follow the steps below.

## Step 1: Download and Install Erlang and Elixir

For starters we'll manually get and install the Erlang and Elixir version we want.

### Download Erlang

First, you'll need to get the correct versions of Erlang and Elixir for your project. As an example, I'll get Erlang 27.0.1 and Elixir 1.17.2. 

To get Erlang we'll go to https://www.erlang.org/downloads, select the version we want from the right menu and click Download Windows installer (64bit version). This is an .exe file named something like `otp_win64_27.0.1.exe`. 

Run run the installer and choose a unique directory for installation, ideally reflecting the Erlang version. I have installed it in `C:\progr\elixir\erlang27`. My erlang27 folder has the following structure:

```plaintext
C:\progr\elixir\erlang27>dir /w
 Volume in drive C is Windows
 Volume Serial Number is D8E3-76BA

 Directory of C:\progr\elixir\erlang27

[.]             [..]            [bin]           [erts-15.0.1]   Install.exe     Install.ini
[lib]           [releases]      Uninstall.exe   [usr]
               3 File(s)         77,202 bytes
               7 Dir(s)  346,058,203,136 bytes free
```               

### Download Elixir

For Elixir, we'll go to https://github.com/elixir-lang/elixir/releases and download the correct `.zip` file for our Erlang and Elixir version. I downloaded elixir-otp-27.zip (https://github.com/elixir-lang/elixir/releases/download/v1.17.2/elixir-otp-27.zip).

Unzip the downloaded Elixir package into a directory with a similar naming convention as the Erlang. I unzipped mine to `C:\progr\elixir\elixir117`. The structure of this folder should be similar to this:

```plaintext
C:\progr\elixir\elixir117>dir /w
 Volume in drive C is Windows
 Volume Serial Number is D8E3-76BA

 Directory of C:\progr\elixir\elixir117

[.]            [..]           [bin]          CHANGELOG.md   [lib]          LICENSE
Makefile       [man]          NOTICE         README.md      VERSION
               6 File(s)         45,871 bytes
               5 Dir(s)  345,943,388,160 bytes free
```               

## Step 2: Set Up the Path

Now that both Erlang and Elixir are installed, you need to configure the PATH environment variable so that your system knows where to find the specific versions you're working with. You can do this by creating a simple batch script.

To do that we'll create a `paths.bat` file with the following content:

```plaintext
@echo off
set PATH=C:\progr\elixir\erlang27\bin;C:\progr\elixir\elixir117\bin;%PATH%
```

This script file prepends the `bin` folders of the erlang and elixir we installed before to the `PATH` environment variable. The `;` is the path separator. So the PATH will be set to the bin subfolder of the folder we installed erlang, the bin subfolder of the folder we unzipped elixir followed by the rest of the PATH.

Even if we have other versions of Erlang and Elixir installed, the versions we set in the `paths.bat` file take precedence since they are *first* in the `PATH` environment variable.

I save the `paths.bat` inside my project's root folder so I can easily run it when switching to the project directory.

## Step 3: Activate the Paths and Verify Installation

Once your paths.bat file is ready, run it from the command prompt:

```plaintext
> paths.bat
```

and verify that the correct versions of Erlang and Elixir are being used by checking their versions:



```plaintext

> erl.exe
Erlang/OTP 27 [erts-15.0.1] [source] [64-bit] [smp:12:12] [ds:12:12:10] [async-threads:1] [jit:ns]

Eshell V15.0.1 (press Ctrl+G to abort, type help(). for help)
 
 # press ctrl+c twice to exit

> elixir.bat -v
Erlang/OTP 27 [erts-15.0.1] [source] [64-bit] [smp:12:12] [ds:12:12:10] [async-threads:1] [jit:ns]

Elixir 1.17.2 (compiled with Erlang/OTP 27)
```

If everything is set up correctly, you should see the version details matching your installation.

## Conclusion

That's it! You can now use multiple Erlang and Elixir versions in Windows. Just remember to run the `paths.bat` file before you start working on your project.


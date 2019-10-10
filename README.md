# Python-Text-MMORPG-Client

Firstly, make sure that Python and pip3 are installed on your computer. You will need pip3 to install the required libraries.

How to setup your own server and client for testing:

Then you need to clone the repository to your computer.

Extra step for windows users: To install some of the required libraries, you need to first download Microsoft Visual C++ from https://visualstudio.microsoft.com/downloads/ (This is only for the libraries used by the server, so you won't need this to connect to the development server)

Once that is done, you need to install the required libraries with pip3. To do that, open the shell of your OS, use cd to go to the location of the repository. In the repository should be a file called requirements.txt. That file contains the names of the libraries. To install them, make sure that you are in the right directory. Then type in the command 'pip3 install -r requirements.txt'.


Then, to start up the server and client, go to their respective directories (start with the server). If you're on a Unix platform, use the command 'python3 MakeDatabase.py' to create the database. Then you should be able to use the command 'python3 Server.py' to start up the server. If you're on Windows, use the commands 'py MakeDatabase.py -3' and 'py Server.py -3'. Then open up a new shell window for the client. Then on Unix, use 'python3 TextMMO.py' and 'py TextMMO.py -3' on Windows. To quit the client, use ctrl-q, and to stop the server do ctrl-c. If you encounter any bugs while testing, please let me know.

It might be that you will receive errors. When I tried to run the client and server on Linux, I still got some errors, and I needed to install some other things first. When this happens, it might be because of the cryptography module. To make sure you have all the dependencies for that installed, go to https://cryptography.io/en/latest/installation/#. When I tried tkinter also gave me problems, and for that I used the command 'sudo apt-get python3-tk'. You might still get errors (I haven't yet tried it on Windows), and if you do, please contact me.

For constant updates on my progress, follow me on Twitter @milo_tier.

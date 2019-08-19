# Python-Text-MMORPG

How to setup server and client for testing:

Firstly, make sure that Python and pip3 are installed on your computer. You will need pip3 to install the needed libraries.

Then you need to copy the repository to your computer.

Extra step for windows users: To install some of the required libraries, you need to first download Microsoft Visual C++ from https://visualstudio.microsoft.com/downloads/ (This is only for the libraries used by the server, so when the server will be hosted you won't need this to play)

Once that is done, you need to install the required libraries with pip3. To do that, open the shell of your OS, use cd to go to the location of the repository. In the repository should be a file called requirements.txt. That file contains the names of the libraries. To install them, make sure that you are in the right directory. Then type in the command 'pip3 install -r requirements.txt'. 

Then, to start up the server and client, go to their respective directories (start with the server). If you're on a Unix platform, use the command 'python3 MakeDatabase.py' to create the database. Then you should be able to use the command 'python3 Server.py' to start up the server. If you're on Windows, use the commands 'py MakeDatabase.py -3' and 'py Server.py -3'. Then open up a new shell window for the client. Then on Unix, use 'python3 TextMMO.py' and 'py TextMMO.py -3' on Windows. To quit the client, use ctrl-q, and to stop the server do ctrl-c. If you encounter any bugs while testing, please let me know.

For constant updates on my progress, follow me on Twitter @TierMilo.
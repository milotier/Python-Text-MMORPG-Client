# Python-Text-MMORPG-Client

How to connect to the development server:

Firstly, make sure that the latest versions of Python 3 and pip3 are installed on your computer. You will need pip3 to install the required libraries.

Then you need to clone the client repository to your computer.

Once that is done, you need to install the required libraries with pip3. To do that, open the shell of your OS, use cd to go to the location of the repository. In the repository should be a file called requirements.txt. That file contains the names of the libraries. To install them, make sure that you are in the right directory. Then type in the command 'pip3 install -r requirements.txt'.

Before you can connect, you have to make sure that in the config file in the repository folder at IP it says vdtier.nl and at port 5555. Those are also the default settings, so you probably don't have to change anything.

Then you just go to the repository folder and in the src folder in your terminal or command prompt and type the command 'python3 TextMMO.py' if you're on a Unix platform and 'py TextMMO.py -3' on Windows.

It might be that you will receive errors. When I tried to run the client and server on Linux, I still got some errors, and I needed to install some other things first. When this happens, it might be because of the cryptography module. To make sure you have all the dependencies for that installed, go to https://cryptography.io/en/latest/installation/#. When I tried tkinter also gave me problems, and for that I used the command 'sudo apt-get python3-tk'. You might still get errors (I haven't yet tried it on Windows), and if you do, please contact me.

For constant updates on my progress, follow me on Twitter @milo_tier.

##Systems Design Project - Group 7##

###Installation

[Python-nxt](https://code.google.com/p/nxt-python/) requires [bluez](http://www.bluez.org/) to be installed in order to communicate with the NXT over BlueTooth correctly. Assuming you are on a debian based Linux system, execute the following:

*sudo apt-get install bluez*.

To install the python library, navigate to *nxt-python* inside the *lib* directory and execute *sudo python setup.py install* to install the library globally. Alternatively, install *virtualenv* and do the following:

*virtualenv venv*<br>
*start ./venv/bin/activate*<br>
*sudo python setup.py install*<br>




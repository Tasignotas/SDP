##Systems Design Project - Group 7##

###Installation

[Python-nxt](https://code.google.com/p/nxt-python/) requires [bluez](http://www.bluez.org/) to be installed in order to communicate with the NXT over BlueTooth correctly. Assuming you are on a debian based Linux system, execute the following:

*sudo apt-get install bluez*.

To install the python library, navigate to *nxt-python* inside the *lib* directory and execute *sudo python setup.py install* to install the library globally. Alternatively, install *virtualenv* and do the following:

*virtualenv venv*<br>
*start ./venv/bin/activate*<br>
*sudo python setup.py install*<br>

### Vision

* At the moment OpenCV + Python are being used. A [book](http://programmingcomputervision.com/downloads/ProgrammingComputerVision_CCdraft.pdf) on Computer Vision with OpenCV in Python is a decent starting point about what OpenCV can do.
* A detailed tutorial with examples and use cases can be found [here](https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_tutorials.html) - going through it can be handy to understand the code
* For OpenCV installation instructions please get in touch with others or have a look at the scripts in *vision/*

### Installing OpenCV on OS X
The problem with installing OpenCV on OS X is because the Python library was installed in the wrong directory. To fix this..:
* Go to usr/local/share/bin
* Copy the contents from python2.7/site-packages to /Library/Python/2.7/site-packages

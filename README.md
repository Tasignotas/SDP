##Systems Design Project - Group 7##

*Rowan Border, Grant Kelly, Victor Dumitrescu, Ryan Davies, Ignotas Sulzenko, Martin Dimitrov, Maneshka Paiva, Mac Chong, Milan Pavlik*

![alt text](http://i.imgur.com/5zEjxX8.jpg "Too Innovative")
------


###Future SDP teams
The planner and vision are very good.

We used an Arduino powered robot but the vision and planning can be effectively used even with the default NXT Brick. All it takes is to modify the Controller class in `controller.py`. 

The vision is very accurate with the correct calibration and achieves around 28 FPS (faster than the camera).
Planner is based on a reactive system. The defender strategy was one of the best in 2014 and the latest attacker strategy worked very well. In the end, it all depends on the build of the robot.

###Running the system

In the root of the project, execute `python controller.py <pitch_number> <our_side> <our_color>` where *pitch_number* is either 0 for the main pitch and 1 for the secondary pitch. Colors are regular yellow and blue. Side can be either left or right.

####Vision controls
Press the following keys to switch the thresholding scheme:
*r* - red
*p* - plate
*b* - black dots

Note that the colors of the plates themselves are ignored - you don't need them.


------
###Installation

#### Linux/DICE

To install the Polygon library, download the [source](https://bitbucket.org/jraedler/polygon2/downloads/Polygon2-2.0.6.zip), navigate inside and execute `python setup.py install --user`.

To isntall Argparse for python, download [ArgParse](http://argparse.googlecode.com/files/argparse-1.2.1.tar.gz), extract and run `python setup.py install --user`. All done.

There are a couple more libraries required:
*serial* - can be removed if bluetooth is to be used (Use *python-nxt* to control the robot over bluetooth - *bluez* required)



#### Debian with root access
[Python-nxt](https://code.google.com/p/nxt-python/) requires [bluez](http://www.bluez.org/) to be installed in order to communicate with the NXT over BlueTooth correctly. Assuming you are on a debian based Linux system, execute the following:

*sudo apt-get install bluez*.

To install the python library, navigate to *nxt-python* inside the *lib* directory and execute *sudo python setup.py install* to install the library globally. Alternatively, install *virtualenv* and do the following:

*virtualenv venv*<br>
*start ./venv/bin/activate*<br>
*sudo python setup.py install*<br>

------
### Vision

* At the moment OpenCV + Python are being used. A [book](http://programmingcomputervision.com/downloads/ProgrammingComputerVision_CCdraft.pdf) on Computer Vision with OpenCV in Python is a decent starting point about what OpenCV can do.
* A detailed tutorial with examples and use cases can be found [here](https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_tutorials.html) - going through it can be handy to understand the code
* For OpenCV installation instructions please get in touch with others or have a look at the scripts in *vision/*

------
### Installing OpenCV

#### Linux/DICE
* Download [OpenCV](http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.8/opencv-2.4.8.zip/download)
* Extract the contents
* When on computers with with video feed, navigate to */disk/scratch/sdp/* and create a directory for OpenCV
* Copy extracted contents over to this directory
* Create directory `build` and navigate inside
* Execute 
```
cmake -D CMAKE_INSTALL_PREFIX=~/.local ..` or *cmake -D WITH_OPENCL=OFF -D WITH_CUDA=OFF -D BUILD_opencv_gpu=OFF -D BUILD_opencv_gpuarithm=OFF -D BUILD_opencv_gpubgsegm=OFF -D BUILD_opencv_gpucodec=OFF -D BUILD_opencv_gpufeatures2d=OFF -D BUILD_opencv_gpufilters=OFF -D BUILD_opencv_gpuimgproc=OFF -D BUILD_opencv_gpulegacy=OFF -D BUILD_opencv_gpuoptflow=OFF -D BUILD_opencv_gpustereo=OFF -D BUILD_opencv_gpuwarping=OFF -D CMAKE_INSTALL_PREFIX=~/.local ..
```
to install without GPU libraries
* Execute `make` and wait (for quite some time)
* Execute `make install`
* Run `ipython` and do `import cv2`, if all executes fine then you're set.


#### Installing OpenCV on OS X
The problem with installing OpenCV on OS X is because the Python library was installed in the wrong directory. To fix this..:
* Go to *usr/local/share/bin*
* Copy the contents from *python2.7/site-packages* to */Library/Python/2.7/site-packages*

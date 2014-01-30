#! /bin/bash
 
STARTDIR=$(pwd)
INSTALL_PREFIX="$STARTDIR"/libs
 
PYTHON_PATH="$INSTALL_PREFIX"/lib/python2.6/site-packages
 
mkdir -p "$INSTALL_PREFIX"
mkdir -p "$PYTHON_PATH"
 
export LOCALBASE="$INSTALL_PREFIX"
export PYTHONPATH="$PYTHONPATH:$PYTHON_PATH" # easy_install needs python path to be set up
 
# Add path to pythonpath
#STR="export PYTHONPATH=\$PYTHONPATH:$PYTHON_PATH"
#grep -Fxq "$STR" ~/.bashrc || echo "$STR" >> ~/.bashrc
 
echo "Installing OpenCV..."
 
cd /disk/scratch/sdp/
git clone git://code.opencv.org/opencv.git

mkdir /disk/scratch/sdp/opencv/release
#cd /disk/scratch/sdp/opencv/
 
cmake -DCMAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" -DWITH_FFMPEG=OFF -DBUILD_NEW_PYTHON_SUPPORT=ON ..
#make && make install
 
#cd "$STARTDIR"
#rm -rf /tmp/opencv_svn
 
echo "Installing PyGame"
mkdir tmp/
cd tmp
 
# Install sdl_font module
wget http://www.libsdl.org/projects/SDL_ttf/release/SDL_ttf-2.0.11.tar.gz
tar -xzvf SDL_ttf-2.0.11.tar.gz
cd SDL_ttf-2.0.11
./configure --prefix="$INSTALL_PREFIX"
make && make install
 
cd "$STARTDIR"
rm -rf tmp/
 
easy_install --prefix="$INSTALL_PREFIX" pygame
 
echo "installing SimpleCV"
easy_install --prefix="$INSTALL_PREFIX" simplecv

#! /bin/bash

cd ~/.local
STARTDIR=$(pwd)
echo "Creating temp directory"
mkdir tmp
cd tmp

echo "Downloading and extracting"
wget https://pybluez.googlecode.com/files/PyBluez-0.18.tar.gz
wget http://bluez.sf.net/download/bluez-libs-3.36.tar.gz
wget http://bluez.sf.net/download/bluez-utils-3.36.tar.gz
wget http://nxt-python.googlecode.com/files/nxt-python-2.2.2.tar.gz
tar -xzvf bluez-libs-3.36.tar.gz
tar -xzvf bluez-utils-3.36.tar.gz
tar -xzvf PyBluez-0.18.tar.gz
tar -xzvf nxt-python-2.2.2.tar.gz

echo "Installing bluez"
cd bluez-libs-3.36
./configure --prefix="$STARTDIR"
make
make install

cd ../bluez-utils-3.36
./configure --prefix="$STARTDIR"
make
make install

echo "Installing pyBluez"
cd ../PyBluez-0.18
python setup.py build_ext --user
python setup.py install --user


echo "Installing nxt-python"
cd ../nxt-python-2.2.2
python setup.py install --user

cd ~/.local

echo "Removing temp directory"
rm -rf tmp/

echo "Done"

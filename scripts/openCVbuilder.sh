# openCVbuilder.sh - A shell script to build a local copy of openCV in DICE..
unzip opencv-2.4.8
cd opencv-2.4.8
sed -i '50 d' ./cmake/cl2cpp.cmake
mkdir build
cd build
cmake -D BUILD_DOCS=ON -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF ..
make
make install

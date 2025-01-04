FROM python:3.13.0b4-bullseye

RUN apt-get update \
&& apt-get install -y gfortran dcmtk libgdcm-tools  libvtkgdcm-tools \
plastimatch \
cmake \
libgtk2.0-dev \
libavcodec-dev \
libavformat-dev \
libswscale-dev  vtk-dicom-tools libgdcm-tools \
libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libpng-dev libjpeg-dev libopenexr-dev \
libtiff-dev libwebp-dev \
g++ make git cmake-curses-gui \
libblas-dev liblapack-dev libsqlite3-dev \
libdcmtk-dev libdlib-dev libfftw3-dev \
libinsighttoolkit4-dev \
libpng-dev libtiff-dev uuid-dev zlib1g-dev  build-essential imagemagick  python3-dev


RUN pip install --upgrade pip setuptools wheel  
RUN pip install numpy cython pybind11

COPY requirements.txt requirements.txt 
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -U setuptools pip


EXPOSE 9999 

WORKDIR /var
CMD ["bash"]
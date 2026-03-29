FROM --platform=linux/arm64 ubuntu:22.04

####### Activationg NonIteractive Mode #######
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
####### Common Setup #####
RUN apt-get update
RUN apt-get install -y software-properties-common
###### ROS2 Humble installation ########
#####Set locale
RUN locale  # check for UTF-8

RUN apt update &&  apt install locales
RUN locale-gen en_US.UTF-8
RUN update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
ENV LANG=en_US.UTF-8

RUN locale  # verify settings

####Setup Sources
RUN apt install -y software-properties-common
RUN add-apt-repository universe

RUN apt update &&  apt install curl -y
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" |  tee /etc/apt/sources.list.d/ros2.list > /dev/null

####Install ROS 2 packages
RUN apt update
RUN apt upgrade -y

RUN apt-get update && apt install -y ros-humble-ros-base ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rviz2 ros-humble-rviz-imu-plugin ros-humble-tf2-ros ros-humble-launch-ros

RUN apt install -y ros-dev-tools

######## Install python3
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#### Environment setup
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN bash /opt/ros/humble/setup.bash
WORKDIR /workspace


#### IMU Setup #####
RUN pip install pyserial
### WIFI commiunication setting 
ENV ROS_DOMAIN_ID=0
ENV ROS_LOCALHOST_ONLY=0
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
######### Entry ######
CMD /bin/bash


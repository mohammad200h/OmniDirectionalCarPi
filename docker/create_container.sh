
sudo docker run -it --name ros2 \
  -v $(pwd)/../../OmniDirectionalCar:/workspace \
  --device=/dev/ttyUSB0:/dev/ttyUSB0 \
  --net=host --privileged omni_directional_car_pi

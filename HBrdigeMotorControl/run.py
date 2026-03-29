from motor import (
  Motor,
  Direction,
  Speed,
  intailize_pi,
  clean_pi
)

import json
from time import sleep

def forward(m1, m2, m3, m4):
  m1.set_direction(Direction.Forward)
  m1.set_speed(Speed.Medium)
  m2.set_direction(Direction.Forward)
  m2.set_speed(Speed.Medium)
  m3.set_direction(Direction.Forward)
  m3.set_speed(Speed.Medium)
  m4.set_direction(Direction.Forward)
  m4.set_speed(Speed.Medium)

def backward(m1, m2, m3, m4):
  m1.set_direction(Direction.Backward)
  m1.set_speed(Speed.Medium)
  m2.set_direction(Direction.Backward)
  m2.set_speed(Speed.Medium)
  m3.set_direction(Direction.Backward)
  m3.set_speed(Speed.Medium)
  m4.set_direction(Direction.Backward)
  m4.set_speed(Speed.Medium)
  
def stop(m1, m2, m3, m4):
  m1.set_direction(Direction.Stop)
  m1.set_speed(Speed.Stop)
  m2.set_direction(Direction.Stop)
  m2.set_speed(Speed.Stop)
  m3.set_direction(Direction.Stop)
  m3.set_speed(Speed.Stop)
  m4.set_direction(Direction.Stop)
  m4.set_speed(Speed.Stop)

def left(m1, m2, m3, m4):
  m1.set_direction(Direction.Backward)
  m1.set_speed(Speed.High)
  m2.set_direction(Direction.Forward)
  m2.set_speed(Speed.High)
  m3.set_direction(Direction.Backward)
  m3.set_speed(Speed.High)
  m4.set_direction(Direction.Forward)
  m4.set_speed(Speed.High)


def main():
  motors_setting = None
  with open("./config.json", "r") as f:
    motors_setting = json.load(f)

  
  clean_pi()
  intailize_pi()

  m1 = Motor(**motors_setting["HbridgeOne"]["MotorOne"])
  m2 = Motor(**motors_setting["HbridgeOne"]["MotorTwo"])
  m3 = Motor(**motors_setting["HbridgeTwo"]["MotorOne"])
  m4 = Motor(**motors_setting["HbridgeTwo"]["MotorTwo"])


  # forward(m1, m2, m3, m4)
  # backward(m1, m2, m3, m4)


 
  while True:
    x = input("Enter a command:(w/s/a/d) ")
    if x == "w":
      print("Moving forward")
      forward(m1, m2, m3, m4)
    elif x == "s":
      print("Moving backward")
      backward(m1, m2, m3, m4)
    elif x == " ":
      print("Stopping the car")
      stop(m1, m2, m3, m4)
    elif x == "a":
      print("Moving left")
      left(m1, m2, m3, m4)
    # elif x == "d":
    #   print("Moving right")
    #   right(m1, m2, m3, m4)





if __name__ =="__main__":
  main()
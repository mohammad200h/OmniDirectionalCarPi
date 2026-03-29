from enum import Enum

import RPi.GPIO as GPIO    

def intailize_pi():
  GPIO.setmode(GPIO.BCM)

def clean_pi():
  GPIO.cleanup()

class Direction(Enum):
  Forward = 1
  Backward = 0
  Stop = 2

class Speed(Enum):
  # Duty Cycles
  Stop = 0
  Low = 25
  Medium = 50
  High = 75

class Motor:
  def __init__(self, in1, in2, en):
    self.in1 = in1
    self.in2 = in2
    self.en = en

    print(f"Motor::self.in1::type::{type(self.in1)}{self.in1}")
    print(f"Motor::self.in2::type::{type(self.in2)}{self.in2}")
    print(f"Motor::self.en::type::{type(self.en)}{self.en}")

    # Set pins to output
    GPIO.setup(self.in1, GPIO.OUT)
    GPIO.setup(self.in2, GPIO.OUT)
    GPIO.setup(self.en, GPIO.OUT)

    # Set pins to 0v
    GPIO.output(self.in1, GPIO.LOW)
    GPIO.output(self.in2, GPIO.LOW)

    # Start PWM
    frequency = 1000
    duty_cycle = 25
    self.p = GPIO.PWM(self.en, frequency)
    self.p.start(25)

    # State
    self.direction = Direction.Stop
    self.p.ChangeDutyCycle(25)



  def set_direction(self, direction:Direction):
    self.direction = direction
    if direction == Direction.Forward:
      GPIO.output(self.in1, GPIO.HIGH)
      GPIO.output(self.in2, GPIO.LOW)
    elif direction == Direction.Backward:
      GPIO.output(self.in1,GPIO.LOW)
      GPIO.output(self.in2,GPIO.HIGH)
    elif direction == Direction.Stop:
      GPIO.output(self.in1, GPIO.LOW)
      GPIO.output(self.in2, GPIO.LOW)
    else:
      raise ValueError("Invalid direction")
  
  def set_speed(self, speed:Speed):
    if not isinstance(speed, Speed):
      raise ValueError(""" Wrong input!
      Valid inputs are: Speed.Stop, Speed.Low, Speed.Medium, Speed.High
      """)
    self.p.ChangeDutyCycle(speed.value)
    






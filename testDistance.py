#coding:utf-8
from socket import *
from time import ctime
import binascii
import RPi.GPIO as GPIO
import time
import threading

#####信号引脚定义######
GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

#####set the interface for the ultra wave####
ECHO = 4 ###RECEIVE###
TRIG = 17 ### SEND ####


GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW) ## set the sending signals
GPIO.setup(ECHO, GPIO.IN, pull_up_down=GPIO.PUD_UP) ## set the receiving signals


#######################
## func name: get_Distance()
## function: detect the distance and print it out

def get_Distance():
  time.sleep(0.05)
  GPIO.output(TRIG, GPIO.HIGH)
  time.sleep(0.000015)
  GPIO.output(TRIG, GPIO.LOW)
  t1 = time.time()
  while not GPIO.input(ECHO):
    pass
  
  while GPIO.input(ECHO):
   pass 
  t2 = time.time()

  time.sleep(0.1)
  return (t2-t1)*340/2*100

while True:
  print("distance:", get_Distance(), " cm")
  time.sleep(1)

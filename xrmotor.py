#coding:utf-8
#Python中声明文件编码的注释，编码格式指定为utf-8
from socket import *
from time import ctime
import binascii
import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

########电机驱动接口定义#################
ENA = 13	#//L298使能A
ENB = 20	#//L298使能B
IN1 = 19	#//电机接口1
IN2 = 16	#//电机接口2
IN3 = 21	#//电机接口3
IN4 = 26	#//电机接口4

#########电机初始化为LOW##########
GPIO.setup(ENA,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(ENB,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN3,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN4,GPIO.OUT,initial=GPIO.LOW)

#########定义电机正转函数##########
def gogo():
	print 'motor gogo'
	GPIO.output(ENA,True)
	GPIO.output(IN1,True)
	GPIO.output(IN2,False)
	
	GPIO.output(ENB,True)
	GPIO.output(IN3,True)
	GPIO.output(IN4,False)

#########定义电机反转函数##########
def back():
	print 'motor_back'
	GPIO.output(ENA,True)
	GPIO.output(IN1,False)
	GPIO.output(IN2,True)
	
	GPIO.output(ENB,True)
	GPIO.output(IN3,False)
	GPIO.output(IN4,True)

#########定义电机停止函数##########
def stop():
	print 'motor_stop'
	GPIO.output(ENA,False)
	GPIO.output(ENB,False)
	GPIO.output(IN1,False)
	
	GPIO.output(IN2,False)
	GPIO.output(IN3,False)
	GPIO.output(IN4,False)	
	
	
'''
整个实验是
正转500ms
反转500ms
'''
i=0
while i<2:
	gogo();
	time.sleep(0.5)
	stop();
	time.sleep(0.1)
	back();
	time.sleep(0.5)
	i=i+1
	stop();

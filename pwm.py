#coding:utf-8
#Python中声明文件编码的注释，编码格式指定为utf-8
import time				#导入time库，可使用时间函数。
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)	##信号引脚模式定义，使用.BCM模式
PWM1 = 13				##PWM波形的IO口定义
GPIO.setwarnings(False)

####PWM初始化，并设置频率为50HZ####
GPIO.setup(PWM1,GPIO.OUT,initial=GPIO.LOW)	#初始化 
Servo1 = GPIO.PWM(PWM1,50) 					#50HZ  
Servo1.start(0)								#启动PWM波形
def SetServo1Angle(angle):					#定义舵机角度函数
	print 'angle = %d'% angle				#打印舵机角度
	Servo1.ChangeDutyCycle(2.5 + 10 * angle / 180) #设置舵机转动角度 
	
for i in range(1,5):		#调用rang（）循环函数，功能类似 for（i =1;i<5;i++ ）执行4遍
	SetServo1Angle(30)			##设置舵机角度30°
	time.sleep(0.1)
	Servo1.ChangeDutyCycle(0)
	time.sleep(0.4)
	SetServo1Angle(90)			##设置舵机角度90°
	time.sleep(0.1)
	Servo1.ChangeDutyCycle(0)
	time.sleep(0.4)
	SetServo1Angle(150)			##设置舵机角度150°
	time.sleep(0.1)
	Servo1.ChangeDutyCycle(0)
	time.sleep(0.4)
	SetServo1Angle(90)			##设置舵机角度90°
	time.sleep(0.1)
	Servo1.ChangeDutyCycle(0)
	time.sleep(0.4)
'''
整个程序功能为：
	舵机循环转动4次，并打印当前角度
	程序结束
'''


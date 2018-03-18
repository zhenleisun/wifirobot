#coding:utf-8
'''
WiFI Car 服务端程序
作者：Alex Sun
程序采用Socket通信，服务端接收指令并根据相应的指令完成相应的动作。

现在支持的指令协议如下：
  协议共5个byte，其中开头第一个byte为FF，结尾最后一个byte也是FF，用于基本校验。其他3个byte的定义如下：
  第二字节一般表示命令模式，第三字节根据模式不同有不同的定义。具体说明如下：
  第二字节为：
    00 小车运动方向控制，其中
        FF 00 0000 FF 表示停止
        FF 00 0100 FF 表示前进
        FF 00 0200 FF 表示后退
        FF 00 0300 FF 表示左转
        FF 00 0400 FF 表示右转
        FF 00 0500 FF 表示左转0.5s后前进
        FF 00 0600 FF 表示右转0.5s后前进
        FF 00 0700 FF 表示左转0.5s后后退
        FF 00 0800 FF 表示右转0.5s后后退
    01 调整舵机，此模式下：
        第三字节为表示舵机号码，现在小车物理链接到7、8号舵机上，7号为水平运动，8号为垂直运动
        第四字节暂时没有太大意义，现在每次接收一个指令，会运动固定的角度，程序设定为15度。
        具体指令如下：
        FF 01 0100 FF 表示调整1号舵机
        FF 01 0200 FF 表示调整2号舵机
        FF 01 0300 FF 表示调整3号舵机
        FF 01 0400 FF 表示调整4号舵机
        FF 01 0500 FF 表示调整5号舵机
        FF 01 0600 FF 表示调整6号舵机
        FF 01 0700 FF 表示调整7号舵机
        FF 01 0800 FF 表示调整8号舵机
    02 调整马达运行速率，此模式下：
        第三字节表示要调整的马达号码，第四字节表示马达速率。
        具体指令如下：
        FF 02 0000 FF 表示恢复默认马达速度，默认值为100。
        FF 02 01xx FF 表示调整1号马达速度。xx为具体数值，表示调整的速度值。
        FF 02 02xx FF 表示调整2号马达速度。xx为具体数值，表示调整的速度值
    04 走马灯测试，具体指令如下：
        FF 04 0000 FF 表示打开指示灯
        FF 04 0100 FF 表示关闭指示灯
        FF 04 0200 FF 表示打开走马灯

现在只支持以上的指令。后续根据功能，还会继续完善。
'''


from socket import *
from time import ctime
import binascii
import RPi.GPIO as GPIO
import time
import threading
from smbus import SMBus


XRservo = SMBus(1)
print '!!! Robot Alex Start!!!'


#######################################
#############信号引脚定义##############
#######################################
GPIO.setmode(GPIO.BCM)

########LED口定义#################
LED0 = 10
LED1 = 9
LED2 = 25

########电机驱动接口定义#################
ENA = 13	#//L298使能A
ENB = 20	#//L298使能B
IN1 = 19	#//电机接口1
IN2 = 16	#//电机接口2
IN3 = 21	#//电机接口3
IN4 = 26	#//电机接口4

########舵机接口定义#################

########超声波接口定义#################
ECHO = 4	#超声波接收脚位  
TRIG = 17	#超声波发射脚位

########红外传感器接口定义#################
IR_R = 18	#小车右侧巡线红外
IR_L = 27	#小车左侧巡线红外
IR_M = 22	#小车中间避障红外
IRF_R = 23	#小车跟随右侧红外
IRF_L = 24	#小车跟随左侧红外
global Cruising_Flag
Cruising_Flag = 0	#//当前循环模式
global Pre_Cruising_Flag
Pre_Cruising_Flag = 0 	#//预循环模式
buffer = ['00','00','00','00','00','00']

#######################################
#########管脚类型设置及初始化##########
#######################################
GPIO.setwarnings(False)

#########led初始化为000##########
GPIO.setup(LED0,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(LED1,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(LED2,GPIO.OUT,initial=GPIO.HIGH)

#########电机初始化为LOW##########
GPIO.setup(ENA,GPIO.OUT,initial=GPIO.LOW)
ENA_pwm=GPIO.PWM(ENA,1000) 
ENA_pwm.start(0) 
ENA_pwm.ChangeDutyCycle(100)
GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(ENB,GPIO.OUT,initial=GPIO.LOW)
ENB_pwm=GPIO.PWM(ENB,1000) 
ENB_pwm.start(0) 
ENB_pwm.ChangeDutyCycle(100)
GPIO.setup(IN3,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN4,GPIO.OUT,initial=GPIO.LOW)



#########红外初始化为输入，并内部拉高#########
GPIO.setup(IR_R,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_L,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_M,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IRF_R,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IRF_L,GPIO.IN,pull_up_down=GPIO.PUD_UP)



##########超声波模块管脚类型设置#########
GPIO.setup(TRIG,GPIO.OUT,initial=GPIO.LOW)#超声波模块发射端管脚设置trig
GPIO.setup(ECHO,GPIO.IN,pull_up_down=GPIO.PUD_UP)#超声波模块接收端管脚设置echo



####################################################
##函数名称 Open_Light()
##函数功能 开大灯LED0
##入口参数 ：无
##出口参数 ：无
####################################################
def	Open_Light():#开大灯LED0
	GPIO.output(LED0,False)#大灯正极接5V  负极接IO口
	time.sleep(1)

####################################################
##函数名称 Close_Light()
##函数功能 关大灯
##入口参数 ：无
##出口参数 ：无
####################################################
def	Close_Light():#关大灯
	GPIO.output(LED0,True)#大灯正极接5V  负极接IO口
	time.sleep(1)
	
####################################################
##函数名称 init_light()
##函数功能 流水灯
##入口参数 ：无
##出口参数 ：无
####################################################
def	init_light():#流水灯
	for i in range(1, 5):
		GPIO.output(LED0,False)#流水灯LED0
		GPIO.output(LED1,False)#流水灯LED1
		GPIO.output(LED2,False)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,True)#流水灯LED0
		GPIO.output(LED1,False)#流水灯LED1
		GPIO.output(LED2,False)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,False)#流水灯LED0
		GPIO.output(LED1,True)#流水灯LED1
		GPIO.output(LED2,False)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,False)#流水灯LED0
		GPIO.output(LED1,False)#流水灯LED1
		GPIO.output(LED2,True)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,False)#流水灯LED0
		GPIO.output(LED1,False)#流水灯LED1
		GPIO.output(LED2,False)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,True)#流水灯LED0
		GPIO.output(LED1,True)#流水灯LED1
		GPIO.output(LED2,True)#流水灯LED2
##########机器人方向控制###########################
def Motor_Forward():
	print 'motor forward'
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,True)
	GPIO.output(IN2,False)
	GPIO.output(IN3,True)
	GPIO.output(IN4,False)
	GPIO.output(LED1,False)#LED1亮
	GPIO.output(LED2,False)#LED1亮
	
def Motor_Backward():
	print 'motor_backward'
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,False)
	GPIO.output(IN2,True)
	GPIO.output(IN3,False)
	GPIO.output(IN4,True)
	GPIO.output(LED1,True)#LED1灭
	GPIO.output(LED2,False)#LED2亮
	
def Motor_TurnLeft():
	print 'motor_turnleft'
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,True)
	GPIO.output(IN2,False)
	GPIO.output(IN3,False)
	GPIO.output(IN4,True)
	GPIO.output(LED1,False)#LED1亮
	GPIO.output(LED2,True) #LED2灭
def Motor_TurnRight():
	print 'motor_turnright'
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,False)
	GPIO.output(IN2,True)
	GPIO.output(IN3,True)
	GPIO.output(IN4,False)
	GPIO.output(LED1,False)#LED1亮
	GPIO.output(LED2,True) #LED2灭
def Motor_Stop():
	print 'motor_stop'
	GPIO.output(ENA,False)
	GPIO.output(ENB,False)
	GPIO.output(IN1,False)
	GPIO.output(IN2,False)
	GPIO.output(IN3,False)
	GPIO.output(IN4,False)
	GPIO.output(LED1,True)#LED1灭
	GPIO.output(LED2,True)#LED2亮
	
##########机器人方向校准（模式中使用）###########################

##########机器人速度控制###########################
def ENA_Speed(EA_num):
	speed=hex(eval('0x'+EA_num))
	speed=int(speed,16)
	print 'EA_A改变啦 %d '%speed
	ENA_pwm.ChangeDutyCycle(speed)

def ENB_Speed(EB_num):
	speed=hex(eval('0x'+EB_num))
	speed=int(speed,16)
	print 'EB_B改变啦 %d '%speed
	ENB_pwm.ChangeDutyCycle(speed)	

##函数功能 ：舵机控制函数
##入口参数 ：ServoNum(舵机号)，angle_from_protocol(舵机角度)
##出口参数 ：无
####################################################
def Angle_cal(angle_from_protocol):
	angle=hex(eval('0x'+angle_from_protocol))
	angle=int(angle,16)
	if angle > 160:
		angle=160
	elif angle < 15:
		angle=15
	return angle
	
def SetServoAngle(ServoNum,angle_from_protocol):
	GPIO.output(LED0,False)
	GPIO.output(LED1,True)
	GPIO.output(LED2,False)
	time.sleep(0.01)
	GPIO.output(LED0,True)
	GPIO.output(LED1,True)
	GPIO.output(LED2,True)
	if ServoNum== 1:
		XRservo.XiaoRGEEK_SetServo(0x01,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 2:
		XRservo.XiaoRGEEK_SetServo(0x02,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 3:
		XRservo.XiaoRGEEK_SetServo(0x03,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 4:
		XRservo.XiaoRGEEK_SetServo(0x04,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 5:
		XRservo.XiaoRGEEK_SetServo(0x05,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 6:
		XRservo.XiaoRGEEK_SetServo(0x06,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 7:
		XRservo.XiaoRGEEK_SetServo(0x07,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 8:
		XRservo.XiaoRGEEK_SetServo(0x08,Angle_cal(angle_from_protocol))
		return
	else:
		return

####################################################
##函数名称 ：Avoiding()
##函数功能 ：红外避障函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	Avoiding(): #红外避障函数
	if GPIO.input(IR_M) == False:
		Motor_Stop()
		time.sleep(0.1)
		return


####################################################
##函数名称 ：Get_Distence()
##函数功能 超声波测距，返回距离（单位是厘米）
##入口参数 ：无
##出口参数 ：无
####################################################
def	Get_Distence():
	time.sleep(0.1)
	GPIO.output(TRIG,GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(TRIG,GPIO.LOW)
	while not GPIO.input(ECHO):
				pass
	t1 = time.time()
	while GPIO.input(ECHO):
				pass
	t2 = time.time()
	time.sleep(0.1)
	return (t2-t1)*340/2*100

####################################################
##函数名称 AvoidByRadar()
##函数功能 超声波避障函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	AvoidByRadar(distance):
	dis = int(Get_Distence())
	if(distance<10):
		distance = 10					#限定最小避障距离为10cm
	if((dis>1)&(dis < distance)):		#避障距离值(单位cm)，大于1是为了避免超声波的盲区
		Motor_Stop()
	
		
def	Avoid_wave():
	dis = Get_Distence()
	if dis<15:
		Motor_Stop()
	else:
		Motor_Forward()


####################################################
##函数名称 Send_Distance()
##函数功能 ：超声波距离PC端显示
##入口参数 ：无
##出口参数 ：无
####################################################
def	Send_Distance():
	dis_send = int(Get_Distence())
	#dis_send = str("%.2f"%dis_send)
	if dis_send < 255:
		print 'Distance: %d cm' %dis_send
		tcpCliSock.send("\xFF")
		time.sleep(0.005)
		tcpCliSock.send("\x03")
		time.sleep(0.005)
		tcpCliSock.send("\x00")
		time.sleep(0.005)
		tcpCliSock.send(chr(dis_send))
		time.sleep(0.005)
		tcpCliSock.send("\xFF")
		time.sleep(0.1)


####################################################
##函数名称 Cruising_Mod()
##函数功能 ：模式切换函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	Cruising_Mod(func):
	print 'into Cruising_Mod-01'
	global Pre_Cruising_Flag
	print 'Pre_Cruising_Flag %d '%Pre_Cruising_Flag
	
	global Cruising_Flag
	print 'Cruising_Flag %d '%Cruising_Flag
	while True:
		if (Pre_Cruising_Flag != Cruising_Flag):			
			if (Pre_Cruising_Flag != 0):
				Motor_Stop()
			Pre_Cruising_Flag = Cruising_Flag
			print 'Pre_Cruising_Flag = Cruising_Flag == 0'
		elif (Cruising_Flag == 4):	#进入超声波壁障模式##
			Avoid_wave()
		else:
			time.sleep(0.001)
		time.sleep(0.001)
####################################################
##函数名称 Communication_Decode()
##函数功能 ：通信协议解码
##入口参数 ：无
##出口参数 ：无
####################################################    
def Communication_Decode():
	global Pre_Cruising_Flag
	global Cruising_Flag
	print 'Communication_decoding...'
	if buffer[0]=='00':
		if buffer[1]=='01':				#前进
			Motor_Forward()
		elif buffer[1]=='02':			#后退
			Motor_Backward()
		elif buffer[1]=='03':			#左转
			Motor_TurnLeft()
		elif buffer[1]=='04':			#右转
			Motor_TurnRight()
		elif buffer[1]=='00':			#停止
			Motor_Stop()
		else:
			Motor_Stop()
	elif buffer[0]=='02':
		if buffer[1]=='01':#左速度
			ENA_Speed(buffer[2])
		elif buffer[1]=='02':#右侧速度
			ENB_Speed(buffer[2])			
	elif buffer[0]=='01':
		if buffer[1]=='01':#1号舵机驱动
			SetServoAngle(1,buffer[2])
		elif buffer[1]=='02':#2号舵机驱动
			SetServoAngle(2,buffer[2])
		elif buffer[1]=='03':#3号舵机驱动
			SetServoAngle(3,buffer[2])
		elif buffer[1]=='04':#4号舵机驱动
			SetServoAngle(4,buffer[2])
		elif buffer[1]=='05':#5号舵机驱动
			SetServoAngle(5,buffer[2])
		elif buffer[1]=='06':#6号舵机驱动
			SetServoAngle(6,buffer[2])
		elif buffer[1]=='07':#7号舵机驱动
			SetServoAngle(7,buffer[2])
		elif buffer[1]=='08':#8号舵机驱动
			SetServoAngle(8,buffer[2])
		else:
			print '舵机角度大于170'
	elif buffer[0]=='32':		#存储角度
		XRservo.XiaoRGEEK_SaveServo()
	elif buffer[0]=='33':		#读取角度
		XRservo.XiaoRGEEK_ReSetServo()
	elif buffer[0]=='04':		#开关灯模式 FF040000FF开灯  FF040100FF关灯
		if buffer[1]=='00':
			Open_Light()
		elif buffer[1]=='01':
			Close_Light()
		else:
			print 'error1 command!'
	elif buffer[0]=='05':		#读取电压 FF050000FF
		if buffer[1]=='00':
			Vol = XRservo.XiaoRGEEK_ReadVol()
			print 'Read_Voltage %d '%Vol
		else:
			print 'error2 command!'
	elif buffer[0]=='06':		#读取脉冲 FF060000FF读取脉冲1号  FF060100FF读取脉冲2号
		if buffer[1]=='00':
			Speed1 = XRservo.XiaoRGEEK_SpeedCounter1()
			print 'Read_Voltage %d '%Speed1
		elif buffer[1]=='01':
			Speed2 = XRservo.XiaoRGEEK_SpeedCounter2()
			print 'Read_Voltage %d '%Speed2
		else:
			print 'error3 command!'
	else:
		print 'error4 command!'




init_light()

#定义TCP服务器相关变量
HOST=''
PORT=2001
BUFSIZ=1
ADDR=(HOST,PORT)
rec_flag=0
i=0
buffer=[]
#启动TCP服务器，监听2001端口
tcpSerSock=socket(AF_INET,SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(1)

threads = []
t1 = threading.Thread(target=Cruising_Mod,args=(u'监听',))
threads.append(t1)

for t in threads:
		t.setDaemon(True)
		t.start()

while True:
    print 'waitting for connection...'
    tcpCliSock,addr=tcpSerSock.accept()
    print '...connected from:',addr
    while True:
        try:
            data=tcpCliSock.recv(BUFSIZ)
            data=binascii.b2a_hex(data)
        except:
            print "Error receiving:"
            break
        
        if not data:
            break
        if rec_flag==0:
            if data=='ff':  
                buffer[:]=[]
                rec_flag=1
                i=0
        else:
            if data=='ff':
                rec_flag=0
                if i==3:
                    print 'Got data',str(buffer)[1:len(str(buffer)) - 1],"\r"
                    Communication_Decode();
                i=0
            else:
                buffer.append(data)
                i+=1
   
        #print(binascii.b2a_hex(data))
    tcpCliSock.close()
tcpSerSock.close()
    


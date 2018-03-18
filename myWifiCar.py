#-*- coding: utf-8 -*-
'''
树莓派小车客户端
作者：Alex Sun
可用的命令：
1.行动命令
    g：前进
    b：后退
    l：左转
    r:右转
    lg：左转0.5s后前进
    rg：右转0.5s后前进
    lb：左转0.5s后后退
    rb：右转0.5s后后退
2.控制命令
    ls：左侧电机速度调整，默认100
    rs：右侧电机速度调整，默认100
    m1-m8：1-8号舵机角度调整，每次调整15度
3.LED灯控制
    ol：开灯
    cl：关灯
    sl：走马灯
'''

from socket import *
import binascii

class TcpClient:

    def __init__(self, skt=None):
        if skt is None:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = skt

    def connect(self, host, port):
        self.sock.connect((host, port))

    def sendCmd(self, cmd):
        self.sock.send(cmd)


if __name__ == '__main__':
    HOST='192.168.1.1'
    PORT=2001
    BUFSIZ=1
    ADDR=(HOST, PORT)
    MAXANGLE=160
    MINANGLE=15
    savedAngle = 10
    increaseAngle = 5

    client=TcpClient()
    client.connect(HOST, PORT)

    usage='''The valid commands are as follows:
    0.程序控制
        exit: 退出程序
        quit：退出程序
    1.行动命令
        g：前进
        b：后退
        l：左转
        r:右转
        lg：左转0.5s后前进
        rg：右转0.5s后前进
        lb：左转0.5s后后退
        rb：右转0.5s后后退
    2.控制命令
        m1-m8：1-8号舵机角度调整
        ss: 重置电机速度
        ls：左侧电机速度调整，默认100
        rs：右侧电机速度调整，默认100
    3.LED灯控制
        ol：开灯
        cl：关灯
        sl：走马灯
    '''
    # cmd and the corresponding protocols bytes
    cmd2pro = {
        "s":"FF000000FF",
        "g":"FF000100FF",
        "b":"FF000200FF",
        "l":"FF000300FF",
        "r":"FF000400FF",
        "lg":"FF000500FF",
        "rg":"FF000600FF",
        "lb":"FF000700FF",
        "rb":"FF000800FF",

        "m1":"FF01012AFF",
        "m2":"FF01022AFF",
        "m3":"FF01032AFF",
        "m4":"FF01042AFF",
        "m5":"FF01052AFF",
        "m6":"FF01062AFF",
        "m7":"FF010700FF",
        "m8":"FF010800FF",

        "ss":"FF020000FF",
        "ls":"FF020164FF",
        "rs":"FF020264FF",

        "ol":"FF040000FF",
        "cl":"FF040100FF",
        "sl":"FF040200FF"
        }
    while True:
        cmd=raw_input('>')
        print("the input cmd ", cmd)
        if not cmd:
            print("Please input the cmd")
            continue
        elif cmd.upper() in ("QUIT", "EXIT", "Q", "E"):
            break
        elif cmd not in cmd2pro.keys():
            print(usage)
            continue
        else:#valid cmds, check them
          sendData = True
          if (cmd in ("ls", "rs")):
            while True:
                speed = raw_input("Please input the speed[1-100] or 'e' to exit:")
                if speed.isdigit() and int(speed)>0 and int(speed)<101:
                  data =  "FF02{1}{0:0>2x}FF".format(int(speed),cmd2pro[cmd][4:6])
                  print("the input data:", data)
                  client.sendCmd(binascii.unhexlify(data))
                  break
                elif speed == 'e':
                  break
                else:
                  print("Invalid value, please input again or 'e' to return") 
          elif cmd in ("m7","m8"):
              while True:
                sendData = False
                angle = raw_input("Please input the angle[%d-%d]: %d?" %(MINANGLE, MAXANGLE, savedAngle))
                if angle == 'e':
                  break
                elif angle == "": # 直接回车，表示用户相输入默认值
                  angle = str(savedAngle)
                  sendData = True
                elif angle.isdigit() and int(angle)>=MINANGLE and int(angle)<=MAXANGLE:
                  savedAngle = int(angle)
                  sendData = True
                else:
                  print("Please input the valid value.")
                  continue
                # change the savedAngle
                savedAngle += increaseAngle
                if savedAngle > MAXANGLE:
                  increaseAngle = -5
                  savedAngle = MAXANGLE-5
                  print("Reach the maximum angle, couldn't move.")
                elif savedAngle < MINANGLE:
                  savedAngle = MINANGLE + 5
                  increaseAngle = 5
                  print("Reach the minimum angle, couldn't move.")
                # send the data
                if sendData:
                  data =  "FF01{1}{0:0>2X}FF".format(int(angle),cmd2pro[cmd][4:6])
                  print("the input data:", data)
                  client.sendCmd(binascii.unhexlify(data))
          else:
            data = cmd2pro[cmd]
            print("the input data:", data)
            client.sendCmd(binascii.unhexlify(data))

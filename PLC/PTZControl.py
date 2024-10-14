#!D:/Code/python
# -*- coding: utf-8 -*-
# @Time : 2021/7/23 9:48
# @Author : chaunwen.peng
# @File : PTZControl.py
# @Software: PyCharm
'''
python操作云台
云台型号：HY-LW18-02B
'''
import math
import socket
import struct
import time

import chardet


class Frame:
    # Frame format:		|synch byte|address|command1|command2|data1|data2|checksum|
    _frame = {
        'synch_byte': '\xFF',  # Synch Byte, always FF		-	1 byte
        'address': '\x01',  # Address			-	1 byte
        'command1': '\x00',  # Command1			-	1 byte
        'command2': '\x00',  # Command2			-	1 byte
        'data1': '\x00',  # Data1	(PAN SPEED):		-	1 byte
        'data2': '\x00',  # Data2	(TILT SPEED):		- 	1 byte
        'checksum': '\x00'  # Checksum:			-       1 byte
    }

    _command2_code = {
        'DOWN': '\x10',
        'UP': '\x08',
        'LEFT': '\x04',
        'RIGHT': '\x02',
        'UP-RIGHT': '\x0A',
        'DOWN-RIGHT': '\x12',
        'UP-LEFT': '\x0C',
        'DOWN-LEFT': '\x14',
        'STOP': '\x00',

        'H_CONTROL': '\x4D',  # 垂直控制
        'V_CONTROL': '\x4B',  # 水平控制

        'V_Angle': '\x51',  # 水平角度查询
        'H_Angle': '\x53',  # 垂直角度查询

    }

    def __init__(self, adress=1, ip_address="192.168.8.200", port=6666):
        self.ip_address = ip_address
        self.port = port
        self._frame['address'] = chr(adress)

    def _construct_cmd(self, command2, data1, data2):
        # self._frame['command1'] = command1
        # self._frame['command2'] = command2
        if command2 not in self._command2_code:
            if (type(command2) == str and (ord(command2) < 255 and ord(command2) >= 0)):
                self._frame['command2'] = command2
            else:
                print('not command')
        else:
            self._frame['command2'] = self._command2_code[command2]
        self._frame['data1'] = data1
        self._frame['data2'] = data2

        self._checksum(self._payload_bytes())
        cmd_str = self._frame['synch_byte'] + self._payload_bytes() + self._frame['checksum']
        cmd = bytes('', encoding='utf-8')
        for ch in cmd_str:
            if ch == '\xFF':
                cmd = b'\xFF'
            else:
                # cmd = cmd + bytes(ch, encoding='utf-8')
                cmd = cmd + ord(ch).to_bytes(1, byteorder='little')
        return cmd

    def _payload_bytes(self):
        return self._frame['address'] + self._frame['command1'] + \
            self._frame['command2'] + self._frame['data1'] + \
            self._frame['data2']

    def _checksum(self, payload_bytes_string):
        self._frame['checksum'] = chr(sum(map(ord, payload_bytes_string)) % 256)

    def send_command(self, command2='\x4b', data1='\x00', data2='\x00'):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 需要发送的命令
        cmd = self._construct_cmd(command2, data1, data2)
        udp_socket.sendto(cmd, (self.ip_address, self.port))
        my_recv, my_port = udp_socket.recvfrom(32)
        # 关闭套接字
        udp_socket.close()
        return my_recv.hex()


class PTZControl:

    def __init__(self, ip_address="192.168.8.200", port=6666):
        self.ip_address = ip_address
        self.port = port

        self.command = Frame()

    def stop_run(self):
        '''
        停止云台转动
        :return:
        '''
        self.command.send_command(command2='STOP')

    def wait_time(self, angle):
        # 大概转一圈32s
        angle = angle if angle < 180 else (360 - angle)
        wait_time = (angle / 360) * 32
        return math.ceil(wait_time)

    def turn_to_angle(self, axis='V', angle=15):
        '''
        按照指定轴旋转指定角度
        :param axis:  默认水平轴， 垂直为H
        :param angle: 默认15°
        :return:
        '''
        # self.reset()
        if abs(self.query_cur_angle() - angle) <= 1:
            return self.query_cur_angle()
        # 转动角度
        data1 = chr(struct.pack(">l", (angle * 100))[-2])
        data2 = chr(struct.pack(">l", (angle * 100))[-1])
        axis_control = "H_CONTROL" if "H" in axis else "V_CONTROL"
        print(self.command.send_command(command2=axis_control, data1=data1, data2=data2))
        wait_time = self.wait_time(angle)
        time.sleep(wait_time + 2)
        print('wait run time %s' % wait_time)

    def query_cur_angle(self, axis="V"):
        '''
        查询当前角度，默认查询x轴
        :param axis: 默认x轴
        :return:  当前角度，int
        '''
        axis_control = "H_Angle" if "H" in axis else "V_Angle"
        ret = self.command.send_command(command2=axis_control)
        cur_angle = int(ret[8:12], 16) / 100
        return int(cur_angle)

    def reset(self):
        '''
        云台复位
        :return: 复位成功与否
        '''
        # 查询角度
        v_cur = self.query_cur_angle()
        # 水平轴复位
        print(self.command.send_command(command2="V_CONTROL"))

        wait_time = self.wait_time(v_cur)
        time.sleep(wait_time)
        print('wait v run time %s' % wait_time)

        # h_cur = self.query_cur_angle(axis="H")
        # # 垂直轴复位 总共655°，超过320就用655-
        # h_cur = h_cur if h_cur < 320 else (655 - h_cur)
        # self.command.send_command(command2="H_CONTROL")

        # wait_time = self.wait_time(h_cur)
        # time.sleep(wait_time)
        # print('wait h run time %s' % wait_time)


if __name__ == '__main__':
    # demo = DemoTest()
    # demo.stop_run()
    frame = Frame()
    demo = PTZControl()
    # print(frame.send_command(command2='STOP'))
    # demo.turn_to_angle(angle=45)
    demo.reset()

    while 1:
        demo.reset()
        time.sleep(2)
        demo.turn_to_angle(angle=25)
        time.sleep(2)
        demo.reset()
        demo.turn_to_angle(angle=335)
        time.sleep(2)

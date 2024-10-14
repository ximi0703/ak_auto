#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: chaunwen.peng
@formatted by: zhifeng.li
@file: ptzkeywords.py
@time: 2021/09/09
"""
import math
import socket
import struct
import time
from robot.api import logger
from robot.api.deco import keyword


class PelcoDFrame(object):
    """
    PelcoD协议帧定义类
    """
    def __init__(self, sync=0xFF, addr=0x01, cmd1=0x00, cmd2=0x00, data1=0x00, data2=0x00):
        self.sync_byte = sync
        self.address = addr
        self.command1 = cmd1
        self.command2 = cmd2
        self.data1 = data1
        self.data2 = data2
        self.crc = self._checksum(addr, cmd1, cmd2, data1, data2)
        self.raw = [self.sync_byte, self.address, self.command1, self.command2, self.data1, self.data2, self.crc]
        self.text = struct.pack(">7b", self.sync_byte, self.address, self.command1, self.command2, self.data1,
                                self.data2, self.crc)

    @staticmethod
    def _checksum(addr, cmd1, cmd2, data1, data2):
        return (addr + cmd1 + cmd2 + data1 + data2) & 0x00ff


class PTZControlKeywords(object):
    """
    PTZControl类提供对云台的控制指令下发能力
    """
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

    def __init__(self, ip_address="192.168.8.200", port=6666):
        self.ip_address = ip_address
        self.port = port
        self.addr = (self.ip_address, self.port)

    def send_command(self, cmd2, cmd1=0x00, data1=0x00, data2=0x00, addr=0x01):
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 需要发送的命令
        cmd = PelcoDFrame(cmd1=cmd1, cmd2=cmd2, data1=data1, data2=data2, addr=addr)
        logger.info(f"待发送的原始指令: {cmd.raw}")
        conn.sendto(cmd.text, self.addr)
        res = self.recv_and_unpack(conn, cmd)
        logger.info(f"接受到的指令：{res}")
        # 关闭套接字
        conn.close()
        return res

    @staticmethod
    def recv_and_unpack(connection: socket.socket, send_msg: PelcoDFrame):
        """
        接收云台返回消息并进行解析
        :param connection:  udp连接
        :param send_msg:    发送的消息体
        :return:
        """
        res, _ = connection.recvfrom(1024)
        if len(res) < 7:
            logger.error("接收云台数据错误")
            raise ConnectionError
        if len(res) == 7:
            unpacked = struct.unpack(">7b", res)
            logger.info(f"经过解析的相应指令：{unpacked}")
            if unpacked[2] == send_msg.command1 and unpacked[3] == send_msg.command2 and unpacked[4] == send_msg.data1 \
                    and unpacked[5] == send_msg.data2:
                logger.info("云台响应: Right, 指令正确, 且执行成功")
            elif unpacked[2] == 0xff and unpacked[3] == 0xff and unpacked[4] == 0xff and unpacked[5] == 0xff:
                logger.error("云台响应: Wrong, 指令错误，CRC校验码错误")
                raise ValueError
            elif unpacked[2] == 0xee and unpacked[3] == 0xee and unpacked[4] == 0xee and unpacked[5] == 0xee:
                logger.error("云台响应: Fail, 指令正确，但执行失败")
                raise ValueError
            else:
                logger.info("云台响应: Query， 查询数据，回复被查询的内容")
            return [unpacked]
        else:   # 查询云台工作状态是否正常 会连续返回多条指令
            if len(res) % 7 != 0:
                logger.error("指令长度不是7byte的整数倍，接收失败")
                raise ConnectionError
            multi_res = []
            for i in range(len(res) // 7):
                unpacked = struct.unpack(">7b", res[i:i+7])
                logger.info(f"第{i+1}条响应: {unpacked}")
                multi_res.append(unpacked)
            return multi_res

    @keyword(name="停止云台转动")
    def stop_run(self):
        """
        停止云台转动
        :return:
        """
        self.send_command(cmd2=self._command2_code["STOP"])

    @staticmethod
    def get_waiting_time(angle):
        """
        计算转动需要等待的时间
        :param angle: 
        :return: 
        """
        # 大概转一圈32s
        angle = angle if angle < 180 else (360 - angle)
        wait_time = (angle / 360) * 32
        return math.ceil(wait_time)

    @keyword(name="按照指定轴旋转指定角度")
    def turn_to_angle(self, axis='V', angle=15):
        """
        按照指定轴旋转指定角度
        :param axis:  默认水平轴， 垂直为H
        :param angle: 默认15°
        :return:
        """
        self.reset()
        # 转动角度
        data1 = struct.pack(">l", (angle * 100))[-2]
        data2 = struct.pack(">l", (angle * 100))[-1]
        axis_control = "H_CONTROL" if "H" in axis else "V_CONTROL"
        self.send_command(cmd2=axis_control, data1=data1, data2=data2)
        wait_time = self.get_waiting_time(angle)
        for _ in range(5):
            time.sleep(wait_time)
            logger.info('wait run time %s' % wait_time)
            if self.query_cur_angle() == angle:
                print('turn % angle done' % angle)
                return True
            else:
                return False

    @keyword(name="查询当前角度")
    def query_cur_angle(self, axis="V"):
        """
        查询当前角度，默认查询x轴
        :param axis: 默认x轴
        :return:  当前角度，int
        """
        axis_control = "H_Angle" if "H" in axis else "V_Angle"
        ret = self.send_command(cmd2=self._command2_code[axis_control])
        cur_angle = int(ret[0][4]*16*16 + ret[0][5], 16)
        return int(cur_angle)

    @keyword(name="云台复位")
    def reset(self):
        """
        云台复位
        :return: 复位成功与否
        """
        # 查询角度
        v_cur = self.query_cur_angle()
        # 水平轴复位
        self.send_command(cmd2=self._command2_code["V_CONTROL"])

        wait_time = self.get_waiting_time(v_cur)
        time.sleep(wait_time)
        print('wait v run time %s' % wait_time)

        h_cur = self.query_cur_angle(axis="H")
        # 垂直轴复位 总共655°，超过320就用655-
        h_cur = h_cur if h_cur < 320 else (655 - h_cur)
        self.send_command(cmd2=self._command2_code["H_CONTROL"])

        wait_time = self.get_waiting_time(h_cur)
        time.sleep(wait_time)
        print('wait h run time %s' % wait_time)


if __name__ == '__main__':
    pass

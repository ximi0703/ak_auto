#!D:/Code/python
# -*- coding: utf-8 -*-
# @Time : 2021/7/21 13:53
# @Author : chaunwen.peng
# @File : TrackControl.py
# @Software: PyCharm
'''
python操作基恩士PLC
'''
import math
import struct
import time

from HslCommunication import MelsecMcNet


class BasicConnect:
    def __init__(self, ip_address="192.168.8.10", port=5000):
        self.ip_address = ip_address
        self.port = port

        self.plc_server = self.plc_connect()

    def plc_connect(self):
        # TODO 是否需要retry机制
        plc_server = MelsecMcNet(self.ip_address, self.port)
        if plc_server.ConnectServer().IsSuccess:
            # print("connect success")
            pass
        else:
            print("connect failed")
        return plc_server

    def safe_protect(self):
        '''
        安全光栅保护
        :return:
        '''
        self.plc_server.WriteBool('M80', [1])
        return self.plc_server.ReadBool('M80').Content

    def is_high_speed(self):
        '''
        设置手动高速，只针对手动  M2
        :return: 查看高速状态
        '''
        self.plc_server.WriteBool('M18', [1])
        return self.plc_server.ReadBool('M18').Content


class XOperation(BasicConnect):
    def __init__(self):
        super().__init__()
        self.is_high_speed()
        self.clear_alarm()

    def set_forward(self):
        '''
        手动控制前进  M0
        :return: 返回前进状态
        '''
        self.plc_server.WriteBool('M0', [1])
        return self.plc_server.ReadBool('M0').Content

    def set_back(self):
        '''
        手动控制后退  M1
        :return: 返回后退状态
        '''
        self.plc_server.WriteBool('M1', [1])
        return self.plc_server.ReadBool('M1').Content

    def reset(self):
        '''
        回零  M3
        :return: 查看回零状态
        '''
        self.plc_server.WriteBool('M3', [1])
        return self.plc_server.ReadBool('M3').Content

    def running(self):
        '''
        定位运行，需要提前设置目标位置和速度  M4
        :return: 查看定位运行状态
        '''
        self.plc_server.WriteBool('M4', [1])
        return self.plc_server.ReadBool('M4').Content

    def clear_alarm(self):
        '''
        清除告警  M5
        :return: 查看清除告警状态
        '''
        # TODO 手动停止后必须再次设为False
        self.plc_server.WriteBool('M5', [1])
        return not self.plc_server.ReadBool('M5').Content

    def stop(self):
        '''
        停止  M6
        :return: 查看停止状态
        '''
        # TODO 手动停止后必须再次设为False
        self.plc_server.WriteBool('M6', [1])
        return self.plc_server.ReadBool('M6').Content

    def in_running(self):
        '''
        定位中(运动中)  M10
        :return: 查看定位中状态
        '''
        return self.plc_server.ReadBool('M10').Content

    def is_finish_running(self):
        '''
        定位完成  M11
        :return: 查看定位完成状态
        '''
        return self.plc_server.ReadBool('M11').Content

    def in_alarm(self):
        '''
        告警中  M12
        :return: 查看告警中状态
        '''
        return self.plc_server.ReadBool('M12').Content

    def is_reseted(self):
        '''
        回零完成  M13
        :return: 查看回零完成状态
        '''
        return self.plc_server.ReadBool('M13').Content

    def get_cur_location(self):
        '''
        当前位置  D0
        :return: 当前位置int
        '''
        bytes_value = self.plc_server.Read("D0", 2).Content
        cur_location = struct.unpack('l', bytes_value)[0]
        return cur_location

    def set_location(self, target):
        '''
        定位目标位置  D22
        :param target: 目标位置值, 范围-120~2720
        :return: 定位目标位置值real_location
        '''
        if -120 <= target <= 3420:
            tar_location = struct.pack('l', target)
            self.plc_server.Write("D22", tar_location)
            # 查看目标位置值
            real_location = self.plc_server.Read("D22", 2).Content
            real_location = struct.unpack('l', real_location)[0]
            return real_location
        else:
            print("输入目标位置超过范围，范围值-120~2720")

    def set_speed(self, speed=80):
        '''
        定位目标速度  D26
        :param speed: 目标速度， 范围0~100
        :return: 目标速度值real_speed
        '''
        if 0 <= speed <= 100:
            tar_speed = struct.pack('l', speed)
            self.plc_server.Write("D26", tar_speed)
            # 查看目标位置值
            real_speed = self.plc_server.Read("D26", 2).Content
            real_speed = struct.unpack('l', real_speed)[0]
            return real_speed
        else:
            print("输入目标速度超过范围，范围值0~100")

    def get_high_speed(self):
        '''
        获取高速速度，只针对手动，设置完需要打开高速才生效  D6
        :param speed: 高速速度， 范围0~150
        :return: 目标高速速度
        '''
        real_high_speed = self.plc_server.Read("D6", 2).Content
        real_high_speed = struct.unpack('l', real_high_speed)[0]
        return real_high_speed

    def set_high_speed(self, speed):
        '''
        设置高速速度，只针对手动，设置完需要打开高速才生效  D6
        :param speed: 高速速度， 范围0~70
        :return: 目标高速速度
        '''
        if 0 <= speed <= 70:
            high_speed = struct.pack('l', speed)
            self.plc_server.Write("D6", high_speed)
            # 查看目标位置值
            real_high_speed = self.plc_server.Read("D6", 2).Content
            real_high_speed = struct.unpack('l', real_high_speed)[0]
            return real_high_speed
        else:
            print("输入高速速度超过范围，范围值0~70")


class YOperation(BasicConnect):
    def __init__(self):
        super().__init__()
        self.is_high_speed()
        self.clear_alarm()

    def set_forward(self):
        '''
        手动控制前进  M0
        :return: 返回前进状态
        '''
        self.plc_server.WriteBool('M16', [1])
        return self.plc_server.ReadBool('M16').Content

    def set_back(self):
        '''
        手动控制后退  M1
        :return: 返回后退状态
        '''
        self.plc_server.WriteBool('M17', [1])
        return self.plc_server.ReadBool('M17').Content

    def reset(self):
        '''
        回零  M3
        :return: 查看回零状态
        '''
        self.plc_server.WriteBool('M19', [1])
        return self.plc_server.ReadBool('M19').Content

    def running(self):
        '''
        定位运行，需要提前设置目标位置和速度  M4
        :return: 查看定位运行状态
        '''
        self.plc_server.WriteBool('M20', [1])
        return self.plc_server.ReadBool('M20').Content

    def clear_alarm(self):
        '''
        清除告警  M5
        :return: 查看清除告警状态
        '''
        self.plc_server.WriteBool('M21', [1])
        return not self.plc_server.ReadBool('M21').Content

    def stop(self):
        '''
        停止  M6
        :return: 查看停止状态
        '''
        self.plc_server.WriteBool('M22', [1])
        return self.plc_server.ReadBool('M22').Content

    def in_running(self):
        '''
        定位中(运动中)  M10
        :return: 查看定位中状态
        '''
        return self.plc_server.ReadBool('M26').Content

    def is_finish_running(self):
        '''
        定位完成  M11
        :return: 查看定位完成状态
        '''
        return self.plc_server.ReadBool('M27').Content

    def in_alarm(self):
        '''
        告警中  M12
        :return: 查看告警中状态
        '''
        return self.plc_server.ReadBool('M28').Content

    def is_reseted(self):
        '''
        回零完成  M13
        :return: 查看回零完成状态
        '''
        return self.plc_server.ReadBool('M29').Content

    def get_cur_location(self):
        '''
        当前位置  D0
        :return: 当前位置int
        '''
        bytes_value = self.plc_server.Read("D10", 2).Content
        cur_location = struct.unpack('l', bytes_value)[0]
        return cur_location

    def set_location(self, target):
        '''
        定位目标位置  D32
        :param target: 目标位置值, 范围-60~3495
        :return: 定位目标位置值real_location
        '''
        if -60 <= target <= 4495:
            tar_location = struct.pack('l', target)
            self.plc_server.Write("D32", tar_location)
            # 查看目标位置值
            real_location = self.plc_server.Read("D32", 2).Content
            real_location = struct.unpack('l', real_location)[0]
            return real_location
        else:
            print("输入目标位置超过范围，范围值-60~3495")

    def set_speed(self, speed=150):
        '''
        定位目标速度  D26
        :param speed: 目标速度， 范围0~200
        :return: 目标速度值real_speed
        '''
        if 0 <= speed <= 200:
            tar_speed = struct.pack('l', speed)
            self.plc_server.Write("D36", tar_speed)
            # 查看目标位置值
            real_speed = self.plc_server.Read("D36", 2).Content
            real_speed = struct.unpack('l', real_speed)[0]
            return real_speed
        else:
            print("输入目标速度超过范围，范围值0~200")

    def get_high_speed(self):
        '''
        获取高速速度，只针对手动，设置完需要打开高速才生效  D6
        :param speed: 高速速度， 范围0~150
        :return: 目标高速速度
        '''
        real_high_speed = self.plc_server.Read("D16", 2).Content
        real_high_speed = struct.unpack('l', real_high_speed)[0]
        return real_high_speed

    def set_high_speed(self, speed):
        '''
        设置高速速度，只针对手动，设置完需要打开高速才生效  D6
        :param speed: 高速速度， 范围0~150
        :return: 目标高速速度
        '''
        if 0 <= speed <= 150:
            high_speed = struct.pack('l', speed)
            self.plc_server.Write("D16", high_speed)
            # 查看目标位置值
            real_high_speed = self.plc_server.Read("D16", 2).Content
            real_high_speed = struct.unpack('l', real_high_speed)[0]
            return real_high_speed
        else:
            print("输入高速速度超过范围，范围值0~150")


class TrackControl:
    _size_to_distance = {
        '40-inch': 1060,
        '60-inch': 1590,
        '80-inch': 2120,
        '100-inch': 2660,
        '120-inch': 3170,
        '150-inch': 3970
    }

    _default_distance = {
        '+x': 3500,
        '+y': 4450,
        '-y': 4600
    }

    _direction_to_class = {
        'x': XOperation,
        'y': YOperation
    }

    _distance_new = {
        'x_dis': 3500,
        'y_dis': 5450
    }

    # def move_to(self, prj_size=60, direction='+y'):
    #     '''
    #     默认从原点出发
    #     :param prj_size:
    #     :param direction:
    #     :return: 返回当前位置
    #     '''
    #     prj_size = str(prj_size) + "-inch"
    #     obj = self._direction_to_class[direction[-1]]()
    #     # 回原点
    #     self.reset(obj)
    #     default_distance = self._default_distance[direction]
    #     orj_distance = self._size_to_distance[prj_size]
    #     total_distance = default_distance - orj_distance
    #     obj.set_location(total_distance)
    #     speed = 0
    #     speed = speed if speed else 150
    #     obj.set_speed()
    #     obj.running()
    #     wait_time = (total_distance // speed) + 2
    #     print(wait_time)
    #     time.sleep(wait_time)
    #     print('run done')
    #     return obj.get_cur_location()
    #     # self.back_org(obj)

    def clear_all_alarm(self):
        XOperation().clear_alarm()
        YOperation().clear_alarm()

    def get_cur(self):
        '''
        获取当前位置坐标信息
        :return: tuple
        '''
        self.clear_all_alarm()
        time.sleep(1)
        x_cur = XOperation().get_cur_location()
        y_cur = YOperation().get_cur_location()
        y_cur = y_cur + 1000
        return x_cur, y_cur

    def move_to(self, *args):
        '''
        移动到指定位置
        :param args: x -> int, y -> int, speed -> int, direction -> str
        :return:
        '''
        # self.reset()
        print("x -> int, 轨道滑动x轴距离坐标(总计3500)； "
              "y -> int, 轨道距离y轴墙面距离（5450 - y轴坐标）；"
              "speed -> int， 默认150")
        x_move, y_move, speed = self.init_parmas(args)
        # x_move = x_move if abs(x_move - con.get_cur()[0]) > 5 else 0
        # y_move = y_move if y_move > 5 else 0
        # print(x_move, y_move, speed)
        if x_move * y_move:
            self.run(args[0], x_move, 100, dri='x')
            self.run((4450 - args[1]), y_move, speed)
        else:
            if x_move:
                speed = 100 if speed > 100 else speed
                self.run(args[0], x_move, speed, dri='x')
            else:
                self.run((4450 - args[1]), y_move, speed)
        return self.get_cur()

    def run(self, location, dis, speed, dri='y'):
        obj = XOperation() if 'x' in dri else YOperation()
        obj.set_location(location)
        obj.set_speed()
        speed = speed if speed else 150
        # rel_dis = abs(cur_dis - dis)
        obj.running()
        wait_time = (dis // speed) + 2
        # wait_time = (rel_dis // speed) + 2
        time.sleep(wait_time)
        print('%s' % wait_time)

    def check_length(self, args):
        if len(args) == 2:
            x, y, speed, direction = args[0], args[1], 150, '+'
        elif len(args) == 3:
            x, y, speed, direction = args[0], args[1], args[2], '+'
        elif len(args) == 4:
            x, y, speed, direction = args[0], args[1], args[2], args[3]
        else:
            print('Parameter error')
            x, y, speed, direction = 0, 0, 0, '+'
        return x, y, speed, direction

    def check_type(self, *args):
        if not isinstance(args[0], int):
            raise Exception("type error")
        if not isinstance(args[1], int):
            raise Exception("type error")
        if not isinstance(args[2], int):
            raise Exception("type error")
        if not isinstance(args[3], str):
            raise Exception("type error")

    def check_value(self, *args):
        direction_map = {
            '+': 1000,
            '-': 860
        }
        if not (0 < args[2] < 200):
            print('Parameter error')
            raise Exception
        # x, y数值有效性判断
        if 0 < args[0] < 70 or 0 < args[1] < 100 or args[0] == args[1] == 0:
            print('Parameter error')
            raise Exception
        else:
            x_move = abs(TrackControl().get_cur()[0] - args[0]) if abs(TrackControl().get_cur()[0] - args[0]) > 5 else 0
            # x_move = (self._distance_new["x_dis"] - args[0]) if args[0] else 0
            if args[3] == '-':
                y_move = args[1] - 1000
            else:
                # y_move = (self._distance_new["y_dis"] - args[1] - direction_map[args[3]]) if args[1] else 0
                # TODO 暂时修改
                y_move = abs(self._distance_new["y_dis"] - TrackControl().get_cur()[-1] - args[1]) if abs(
                    self._distance_new["y_dis"] - TrackControl().get_cur()[-1] - args[1]) > 5 else 0

        return x_move, y_move, args[2]

    def init_parmas(self, args):
        x, y, speed, direction = self.check_length(args)
        # 数据类型合法性判断
        self.check_type(x, y, speed, direction)
        # 速度有效性判断
        x_move, y_move, speed = self.check_value(x, y, speed, direction)
        return x_move, y_move, speed

    def reset(self):
        '''
        回到原点
        :param obj: 坐标轴对象, 默认Y轴
        :return:
        '''
        obj = XOperation()
        back_distance = obj.get_cur_location()
        obj.reset()
        x_time = (back_distance // 78) + 2
        print('back X done!')
        obj2 = YOperation()
        back_distance = obj2.get_cur_location()
        obj2.reset()
        y_time = (back_distance // 78) + 2
        wait_time = x_time if x_time > y_time else y_time
        print(wait_time)
        time.sleep(wait_time)
        print('back Y done!')


if __name__ == '__main__':
    conn = BasicConnect()
    # x_opera = XOperation()
    # y_opera = YOperation()
    # x_opera.forward()
    con = TrackControl()
    print(111)

    while True:
        con.move_to(0, 2160)
        time.sleep(2)
        con.move_to(500, 2160)
        time.sleep(2)
        con.move_to(500, 3160)
        time.sleep(2)
        con.move_to(0, 3160)

    # con.move_to(0, 2660)
    # con.back_org(y_opera)
    # con.move_new(2120, 2120, 120, '-')
    # con.reset()

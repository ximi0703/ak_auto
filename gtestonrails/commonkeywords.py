#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: zhifeng.li
@file: commonkeywords.py
@time: 2021/09/10
"""

import time
from robot.api import logger
from robot.api.deco import keyword
from gtestonrails.connectionkeywords import ConnectionKeywords


class CommonKeywords(ConnectionKeywords):
    """
    业务场景关键字
    """
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

    _distance_new = {
        'x_dis': 3500,
        'y_dis': 5450
    }

    @keyword(name="清除所有告警")
    def clear_all_alarm(self):
        """
        清除所有告警
        :return:
        """
        self.clear_alarm_x()
        self.clear_alarm_y()

    @keyword(name="获取当前位置坐标信息")
    def get_cur(self):
        """
        获取当前位置坐标信息
        :return: tuple
        """
        self.clear_all_alarm()
        time.sleep(1)
        x_cur = self.get_cur_location_x()
        y_cur = self.get_cur_location_y()
        y_cur = y_cur + 1000
        return x_cur, y_cur

    @keyword(name="移动到指定位置")
    def move(self, x=0, y=0, speed=150, direction="+"):
        """
        移动到指定位置
        :param x:           x轴移动数值
        :param y:           y轴移动数值
        :param speed:       移动速度
        :param direction:   待确认
        :return:
        """
        x_move, y_move, speed = self.init_params(x, y, speed, direction)
        # print(x_move, y_move, speed)
        if x_move * y_move:
            self.run(x_move, 100, dri='x')
            self.run(y_move, speed)
        else:
            if x_move:
                speed = 100 if speed > 100 else speed
                self.run(x_move, speed, dri='x')
            else:
                self.run(y_move, speed)
        return self.get_cur()

    def run(self, dis, speed, dri='y'):
        set_location = self.set_location_x if "x" in dri else self.set_location_y
        set_speed = self.set_speed_x if "x" in dri else self.set_speed_y
        running = self.running_x if "x" in dri else self.running_y
        set_location(dis)
        set_speed()
        running()
        cur_dis = self.get_cur()[0] if 'x' in dri else self.get_cur()[1]
        speed = speed if speed else 150
        rel_dis = abs(cur_dis - dis)
        wait_time = (rel_dis // speed) + 5
        time.sleep(wait_time)
        logger.info('%s' % wait_time)

    @staticmethod
    def check_type(*args):
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
            logger.error('Parameter error')
            raise ValueError        # x, y数值有效性判断
        if 0 < args[0] < 70 or 0 < args[1] < 100 or args[0] == args[1] == 0:
            logger.error('Parameter error')
            raise ValueError
        else:
            x_move = (self._distance_new["x_dis"] - args[0]) if args[0] else 0
            if args[3] == '-':
                y_move = args[1] - 1000
            else:
                y_move = (self._distance_new["y_dis"] - args[1] - direction_map[args[3]]) if args[1] else 0

        return x_move, y_move, args[2]

    def init_params(self, x, y, speed, direction):
        # 数据类型合法性判断
        self.check_type(x, y, speed, direction)
        # 速度有效性判断
        x_move, y_move, speed = self.check_value(x, y, speed, direction)
        return x_move, y_move, speed

    @keyword(name="回到原点")
    def reset(self):
        """
        回到原点
        :return:
        """
        x_offset = self.get_cur_location_x()
        self.reset_x()
        x_time = (x_offset // 78) + 2
        logger.info('back X done!')
        y_offset = self.get_cur_location_y()
        self.reset_y()
        y_time = (y_offset // 78) + 2
        wait_time = x_time if x_time > y_time else y_time
        print(wait_time)
        time.sleep(wait_time)
        logger.info('back Y done!')

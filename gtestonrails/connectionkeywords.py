#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: zhifeng.li
@file: connectionkeywords.py
@time: 2021/09/10
"""
import time
import struct

import robot.utils
from robot.api import logger
from robot.api.deco import keyword
from HslCommunication import MelsecMcNet


class ConnectionKeywords(object):
    """
    底层位元操作关键字
    """
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self._cache = robot.utils.ConnectionCache("No connection created")

    @keyword(name="创建轨道控制连接")
    def create_connection(self, alias: str, ip_address: str, port, max_retries=5, interval=30):
        """
        创建轨道控制连接
        :param alias:           连接的名称，作为唯一标识符
        :param ip_address:      轨道通信ip地址
        :param port:            轨道通信端口
        :param max_retries:     最大重试次数
        :param interval:        重试间隔
        :return:
        """
        logger.debug(f"Creating connection: {alias}")
        conn = MelsecMcNet(ip_address, int(port))
        for i in range(int(max_retries)):
            if conn.ConnectServer().IsSuccess:
                logger.info(f"Connection({alias}) connected success")
                self._cache.register(conn, alias=alias)
                return conn
            else:
                logger.info(f"第{i+1}次连接失败，等待{interval}秒后重试")
                time.sleep(int(interval))
        logger.error("连接失败，请检查网络情况")
        raise ConnectionError

    @keyword("关闭指定连接")
    def close_connection(self, alias: str):
        """
        关闭指定连接
        :param alias:   连接的名称
        :return: 
        """
        conn = self._cache[alias]
        conn.ConnectClose()
    
    @keyword("删除所有连接")
    def delete_all_connections(self):
        """ Removes all the connection objects """
        logger.info('Deleting All Connections')
        self._cache.empty_cache()

    def _write_bool(self, alias: str, address: str, values: list):
        """
        底层位元发送方法
        :param alias:       连接的名称
        :param address:     待写入的位元地址
        :param values:      待写入的bool数组
        :return:
        """
        conn = self._cache.switch(alias)
        logger.info(f"待写入的位元地址: {address}, 待写入的布尔数组: {values}")
        conn.WriteBool(address, values)

    def _write_bytes(self, alias: str, address: str, values: bytearray):
        """
        底层位元发送方法
        :param alias:       连接的名称
        :param address:     待写入的位元地址
        :param values:      待写入的bytes数组
        :return:
        """
        conn = self._cache.switch(alias)
        logger.info(f"待写入的位元地址: {address}, 待写入的bytes数组: {values}")
        conn.Write(address, values)

    def _read(self, alias: str, address: str, length: int = None):
        """
        底层位元接收方法
        :param alias:       连接的名称
        :param address:     待读取的位元地址
        :param length:      读取长度
        :return:
        """
        conn = self._cache.switch(alias)
        if not length:
            res = conn.ReadBool(address).Content
        else:
            res = conn.Read(address, length).Content
        logger.info(f"收到返回消息: {res}")
        return res

    @keyword("安全光栅保护")
    def safe_protect(self, alias):
        """
        安全光栅保护  M80
        :param alias:   连接的名称
        :return:
        """
        address = 'M80'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="设置手动高速")
    def is_high_speed(self, alias):
        """
        设置手动高速，只针对手动  M18
        :param alias:   连接的名称
        :return: 查看高速状态
        """
        address = 'M18'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="手动控制X轴前进")
    def set_x_forward(self, alias):
        """
        手动控制x轴前进  M0
        :param alias:   连接的名称
        :return: 返回前进状态
        """
        address = 'M0'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="手动控制X轴后退")
    def set_x_back(self, alias):
        """
        手动控制X轴后退  M1
        :param alias:   连接的名称
        :return: 返回后退状态
        """
        address = 'M1'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="x轴回零")
    def reset_x(self, alias):
        """
        x轴回零  M3
        :param alias:   连接的名称
        :return: 查看回零状态
        """
        address = 'M3'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="x轴定位运行")
    def running_x(self, alias):
        """
        x轴定位运行，需要提前设置目标位置和速度  M4
        :param alias:   连接的名称
        :return: 查看定位运行状态
        """
        address = 'M4'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="x轴清除告警")
    def clear_alarm_x(self, alias):
        """
        x轴清除告警  M5
        :param alias:   连接的名称
        :return: 查看清除告警状态
        """
        # TODO 手动停止后必须再次设为False
        address = 'M5'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="停止x轴")
    def stop_x(self, alias):
        """
        停止x轴  M6
        :param alias:   连接的名称
        :return: 查看停止状态
        """
        # TODO 手动停止后必须再次设为False
        address = 'M6'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="x轴查看定位中状态")
    def in_running_x(self, alias):
        """
        x轴定位中(运动中)  M10
        :param alias:   连接的名称
        :return: 查看定位中状态
        """
        address = 'M10'
        return self._read(alias, address)

    @keyword(name="x轴是否定位完成")
    def is_finish_running_x(self, alias):
        """
        y轴是否定位完成  M11
        :param alias:   连接的名称
        :return: 查看定位完成状态
        """
        address = 'M11'
        return self._read(alias, address)

    @keyword(name="查看x轴告警中状态")
    def in_alarm_x(self, alias):
        """
        查看x轴告警中状态  M12
        :param alias:   连接的名称
        :return: 查看告警中状态
        """
        address = 'M12'
        return self._read(alias, address)

    @keyword(name="x轴是否回零完成")
    def is_reseted_x(self, alias):
        """
        x轴是否回零完成  M13
        :param alias:   连接的名称
        :return: 查看回零完成状态
        """
        address = 'M13'
        return self._read(alias, address)

    @keyword(name="获取x轴当前位置")
    def get_cur_location_x(self, alias):
        """
        获取x轴当前位置  D0
        :param alias:   连接的名称
        :return: int    当前位置
        """
        address = 'D0'
        bytes_value = self._read(alias, address)
        logger.info(f"收到返回消息: {bytes_value}")
        cur_location = struct.unpack('l', bytes_value)[0]
        logger.info(f"当前位置: {cur_location}")
        return cur_location

    @keyword(name="定位x轴目标位置")
    def set_location_x(self, alias, target):
        """
        定位x轴目标位置  D22
        :param alias:   连接的名称
        :param target: 目标位置值, 范围-120~3420
        :return: 定位目标位置值real_location
        """
        address = 'D22'
        if -120 <= target <= 3420:
            tar_location = bytearray(struct.pack('l', target))
            self._write_bytes(alias, address, tar_location)
            # 查看目标位置值
            real_location = self._read(alias, "D22", 2)
            real_location = struct.unpack('l', real_location)[0]
            logger.info(f"目标位置值: {real_location}")
            return real_location
        else:
            logger.error("输入目标位置超过范围，范围值-120~3420")
            raise ValueError

    @keyword(name="定位x轴目标速度")
    def set_speed_x(self, alias, speed=80):
        """
        定位x轴目标速度  D26
        :param alias:   连接的名称
        :param speed: 目标速度， 范围0~100
        :return: 目标速度值real_speed
        """
        address = "D26"
        if 0 <= speed <= 100:
            tar_speed = bytearray(struct.pack('l', speed))
            self._write_bytes(alias, address, tar_speed)
            # 查看目标位置值
            real_speed = self._read(alias, address, 2)
            real_speed = struct.unpack('l', real_speed)[0]
            logger.info(f"x轴目标速度: {real_speed}")
            return real_speed
        else:
            logger.error("输入目标速度超过范围，范围值0~100")
            raise ValueError

    @keyword(name="获取x轴高速速度")
    def get_high_speed_x(self, alias):
        """
        获取x轴高速速度，只针对手动，设置完需要打开高速才生效  D6
        :param alias:   连接的名称
        :return: 目标高速速度
        """
        address = "D6"
        real_high_speed = self._read(alias, address, 2)
        real_high_speed = struct.unpack('l', real_high_speed)[0]
        return real_high_speed

    @keyword(name="设置x轴高速速度")
    def set_high_speed_x(self, alias, speed):
        """
        设置x轴高速速度，只针对手动，设置完需要打开高速才生效  D6
        :param alias:   连接的名称
        :param speed: 高速速度， 范围0~70
        :return: 目标高速速度
        """
        address = "D6"
        if 0 <= speed <= 70:
            high_speed = bytearray(struct.pack('l', speed))
            self._write_bytes(alias, address, high_speed)
        else:
            logger.error("输入高速速度超过范围，范围值0~70")
            raise ValueError

    @keyword(name="手动控制y轴前进")
    def set_y_forward(self, alias):
        """
        手动控制y轴前进  M16
        :param alias:   连接的名称
        :return: 返回前进状态
        """
        address = 'M16'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="手动控制y轴后退")
    def set_y_back(self, alias):
        """
        手动控制y轴后退  M17
        :param alias:   连接的名称
        :return: 返回后退状态
        """
        address = 'M17'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="y轴回零")
    def reset_y(self, alias):
        """
        y轴回零  M19
        :param alias:   连接的名称
        :return: 查看回零状态
        """
        address = 'M19'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="y轴定位运行")
    def running_y(self, alias):
        """
        y轴定位运行，需要提前设置目标位置和速度  M20
        :param alias:   连接的名称
        :return: 查看定位运行状态
        """
        address = 'M20'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="y轴清除告警")
    def clear_alarm_y(self, alias):
        """
        y轴清除告警  M21
        :param alias:   连接的名称
        :return: 查看清除告警状态
        """
        address = 'M21'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword(name="停止y轴")
    def stop_y(self, alias):
        """
        停止y轴  M22
        :param alias:   连接的名称
        :return: 查看停止状态
        """
        address = 'M22'
        self._write_bool(alias, address, [1])
        return self._read(alias, address)

    @keyword("y轴查看定位中状态")
    def in_running_y(self, alias):
        """
        y轴定位中(运动中)  M26
        :param alias:   连接的名称
        :return: 查看y轴定位中状态
        """
        address = 'M26'
        return self._read(alias, address)

    @keyword(name="y轴是否定位完成")
    def is_finish_running_y(self, alias):
        """
        y轴是否定位完成  M27
        :param alias:   连接的名称
        :return: 查看定位完成状态
        """
        address = 'M27'
        return self._read(alias, address)

    @keyword(name="查看y轴告警中状态")
    def in_alarm_y(self, alias):
        """
        查看y轴告警中状态  M28
        :param alias:   连接的名称
        :return: 查看告警中状态
        """
        address = 'M28'
        return self._read(alias, address)

    @keyword(name="y轴是否回零完成")
    def is_reseted_y(self, alias):
        """
        y轴是否回零完成  M29
        :param alias:   连接的名称
        :return: 查看回零完成状态
        """
        address = 'M29'
        return self._read(alias, address)

    @keyword(name="获取y轴当前位置")
    def get_cur_location_y(self, alias):
        """
        获取y轴当前位置  D10
        :param alias:   连接的名称
        :return: int    当前位置
        """
        address = 'D10'
        return self._read(alias, address)

    @keyword(name="定位y轴目标位置")
    def set_location_y(self, alias, target):
        """
        定位y轴目标位置  D32
        :param alias:   连接的名称
        :param target: 目标位置值, 范围-60~3495
        :return: 定位目标位置值real_location
        """
        address = 'D32'
        if -60 <= target <= 4495:
            tar_location = bytearray(struct.pack('l', target))
            self._write_bytes(alias, address, tar_location)
            # 查看目标位置值
            real_location = self._read(alias, "D22", 2)
            real_location = struct.unpack('l', real_location)[0]
            logger.info(f"目标位置值: {real_location}")
            return real_location
        else:
            print("输入目标位置超过范围，范围值-60~3495")

    @keyword(name="定位y轴目标速度")
    def set_speed_y(self, alias, speed=150):
        """
        定位y轴目标速度  D36
        :param alias:   连接的名称
        :param speed: 目标速度， 范围0~200
        :return: 目标速度值real_speed
        """
        address = 'D36'
        if 0 <= speed <= 200:
            tar_speed = bytearray(struct.pack('l', speed))
            self._write_bytes(alias, address, tar_speed)
            # 查看目标位置值
            real_speed = self._read(alias, address, 2)
            real_speed = struct.unpack('l', real_speed)[0]
            logger.info(f"x轴目标速度: {real_speed}")
            return real_speed
        else:
            print("输入目标速度超过范围，范围值0~200")

    @keyword(name="获取y轴高速速度")
    def get_high_speed_y(self, alias):
        """
        获取y轴高速速度，只针对手动，设置完需要打开高速才生效  D16
        :param alias:   连接的名称
        :return: 目标高速速度
        """
        address = "D16"
        real_high_speed = self._read(alias, address, 2)
        real_high_speed = struct.unpack('l', real_high_speed)[0]
        return real_high_speed

    @keyword(name="设置y轴高速速度")
    def set_high_speed_y(self, alias, speed):
        """
        设置y轴高速速度，只针对手动，设置完需要打开高速才生效  D16
        :param alias:   连接的名称
        :param speed: 高速速度， 范围0~150
        :return: 目标高速速度
        """
        address = "D16"
        if 0 <= speed <= 150:
            high_speed = bytearray(struct.pack('l', speed))
            self._write_bytes(alias, address, high_speed)
        else:
            logger.error("输入高速速度超过范围，范围值0~150")
            raise ValueError

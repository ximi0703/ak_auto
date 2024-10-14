#!D:/Code/python
# -*- coding: utf-8 -*-
# @Time : 2021/8/23 16:35
# @Author : chaunwen.peng
# @File : main.py
# @Software: PyCharm
import os
import time
from ctypes import *
import cv2
import numpy as np

import gxipy as gx


def getValue(config=r'left_cam_config.txt'):
    # show_win()
    img1 = DahengCam(config).save_img()
    img2 = DahengCam(config, num=2).save_img()
    pDll = CDLL(r"./AK_dll/dll/AKMeasureTool.dll")
    print(img2, img1)
    # leftImg, rightImg = img1, img2
    leftImg, rightImg = img2, img1
    ret = (c_double * 12)()
    img1_pointer = create_string_buffer(bytes(leftImg, encoding='utf8'))
    img2_pointer = create_string_buffer(bytes(rightImg, encoding='utf8'))
    pDll.calculateProjRect.restype = POINTER(c_double)
    pDll.calculateProjRect(img2_pointer, img1_pointer, ret)
    time.sleep(8)

    return ret

class DahengCam:
    def __init__(self, config, num=1):
        self.initdone = 0
        self.num = num
        self.conf = config
        self.device_manager = gx.DeviceManager()

    def open_cam(self):
        self.cam = self.device_manager.open_device_by_index(self.num)
        self.cam.import_config_file(self.conf)
        self.cam.stream_on()
        # print(self.cam)

    def save_img(self):
        self.open_cam()
        raw_image = self.cam.data_stream[0].get_image()
        rgb_image = raw_image.convert("RGB")
        numpy_image = rgb_image.get_numpy_array()
        # cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)

        img_path = "./pictures/calculate"
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        test_date = time.strftime("%Y%m%d_%H%M%S")
        file_name = os.path.join(img_path, str(self.num) + '_' + test_date + '.png')
        cv2.imwrite(file_name, numpy_image)
        time.sleep(6)
        self.cam.close_device()
        return file_name

    def save_img_to_cail(self, count):
        self.open_cam()
        raw_image = self.cam.data_stream[0].get_image()
        rgb_image = raw_image.convert("RGB")
        numpy_image = rgb_image.get_numpy_array()
        # cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)

        img_path = "./pictures/cail"
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        # test_date = time.strftime("%Y%m%d_%H%M%S")
        file_name = os.path.join(img_path, str(self.num) + '_' + str(count) + '.png')
        cv2.imwrite(file_name, numpy_image)
        time.sleep(3)
        self.cam.close_device()
        return file_name

def show(num=1):
    l_config = r'left_cam_config.txt'
    da_cam = DahengCam(l_config, num)
    da_cam.open_cam()
    image = da_cam.cam.data_stream[0].get_image().get_numpy_array()
    # 按照原图等比例resize
    show = cv2.resize(image, (640, 428))
    show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
    return show


def show_win():
    while 1:
        # img2, img1 = show(), show(num=2)
        img1, img2 = show(), show(num=2)
        imgs = np.hstack([img1, img2])
        # print(imgs)
        cv2.imshow("live camera", imgs)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty("live camera", cv2.WND_PROP_AUTOSIZE) < 1:
            break

if __name__ == "__main__":
    l_config = r'left_cam_config.txt'
    # cap = DahengCam(l_config)
    # for i in range(21):
    #     # show_win()
    #     cap.save_img_to_cail(i)

    # show_win()
    ret = getValue()
    # ret = [i for i in ret]
    # ret.pop(5)
    # while len(set(ret)) == 1:
    #     ret = getValue()
    #     ret = [i for i in ret]
    #     ret.pop(5)
    #     print(111)
    # print(ret)
    # show_win()
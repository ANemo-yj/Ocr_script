# coding:utf-8
import json
import msvcrt
import os
import re
import shutil
import sys
import time

from ScreenImage import screen_main
from ocr import basedir, ocr_result, get_grcode, postprocess
from open_sdk import haikang_sdk_main, enum_devices, identify_different_devices, input_num_camera, creat_camera, \
    set_Value, open_device, call_back_get_image, start_grab_and_get_data_size, close_and_destroy_device


def response_results(result):
    box = []
    for line in result:
        weizhi = line[0]
        wenben = line[1][0]
        scores = line[1][1]
        content = {
            '位置': weizhi,
            '文本': wenben,
            '置信度': scores
        }
        box.append(content)
    return box


def check(mystr):
    '''
    正则筛选符合标准的箱号
    :param mystr:
    :return:
    '''
    pattern = re.compile(r'^[0-9]{4,5}$')
    if pattern.fullmatch(mystr) is None:
        return False
    else:
        return True


def saveImageAs(save_image_dir):
    # 将筛选出来的图片另存为save_image_dir，图片名为当前时间戳
    if not os.path.exists(save_image_dir):
        os.mkdir(save_image_dir)
    now_time = int(time.mktime(time.localtime(time.time())))
    new_img_name = str(now_time) + '.jpg'
    new_img_path = os.path.join(save_image_dir, new_img_name)
    shutil.copy(final_imgpath, new_img_path)
    return new_img_path

def selectKeyValue(text):
    # 筛选出固定的4-5箱号值
    caseNum = [re.findall("[0-9]{4,5}", i) for i in text if '箱号' in i][0]
    print('caseNum正则；', caseNum)
    if not caseNum:
        caseNo = postprocess(text)

        if not caseNo:
            caseNo = None
        else:
            caseNo = caseNo[0]
    else:
        caseNo = caseNum[0]
    return caseNo

if __name__ == '__main__':
    # 连接海康威视射线头
    deviceList = enum_devices(device=0, device_way=False)
    # 判断不同类型设备
    device_infos = identify_different_devices(deviceList)
    # 输入需要被连接的设备
    nConnectionNum = input_num_camera(deviceList)
    global camera_dir_path
    camera_dir_path = './Output'
    # 创建相机实例并创建句柄,(设置日志路径)
    cam, stDeviceList, camera_dir_path = creat_camera(deviceList, nConnectionNum, device_infos, log=False,
                                                      log_path=os.getcwd())
    # 打开设备
    open_device(cam)
    # 设置设备的一些参数
    xuelie_num = device_infos.get(str(nConnectionNum)).get('EquipmentSerialNumber')
    with open('Config/HaiKan_profile.json', 'r', encoding='utf-8') as fp:
        json_data = json.load(fp)
        for node_param in json_data[xuelie_num]:
            if node_param != '//':
                tp = json_data[xuelie_num][node_param]['type']
                value = json_data[xuelie_num][node_param]['value']
                if node_param == 'ExposureAuto' and value != 0:
                    set_Value(cam, param_type=tp, node_name=node_param, node_value=value)
    # 创建图片保存路径
    if not os.path.exists(camera_dir_path):
        os.mkdir(camera_dir_path)
    # 回调方式抓取图像
    call_back_get_image(cam)
    # 开启设备取流
    start_grab_and_get_data_size(cam)
    # 当使用 回调取流时，需要在此处添加
    print("按下任意键取消将采集/press a key to stop grabbing.")
    msvcrt.getch()
    # 关闭设备与销毁句柄
    close_and_destroy_device(cam)


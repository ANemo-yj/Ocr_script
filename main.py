# coding:utf-8

import os
import re
import shutil
import sys
import time

from ScreenImage import screen_main
from ocr import basedir, ocr_result, get_grcode
from open_sdk import haikang_sdk_main


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


if __name__ == '__main__':
    # 连接海康威视射线头
    # haikang_sdk_main()

    # 筛选清晰度最高的图片
    imgPath = os.path.join(basedir, 'output')
    print(imgPath)
    img_list = screen_main(imgPath)
    final_imgpath = [*max(img_list, key=lambda x: list(x.values())).keys()][0]  # 获取清晰清晰度最高的图片
    save_image_dir = os.path.join(basedir, 'save_image_dir')
    new_img_path = saveImageAs(save_image_dir)
    if not os.path.exists(new_img_path):
        print('图片另存为失败')
        sys.exit()
    # 调用ocr进行识别,优先检测是否有二维码
    res = get_grcode(new_img_path)
    print(res)
    if not res.get('result'):
        res = ocr_result(final_imgpath)
        print(response_results(res['result']))
        #
    else:
        caseNo = res['result'][-5:]
        if check(caseNo):
            print(caseNo)

#  写入数据库/opcua服务器中
import os
import threading
import time
import cv2
import numpy as np
import threadpool

from logger.logging import logger
from ocr import ocr_result

try:
    from PIL import Image
except ImportError:
    import Image

img_list = []


def getImageVar(imgPath):
    '''
    使用拉普拉斯算子挑选出清晰度最高的图片
    :param imgPath:
    :return:
    '''
    image = cv2.imread(imgPath)
    # 若有中文路径 np.array(image)
    # img = Image.open(imgPath)
    img2gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imageVar = cv2.Laplacian(img2gray, cv2.CV_64F).var()
    res = {}
    res[imgPath] = imageVar
    return res


def select_max_img(dirpath):
    start_time = time.time()
    filelist = os.listdir(dirpath)
    imgs_path = [os.path.join(imgPath, i) for i in filelist if i.endswith(('.png', 'jpg'))]
    imagevars = [getImageVar(i) for i in imgs_path]  # 清晰度列表
    value = min(imagevars)
    idx = imagevars.index(value)
    print('消耗时间：', time.time() - start_time)
    return imgs_path[idx]


def callback(request, results):  # 回调函数，用于取回结果
    img_list.append(results)
    # print("callback result = %s" % results)


def screen_main(imgPath):
    '''筛选清晰度最高的图片'''
    filelist = os.listdir(imgPath)
    imgs_path = [os.path.join(imgPath, i) for i in filelist if i.endswith(('.png', 'jpg', 'bmp'))]

    start_time = time.time()
    pool = threadpool.ThreadPool(5)  # 创建线程池
    requests = threadpool.makeRequests(getImageVar, imgs_path, callback)  # 创建任务

    a = [pool.putRequest(req) for req in requests]  # 加入任务
    pool.wait()
    print('%s cost %d second' % (threading.current_thread().getName(), time.time() - start_time))
    return img_list


if __name__ == '__main__':
    imgPath = r"E:\123"
    # print(select_max_img(imgPath))
    img_list = screen_main(imgPath)
    print(img_list)
    # [i.values() for i in img_list]
    # final_imgpath = [*max(img_list, key=lambda x: list(x.values())).keys()] # 获取清晰清晰度最高的图片
    # print(final_imgpath)
    # ocr_result(final_imgpath)

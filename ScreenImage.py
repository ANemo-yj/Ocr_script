import os
import threading
import time

import cv2
import numpy as np
import threadpool

from logger.logging import logger

try:
    from PIL import Image
except ImportError:
    import Image


def getImageVar(imgPath):
    # image = cv2.imread(imgPath);
    img = Image.open(imgPath)
    img2gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_BGR2GRAY)
    imageVar = cv2.Laplacian(img2gray, cv2.CV_64F).var()

    return imageVar


def select_max_img(dirpath):
    start_time = time.time()
    filelist = os.listdir(dirpath)
    imgs_path = [os.path.join(imgPath, i) for i in filelist if i.endswith(('.png', 'jpg'))]
    imagevars = [getImageVar(i) for i in imgs_path]  # 清晰度列表
    value = min(imagevars)
    idx = imagevars.index(value)
    print('消耗时间：',time.time() - start_time)
    return imgs_path[idx]


def callback(request, result):  # 回调函数，用于取回结果
    print("callback result = %s" % result)


if __name__ == '__main__':
    imgPath = r"D:\图片\output"
    # select_max_img(imgPath)
    filelist = os.listdir(imgPath)
    imgs_path = [os.path.join(imgPath, i) for i in filelist if i.endswith(('.png', 'jpg'))]

    start_time = time.time()
    pool = threadpool.ThreadPool(2)  # 创建线程池
    requests = threadpool.makeRequests(getImageVar, imgs_path, callback)  # 创建任务

    a = [pool.putRequest(req) for req in requests]  # 加入任务
    pool.wait()
    print('%s cost %d second' % (threading.current_thread().getName(), time.time() - start_time))
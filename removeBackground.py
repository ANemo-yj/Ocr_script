# encoding：utf-8

import cv2
from PIL import Image, ImageEnhance, ImageFilter
import time
import numpy as np

time1 = time.time()


def process(img):
    '''
    图片二值化操作
    :param img:
    :return:
    '''
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY) # 固定阈值处理
    thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 3)  # 自适应阈值处理
    # cv2.imshow("dst2", dst2)
    img_canny = cv2.Canny(thresh, 0, 0)
    img_dilate = cv2.dilate(img_canny, None, iterations=7)
    return cv2.erode(img_dilate, None, iterations=7)


def get_contours(img):
    '''
    裁剪图片 并处理图片（适当加大对比度等）
    :param img:
    :return:
    '''
    contours, _ = cv2.findContours(process(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    cropImg = img[y: y + h, x: x + w]
    img_image = Image.fromarray(np.uint8(cropImg))  # 转换为Image对象
    # imgE = Image.open(img_image)
    imgEH = ImageEnhance.Contrast(img_image)  # 增加对比度
    img1 = imgEH.enhance(2.8)
    gray1 = img1.convert("L")
    gary2 = gray1.filter(ImageFilter.DETAIL)  # 创建滤波器，使用不同的卷积核
    gary3 = gary2.point(lambda i: i * 0.9)  # 图像点运算
    gary3.save('./test/image/cut.png')
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    time2 = time.time()
    print(u'总共耗时：' + str(time2 - time1) + 's')


img = cv2.imread(r"E:\123\Image_20220928113300235.bmp")
# img = cv2.resize(img, (1080, int(img.shape[0]*1080/img.shape[1])), interpolation=cv2.INTER_AREA)
img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
get_contours(img)
cv2.imshow("img_processed", img)
cv2.waitKey(0)

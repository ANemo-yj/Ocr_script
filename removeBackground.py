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
    # img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)  # 滤波降噪
    # _, thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY) # 固定阈值处理
    thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 3)  # 自适应阈值处理

    img_canny = cv2.Canny(thresh, 0, 0)

    # cv2.imshow("dst2", img_canny)
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
    img1 = imgEH.enhance(2.0)
    gray1 = img1.convert("L")
    gary2 = gray1.filter(ImageFilter.DETAIL)  # 创建滤波器，使用不同的卷积核
    gary3 = gary2.point(lambda i: i * 0.9)  # 图像点运算
    print('裁剪后的图片大小:', gary3.size)
    cv_img = np.array(gary3)
    cv_img = cv2.resize(cv_img, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_AREA)
    cv2.imwrite('./test/image/cut.png', cv_img)
    # gary3 = gary3.resize((960, 800))
    # gary3.save('./test/image/cut.png')
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    # time2 = time.time()
    # print(u'总共耗时：' + str(time2 - time1) + 's')


def barcode_angle(image):
    # 通过膨胀和腐蚀p判断旋转角度,并对图片进行矫正
    im_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    im_gray = cv2.GaussianBlur(im_gray, (3, 3), 0)  # 滤波降噪
    # imgEH = ImageEnhance.Contrast(im_gray)  # 增加对比度
    # im_gray = imgEH.enhance(2.8)
    im_edge = cv2.Canny(im_gray, 30, 50)  # 边缘检测
    kernel = np.ones(shape=[3, 3], dtype=np.uint8)
    im_edge = cv2.dilate(im_edge, kernel, iterations=1)  # 膨胀处理
    cv2.imshow('im_edge', im_edge)  # 显示边缘检测结果
    # cv2.waitKey(0)
    contours, hierarchy = cv2.findContours(im_edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 提取轮廓
    rect, area = None, 0  # 找到的最大四边形及其面积
    for item in contours:
        hull = cv2.convexHull(item)  # 寻找凸包
        epsilon = 0.1 * cv2.arcLength(hull, True)  # 忽略弧长10%的点
        approx = cv2.approxPolyDP(hull, epsilon, True)  # 将凸包拟合为多边形
        if len(approx) == 4 and cv2.isContourConvex(approx):  # 如果是凸四边形
            ps = np.reshape(approx, (4, 2))
            ps = ps[np.lexsort((ps[:, 0],))]
            lt, lb = ps[:2][np.lexsort((ps[:2, 1],))]
            rt, rb = ps[2:][np.lexsort((ps[2:, 1],))]
            a = cv2.contourArea(approx)  # 计算四边形面积
            if a > area:
                area = a
                rect = (lt, lb, rt, rb)
    im = np.copy(image)
    for p in rect:
        im = cv2.line(im, (p[0] - 10, p[1]), (p[0] + 10, p[1]), (0, 0, 255), 1)
        im = cv2.line(im, (p[0], p[1] - 10), (p[0], p[1] + 10), (0, 0, 255), 1)
    lt, lb, rt, rb = rect
    pts1 = np.float32([(0, 0), (0, 960), (960, 0), (960, 960)])  # 预期的棋盘四个角的坐标
    pts2 = np.float32([lt, lb, rt, rb])  # 当前找到的棋盘四个角的坐标
    m = cv2.getPerspectiveTransform(pts2, pts1)  # 生成透视矩阵
    board_gray = cv2.warpPerspective(im_gray, m, (960, 960))  # 对灰度图执行透视变换
    board_bgr = cv2.warpPerspective(image, m, (960, 960))  # 对彩色图执行透视变换
    # cv2.imwrite('./test/image/bianhuan.png',board_bgr)
    cv2.imshow('board_bgr', board_bgr)

    cv2.imshow('go', im)
    cv2.waitKey(0)


def shape_correction(img):
    '''进行角度倾斜矫正'''
    (height, width) = img.shape[:2]
    print(img.shape)
    img_gau = cv2.GaussianBlur(img, (5, 5), 0)
    canny = cv2.Canny(img_gau, 60, 200)
    # cv.imshow("g-canny", canny)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 3))

    dilated = cv2.dilate(canny, kernel, iterations=8)
    # cv.imshow('img_dilated', dilated)
    # 寻找轮廓
    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # print(len(contours), hierarchy, sep='\n')
    # 找到最外层面积最大的轮廓
    area = 0
    # print("area:{}".format(area))
    index = 0
    for i in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        # 排除非文本区域
        if w < 35 and h < 35:
            continue
        # 防止矩形区域过大不精准
        if h > 0.99 * height or w > 0.99 * width:
            continue
        # draw rectangle around contour on original image
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
        tmpArea = w * h
        if tmpArea >= area:
            area = tmpArea
            index = i
    # 得到最小外接矩形的（中心(x,y), (宽,高), 旋转角度）
    rect = cv2.minAreaRect(contours[index])
    # 画出矩形框
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
    # cv2.imshow('img', img)
    print("rect:{}".format(rect))
    angle = rect[-1]
    print('倾斜角度：', angle)
    # 角度大于85度或小于5度不矫正
    if angle > 85 :
        angle = 0
    elif angle < 45:
        angle = 90 + angle
    else:
        angle = angle - 90

    print('旋转角度：', angle)
    M = cv2.getRotationMatrix2D(rect[0], angle, 1)
    rotated = cv2.warpAffine(img, M, (width, height))
    cv2.imshow('Rotated', rotated)
    return rotated


if __name__ == '__main__':
    img = cv2.imread(r"E:\123\Image_20220928113119934.bmp")
    # img = cv2.resize(img, (1080, int(img.shape[0]*1080/img.shape[1])), interpolation=cv2.INTER_AREA)
    img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA) #  缩小至原图片的四分之一大小
    # get_contours(img)x
    # print('介是嘛：', barcode_angle(cv2.imread('./test/image/paper.jpeg')))
    shape_correction(cv2.imread('./test/image/0220930151108.png'))
    # cv2.imshow("img_processed", img)
    cv2.waitKey(0)

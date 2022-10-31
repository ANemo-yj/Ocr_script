# encoding：utf-8
import os
import re

import cv2
from PIL import Image, ImageEnhance, ImageFilter
import time
import numpy as np




def process(img):
    '''
    图片二值化操作
    :param img:
    :return:
    '''
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)  # 滤波降噪
    _, thresh = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY) # 固定阈值处理
    # thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)  # 自适应阈值处理

    img_canny = cv2.Canny(img_gray, 50, 30)

    # cv2.imshow("dst2", img_canny)
    img_dilate = cv2.dilate(img_canny, None, iterations=7)
    return cv2.erode(img_dilate, None, iterations=7)


def get_contours(img,img_path='./Output'):
    '''
    裁剪图片 并处理图片（适当加大对比度等）
    消耗时间大约0.02秒
    :param img:
    :return:
    '''

    contours, _ = cv2.findContours(process(img), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
    cropImg = img[y: y + h, x: x + w]
    img_image = Image.fromarray(np.uint8(cropImg))  # 转换为Image对象
    # imgE = Image.open(img_image)
    imgEH = ImageEnhance.Contrast(img_image)  # 增加对比度
    img1 = imgEH.enhance(1)
    gray1 = img1.convert("L")
    gary2 = gray1.filter(ImageFilter.DETAIL)  # 创建滤波器，使用不同的卷积核
    gary3 = gary2.point(lambda i: i * 0.9)  # 图像点运算
    print('裁剪后的图片大小:', gary3.size)

    # cv_img = np.array(gary3)
    # cv_img = cv2.resize(cv_img, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_AREA)
    # cv2.imwrite('./test/image/cut.png', cv_img)
    # oringin_name = os.path.basename(img_path).split('.')[0] + '.jpg'
    # save_path = os.path.join('E:\\烟叶标签照片\\152组盘矫正处理', oringin_name)
    # cv_img = Image.fromarray(np.uint8(cv_img))
    # cv2.imshow("裁剪后", gary3)

    # cv_img.save(save_path)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    return gary3
    # time2 = time.time()
    # print(u'总共耗时：' + str(time2 - time1) + 's')


def barcode_angle(image, img_path='./Output', ps_image_dir = './ps_image_dir'):
    '''消耗时间大约0.02秒'''
    t1 = time.time()
    # 通过膨胀和腐蚀p判断旋转角度,并对图片进行矫正
    im_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    im_gray = cv2.GaussianBlur(im_gray, (3, 3), 0)  # 滤波降噪
    # imgEH = ImageEnhance.Contrast(im_gray)  # 增加对比度
    # im_gray = imgEH.enhance(2.8)
    im_edge = cv2.Canny(im_gray, 30, 50)  # 边缘检测
    kernel = np.ones(shape=[3, 3], dtype=np.uint8)
    im_edge = cv2.dilate(im_edge, kernel, iterations=1)  # 膨胀处理
    # cv2.imshow('im_edge', im_gray)  # 显示边缘检测结果
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
    if not rect:
        return
    # print('\t左上角：(%d,%d)' % (rect[0][0], rect[0][1]))
    # print('\t左下角：(%d,%d)' % (rect[1][0], rect[1][1]))
    # print('\t右上角：(%d,%d)' % (rect[2][0], rect[2][1]))
    # print('\t右下角：(%d,%d)' % (rect[3][0], rect[3][1]))
    w1 = rect[2][0] - rect[0][0]
    w2 = rect[3][0] - rect[1][0]
    h1 = rect[1][1] - rect[0][1]
    h2 = rect[3][1] - rect[2][1]
    # print('图像长', w1,w2)
    # print('图像宽', h1,h2)
    im = np.copy(image)
    for p in rect:
        im = cv2.line(im, (p[0] - 10, p[1]), (p[0] + 10, p[1]), (0, 0, 255), 1)
        im = cv2.line(im, (p[0], p[1] - 10), (p[0], p[1] + 10), (0, 0, 255), 1)
    lt, lb, rt, rb = rect
    pts1 = np.float32([(0, 0), (0, h1), (w1, 0), (w1, h1)])  # 预期的棋盘四个角的坐标
    pts2 = np.float32([lt, lb, rt, rb])  # 当前找到的棋盘四个角的坐标

    m = cv2.getPerspectiveTransform(pts2, pts1)  # 生成透视矩阵
    board_gray = cv2.warpPerspective(im_gray, m, (800, 800))  # 对灰度图执行透视变换
    board_bgr = cv2.warpPerspective(image, m, (w1, h1))  # 对彩色图执行透视变换
    img_image = Image.fromarray(np.uint8(board_bgr))  # 转换为Image对象
    # imgE = Image.open(img_image)
    enh_bri = ImageEnhance.Brightness(img_image) # 亮度增强
    image_brightened = enh_bri.enhance(1.5)
    enh_col = ImageEnhance.Color(image_brightened) # 色度增强
    image_colored = enh_col.enhance(1.2)
    imgEH = ImageEnhance.Contrast(image_colored)  # 增加对比度
    img1 = imgEH.enhance(1.3)
    enh_sha = ImageEnhance.Sharpness(img1)  # 锐度增强
    image_sharped = enh_sha.enhance(1.2)
    gray1 = image_sharped.convert("L")
    gary2 = gray1.filter(ImageFilter.DETAIL)  # 创建滤波器，使用不同的卷积核
    gary3 = gary2.point(lambda i: i * 0.9)  # 图像点运算
    oringin_name = os.path.basename(img_path).split('.')[0] + '.jpg'
    save_path = os.path.join(ps_image_dir, oringin_name)
    wheight = w1 * 2
    height = h1 * 2
    gary3 = letterbox_image(gary3,(wheight,height))
    gary3_cv = np.array(gary3)
    cv2.imencode('.jpg', gary3_cv)[1].tofile(save_path)
    cv2.imshow('board_bgr', np.array(gary3_cv))
    return save_path

def letterbox_image(image, size):
    # 对图片进行resize，使图片不失真。在空缺的地方进行padding
    iw, ih = image.size
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)
    image = image.resize((nw,nh), Image.BICUBIC)
    new_image = Image.new('RGB', size, (128,128,128))
    new_image.paste(image, ((w-nw)//2, (h-nh)//2))
    return new_image


def batch_toprocess_img(imgPath):
    '''批量处理文件夹中的图片'''
    t = time.time()
    filelist = os.listdir(imgPath)
    imgs_path = [os.path.join(imgPath, i) for i in filelist if i.endswith(('.png', 'jpg', 'bmp'))]
    for i in imgs_path:
        # img = cv2.imdecode(np.fromfile(i, dtype=np.uint8), cv2.IMREAD_COLOR)
        # img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        img = letterbox_image(Image.open(i),(1980,1080))
        # img.show()
        gary3_cv = np.array(img)
        barcode_angle(gary3_cv,i)
        # get_contours(img,i)
    t2 = time.time() - t
    print('共有{num}张图片'.format(num =len(imgs_path)))
    print('总需要消耗时间：', t2)
    print('平均用时：', t2/len(imgs_path))

if __name__ == '__main__':
    imgPath = r"E:\烟叶标签照片\2022-10-25_00K42994152"
    # batch_toprocess_img(imgPath)
    rec_res =  ['上海烟草集团有限责任公司', '1', '烟叶烟箱条形码标签', '中国烟草', 'CHINATOBACCO', '加工单位：', '贵州渭潭复烤厂', '烟叶名称：', '2022贵州烤烟混打片烟', 'C（挑）纸箱', '215.0KG', '净重：', '毛重：', '200.0KG', '箱号：', '批次：第1批', '3098', '生产日期：2022-10-27', '28483521831561882132718399']
    keys = ['安徽中烟工业有限责任公司', '年份：2021', '产地：贵州绥阳', '等级：C3FA', '箱号：00633', '毛重：213.8Kg净重：200.0Kg品种：云烟87含水率：11.8%', '打叶员：安徽中烟加工六组', '类型：烤烟', '加工单位：贵州烟叶复烤有限责任公司', '900152000611021112710213095203231030220200633']

    print([re.findall(r'\b\d+\b', i) for i in keys if '箱号' in i])



    #读取中文路径
    # ch_img = cv2.imdecode(np.fromfile(r"E:\Ocr_Script\test\276.jpg", dtype=np.uint8), -1)
    # cv_img = cv2.cvtColor(ch_img, cv2.COLOR_RGB2BGR)
    # img = cv2.resize(img, (1080, int(img.shape[0]*1080/img.shape[1])), interpolation=cv2.INTER_AREA)
    # get_contours(img)
    # res = barcode_angle(ch_img)

    # # shape_correction(cv2.imread('./test/image/cut.png'))
    # # cv2.imshow("img_processed", img)
    # cv2.waitKey(0)

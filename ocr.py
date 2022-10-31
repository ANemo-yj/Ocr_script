# encoding: utf-8
import os
import re
import sys
import traceback
import numpy as np
import cv2

from pyzbar import pyzbar
from pyzbar.wrapper import ZBarSymbol
from logger.logging import logger, MyLogger
import warnings
warnings.filterwarnings("ignore")
from removeBackground import letterbox_image, get_contours, barcode_angle

try:
    from PIL import Image, ImageEnhance
except ImportError:
    import Image
from paddleocr import PaddleOCR, draw_ocr
import time

basedir = os.path.dirname(os.path.abspath(__file__))  # E:\PdFast
pocr_name = os.path.join(basedir, 'pp_model')

my_logloggerger = MyLogger().get_logger()


def ocr_result(img_path='./test/image/chenjun.jpg', use_angle=True, cls=True, rec=True, det=True, lan="ch"):
    t1 = time.time()
    img_path = img_path
    # default_lan = lan
    try:
        ocr = PaddleOCR(
            use_angle_cls=True,
            rec_model_dir=os.path.join(pocr_name, 'rec/ch_PP-OCRv3_rec_infer').replace('\\', '/'),
            # r'E:\PdFast\pp_model\rec\ch_PP-OCRv3_rec_infer',
            det_model_dir=os.path.join(pocr_name, 'det/ch_ppocr_mobile_v2.0_det_prune_infer').replace('\\', '/'),
            # 'E:/PdFast/pp_model/det/ch_PP-OCRv3_det_infer',
            rec_char_dict_path=os.path.join(basedir, 'test/font/ppocr_keys_v1.txt').replace('\\', '/'),
            # 'E:/PdFast/test/font/ppocr_keys_v1.txt',
            cls_model_dir=os.path.join(pocr_name, 'cls/ch_ppocr_mobile_v2.0_cls_slim_infer').replace('\\', '/'),
            # E:\PdFast\pp_model\cls\ch_ppocr_mobile_v2.0_cls_slim_infer',
            det_db_unclip_ratio=1.5,
            max_text_length=16,
            rec_batch_num=6,
            lang=lan,
            show_log=False,
            enable_mkldnn=True,
            use_tensorrt=True,
            use_mp=True,  # 是否开启多进程预测
            total_process_num=16,
            cpu_threads=10,
            det_db_box_thresh=0.5,
            use_gpu=False,
            rec_algorithm='SVTR_LCNet',  # 识别模型默认使用的rec_algorithm为SVTR_LCNet，CRNN
            det_limit_side_len=320,
        )  # need to run only once to download and load model into memory
        result = ocr.ocr(img_path)
        str_time = time.time() - t1
        print('所需时间：', str_time)
        results = {
            'result': result,
            'str_time': str_time
        }
        logger.info(' filename:, result: %s' % (results))
        return results
    except Exception:
        trace_err = traceback.format_exc().replace("\n", "\\n")
        logger.error(trace_err)


def vis_structure_result(image, result, save_folder='./output/'):
    # 生成版面分析图片
    font_path = os.path.join(basedir, 'test/font/simsun.ttc').replace('\\',
                                                                      '/')  # './fonts/simfang.ttf' PaddleOCR下提供字体包
    images = Image.open(image).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(images, boxes, txts, scores, font_path=font_path)
    im_show = Image.fromarray(im_show)
    im_show.save(os.path.join(save_folder, 'result_struct.jpg'))
    return im_show


def get_grcode(images_input, binary_max=230, binary_step=2):
    # 1、读取二维码图片
    try:
        t1 = time.time()
        image_input = cv2.imdecode(np.fromfile(images_input, dtype=np.uint8), -1)
        # 2、解析二维码中的数据
        # 把输入图像灰度化
        if len(image_input.shape) >= 3:
            image_input = cv2.cvtColor(image_input, cv2.COLOR_RGB2GRAY)  # 转换灰度图
        # 获取自适配阈值
        binary, _ = cv2.threshold(image_input, 0, 255, cv2.THRESH_OTSU)
        # 二值化递增检测
        res = []
        while (binary < binary_max) and (len(res) == 0):
            binary, mat = cv2.threshold(image_input, binary, 255, cv2.THRESH_BINARY)
            res = pyzbar.decode(mat,symbols=[ZBarSymbol.CODE128])
            binary += binary_step
        barcodeData = ''
        barcodeType = ''
        for barcode in res:
            barcodeData += barcode.data.decode("utf-8")
            barcodeType += barcode.type
        results = {}
        results['barcodeType'] = barcodeType
        results['str_time'] = time.time() - t1
        if barcodeData:
            results['result'] = barcodeData
            logger.info('fliename:{name},条码类型{type},result:{res}'.format(name=images_input,type=barcodeType,res=results))
            return results
        else:
            results['result'] = None
            logger.debug('fliename:{name},条码类型{type},result:{res}'.format(name=images_input, type=barcodeType, res=results))
            return results
    except Exception:
        trace_err = traceback.format_exc()
        logger.error(trace_err)


def postprocess(rec_res):
    keys = ["加工单位", "烟叶名称", "箱号",
            "生产日期", "类别", "产地", "年份", "形态", "等级", "加工日期",
            "品种", "含水率", "打叶员", "类型", "加工方式"]
    for _ in rec_res:
        if '批次' in _:
            rec_res.remove(_)
    key_value = []
    if len(rec_res) > 1:
        for i in range(len(rec_res) - 1):
            rec_str = rec_res[i]
            for key in keys:
                if rec_str[:2] in key:
                    key_value.append([rec_str, rec_res[i + 1]])
                    break
    # key_value 匹配的key-value值
    carton = [i for i in key_value for j in i if '箱号' in j]
    print(key_value)
    for _ in carton:
        for j in _:
            cartonNo = re.findall(r'\b\d+\b', j)
            if cartonNo:
                return cartonNo


def batch_ocr(imgPath):
    t = time.time()
    filelist = os.listdir(imgPath)
    imgs_path = [os.path.join(imgPath, i) for i in filelist if i.endswith(('.png', 'jpg', 'bmp'))]
    num = 0
    for i in imgs_path:
        # res = get_grcode(i)
        # txt = '文件名:{filename} result:{caseNo}'.format(filename=i, caseNo=res.get('result',None))
        res = ocr_result(i)
        result = res.get('result')
        txts = [line[1][0] for line in result]
        caseNum = [re.findall("[0-9]{1,5}", i) for i in txts if '箱号' in i]
        print('正则caseNum:', caseNum)
        if not (caseNum and caseNum[0]):
            print('未使用正则')
            caseNo = postprocess(txts)
        else:
            caseNo = caseNum
        txt = '文件名:{filename} 这是caseNo: {caseNo}'.format(filename=i, caseNo=getFirst(caseNo))
        f_name = os.path.join(basedir, os.path.split(imgPath)[-1] + '.txt')
        with open(f_name, mode='a') as f:
            f.write(str(txt))
            f.write("\n")
        num += 1
    time_sum = time.time() - t
    print('共识别 {num} 张图片'.format(num=len(imgs_path)))
    print('总需要消耗时间：', time_sum)
    print('平均消耗：', time_sum / num)


def getFirst(l):
    if l:
        return  l[0] if not isinstance(l[0], list) else getFirst(l[0])
    else:
        return None

def format_result(result):
    keys = ["加工单位", "烟叶名称", "箱号",
            "生产日期", "类别", "产地", "年份", "形态", "等级", "加工日期",
            "品种", "含水率", "打叶员", "类型", "加工方式", "物料代码", "生产线"]
    txts = [line[1][0] for line in result]




if __name__ == '__main__':
    imgPath = r"E:\烟叶标签照片\2022-10-27_00K42994168"
    path = r"E:\烟叶标签照片\2022-10-27_00K42994168\557.jpg"
    # batch_ocr(imgPath)


    img = Image.open(path)
    enh_bri = ImageEnhance.Brightness(img)  # 亮度增强
    image_brightened = enh_bri.enhance(1.5)
    # image_brightened.show()
    image_brightened = np.array(image_brightened)
    # image = Image.open(path).convert('RGB')
    # print('二维码识别：', get_grcode(path))
    # img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    # img = letterbox_image(img,(960, 694))
    # img.show()

    res = ocr_result(path)
    #
    # # print(response_results(res['result']))
    # # 将识别出来的文字进行关键字匹配，删选出箱号
    result = res.get('result')
    if not res:
        sys.exit()
    print('result:'
          '\n', result)
    txts = [line[1][0] for line in result]
    print('text\n', txts)
    caseNum = [re.findall("[0-9]{1,5}", i) for i in txts if '箱号' in i]
    print('正则caseNum:',caseNum)
    if not (caseNum and caseNum[0]):
        print('未使用正则')
        caseNo = postprocess(txts)
    else:
        caseNo = caseNum
    print('JB:',caseNo)
    print('这是caseNo：', getFirst(caseNo))
    # #
    # # vis_structure_result(path, result)
    # # path = r"E:\烟叶标签照片\imgtest\Image_20221019104807882.jpg"
    # imgpa = r"E:\烟叶标签照片\2022-10-27_00K42994168\557.jpg"
    # code128 = get_grcode(imgpa)
    # print(code128)


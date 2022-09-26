import os
import traceback

from pyzbar import pyzbar
from  logger.logging import logger

try:
    from PIL import Image
except ImportError:
    import Image
from paddleocr import PaddleOCR, draw_ocr
import time

basedir = os.path.dirname(os.path.abspath(__file__))  # E:\PdFast
pocr_name = os.path.join(basedir, 'pp_model')




def ocr_result(img_path='./test/image/chenjun.jpg', use_angle=True, cls=True, rec=True, det=True, lan="ch"):
    t1 = time.time()
    img_path = img_path
    # default_lan = lan
    try:
        ocr = PaddleOCR(
            use_angle_cls=use_angle,
            rec_model_dir=os.path.join(pocr_name, 'rec/ch_PP-OCRv3_rec_infer').replace('\\', '/'),
            # r'E:\PdFast\pp_model\rec\ch_PP-OCRv3_rec_infer',
            det_model_dir=os.path.join(pocr_name, 'det/ch_PP-OCRv3_det_infer').replace('\\', '/'),
            # 'E:/PdFast/pp_model/det/ch_PP-OCRv3_det_infer',
            rec_char_dict_path=os.path.join(basedir, 'test/font/ppocr_keys_v1.txt').replace('\\', '/'),
            # 'E:/PdFast/test/font/ppocr_keys_v1.txt',
            cls_model_dir=os.path.join(pocr_name, 'cls/ch_ppocr_mobile_v2.0_cls_slim_infer').replace('\\', '/'),
            # E:\PdFast\pp_model\cls\ch_ppocr_mobile_v2.0_cls_slim_infer',
            det_db_unclip_ratio=1.5,
            lang=lan,
            show_log=False,
            enable_mkldnn=False,
            use_tensorrt=False,

            use_mp=True,  # 是否开启多进程预测
            total_process_num=30,
            cpu_threads=4,
            det_db_box_thresh=0.5,
            use_gpu=False,
            # rec_algorithm='CRNN', #识别模型默认使用的rec_algorithm为SVTR_LCNet
            det_limit_side_len=960
        )  # need to run only once to download and load model into memory
        result = ocr.ocr(img_path)
        str_time = time.time() - t1
        print('所需时间：', str_time)
        results = {
            'result': result,
            'str_time': str_time
        }
        logger.info('filename: %s, result: %s' % (img_path, results))
        return results
    except Exception:
        trace_err = traceback.format_exc().replace("\n", "\\n")
        logger.error(trace_err)


def vis_structure_result(image, result, save_folder='../output/'):
    # 生成版面分析图片
    font_path = '../test/font/仿宋_GB2312.ttf'  # './fonts/simfang.ttf' PaddleOCR下提供字体包
    images = Image.open(image).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(images, boxes, txts, scores, font_path=font_path)
    im_show = Image.fromarray(im_show)
    im_show.save(os.path.join(save_folder, 'result_struct.jpg'))
    return im_show



def get_grcode(img_path):
    # 1、读取二维码图片
    try:
        t1 = time.time()
        frame = Image.open(img_path)
        # image = cv2.imread(img_path)
        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # 2、解析二维码中的数据
        barcodes = pyzbar.decode(frame)
        # 3、在数据中解析出二维码的data信息
        data = ''
        for barcode in barcodes:
            data += barcode.data.decode("utf-8")
        str_time = time.time() - t1
        results = {}
        results['str_time'] = str_time
        if data:
            results['result'] = data
            logger.info('filename: %s, result: %s' % (img_path, results))
            return results
        else:
            results['result'] = None
            return results
    except Exception:
        trace_err = traceback.format_exc().replace("\n", "\\n")
        logger.error(trace_err)


if __name__ == '__main__':
    path = r"E:\烟叶标签照片\1994647c4277ca8a5ede505166aae8f0.jpg"
    # image = Image.open(path).convert('RGB')
    results = ocr_result(r'E:\\Ocr_Script\\output\\69.jpg')
    for i in results.get('result'):
        print(i)
    # vis_structure_result(path, result)
    # img_path = '../test/image/barcode_example.png'
    # print(get_grcode(path))


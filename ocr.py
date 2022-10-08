import os
import re
import sys
import traceback
import paddle.inference as paddle_infer
from pyzbar import pyzbar
from logger.logging import logger

try:
    from PIL import Image
except ImportError:
    import Image
from paddleocr import PaddleOCR, draw_ocr
import time

basedir = os.path.dirname(os.path.abspath(__file__))  # E:\PdFast
pocr_name = os.path.join(basedir, 'pp_model')

# 创建 config
config = paddle_infer.Config()
# 设置模型的文件夹路径
config.set_model("model.pdmodel", "model.pdiparam")
# 设置 CPU Blas 库线程数为 10
config.set_cpu_math_library_num_threads(10)
config.switch_ir_optim()
config.enable_mkldnn()
config.enable_memory_optim()
# 通过 API 获取 CPU 信息 - 10
print('默认开启CPU',config.cpu_math_library_num_threads())

def ocr_result(img_path='./test/image/chenjun.jpg', use_angle=True, cls=True, rec=True, det=True, lan="ch"):
    t1 = time.time()
    img_path = img_path
    # default_lan = lan
    try:
        ocr = PaddleOCR(
            use_angle_cls=use_angle,
            rec_model_dir=os.path.join(pocr_name, 'rec/ch_PP-OCRv3_rec_infer').replace('\\', '/'),
            # r'E:\PdFast\pp_model\rec\ch_PP-OCRv3_rec_infer',
            det_model_dir=os.path.join(pocr_name, 'det/ch_ppocr_mobile_v2.0_det_prune_infer').replace('\\', '/'),
            # 'E:/PdFast/pp_model/det/ch_PP-OCRv3_det_infer',
            rec_char_dict_path=os.path.join(basedir, 'test/font/ppocr_keys_v1.txt').replace('\\', '/'),
            # 'E:/PdFast/test/font/ppocr_keys_v1.txt',
            cls_model_dir=os.path.join(pocr_name, 'cls/ch_ppocr_mobile_v2.0_cls_slim_infer').replace('\\', '/'),
            # E:\PdFast\pp_model\cls\ch_ppocr_mobile_v2.0_cls_slim_infer',
            det_db_unclip_ratio=1.5,
            max_text_length=15,
            rec_batch_num=6,
            # det = False,
            # rec = False,
            lang=lan,
            show_log=False,
            enable_mkldnn=True,
            use_tensorrt=False,
            use_mp=True,  # 是否开启多进程预测
            total_process_num=16,
            cpu_threads=10,
            det_db_box_thresh=0.5,
            use_gpu=False,
            rec_algorithm='SVTR_LCNet',  # 识别模型默认使用的rec_algorithm为SVTR_LCNet，CRNN
            det_limit_side_len=960,
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


def vis_structure_result(image, result, save_folder='./output/'):
    # 生成版面分析图片
    font_path = os.path.join(basedir, 'test/font/simsun.ttc').replace('\\', '/')  # './fonts/simfang.ttf' PaddleOCR下提供字体包
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


def postprocess(rec_res):
    keys = ["加工单位", "烟叶名称", "毛重", "净重", "批次", "箱号",
            "生产日期", "类别", "产地", "年份", "形态", "等级", "加工日期",
            "品种", "含水率", "打叶员", "类型", "加工方式", "物料代码", "生产线"]
    key_value = []
    if len(rec_res) > 1:
        for i in range(len(rec_res) - 1):
            rec_str = rec_res[i]
            for key in keys:
                if rec_str[:2] in key:
                    key_value.append([rec_str, rec_res[i + 1]])
                    break
    # key_value 匹配的key-value值
    print('key-value', key_value)
    carton = [i for i in key_value for j in i if '箱号' in j]
    print('carno:', carton)
    for _ in carton:
        for j in _:
            cartonNo = re.findall('[0-9]{4,5}', j)
            if cartonNo:
                return cartonNo


if __name__ == '__main__':
    path = r"E:\烟叶标签照片\0220930151108.png"
    # image = Image.open(path).convert('RGB')
    print('二维码识别：', get_grcode(path))
    res = ocr_result(path)

    # print(response_results(res['result']))
    # 将识别出来的文字进行关键字匹配，删选出箱号
    if not res:
        sys.exit()
    result = res.get('result')
    if not result:
        sys.exit()
    print('result:\n',result)
    txts = [line[1][0] for line in result]
    print('text\n', txts)
    caseNum = [re.findall("[0-9]{4,5}", i) for i in txts if '箱号' in i]
    print('正则caseNum:', caseNum)

    if not caseNum[0]:
        print('未使用正则')
        caseNo = postprocess(txts)
    else:
        caseNo = caseNum[0]
    print('这是caseNo：', caseNo)
    # vis_structure_result(path, result)
    # img_path = '../test/image/barcode_example.png'
    # print(get_grcode(path))

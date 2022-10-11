# Ocr_script
使用百度飞桨开源模型建立的ocr文字识别,包含二维码识别/cv2清晰度筛选，使用海康威视工业相机sdk二次开发使用opcua连接
#### MvImport 
海康威视官方sdk文件，安装mvs后在位于安装目录
``
sys.path.append("C:\Program Files (x86)\MVS\Development\Samples\Python\MvImport")  
``
下载地址 海康机器人官网
#### logger/nb_log_config,py
日志文件配置，使用国产三方库nb_log，个人觉得很强大(只要import nb_log，项目所有地方的print自动现型并在控制台可点击几精确跳转到print的地方)
```
#github地址
https://github.com/ydf0509/nb_log/
```
#### pp_model
百度飞桨ocr识别模型，详情可前往百度飞浆查看
https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.5/doc/doc_ch/models_list.md
#### opcua_kepserver.py
``pip install opcua  ``

OPC UA 是什么 可参考 http://t.zoukankan.com/haozi0804-p-12751127.html

构建客户端连接opcua服务器

#### open_sdk.py
python调用海康威视工业相机SDK主动/回调取流实例，官方SDK文件在MvImport中（用C语言的动态链接库实现的python库）

#### ScreeImage.py
使用opencv的Laplacian库进行清晰度识别
高斯模糊-去噪点Gausslur()
转换为灰度图像cvtColor()
拉普拉斯-二阶导数计算Laplancian()
取绝对值convertScaleAbs()
显示结果

#### removeBackground.py
将图片二值化处理，边缘检测等方式将标签区域裁剪下来，降低背景干扰
利用仿射变换/透视变换进行图片矫正，利用最大外切矩形面积判断 barcode_angle()
图片倾斜矫正，适合图片中轮廓清晰部分shape_correction() 
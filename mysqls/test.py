# -*- coding:utf-8 -*-

from mysqls.mysql import ConnectMysql

sql ='''INSERT INTO redrycompany.gs_prod_box_tag_img (PK_PROD_BOX_TAG_IMG, 
SRC_IMG, CUT_IMG, SMALL_IMG, CODE_INFO, FACTORY_BOX_CODE,
 INDUSTRY_BOX_NO, IMG_INFO, BUSINESS_YEAR, ORG_UNIQUE_CD,
  ORG_NAME, SEND_TIME, SEND_STATE, CREATE_TIME, MODIFY_TIME, DATA_STATE) 
  VALUES ('44444444444444444444444444444444', 'connect_test.jpg', 
  'connect_test.jpg', 
  '/boxTagImg/21090002889-444bdad5f131499c91afe5ecfdd17ee1_small.png', 
  null, '21090002889', '0643', 
  '{"body":"[''复烤云码'', ''(中国烟草]云南烟叶复烤有限责任公司'', ''ATOBACCOYUNNANTOBACCOREDRYNGLIMITBDLIABILITYCO'', ''M:2109000288'', ''年份2021'', ''产地云南临论'', ''级W/CFA/CFA'', ''类别烤'', ''帐务等级CIE-WLC'', ''类型片烟'', ''班次四班'', ''品种铤'', ''毛重218.4Kg'', ''净重200Kg'', ''箱号0643'', ''加工时间2021-11-11'', ''质检员I-T2'', ''临打员IETC'', ''采购员'', ''委托单位湖南中烟工业有限责任公司'', ''加工单位云南烟叶复将有限责任公司保山复悔'', ''558889:'', ''防城'']","headers":{"Content-Type":["text/html; charset=utf-8"],"Content-Length":["525"],"Server":["Werkzeug/2.0.2 Python/3.6.13"],"Date":["Mon, 22 Nov 2021 06:29:57 GMT"]},"statusCode":"OK","statusCodeValue":200}',
   null, null, null, null, null,
    '2022-09-15 15:47:39', 
    null, '0')'''
sqls = 'select * from redrycompany.gs_prod_box_tag_img'
show = 'show tables'
with ConnectMysql(log_time=False) as my:
    print(my.execute(show))


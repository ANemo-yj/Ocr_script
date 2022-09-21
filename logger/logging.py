#coding: utf-8
import os
import time

from nb_log import LogManager

basedir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(basedir, 'log')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
filename = time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
logger = LogManager('log_demo').get_logger_and_add_handlers(log_path=log_dir,
                                                            log_filename=filename,
                                                            formatter_template=5)

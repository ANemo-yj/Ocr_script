"""
windows系统监听指定文件夹下 文件 文件夹变更
"""

import datetime
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_any_event(self, event):
        print("-----")
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    # 移动
    def on_moved(self, event):
        if event.is_directory:
            print("目录 moved:{src_path} -> {dest_path}".format(src_path=event.src_path, dest_path=event.dest_path))
        else:
            print("文件 moved:{src_path} -> {dest_path}".format(src_path=event.src_path, dest_path=event.dest_path))

    # 新建
    def on_created(self, event):
        if event.is_directory:
            print("目录 created:{file_path}".format(file_path=event.src_path))
        else:
            print("文件 created:{file_path}".format(file_path=event.src_path))

    # 删除
    def on_deleted(self, event):
        if event.is_directory:
            print("目录 deleted:{file_path}".format(file_path=event.src_path))
        else:
            print("文件 deleted:{file_path}".format(file_path=event.src_path))

    # 修改
    def on_modified(self, event):

        if event.is_directory:
            print("目录 modified:{file_path}".format(file_path=event.src_path))
        else:
            print("文件 modified:{file_path}".format(file_path=event.src_path))


if __name__ == '__main__':
    #path = r"E:\windos自动监听文件夹"
    path = sys.argv[1]
    print(str(sys.argv))
    if os.path.exists(path):
        print(path)
        myEventHandler = MyEventHandler()
        # 观察者
        observer = Observer()
        # recursive:True 递归的检测文件夹下所有文件变化。
        observer.schedule(myEventHandler, path, recursive=True)

        # 观察线程，非阻塞式的。
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        # 等待其他子线程执行结束之后，主线程再终止
        observer.join()
    print('路径错误,请检查路径格式！')
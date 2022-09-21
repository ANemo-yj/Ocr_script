import os
import logging
import logging.config
import json
import sys
import traceback
import time
import threading

from opcua import Client
from opcua import ua
import opcua


class Opcua_client:
    """
    OPCUA Client class
    """

    # opcua_server_ipaddr = settings.plc_ip
    # opcua_server_port = settings.plc_port

    def __init__(self, ip, port):
        self._is_connect = False
        self.ip = ip
        self.port = port
        self.client = Client("opc.tcp://{}:{}".format(ip, port))
        # self.client = Client("opc.tcp://localhost:4840/freeopcua/server/")
        self.first_connect()
        self.root = self.client.get_root_node()
        # this dict manager the node that we can not add the node duplicatly（复制）
        # 这个dict管理器是我们不能重复添加节点的节点
        self._node_dict = {}
        # t = threading.Thread(target=self.check_alive_and_connect_daemon, args=(3,))
        # t.setDaemon(True)
        # t.start()

    def disconnect(self):
        self.client.disconnect()
        print("链接断开")

    def connect(self):
        try:
            print("now connect to opcua server")
            self.client.connect()
        except:
            self._is_connect = False
            print("the connection to opcua is disconnect")
            return False
        self._is_connect = True
        print("The opcua connection is created now")
        return True

    def first_connect(self):
        tmp = self.connect()
        if tmp is False:
            time.sleep(1)
            self.first_connect()
        else:
            return True

# =======================================================================================================================================================

    def check_alive(self):
        try:
            self.client.send_hello()
        except:
            try:
                self.client.disconnect()
            except:
                pass
            self._is_connect = False
            return False
        self._is_connect = True
        return True

    def check_alive_and_connect(self):
        with threading.Lock():
            result = self.check_alive()
        if result is True:
            return True
        else:
            tmp = self.connect()
            return tmp

    def check_alive_and_connect_daemon(self, timedelta):
        while 1:
            result = self.check_alive_and_connect()
            if result is True:
                time.sleep(timedelta)
            else:
                time.sleep(timedelta)
                pass

    def get_node(self, node_id):
        return self.client.get_node(node_id)

    def get_node_and_add(self, node_id):
        if node_id not in self._node_dict:
            self._node_dict[node_id] = self.get_node(node_id)
        return self._node_dict[node_id]

    def get_value(self, node):
        # TODO ADD the function if node type is not right return None or raise Exception
        # if not isinstance(node, opcua.common.node.Node):
        #     return False
        with threading.Lock():
            result = node.get_value()
        return result

    def set_value(self, node, node_value):
        # TO DO CHECK THE TYPE OF THE node and the node_value
        return node.set_value(node_value)

Opcua_client(ip='127.0.0.1',port=49320)
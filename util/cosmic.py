import asyncio
import multiprocessing
import time
from queue import Queue
from threading import Lock


class Cosmic:
    """全局状态管理类，类似参考项目的Cosmic类"""

    # 单例模式
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        """初始化状态"""
        # 事件循环
        self.loop = None

        # 录音状态控制
        self.on = False  # 是否正在录音
        self.recording_start_time = None

        # 队列用于进程间通信
        self.audio_queue = Queue()  # 音频数据队列
        self.result_queue = Queue()  # 识别结果队列

        # WebSocket连接
        self.websocket = None

        # 音频流
        self.audio_stream = None

        # 录音文件路径
        self.current_audio_file = None

        # 识别结果
        self.current_result = None

    def set_loop(self, loop):
        """设置事件循环"""
        self.loop = loop

    def start_recording(self):
        """开始录音"""
        self.on = True
        self.recording_start_time = time.time()

    def stop_recording(self):
        """停止录音"""
        self.on = False
        return self.recording_start_time

    def is_recording(self):
        """检查是否正在录音"""
        return self.on

    def set_audio_file(self, file_path):
        """设置当前录音文件路径"""
        self.current_audio_file = file_path

    def get_audio_file(self):
        """获取当前录音文件路径"""
        return self.current_audio_file

    def set_result(self, result):
        """设置识别结果"""
        self.current_result = result

    def get_result(self):
        """获取识别结果"""
        return self.current_result

    def reset(self):
        """重置状态"""
        self.on = False
        self.recording_start_time = None
        self.current_audio_file = None
        self.current_result = None


# 全局实例
cosmic = Cosmic()
import json
import uuid
import base64
import requests
from pathlib import Path


class VolcengineASRClient:
    """火山引擎大模型ASR客户端"""
    
    def __init__(self, app_id, access_key):
        """
        初始化火山引擎ASR客户端
        
        Args:
            app_id: 火山引擎APP ID
            access_key: 火山引擎Access Token
        """
        self.app_id = app_id
        self.access_key = access_key
        self.base_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
        
    def _prepare_headers(self):
        """准备请求头"""
        return {
            "X-Api-App-Key": self.app_id,
            "X-Api-Access-Key": self.access_key,
            "X-Api-Resource-Id": "volc.bigasr.auc_turbo",
            "X-Api-Request-Id": str(uuid.uuid4()),
            "X-Api-Sequence": "-1",
            "Content-Type": "application/json"
        }
    
    def recognize_audio_file(self, file_path):
        """
        识别音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            dict: 识别结果
        """
        # 读取音频文件并转换为base64
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        
        base64_data = base64.b64encode(audio_data).decode('utf-8')
        
        # 构造请求体
        request_body = {
            "user": {
                "uid": self.app_id
            },
            "audio": {
                "data": base64_data
            },
            "request": {
                "model_name": "bigmodel"
            }
        }
        
        # 发送请求
        headers = self._prepare_headers()
        response = requests.post(self.base_url, json=request_body, headers=headers)
        
        # 检查响应
        if response.status_code != 200:
            raise Exception(f"HTTP Error: {response.status_code}, {response.text}")
        
        # 检查API状态码
        status_code = response.headers.get('X-Api-Status-Code')
        if status_code != '20000000':
            message = response.headers.get('X-Api-Message', 'Unknown error')
            raise Exception(f"API Error: {status_code} - {message}")
        
        return response.json()
    
    def recognize_audio_data(self, audio_data):
        """
        识别音频数据
        
        Args:
            audio_data: 音频数据（bytes）
            
        Returns:
            dict: 识别结果
        """
        base64_data = base64.b64encode(audio_data).decode('utf-8')
        
        # 构造请求体
        request_body = {
            "user": {
                "uid": self.app_id
            },
            "audio": {
                "data": base64_data
            },
            "request": {
                "model_name": "bigmodel"
            }
        }
        
        # 发送请求
        headers = self._prepare_headers()
        response = requests.post(self.base_url, json=request_body, headers=headers)
        
        # 检查响应
        if response.status_code != 200:
            raise Exception(f"HTTP Error: {response.status_code}, {response.text}")
        
        # 检查API状态码
        status_code = response.headers.get('X-Api-Status-Code')
        if status_code != '20000000':
            message = response.headers.get('X-Api-Message', 'Unknown error')
            raise Exception(f"API Error: {status_code} - {message}")
        
        return response.json()
    
    def get_text_result(self, result):
        """
        从识别结果中提取文本
        
        Args:
            result: API返回的完整结果
            
        Returns:
            str: 识别的文本内容
        """
        try:
            return result.get('result', {}).get('text', '')
        except (KeyError, AttributeError):
            return ''
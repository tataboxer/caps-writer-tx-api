"""
ASR服务管理器 - 统一管理腾讯ASR和火山引擎ASR
"""

import os
from config import asr_config, tencent_asr_config, volcengine_asr_config
from util.volcengine_asr import VolcengineASRClient


class ASRManager:
    """ASR服务管理器"""
    
    def __init__(self):
        self.service_type = None
        self.client = None
        self._init_client()
    
    def reload_config(self):
        """重新加载配置并重创建客户端"""
        import os
        from importlib import reload
        import sys
        
        # 重新加载配置模块
        if 'config' in sys.modules:
            reload(sys.modules['config'])
        
        # 重新初始化
        self._init_client()
    
    def _init_client(self):
        """初始化ASR客户端"""
        try:
            # 获取当前配置
            current_service = os.getenv('ASR_SERVICE', 'volcengine')
            self.service_type = current_service
            
            if self.service_type == 'volcengine':
                self.client = VolcengineASRClient(
                    volcengine_asr_config.app_id,
                    volcengine_asr_config.access_key
                )
                print(f"已启用火山引擎ASR服务")
            else:  # tencent
                # 重新创建腾讯ASR客户端
                from util.tencent_asr import TencentASRClient
                self.client = TencentASRClient()
                if self.client and hasattr(self.client, 'client') and self.client.client:
                    print(f"已启用腾讯云ASR服务")
                else:
                    print(f"腾讯云ASR客户端初始化失败，请检查配置")
                    self.client = None
                
        except Exception as e:
            print(f"ASR客户端初始化失败: {e}")
            self.client = None
    
    def recognize_audio_file(self, audio_file_path):
        """识别音频文件"""
        if not self.client:
            raise Exception("ASR客户端未初始化")
        
        if self.service_type == 'volcengine':
            result = self.client.recognize_audio_file(audio_file_path)
            return self.client.get_text_result(result)
        else:  # tencent
            return self.client.recognize_audio_file(audio_file_path)
    
    def recognize_audio_data(self, audio_data):
        """识别音频数据"""
        if not self.client:
            raise Exception("ASR客户端未初始化")
        
        if self.service_type == 'volcengine':
            result = self.client.recognize_audio_data(audio_data)
            return self.client.get_text_result(result)
        else:  # tencent
            return self.client.recognize_audio_data(audio_data)


# 全局ASR管理器实例
asr_manager = ASRManager()


def recognize_audio(audio_file_path):
    """便捷的音频识别函数"""
    return asr_manager.recognize_audio_file(audio_file_path)


def recognize_audio_data(audio_data):
    """便捷的音频数据识别函数"""
    return asr_manager.recognize_audio_data(audio_data)
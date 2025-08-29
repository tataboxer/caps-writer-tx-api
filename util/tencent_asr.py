import base64
import random
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models
from config import tencent_asr_config as TencentASRConfig


class TencentASRClient:
    """腾讯云ASR客户端 - 使用官方SDK"""

    def __init__(self):
        try:
            # 获取随机配置（负载均衡）
            config = TencentASRConfig.get_random_config()
            config_count = TencentASRConfig.get_config_count()

            # 保存配置信息用于调试
            self.secret_id = config['secret_id']
            self.secret_key = config['secret_key']
            self.region = config['region']
            self.bucket = config['bucket']

            # 显示当前使用的配置信息
            masked_secret_id = self.secret_id[:8] + "****" + self.secret_id[-4:] if len(self.secret_id) > 12 else self.secret_id
            if config_count > 1:
                print(f"🔄 使用腾讯云ASR配置 (负载均衡: {config_count}组配置)")
                print(f"📍 当前配置: {self.region} | SecretId: {masked_secret_id}")
            else:
                print(f"📍 使用腾讯云ASR配置: {self.region}")

            # 使用腾讯云官方SDK
            cred = credential.Credential(self.secret_id, self.secret_key)
            http_profile = HttpProfile()
            http_profile.endpoint = "asr.tencentcloudapi.com"

            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile

            self.client = asr_client.AsrClient(cred, self.region, client_profile)
            print("✅ 腾讯云ASR客户端初始化成功")

        except Exception as e:
            print(f"❌ 腾讯云ASR客户端初始化失败: {str(e)}")
            self.client = None

    def recognize_audio_file(self, audio_file_path, audio_format='wav'):
        """
        录音文件识别（一句话）

        Args:
            audio_file_path: 音频文件路径
            audio_format: 音频格式 ('wav', 'mp3', 'm4a', 'flac', 'ogg', 'wma', 'aac')

        Returns:
            str: 识别结果文本
        """
        if not self.client:
            raise Exception("ASR客户端未初始化")

        try:
            # 读取音频文件并编码为base64
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()

            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # 构造请求
            req = models.SentenceRecognitionRequest()
            req.ProjectId = 0
            req.SubServiceType = 2  # 腾讯云通用版本
            req.EngSerViceType = "16k_zh"  # 16k中文普通话
            req.SourceType = 1  # 本地音频文件
            req.VoiceFormat = audio_format
            req.Data = audio_base64
            req.DataLen = len(audio_data)

            # 调用API
            resp = self.client.SentenceRecognition(req)

            # 返回结果
            return resp.Result

        except TencentCloudSDKException as e:
            raise Exception(f"ASR API Error: {e.get_code()} - {e.get_message()}")
        except Exception as e:
            raise Exception(f"Tencent ASR recognition failed: {str(e)}")

    def recognize_audio_data(self, audio_data, audio_format='wav'):
        """
        录音数据识别（一句话）

        Args:
            audio_data: 音频数据（bytes）
            audio_format: 音频格式

        Returns:
            str: 识别结果文本
        """
        if not self.client:
            raise Exception("ASR客户端未初始化")

        try:
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # 构造请求
            req = models.SentenceRecognitionRequest()
            req.ProjectId = 0
            req.SubServiceType = 2
            req.EngSerViceType = "16k_zh"
            req.SourceType = 1
            req.VoiceFormat = audio_format
            req.Data = audio_base64
            req.DataLen = len(audio_data)

            # 调用API
            resp = self.client.SentenceRecognition(req)

            # 返回结果
            return resp.Result

        except TencentCloudSDKException as e:
            raise Exception(f"ASR API Error: {e.get_code()} - {e.get_message()}")
        except Exception as e:
            raise Exception(f"Tencent ASR recognition failed: {str(e)}")


# 全局ASR客户端实例
asr_client = TencentASRClient()


def recognize_audio(audio_file_path, audio_format='wav'):
    """便捷的音频识别函数"""
    return asr_client.recognize_audio_file(audio_file_path, audio_format)


def recognize_audio_data(audio_data, audio_format='wav'):
    """便捷的音频数据识别函数"""
    return asr_client.recognize_audio_data(audio_data, audio_format)
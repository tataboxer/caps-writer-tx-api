import wave
import pyaudio
import threading
import time
import os
import numpy as np
from pathlib import Path
from util.cosmic import cosmic
from config import ClientConfig


class AudioRecorder:
    """音频录制器"""

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.thread = None

        # 音频参数
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # 16kHz采样率，适合语音识别
        self.chunk = 1024

    def find_input_device(self):
        """查找可用的输入设备"""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:
                print(f"找到输入设备: {device_info.get('name')}")
                return i
        return None

    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            return

        device_index = self.find_input_device()
        if device_index is None:
            raise Exception("未找到音频输入设备")

        self.frames = []
        self.is_recording = True
        
        # 设置 cosmic 状态
        cosmic.start_recording()

        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk
            )

            self.thread = threading.Thread(target=self._record_loop)
            self.thread.start()
            print(f"音频录制已启动 (设备: {device_index}, 采样率: {self.rate}Hz)")

        except Exception as e:
            self.is_recording = False
            cosmic.stop_recording()
            raise Exception(f"启动录音失败: {str(e)}")

    def _record_loop(self):
        """录音循环"""
        try:
            while self.is_recording:
                if self.stream:
                    data = self.stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # 计算实时音频电平
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # 安全计算RMS，避免无效值
                    if len(audio_data) > 0:
                        audio_squared = audio_data.astype(np.float64) ** 2
                        mean_squared = np.mean(audio_squared)
                        if mean_squared > 0 and not np.isnan(mean_squared):
                            rms = np.sqrt(mean_squared)
                        else:
                            rms = 0
                    else:
                        rms = 0
                    
                    # 增强灵敏度：使用对数缩放 + 放大系数
                    if rms > 0:
                        power_level = min(100, max(0, np.log10(rms + 1) * 25))  # 对数缩放，更敏感
                    else:
                        power_level = 0
                    
                    # 简化的调试输出（去掉RMS和Power信息）
                    # if power_level > 2:  # 降低阈值
                    #     print(f"🎵 RMS: {rms:.1f}, Power: {power_level:.1f}%")
                    
                    # 更新波形显示（平滑过渡）
                    try:
                        from util.waveform_display import update_waveform_level
                        update_waveform_level(power_level)
                    except Exception as e:
                        print(f"波形更新失败: {e}")
        except Exception as e:
            print(f"录音过程出错: {str(e)}")

    def stop_recording(self, output_path=None):
        """停止录音并保存文件"""
        if not self.is_recording:
            return None

        self.is_recording = False
        cosmic.stop_recording()

        if self.thread:
            self.thread.join(timeout=1.0)

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        # 检查是否需要保存音频文件
        if not ClientConfig.save_audio:
            print("音频保存已禁用，不保存录音文件")
            return None

        # 保存音频文件
        if output_path and self.frames:
            return self.save_audio_file(output_path)
        elif self.frames:
            # 使用默认文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            default_path = f"recordings/recording_{timestamp}.wav"
            return self.save_audio_file(default_path)

        return None

    def save_audio_file(self, file_path):
        """保存音频文件"""
        try:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # 保存WAV文件
            wf = wave.open(file_path, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()

            print(f"音频文件已保存: {file_path}")
            return file_path

        except Exception as e:
            print(f"保存音频文件失败: {str(e)}")
            return None


    def cleanup(self):
        """清理资源"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()

    def get_audio_data(self):
        """获取音频数据（用于直接处理）"""
        if self.frames:
            return b''.join(self.frames)
        return None
    
    def get_wav_data(self):
        """获取WAV格式的音频数据"""
        if not self.frames:
            return None
        
        try:
            import io
            # 创建内存中的WAV文件
            wav_buffer = io.BytesIO()
            wf = wave.open(wav_buffer, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            
            # 返回WAV数据
            wav_data = wav_buffer.getvalue()
            wav_buffer.close()
            return wav_data
            
        except Exception as e:
            print(f"生成WAV数据失败: {e}")
            return None


# 全局录音器实例
audio_recorder = AudioRecorder()


def start_recording():
    """便捷的开始录音函数"""
    audio_recorder.start_recording()


def stop_recording(output_path=None):
    """便捷的停止录音函数"""
    return audio_recorder.stop_recording(output_path)
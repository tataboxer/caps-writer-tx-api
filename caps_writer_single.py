#!/usr/bin/env python3
"""
CapsWriter单进程版本
整合客户端和服务端功能
"""

import asyncio
import os
import signal
import sys
import time
import threading
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config import ClientConfig, asr_config
from util.cosmic import cosmic
from util.keyboard_handler import keyboard_handler
from util.audio_recorder import audio_recorder
from util.asr_manager import recognize_audio
from util.result_handler import save_recognition_result
from util.config_manager import config_manager

# 系统托盘相关
try:
    import pystray
    from PIL import Image
    HAS_SYSTEM_TRAY = True
except ImportError:
    HAS_SYSTEM_TRAY = False


class CapsWriterSingle:
    """CapsWriter单进程版本"""

    def __init__(self):
        self.running = False
        self.recording_thread = None
        self.system_tray = None
        self.tray_thread = None

    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            print("\n收到退出信号，正在关闭...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def create_system_tray_icon(self):
        """创建系统托盘图标"""
        if not HAS_SYSTEM_TRAY:
            print("系统托盘功能不可用，请安装 pystray 和 Pillow")
            return None

        try:
            # 加载图标
            icon_path = Path(__file__).parent / "assets" / "icon.ico"
            if icon_path.exists():
                icon = Image.open(icon_path)
            else:
                print(f"图标文件不存在: {icon_path}")
                # 创建一个默认的简单图标
                icon = Image.new('RGB', (64, 64), color='red')

            # 创建简单菜单
            menu = pystray.Menu(
                pystray.MenuItem(
                    "CapsWriter 语音输入工具",
                    lambda: None,
                    enabled=False
                ),
                pystray.Menu.SEPARATOR,

                pystray.MenuItem(
                    "火山引擎 (Volcengine)",
                    lambda: self.switch_asr_service('volcengine'),
                    checked=lambda item: os.getenv('ASR_SERVICE', 'volcengine') == 'volcengine'
                ),
                pystray.MenuItem(
                    "腾讯云 (Tencent)",
                    lambda: self.switch_asr_service('tencent'),
                    checked=lambda item: os.getenv('ASR_SERVICE', 'volcengine') == 'tencent'
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    "退出",
                    self.stop
                )
            )

            # 创建托盘图标
            tray = pystray.Icon(
                "CapsWriter",
                icon,
                "CapsWriter - 语音输入工具",
                menu
            )

            return tray

        except Exception as e:
            print(f"创建系统托盘图标失败: {e}")
            return None
    


    def start_system_tray(self):
        """启动系统托盘"""
        if not HAS_SYSTEM_TRAY:
            return

        self.system_tray = self.create_system_tray_icon()
        if self.system_tray:
            def tray_worker():
                try:
                    self.system_tray.run()
                except Exception as e:
                    print(f"系统托盘运行出错: {e}")

            self.tray_thread = threading.Thread(target=tray_worker, daemon=True)
            self.tray_thread.start()
            print("系统托盘图标已启动")

    def stop_system_tray(self):
        """停止系统托盘"""
        if self.system_tray:
            try:
                self.system_tray.stop()
                print("系统托盘图标已停止")
            except Exception as e:
                print(f"停止系统托盘时出错: {e}")
    
    def create_switch_handler(self, service):
        """创建切换处理器"""
        def handler():
            self.switch_asr_service(service)
        return handler
    
    def switch_asr_service(self, service):
        """切换ASR服务"""
        try:
            current_service = config_manager.get_current_asr_service()
            if current_service == service:
                print(f"已经是{service.upper()}服务，无需切换")
                return
            
            print(f"切换ASR服务: {current_service} -> {service}")
            
            # 更新配置文件
            if config_manager.update_asr_service(service):
                print(f"ASR服务已切换为: {service.upper()}")
                
                # 重新加载ASR配置
                from util.asr_manager import asr_manager
                asr_manager.reload_config()
                print("配置已立即生效，无需重启程序")
            else:
                print("更新配置失败")
                
        except Exception as e:
            print(f"切换ASR服务失败: {e}")

    def start_audio_recording(self, audio_file):
        """开始音频录制"""
        try:
            audio_recorder.start_recording()

            def recording_worker():
                # 等待录音开始
                while not cosmic.is_recording():
                    time.sleep(0.01)

                # 等待录音结束
                while cosmic.is_recording():
                    time.sleep(0.01)

                # 停止录音
                saved_file = audio_recorder.stop_recording(audio_file)
                
                # 获取音频数据进行识别
                if saved_file:
                    print(f"录音已保存: {saved_file}")
                    # 使用文件路径识别
                    recognition_thread = threading.Thread(
                        target=self.process_recognition,
                        args=(saved_file, None)
                    )
                    recognition_thread.daemon = True
                    recognition_thread.start()
                else:
                    # 获取WAV格式的音频数据
                    wav_data = audio_recorder.get_wav_data()
                    if wav_data:
                        print("使用音频数据进行识别")
                        # 使用音频数据识别
                        recognition_thread = threading.Thread(
                            target=self.process_recognition,
                            args=(None, wav_data)
                        )
                        recognition_thread.daemon = True
                        recognition_thread.start()
                    else:
                        print("未获取到音频数据")

            self.recording_thread = threading.Thread(target=recording_worker)
            self.recording_thread.daemon = True
            self.recording_thread.start()

        except Exception as e:
            print(f"启动录音失败: {str(e)}")

    def process_recognition(self, audio_file, audio_data):
        """处理语音识别"""
        try:
            if audio_file:
                print(f"开始识别音频文件: {audio_file}")
                # 使用文件识别
                from util.asr_manager import recognize_audio
                result = recognize_audio(audio_file)
                source = audio_file
            elif audio_data:
                print("开始识别音频数据")
                # 使用音频数据识别
                from util.asr_manager import recognize_audio_data
                result = recognize_audio_data(audio_data)
                source = "audio_data"
            else:
                print("无效的音频数据")
                return

            if result:
                print(f"识别结果: {result}")
                # 保存结果并自动粘贴
                save_recognition_result(source, result)
                print("识别完成，系统已准备下次录音")
            else:
                print("识别失败：未获取到有效结果")
                print("系统已准备下次录音")

        except Exception as e:
            print(f"识别过程出错: {str(e)}")
            print("系统已准备下次录音")

    def start(self):
        """启动应用"""
        print("=== CapsWriter 单进程版本 ===")
        print(f"快捷键: {ClientConfig.shortcut}")
        print(f"模式: {'长按模式' if ClientConfig.hold_mode else '单击模式'}")
        print(f"ASR服务: {asr_config.asr_service.upper()}")

        self.running = True
        self.setup_signal_handlers()

        # 设置事件循环
        cosmic.set_loop(asyncio.new_event_loop())

        try:
            # 启动系统托盘
            self.start_system_tray()

            # 自定义键盘处理器，集成录音和识别
            self.setup_custom_keyboard_handler()

            # 启动键盘监听
            keyboard_handler.start()

            print("CapsWriter已就绪，按下快捷键开始录音")
            print("按Ctrl+C退出或右键托盘图标选择退出")

            # 保持运行
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n用户中断")
        except Exception as e:
            print(f"运行出错: {str(e)}")
        finally:
            self.stop()

    def setup_custom_keyboard_handler(self):
        """设置自定义键盘处理器"""
        import keyboard
        from util.keyboard_handler import KeyboardHandler

        # 创建自定义处理器
        class CustomKeyboardHandler(KeyboardHandler):
            def __init__(self, app):
                super().__init__()
                self.app = app

            def launch_recording(self):
                """启动录音"""
                super().launch_recording()
                audio_file = cosmic.get_audio_file()
                if audio_file:
                    self.app.start_audio_recording(audio_file)

        # 替换键盘处理器
        global keyboard_handler
        keyboard_handler = CustomKeyboardHandler(self)

    def stop(self):
        """停止应用"""
        if not self.running:
            return

        print("正在关闭CapsWriter...")
        self.running = False

        # 停止录音
        if cosmic.is_recording():
            audio_recorder.stop_recording()

        # 停止键盘监听
        keyboard_handler.stop()

        # 停止系统托盘
        self.stop_system_tray()

        print("CapsWriter已关闭")


def main():
    """主函数"""
    app = CapsWriterSingle()
    app.start()


if __name__ == "__main__":
    main()
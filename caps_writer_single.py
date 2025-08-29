#!/usr/bin/env python3
"""
CapsWriter单进程版本
整合客户端和服务端功能
"""

import asyncio
import signal
import sys
import time
import threading
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config import ClientConfig, TencentASRConfig
from util.cosmic import cosmic
from util.keyboard_handler import keyboard_handler
from util.audio_recorder import audio_recorder
from util.tencent_asr import recognize_audio
from util.result_handler import save_recognition_result

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

            # 创建菜单
            menu = pystray.Menu(
                pystray.MenuItem(
                    "CapsWriter 语音输入工具",
                    lambda: None,
                    enabled=False
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    f"快捷键: {ClientConfig.shortcut}",
                    lambda: None,
                    enabled=False
                ),
                pystray.MenuItem(
                    f"模式: {'长按' if ClientConfig.hold_mode else '单击'}",
                    lambda: None,
                    enabled=False
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

                # 停止录音并保存
                saved_file = audio_recorder.stop_recording(audio_file)
                if saved_file:
                    print(f"录音已保存: {saved_file}")
                    # 启动识别线程
                    recognition_thread = threading.Thread(
                        target=self.process_recognition,
                        args=(saved_file,)
                    )
                    recognition_thread.daemon = True
                    recognition_thread.start()

            self.recording_thread = threading.Thread(target=recording_worker)
            self.recording_thread.daemon = True
            self.recording_thread.start()

        except Exception as e:
            print(f"启动录音失败: {str(e)}")

    def process_recognition(self, audio_file):
        """处理语音识别"""
        try:
            print(f"开始识别音频文件: {audio_file}")

            # 调用腾讯ASR
            result = recognize_audio(audio_file, audio_format='wav')

            if result:
                print(f"识别结果: {result}")
                # 保存结果并自动粘贴
                save_recognition_result(audio_file, result)
            else:
                print("识别失败：未获取到有效结果")

        except Exception as e:
            print(f"识别过程出错: {str(e)}")

    def start(self):
        """启动应用"""
        print("=== CapsWriter 单进程版本 ===")
        print(f"快捷键: {ClientConfig.shortcut}")
        print(f"模式: {'长按模式' if ClientConfig.hold_mode else '单击模式'}")
        print("使用腾讯ASR进行语音识别")

        # 检查腾讯ASR配置
        if not TencentASRConfig.secret_id or not TencentASRConfig.secret_key:
            print("错误：腾讯ASR配置不完整")
            print("请在config.py中配置secret_id和secret_key")
            return

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
import keyboard
import time
import asyncio
from threading import Event
from concurrent.futures import ThreadPoolExecutor
from config import ClientConfig
from util.cosmic import cosmic


class KeyboardHandler:
    """键盘监听处理器"""

    def __init__(self):
        self.pressed = False
        self.released = True
        self.event = Event()
        self.pool = ThreadPoolExecutor(max_workers=2)
        self.task = None

    def shortcut_correct(self, e):
        """验证按键是否正确"""
        key_expect = keyboard.normalize_name(ClientConfig.shortcut).replace('left ', '')
        key_actual = e.name.replace('left ', '')
        return key_expect == key_actual

    def launch_recording(self):
        """启动录音"""
        print("开始录音...")
        cosmic.start_recording()
        cosmic.set_audio_file(self.generate_audio_filename())

    def cancel_recording(self):
        """取消录音"""
        print("取消录音")
        cosmic.stop_recording()
        cosmic.reset()

    def finish_recording(self):
        """完成录音"""
        duration = cosmic.stop_recording()
        if duration:
            duration_sec = time.time() - duration
            print(f"录音完成，持续时间: {duration_sec:.2f}秒")
        else:
            print("录音完成")
        return cosmic.get_audio_file()

    def generate_audio_filename(self):
        """生成录音文件名"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return f"recordings/recording_{timestamp}.wav"

    def smart_restore_key(self):
        """智能恢复按键状态，避免干扰输入法"""
        try:
            import win32gui
            import win32process
            import psutil
            
            # 获取当前活动窗口
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                process_name = process.name().lower()
                
                # 如果是输入法相关进程，不恢复按键
                input_method_processes = [
                    'sogouinput.exe', 'qqpinyin.exe', 'baiduinput.exe',
                    'microsoftpinyin.exe', 'ctfmon.exe', 'inputmethod.exe'
                ]
                
                if any(ime in process_name for ime in input_method_processes):
                    print(f"检测到输入法进程 {process_name}，跳过按键恢复")
                    return
            
            # 延迟后恢复按键
            time.sleep(0.1)  # 增加延迟时间
            keyboard.send(ClientConfig.shortcut)
            
        except ImportError:
            # 如果没有win32库，使用简单延迟
            time.sleep(0.1)
            keyboard.send(ClientConfig.shortcut)
        except Exception as e:
            print(f"智能恢复按键失败: {e}")
            # 失败时使用原始方法
            time.sleep(0.01)
            keyboard.send(ClientConfig.shortcut)

    def count_down(self, e):
        """按下后开始倒数"""
        time.sleep(ClientConfig.threshold)
        e.set()

    def manage_task(self, e):
        """管理录音任务"""
        was_recording = cosmic.is_recording()

        # 启动录音
        if not was_recording:
            self.launch_recording()

        # 检查是否是单击（及时松开）
        if e.wait(timeout=ClientConfig.threshold * 0.8):
            if cosmic.is_recording() and was_recording:
                audio_file = self.finish_recording()
                # 异步处理识别
                asyncio.run_coroutine_threadsafe(
                    self.process_recognition(audio_file),
                    cosmic.loop
                )
        else:
            # 长按，取消录音并发送按键
            if not was_recording:
                self.cancel_recording()
            keyboard.send(ClientConfig.shortcut)

    def click_mode_handler(self, e):
        """单击模式处理器"""
        if e.event_type == 'down' and self.released:
            self.pressed, self.released = True, False
            self.event = Event()
            self.pool.submit(self.count_down, self.event)
            self.pool.submit(self.manage_task, self.event)

        elif e.event_type == 'up' and self.pressed:
            self.pressed, self.released = False, True
            self.event.set()

    def hold_mode_handler(self, e):
        """长按模式处理器"""
        if e.event_type == 'down' and not cosmic.is_recording():
            self.launch_recording()

        elif e.event_type == 'up':
            start_time = cosmic.recording_start_time
            if start_time:
                duration = time.time() - start_time

                if duration < ClientConfig.threshold:
                    self.cancel_recording()
                else:
                    audio_file = self.finish_recording()
                    # 异步处理识别
                    asyncio.run_coroutine_threadsafe(
                        self.process_recognition(audio_file),
                        cosmic.loop
                    )

                    # 智能恢复按键状态
                    if ClientConfig.restore_key:
                        self.smart_restore_key()

    def keyboard_event_handler(self, e):
        """键盘事件处理器"""
        if not self.shortcut_correct(e):
            return

        if ClientConfig.hold_mode:
            self.hold_mode_handler(e)
        else:
            self.click_mode_handler(e)

    async def process_recognition(self, audio_file):
        """处理语音识别（由服务端完成，此处仅占位）"""
        # 这里将通过WebSocket发送给服务端处理
        if cosmic.websocket:
            await cosmic.websocket.send_json({
                'type': 'recognize',
                'audio_file': audio_file
            })

    def start(self):
        """启动键盘监听"""
        suppress = ClientConfig.suppress or not ClientConfig.hold_mode
        keyboard.hook_key(
            ClientConfig.shortcut,
            self.keyboard_event_handler,
            suppress=suppress
        )
        print(f"键盘监听已启动，使用按键: {ClientConfig.shortcut}")
        print("长按模式" if ClientConfig.hold_mode else "单击模式")

    def stop(self):
        """停止键盘监听"""
        keyboard.unhook_all()
        self.pool.shutdown(wait=True)
        print("键盘监听已停止")


# 全局键盘处理器实例
keyboard_handler = KeyboardHandler()
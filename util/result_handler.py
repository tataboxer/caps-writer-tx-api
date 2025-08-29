import json
import time
import os
from pathlib import Path
from datetime import datetime
from config import ProjectPaths


class ResultHandler:
    """结果处理器，负责保存识别结果"""

    def __init__(self):
        # 确保结果目录存在
        ProjectPaths.results_dir.mkdir(parents=True, exist_ok=True)

    def save_result(self, audio_file, recognition_result):
        """保存识别结果"""
        timestamp = datetime.now()

        # 创建结果数据
        result_data = {
            'timestamp': timestamp.isoformat(),
            'audio_file': audio_file,
            'recognition_result': recognition_result,
            'date': timestamp.strftime('%Y-%m-%d'),
            'time': timestamp.strftime('%H:%M:%S')
        }

        # 保存JSON格式结果
        self.save_json_result(result_data)

        # 保存文本格式结果
        self.save_text_result(result_data)

        print(f"识别结果已保存: {recognition_result}")

    def save_json_result(self, result_data):
        """保存JSON格式结果"""
        date_str = result_data['date']
        date_dir = ProjectPaths.results_dir / date_str
        date_dir.mkdir(exist_ok=True)

        timestamp_short = result_data['time'].replace(':', '')
        json_file = date_dir / f"result_{timestamp_short}.json"

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

    def save_text_result(self, result_data):
        """保存文本格式结果"""
        date_str = result_data['date']
        date_dir = ProjectPaths.results_dir / date_str
        date_dir.mkdir(exist_ok=True)

        text_file = date_dir / f"results_{date_str}.txt"

        # 添加到文本文件（追加模式）
        time_str = result_data['time']
        result_text = result_data['recognition_result']

        with open(text_file, 'a', encoding='utf-8') as f:
            f.write(f"[{time_str}] {result_text}\n")

    def paste_to_clipboard(self, text):
        """将结果粘贴到剪贴板并模拟粘贴"""
        try:
            import pyperclip
            import keyboard
            import time
            from config import ClientConfig

            # 保存当前剪贴板内容（如果需要恢复）
            original_clipboard = None
            if ClientConfig.restore_clip:
                try:
                    original_clipboard = pyperclip.paste()
                except:
                    original_clipboard = None

            # 复制识别结果到剪贴板
            pyperclip.copy(text)

            # 模拟Ctrl+V粘贴
            keyboard.press_and_release('ctrl+v')

            print(f"已粘贴到剪贴板和当前界面: {text}")

            # 如果需要恢复剪贴板，延迟后恢复原内容
            if ClientConfig.restore_clip and original_clipboard is not None:
                def restore_clipboard():
                    try:
                        time.sleep(0.5)  # 等待粘贴完成
                        pyperclip.copy(original_clipboard)
                        print("剪贴板已恢复到原始内容")
                    except Exception as e:
                        print(f"恢复剪贴板失败: {str(e)}")

                # 在后台线程中恢复剪贴板，避免阻塞主程序
                import threading
                restore_thread = threading.Thread(target=restore_clipboard, daemon=True)
                restore_thread.start()

        except ImportError:
            print("警告: pyperclip未安装，无法自动粘贴")
        except Exception as e:
            print(f"自动粘贴失败: {str(e)}")

    def process_result(self, audio_file, recognition_result, auto_paste=True):
        """处理识别结果"""
        # 保存结果
        self.save_result(audio_file, recognition_result)

        # 自动粘贴
        if auto_paste:
            from config import ClientConfig
            if ClientConfig.paste:
                self.paste_to_clipboard(recognition_result)


# 全局结果处理器实例
result_handler = ResultHandler()


def save_recognition_result(audio_file, result, auto_paste=True):
    """便捷的保存结果函数"""
    result_handler.process_result(audio_file, result, auto_paste)
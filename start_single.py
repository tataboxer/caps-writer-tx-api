#!/usr/bin/env python3
"""
CapsWriter 单进程版本启动脚本
"""

import sys
import os
import tempfile
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        return False
    return True

def check_dependencies():
    """检查依赖"""
    try:
        import keyboard
        import pyaudio
        import websockets
        import requests
        import pyperclip
        import psutil
        return True
    except ImportError as e:
        print(f"缺少依赖包: {e}")
        print("请运行以下命令安装依赖：")
        print("pip install -r requirements.txt")
        return False

def check_config():
    """检查配置"""
    try:
        sys.path.append(str(Path(__file__).parent))
        from config import TencentASRConfig

        if not TencentASRConfig.secret_id or TencentASRConfig.secret_id == '你的腾讯云SecretId':
            print("错误：请在config.py中配置腾讯云SecretId")
            return False

        if not TencentASRConfig.secret_key or TencentASRConfig.secret_key == '你的腾讯云SecretKey':
            print("错误：请在config.py中配置腾讯云SecretKey")
            return False

        return True
    except Exception as e:
        print(f"配置检查失败: {e}")
        return False

def check_single_instance():
    """检查是否已有实例在运行"""
    import psutil

    lock_file = os.path.join(tempfile.gettempdir(), 'caps_writer.lock')

    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())

            # 检查进程是否还在运行
            if psutil.pid_exists(pid):
                print("CapsWriter 已在运行中")
                print("如需重新启动，请先关闭现有的实例")
                return False
            else:
                # 进程已死，删除锁文件
                os.remove(lock_file)
        except (ValueError, psutil.NoSuchProcess, ProcessLookupError):
            # 锁文件损坏或进程不存在，删除锁文件
            if os.path.exists(lock_file):
                os.remove(lock_file)

    # 创建新的锁文件
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"创建进程锁文件失败: {e}")
        return False

def main():
    """主函数"""
    print("=== CapsWriter 启动器 ===\n")

    # 检查Python版本
    if not check_python_version():
        return

    # 检查依赖
    if not check_dependencies():
        return

    # 检查配置
    if not check_config():
        return

    # 检查是否已有实例运行
    if not check_single_instance():
        return

    print("所有检查通过，开始启动CapsWriter...\n")

    # 启动单进程版本
    try:
        from caps_writer_single import main as single_main
        single_main()
    except KeyboardInterrupt:
        print("\nCapsWriter已关闭")
    except Exception as e:
        print(f"启动失败: {str(e)}")
    finally:
        # 清理锁文件
        lock_file = os.path.join(tempfile.gettempdir(), 'caps_writer.lock')
        if os.path.exists(lock_file):
            try:
                with open(lock_file, 'r') as f:
                    pid = int(f.read().strip())
                if pid == os.getpid():
                    os.remove(lock_file)
            except (ValueError, OSError):
                pass

if __name__ == "__main__":
    main()
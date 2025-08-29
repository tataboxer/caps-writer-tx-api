#!/usr/bin/env python3
"""
CapsWriter 单进程版本启动脚本
"""

import sys
import os
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

    print("✓ 所有检查通过，开始启动CapsWriter...\n")

    # 启动单进程版本
    try:
        from caps_writer_single import main as single_main
        single_main()
    except KeyboardInterrupt:
        print("\nCapsWriter已关闭")
    except Exception as e:
        print(f"启动失败: {str(e)}")

if __name__ == "__main__":
    main()
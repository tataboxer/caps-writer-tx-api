from collections.abc import Iterable
from pathlib import Path
import random
import os

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    # 加载.env文件
    dotenv_path = Path(__file__).parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        print("已加载 .env 配置文件")
    else:
        print("未找到 .env 文件，将使用默认配置")
except ImportError:
    print("python-dotenv 未安装，将使用默认配置")


# 腾讯ASR配置
class TencentASRConfig:
    """腾讯云ASR配置类"""
    
    secret_id = os.getenv('TENCENT_SECRET_ID', '')
    secret_key = os.getenv('TENCENT_SECRET_KEY', '')
    region = os.getenv('TENCENT_REGION', 'ap-shanghai')


# 创建全局配置实例
tencent_asr_config = TencentASRConfig()


# 火山引擎ASR配置
class VolcengineASRConfig:
    """火山引擎ASR配置类"""
    
    app_id = os.getenv('VOLCENGINE_APP_ID', '7262428661')
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY', '-KqMDs8LhnRInYaTAjMr8BOyY-RqUQnx')


# ASR服务选择配置
class ASRConfig:
    """ASR服务配置"""
    
    # ASR服务类型: 'volcengine' 或 'tencent'
    asr_service = os.getenv('ASR_SERVICE', 'volcengine')  # 默认使用火山引擎


# 创建全局配置实例
volcengine_asr_config = VolcengineASRConfig()
asr_config = ASRConfig()


# 客户端配置
class ClientConfig:

    shortcut     = 'caps lock'  # 控制录音的快捷键，默认是 CapsLock
    hold_mode    = True         # 长按模式，按下录音，松开停止，像对讲机一样用。
                                # 改为 False，则关闭长按模式，也就是单击模式
                                #       即：单击录音，再次单击停止
                                #       且：长按会执行原本的单击功能
    suppress     = False        # 是否阻塞按键事件（让其它程序收不到这个按键消息）
    restore_key  = True        # 录音完成，松开按键后，是否自动再按一遍，以恢复 CapsLock 或 Shift 等按键之前的状态
    threshold    = 0.5          # 按下快捷键后，触发语音识别的时间阈值
    paste        = True         # 是否以写入剪切板然后模拟 Ctrl-V 粘贴的方式输出结果
    restore_clip = True         # 模拟粘贴后是否恢复剪贴板

    save_audio = False           # 是否保存录音文件


# 项目路径配置
class ProjectPaths:
    base_dir = Path(__file__).parent
    recordings_dir = base_dir / 'recordings'
    results_dir = base_dir / 'results'
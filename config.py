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
        print("✅ 已加载 .env 配置文件")
    else:
        print("⚠️  未找到 .env 文件，将使用默认配置")
except ImportError:
    print("⚠️  python-dotenv 未安装，将使用默认配置")


# 腾讯ASR配置 - 从环境变量读取
class TencentASRConfig:
    """腾讯云ASR配置类，从环境变量读取，支持多组配置随机负载均衡"""

    def __init__(self):
        self._configs = []
        self._load_configs_from_env()

    def _load_configs_from_env(self):
        """从环境变量加载配置"""
        self._configs = []

        # 遍历所有配置组
        config_index = 1
        while True:
            secret_id_key = f'TENCENT_SECRET_ID_{config_index}'
            secret_key_key = f'TENCENT_SECRET_KEY_{config_index}'
            region_key = f'TENCENT_REGION_{config_index}'

            secret_id = os.getenv(secret_id_key)
            secret_key = os.getenv(secret_key_key)
            region = os.getenv(region_key, 'ap-shanghai')

            # 如果没有找到配置，停止遍历
            if not secret_id or not secret_key:
                break

            self._configs.append({
                'secret_id': secret_id,
                'secret_key': secret_key,
                'region': region,
                'bucket': None
            })

            config_index += 1

        # 如果没有环境变量配置，抛出错误
        if not self._configs:
            raise ValueError(
                "\n❌ 未找到腾讯云ASR配置！\n"
                "请按照以下步骤配置：\n"
                "1. 复制 .env.example 为 .env\n"
                "2. 编辑 .env 文件，填入你的腾讯云SecretId和SecretKey\n"
                "3. 重新运行程序\n\n"
                "示例配置：\n"
                "TENCENT_SECRET_ID_1=你的SecretId\n"
                "TENCENT_SECRET_KEY_1=你的SecretKey\n"
                "TENCENT_REGION_1=ap-guangzhou\n"
            )

    def get_random_config(self):
        """随机获取一组配置，实现负载均衡"""
        if not self._configs:
            raise ValueError("没有配置的腾讯云ASR凭证")

        return random.choice(self._configs)

    def get_config_count(self):
        """获取配置组数量"""
        return len(self._configs)

    # 向后兼容属性 - 如果只有一个配置，使用第一个
    @property
    def secret_id(self):
        return self._configs[0]['secret_id'] if self._configs else ''

    @property
    def secret_key(self):
        return self._configs[0]['secret_key'] if self._configs else ''

    @property
    def region(self):
        return self._configs[0]['region'] if self._configs else 'ap-shanghai'

    @property
    def bucket(self):
        return self._configs[0]['bucket'] if self._configs else None


# 创建全局配置实例
tencent_asr_config = TencentASRConfig()


# 客户端配置
class ClientConfig:

    shortcut     = 'caps lock'  # 控制录音的快捷键，默认是 CapsLock
    hold_mode    = True         # 长按模式，按下录音，松开停止，像对讲机一样用。
                                # 改为 False，则关闭长按模式，也就是单击模式
                                #       即：单击录音，再次单击停止
                                #       且：长按会执行原本的单击功能
    suppress     = False        # 是否阻塞按键事件（让其它程序收不到这个按键消息）
    restore_key  = True         # 录音完成，松开按键后，是否自动再按一遍，以恢复 CapsLock 或 Shift 等按键之前的状态
    threshold    = 0.3          # 按下快捷键后，触发语音识别的时间阈值
    paste        = True         # 是否以写入剪切板然后模拟 Ctrl-V 粘贴的方式输出结果
    restore_clip = True         # 模拟粘贴后是否恢复剪贴板

    save_audio = True           # 是否保存录音文件
    audio_name_len = 20         # 将录音识别结果的前多少个字存储到录音文件名中，建议不要超过200

    trash_punc = '，。,.'        # 识别结果要消除的末尾标点

    mic_seg_duration = 15       # 麦克风听写时分段长度：15秒
    mic_seg_overlap = 2         # 麦克风听写时分段重叠：2秒


# 项目路径配置
class ProjectPaths:
    base_dir = Path(__file__).parent
    recordings_dir = base_dir / 'recordings'
    results_dir = base_dir / 'results'
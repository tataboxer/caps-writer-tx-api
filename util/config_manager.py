"""
配置管理器 - 用于动态更新.env文件
"""

import os
import re
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.env_file = Path(__file__).parent.parent / '.env'
    
    def get_current_asr_service(self):
        """获取当前ASR服务"""
        return os.getenv('ASR_SERVICE', 'volcengine')
    
    def update_asr_service(self, service):
        """更新ASR服务配置"""
        if service not in ['volcengine', 'tencent']:
            raise ValueError(f"不支持的ASR服务: {service}")
        
        # 读取.env文件
        if not self.env_file.exists():
            return False
        
        with open(self.env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新ASR_SERVICE配置
        pattern = r'ASR_SERVICE=\w+'
        replacement = f'ASR_SERVICE={service}'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
        else:
            # 如果没找到配置行，添加到文件末尾
            new_content = content.rstrip() + f'\nASR_SERVICE={service}\n'
        
        # 写回文件
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # 更新环境变量
        os.environ['ASR_SERVICE'] = service
        
        return True


# 全局配置管理器实例
config_manager = ConfigManager()
# CapsWriter - 腾讯ASR语音输入工具

基于腾讯云ASR的PC端离线语音输入和字幕转录工具，支持CapsLock按键控制语音采集。

## 功能特性

- **CapsLock按键录音**：按下大写锁定键开始录音，松开键结束识别并输入结果
- **腾讯云ASR集成**：使用腾讯云ASR进行高质量语音识别
- **长按/单击模式**：支持长按模式（按下录音，松开停止）和单击模式
- **系统托盘图标**：运行时在系统托盘显示图标，支持右键菜单退出
- **音频文件保存**：自动保存录音文件到本地
- **结果本地记录**：将识别结果保存到本地文件
- **自动粘贴**：支持自动将识别结果粘贴到当前界面

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置腾讯云ASR

#### 方法一：环境变量配置（推荐）

1. **复制环境变量模板**：
   ```bash
   cp .env.example .env
   ```

2. **编辑 `.env` 文件**：
   ```env
   # 第一组配置
   TENCENT_SECRET_ID_1=你的腾讯云SecretId
   TENCENT_SECRET_KEY_1=你的腾讯云SecretKey
   TENCENT_REGION_1=ap-guangzhou

   # 第二组配置（可选，用于负载均衡）
   TENCENT_SECRET_ID_2=你的腾讯云SecretId_2
   TENCENT_SECRET_KEY_2=你的腾讯云SecretKey_2
   TENCENT_REGION_2=ap-shanghai
   ```

3. **安装依赖**：
   ```bash
   pip install python-dotenv
   ```

#### 方法二：直接配置环境变量

你也可以直接设置系统环境变量：

**Windows:**
```cmd
set TENCENT_SECRET_ID_1=你的SecretId
set TENCENT_SECRET_KEY_1=你的SecretKey
set TENCENT_REGION_1=ap-guangzhou
```

**Linux/Mac:**
```bash
export TENCENT_SECRET_ID_1=你的SecretId
export TENCENT_SECRET_KEY_1=你的SecretKey
export TENCENT_REGION_1=ap-guangzhou
```

## 🔒 安全说明

- `.env` 文件已添加到 `.gitignore`，不会被上传到Git
- 建议使用环境变量配置，避免敏感信息泄露
- 多组配置支持自动负载均衡，提高服务可用性

### 3. 运行程序

#### 方式一：单进程版本（推荐）

使用启动脚本（会自动检查依赖和配置）：

```bash
python start_single.py
```

或直接运行：

```bash
python caps_writer_single.py
```

或使用批处理文件：

```cmd
# 简单启动（推荐）
rcaps.bat


### 4. 开始使用

1. **启动程序**：运行上述任一命令启动CapsWriter
2. **录音控制**：
   - 长按模式（默认）：按下CapsLock开始录音，松开结束
   - 单击模式：单击CapsLock开始，再次单击结束
3. **查看结果**：
   - 录音文件保存在 `recordings/` 目录
   - 识别结果保存在 `results/` 目录
   - 结果会自动粘贴到当前光标位置

## 使用方法

1. **启动程序**：运行 `python start_single.py` 或 `python caps_writer_single.py`
2. **系统托盘**：程序启动后会在系统托盘显示图标，可以右键查看状态或退出
3. **录音控制**：
    - 长按模式（默认）：按下CapsLock开始录音，松开结束并识别
    - 单击模式：单击CapsLock开始录音，再次单击结束并识别
4. **退出程序**：
    - 按Ctrl+C终止程序
    - 或右键托盘图标选择"退出"
5. **查看结果**：
    - 识别结果会自动保存到 `results/` 目录
    - 录音文件保存在 `recordings/` 目录
    - 结果会自动粘贴到当前光标位置

## 配置说明

### 客户端配置 (ClientConfig)

- `shortcut`: 控制录音的快捷键（默认：'caps lock'）
- `hold_mode`: 是否启用长按模式（默认：True）
- `save_audio`: 是否保存录音文件（默认：True）
- `paste`: 是否自动粘贴结果（默认：True）


## 项目结构

```
CapsWriter/
├── config.py              # 配置文件
├── caps_writer_single.py # 单进程主程序
├── start_single.py       # 启动脚本
├── requirements.txt      # 依赖包列表
├── recordings/           # 录音文件目录
├── results/              # 识别结果目录
├── util/                 # 工具模块
│   ├── cosmic.py         # 全局状态管理
│   ├── keyboard_handler.py # 键盘监听
│   ├── audio_recorder.py # 音频录制
│   ├── tencent_asr.py    # 腾讯ASR集成
│   └── result_handler.py # 结果处理
└── README.md             # 说明文档
```

## 技术栈

- **Python 3.8+**: 主开发语言
- **腾讯云ASR**: 语音识别服务
- **PyAudio**: 音频录制
- **Keyboard**: 键盘监听
- **Pyperclip**: 剪贴板操作
- **Pystray**: 系统托盘图标
- **Pillow**: 图像处理

## 🚀 未来优化计划

### 🎯 预初始化音频流优化

**当前问题**：按键时初始化音频设备会导致约300-500ms延迟，可能丢失录音开头。

**优化方案**：
- 程序启动时预初始化音频流
- 使用环形缓冲区保存最近音频数据
- 按键时直接控制录音状态，无延迟

**预期效果**：
- ✅ 录音响应时间 < 50ms
- ✅ 完整捕获录音内容，无遗漏
- ✅ 更好的用户体验

**实现复杂度**：中等
**优先级**：高（影响用户体验）

### 🔧 其他可能的优化

- **文件名唯一性**：确保每次录音生成不同的文件名
- **批量识别**：支持多个音频文件批量处理
- **热词集成**：添加自定义词汇识别优化
- **实时流式识别**：支持边录音边识别

## 注意事项

1. **权限要求**：
   - Windows：需要管理员权限运行
   - Linux：需要相应音频设备权限

2. **网络要求**：
   - 需要网络连接访问腾讯云ASR服务

3. **音频设备**：
   - 确保系统有可用的麦克风设备

4. **腾讯云配置**：
   - 需要有效的腾讯云账号和ASR服务
   - 确保SecretId和SecretKey正确配置

## 常见问题

### Q: 无法连接到腾讯云ASR服务
A: 检查网络连接和腾讯云配置信息

### Q: 录音无响应
A: 检查麦克风权限和音频设备设置

### Q: 键盘监听无效
A: 尝试以管理员权限运行程序

## 许可证

本项目仅供学习和个人使用，请遵守腾讯云ASR服务的使用条款。
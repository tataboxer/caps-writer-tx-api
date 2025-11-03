"""
最终波形显示窗口
tkinter + 移植的demo算法 = 完美方案
"""

import tkinter as tk
import threading
import time
import math
import random


class WaveformWindow:
    """最终波形显示窗口"""
    
    def __init__(self, width=300, height=60, bottom_margin=120):
        self.width = width
        self.height = height
        self.bottom_margin = bottom_margin
        
        self.window = None
        self.canvas = None
        self.is_visible = False
        self.window_thread = None
        self.animation_running = False
        
        # 波形参数 - 来自demo
        self.scale = 2
        self.speed = 9
        self.phase_offset = 21.8
        self.fps = 60
        self.line_width = 2
        
        # 动画状态
        self._phase = 0
        self.power_level = 0
        self.target_power_level = 0  # 目标振幅
        self.smooth_factor = 0.15    # 平滑系数，越小越平滑
        
    def _create_window(self):
        """创建tkinter窗口"""
        try:
            self.window = tk.Tk()
            
            # 窗口配置
            self.window.title("")
            self.window.geometry(f"{self.width}x{self.height}")
            self.window.overrideredirect(True)
            self.window.attributes('-topmost', True)
            self.window.attributes('-alpha', 0.7)  # 70%透明度
            
            # 深色背景
            bg_color = '#1a1a1a'
            self.window.configure(bg=bg_color)
            
            # 居中定位
            self._center_window()
            
            # 创建画布
            self.canvas = tk.Canvas(
                self.window,
                width=self.width,
                height=self.height,
                bg=bg_color,
                highlightthickness=0,
                bd=0
            )
            self.canvas.pack()
            
            # 开始动画
            self.animation_running = True
            self._animate()
            
            # 启动事件循环
            self.window.mainloop()
            
        except Exception as e:
            print(f"[调试] 波形窗口创建失败: {e}")
        finally:
            # 确保清理资源
            self._cleanup_references()
            self.is_visible = False
            self.animation_running = False
    
    def _center_window(self):
        """窗口居中定位"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = (screen_width - self.width) // 2
        y = screen_height - self.height - self.bottom_margin
        
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")
    
    def _animate(self):
        """动画循环"""
        if not self.animation_running or not self.canvas:
            return
        
        # 平滑插值到目标振幅
        self.power_level += (self.target_power_level - self.power_level) * self.smooth_factor
        self.power_level = max(0, min(100, self.power_level))
        
        # 绘制波形
        self._draw_waveform()
        
        # 调度下一帧
        if self.window:
            self.window.after(16, self._animate)  # ~60 FPS
    
    def _draw_waveform(self):
        """绘制波形 - 移植demo算法"""
        if not self.canvas:
            return
        
        # 清除画布
        self.canvas.delete("all")
        
        # 计算参数 - 来自demo
        speed_x = self.speed / self.fps
        self._phase -= speed_x
        phase2 = self._phase + speed_x * self.phase_offset
        amplitude = self.power_level / 100
        
        # 增强振幅效果
        enhanced_amplitude = min(1.0, amplitude * 2.5)  # 放大2.5倍
        
        # 生成两条波形路径 - 来自demo算法
        path1 = self._gen_path(2.0, enhanced_amplitude, self._phase)
        path2 = self._gen_path(1.8, enhanced_amplitude, phase2)
        
        # 绘制背景填充
        self._draw_background_fill(path1, path2)
        
        # 绘制波形线条
        self._draw_wave_line(path2, '#4a9eff', 1)  # 蓝色波形
        self._draw_wave_line(path1, '#00d4ff', 2)  # 青色主波形
    
    def _gen_path(self, frequency, amplitude, phase):
        """生成波形路径 - 优化振幅"""
        path = []
        max_amplitude = self.height / 2
        
        for x in range(0, self.width + 1, 2):
            # 缩放因子 - demo算法
            scaling = (1 + math.cos(math.pi + (x / self.width) * 2 * math.pi)) / 2
            
            # 增强基础振幅，确保有最小波动
            base_amplitude = max(0.15, amplitude)  # 最小15%振幅
            
            # 波形计算 - demo算法
            y = scaling * max_amplitude * base_amplitude * math.sin(
                2 * math.pi * (x / self.width) * frequency + phase
            ) + max_amplitude
            
            path.append((x, y))
        
        return path
    
    def _draw_background_fill(self, path1, path2):
        """绘制背景填充"""
        if len(path1) < 2 or len(path2) < 2:
            return
        
        # 创建填充路径
        fill_points = []
        for x, y in path1:
            fill_points.extend([x, y])
        for x, y in reversed(path2):
            fill_points.extend([x, y])
        
        if len(fill_points) >= 6:
            self.canvas.create_polygon(
                fill_points,
                fill='#2a4a6b',
                outline='',
                stipple='gray25'
            )
    
    def _draw_wave_line(self, path, color, width):
        """绘制波形线条"""
        if len(path) < 2:
            return
        
        # 绘制平滑曲线
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=width,
                smooth=True,
                capstyle='round'
            )
    
    def show(self):
        """显示波形窗口"""
        if self.is_visible:
            return
        
        # 确保之前的窗口已经完全清理
        if self.window:
            self.hide()
            time.sleep(0.1)  # 等待清理完成
            
        self.is_visible = True
        self.window_thread = threading.Thread(target=self._create_window, daemon=True)
        self.window_thread.start()
        
        print("🎵 半透明波形窗口已显示")
    
    def hide(self):
        """隐藏波形窗口"""
        if not self.is_visible:
            return
            
        self.is_visible = False
        self.animation_running = False
        
        # 在主线程中安全关闭窗口
        if self.window:
            try:
                # 使用after在主线程中执行关闭操作
                self.window.after(0, self._safe_destroy)
            except:
                # 如果窗口已经被销毁，直接清理
                self._cleanup_references()
        
        print("🔇 半透明波形窗口已隐藏")
    
    def _safe_destroy(self):
        """安全销毁窗口"""
        try:
            if self.window:
                self.window.quit()
                self.window.destroy()
        except:
            pass
        finally:
            self._cleanup_references()
    
    def _cleanup_references(self):
        """清理引用"""
        self.window = None
        self.canvas = None
    
    def is_showing(self):
        """检查窗口是否显示"""
        return self.is_visible and self.window is not None


# 全局实例
waveform_window = WaveformWindow()


def update_waveform_level(level):
    """更新波形电平（平滑过渡）"""
    try:
        if waveform_window.is_visible:
            waveform_window.target_power_level = level
    except:
        pass


def show_waveform():
    """显示波形窗口"""
    try:
        waveform_window.show()
    except Exception as e:
        print(f"[调试] 显示波形失败: {e}")


def hide_waveform():
    """隐藏波形窗口"""
    try:
        waveform_window.hide()
    except Exception as e:
        print(f"[调试] 隐藏波形失败: {e}")


def is_waveform_showing():
    """检查波形窗口是否显示"""
    try:
        return waveform_window.is_showing()
    except:
        return False
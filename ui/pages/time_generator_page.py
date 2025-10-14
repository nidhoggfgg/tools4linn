"""
时间生成器页面
提供时间点生成的用户界面
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog

from ui.controllers.time_generator_controller import TimeGeneratorController


class TimeGeneratorPage(ctk.CTkFrame):
    """时间生成器页面"""

    def __init__(self, parent):
        super().__init__(parent)
        self.controller = TimeGeneratorController()
        self.current_format = "%Y-%m-%d %H:%M:%S"  # 默认格式
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        title_label = ctk.CTkLabel(
            self, text="时间点生成器", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # 创建主容器
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # 左侧输入区域
        input_frame = ctk.CTkFrame(main_container)
        input_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        # 右侧结果区域
        result_frame = ctk.CTkFrame(main_container)
        result_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        self.setup_input_area(input_frame)
        self.setup_result_area(result_frame)

    def setup_input_area(self, parent):
        """设置输入区域"""
        # 输入区域标题
        input_title = ctk.CTkLabel(
            parent, text="参数设置", font=ctk.CTkFont(size=18, weight="bold")
        )
        input_title.pack(pady=(10, 20))

        # 时间范围设置
        time_frame = ctk.CTkFrame(parent)
        time_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(time_frame, text="时间范围", font=ctk.CTkFont(weight="bold")).pack(
            pady=(10, 5)
        )

        # 开始时间
        start_frame = ctk.CTkFrame(time_frame)
        start_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(start_frame, text="开始时间:").pack(side="left", padx=5)
        self.start_time_entry = ctk.CTkEntry(
            start_frame, placeholder_text="YYYY-MM-DD HH:MM:SS", width=200
        )
        self.start_time_entry.pack(side="right", padx=5)

        # 结束时间
        end_frame = ctk.CTkFrame(time_frame)
        end_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(end_frame, text="结束时间:").pack(side="left", padx=5)
        self.end_time_entry = ctk.CTkEntry(
            end_frame, placeholder_text="YYYY-MM-DD HH:MM:SS", width=200
        )
        self.end_time_entry.pack(side="right", padx=5)

        # 快速设置按钮
        quick_frame = ctk.CTkFrame(time_frame)
        quick_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(
            quick_frame, text="设置为今天", command=self.set_today_range, width=100
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            quick_frame, text="设置为本周", command=self.set_week_range, width=100
        ).pack(side="left", padx=5)

        # 生成模式设置
        mode_frame = ctk.CTkFrame(parent)
        mode_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(mode_frame, text="生成模式", font=ctk.CTkFont(weight="bold")).pack(
            pady=(10, 5)
        )

        self.mode_var = ctk.StringVar(value="fixed_step")
        ctk.CTkRadioButton(
            mode_frame, text="固定步长", variable=self.mode_var, value="fixed_step"
        ).pack(pady=5)
        ctk.CTkRadioButton(
            mode_frame, text="随机步长", variable=self.mode_var, value="random_step"
        ).pack(pady=5)

        # 时间点数量设置
        count_frame = ctk.CTkFrame(parent)
        count_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            count_frame, text="时间点数量", font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))

        count_input_frame = ctk.CTkFrame(count_frame)
        count_input_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(count_input_frame, text="数量:").pack(side="left", padx=5)
        self.count_entry = ctk.CTkEntry(
            count_input_frame, placeholder_text="10", width=100
        )
        self.count_entry.pack(side="right", padx=5)
        self.count_entry.insert(0, "10")

        # 随机步长设置（仅随机模式时显示）
        self.step_frame = ctk.CTkFrame(parent)
        self.step_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            self.step_frame, text="步长范围（秒）", font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))

        min_step_frame = ctk.CTkFrame(self.step_frame)
        min_step_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(min_step_frame, text="最小步长:").pack(side="left", padx=5)
        self.min_step_entry = ctk.CTkEntry(
            min_step_frame, placeholder_text="60", width=100
        )
        self.min_step_entry.pack(side="right", padx=5)
        self.min_step_entry.insert(0, "60")

        max_step_frame = ctk.CTkFrame(self.step_frame)
        max_step_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(max_step_frame, text="最大步长:").pack(side="left", padx=5)
        self.max_step_entry = ctk.CTkEntry(
            max_step_frame, placeholder_text="3600", width=100
        )
        self.max_step_entry.pack(side="right", padx=5)
        self.max_step_entry.insert(0, "3600")

        # 绑定模式变化事件
        self.mode_var.trace_add("write", self.on_mode_change)
        self.on_mode_change()  # 初始化显示状态

        # 生成按钮
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkButton(
            button_frame,
            text="生成时间点",
            command=self.generate_time_points,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=10)

    def setup_result_area(self, parent):
        """设置结果区域"""
        # 结果区域标题
        result_title = ctk.CTkLabel(
            parent, text="生成结果", font=ctk.CTkFont(size=18, weight="bold")
        )
        result_title.pack(pady=(10, 10))

        # 结果信息显示
        self.info_text = ctk.CTkTextbox(parent, height=100)
        self.info_text.pack(fill="x", padx=10, pady=5)

        # 时间点列表
        list_label = ctk.CTkLabel(
            parent, text="时间点列表", font=ctk.CTkFont(weight="bold")
        )
        list_label.pack(pady=(10, 5))

        # 创建滚动文本框显示结果
        self.result_text = ctk.CTkTextbox(parent)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=5)

        # 时间格式选择区域
        format_frame = ctk.CTkFrame(parent)
        format_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            format_frame, text="输出格式", font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))

        # 格式按钮容器
        format_buttons_frame = ctk.CTkFrame(format_frame)
        format_buttons_frame.pack(fill="x", padx=10, pady=5)

        # 第一行格式按钮
        format_row1 = ctk.CTkFrame(format_buttons_frame)
        format_row1.pack(fill="x", pady=2)

        ctk.CTkButton(
            format_row1,
            text="标准格式\nYYYY-MM-DD HH:MM:SS",
            command=lambda: self.change_format("%Y-%m-%d %H:%M:%S"),
            width=120,
            height=40,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            format_row1,
            text="日期格式\nYYYY-MM-DD",
            command=lambda: self.change_format("%Y-%m-%d"),
            width=120,
            height=40,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            format_row1,
            text="时间格式\nHH:MM:SS",
            command=lambda: self.change_format("%H:%M:%S"),
            width=120,
            height=40,
        ).pack(side="left", padx=2)

        # 第二行格式按钮
        format_row2 = ctk.CTkFrame(format_buttons_frame)
        format_row2.pack(fill="x", pady=2)

        ctk.CTkButton(
            format_row2,
            text="中文格式\nYYYY年MM月DD日 HH:MM",
            command=lambda: self.change_format("%Y年%m月%d日 %H:%M"),
            width=120,
            height=40,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            format_row2,
            text="ISO格式\nYYYY-MM-DDTHH:MM:SS",
            command=lambda: self.change_format("%Y-%m-%dT%H:%M:%S"),
            width=120,
            height=40,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            format_row2,
            text="时间戳\nUnix Timestamp",
            command=lambda: self.change_format("timestamp"),
            width=120,
            height=40,
        ).pack(side="left", padx=2)

        # 自定义格式输入
        custom_format_frame = ctk.CTkFrame(format_buttons_frame)
        custom_format_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(custom_format_frame, text="自定义格式:").pack(side="left", padx=5)
        self.custom_format_entry = ctk.CTkEntry(
            custom_format_frame, placeholder_text="例如: %Y/%m/%d %H:%M", width=200
        )
        self.custom_format_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            custom_format_frame, text="应用", command=self.apply_custom_format, width=60
        ).pack(side="left", padx=5)

        # 操作按钮
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame, text="复制结果", command=self.copy_results, width=100
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            button_frame, text="导出文件", command=self.export_results, width=100
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            button_frame, text="清空结果", command=self.clear_results, width=100
        ).pack(side="right", padx=5)

    def on_mode_change(self, *args):
        """模式变化时的处理"""
        if self.mode_var.get() == "random_step":
            self.step_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.step_frame.pack_forget()

    def set_today_range(self):
        """设置今天的时间范围"""
        now = datetime.now()
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=0)

        self.start_time_entry.delete(0, "end")
        self.start_time_entry.insert(0, start_time.strftime("%Y-%m-%d %H:%M:%S"))
        self.end_time_entry.delete(0, "end")
        self.end_time_entry.insert(0, end_time.strftime("%Y-%m-%d %H:%M:%S"))

    def set_week_range(self):
        """设置本周的时间范围"""
        now = datetime.now()
        # 获取本周一
        days_since_monday = now.weekday()
        monday = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
            days=days_since_monday
        )
        # 获取本周日
        sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)

        self.start_time_entry.delete(0, "end")
        self.start_time_entry.insert(0, monday.strftime("%Y-%m-%d %H:%M:%S"))
        self.end_time_entry.delete(0, "end")
        self.end_time_entry.insert(0, sunday.strftime("%Y-%m-%d %H:%M:%S"))

    def generate_time_points(self):
        """生成时间点"""
        try:
            # 获取输入参数
            start_time = self.start_time_entry.get().strip()
            end_time = self.end_time_entry.get().strip()
            mode = self.mode_var.get()
            count = int(self.count_entry.get().strip())

            if not start_time or not end_time:
                messagebox.showerror("错误", "请输入开始时间和结束时间")
                return

            # 设置控制器参数
            if not self.controller.set_time_range(start_time, end_time):
                messagebox.showerror(
                    "错误", "时间格式不正确，请使用 YYYY-MM-DD HH:MM:SS 格式"
                )
                return

            self.controller.set_mode(mode)

            if not self.controller.set_point_count(count):
                messagebox.showerror("错误", "时间点数量必须大于0")
                return

            # 如果是随机模式，设置步长范围
            if mode == "random_step":
                min_step = int(self.min_step_entry.get().strip())
                max_step = int(self.max_step_entry.get().strip())
                if not self.controller.set_step_range(min_step, max_step):
                    messagebox.showerror("错误", "步长范围设置不正确")
                    return

            # 生成时间点
            if self.controller.generate_time_points():
                self.display_results()
            else:
                messagebox.showerror("错误", "生成时间点失败")

        except ValueError as e:
            messagebox.showerror("错误", f"参数错误: {e}")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败: {e}")

    def change_format(self, format_str):
        """切换时间格式"""
        self.current_format = format_str
        if self.controller.result_time_points:
            self.display_results()

    def apply_custom_format(self):
        """应用自定义格式"""
        custom_format = self.custom_format_entry.get().strip()
        if custom_format:
            self.change_format(custom_format)
        else:
            messagebox.showwarning("警告", "请输入自定义格式")

    def display_results(self):
        """显示生成结果"""
        # 显示时间范围信息
        info = self.controller.get_duration_info()
        info_text = f"""时间范围: {info.get('start_time', 'N/A')} 到 {info.get('end_time', 'N/A')}
总时长: {info.get('total_duration_seconds', 0):.0f} 秒 ({info.get('total_duration_hours', 0):.2f} 小时)
生成模式: {info.get('mode', 'N/A')}
时间点数量: {info.get('point_count', 0)}
当前格式: {self.current_format}"""

        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info_text)

        # 显示时间点列表
        formatted_results = self.controller.get_formatted_results(self.current_format)
        result_text = "\n".join(formatted_results)

        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", result_text)

    def copy_results(self):
        """复制结果到剪贴板"""
        if not self.controller.result_time_points:
            messagebox.showwarning("警告", "没有可复制的结果")
            return

        result_text = self.controller.export_to_text(self.current_format)
        self.clipboard_clear()
        self.clipboard_append(result_text)
        messagebox.showinfo("成功", "结果已复制到剪贴板")

    def export_results(self):
        """导出结果到文件"""
        if not self.controller.result_time_points:
            messagebox.showwarning("警告", "没有可导出的结果")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )

        if file_path:
            try:
                result_text = self.controller.export_to_text(self.current_format)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result_text)
                messagebox.showinfo("成功", f"结果已导出到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {e}")

    def clear_results(self):
        """清空结果"""
        self.info_text.delete("1.0", "end")
        self.result_text.delete("1.0", "end")
        self.controller.result_time_points = []

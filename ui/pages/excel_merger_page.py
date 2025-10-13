"""
Excel 合并功能页面
提供用户友好的界面来使用 Excel 合并功能
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging

# 导入控制器
from ui.controllers.excel_merger_controller import ExcelMergerController


class ExcelMergerPage(ctk.CTkFrame):
    """Excel 合并功能页面"""

    def __init__(self, parent):
        super().__init__(parent)

        # 设置日志
        self.logger = self._setup_logger()

        # 状态变量
        self.input_dir = ctk.StringVar()
        self.output_file = ctk.StringVar()
        self.naming_strategy = ctk.StringVar(value="文件名")

        # 创建控制器
        self.controller = ExcelMergerController(self, self.logger)
        self.controller.set_callbacks(
            progress_callback=self._on_progress_update,
            log_callback=self._on_log_message,
            complete_callback=self._on_merge_complete,
        )

        # 创建界面
        self._create_ui()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("excel_merger")
        logger.setLevel(logging.INFO)

        # 创建处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _create_ui(self):
        """创建用户界面"""
        # 创建滚动区域
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 创建各个区域
        self._create_header()
        self._create_input_section()
        self._create_output_section()
        self._create_options_section()
        self._create_control_section()
        self._create_progress_section()
        self._create_log_section()

    def _create_header(self):
        """创建页面标题"""
        header_frame = ctk.CTkFrame(self.scrollable_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Excel 文件合并工具",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.pack(pady=20)

        desc_label = ctk.CTkLabel(
            header_frame,
            text="将多个 Excel 文件合并为一个文件，支持自定义命名策略和文件过滤",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),
        )
        desc_label.pack(pady=(0, 20))

    def _create_input_section(self):
        """创建输入区域"""
        input_frame = ctk.CTkFrame(self.scrollable_frame)
        input_frame.pack(fill="x", pady=(0, 20))

        # 标题
        input_title = ctk.CTkLabel(
            input_frame, text="输入设置", font=ctk.CTkFont(size=18, weight="bold")
        )
        input_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 输入目录选择
        dir_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        dir_frame.pack(fill="x", padx=20, pady=(0, 15))

        dir_label = ctk.CTkLabel(
            dir_frame, text="选择包含 Excel 文件的目录:", font=ctk.CTkFont(size=14)
        )
        dir_label.pack(anchor="w", pady=(0, 5))

        dir_entry_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_entry_frame.pack(fill="x")

        self.dir_entry = ctk.CTkEntry(
            dir_entry_frame,
            textvariable=self.input_dir,
            placeholder_text="请选择包含 Excel 文件的目录...",
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.dir_button = ctk.CTkButton(
            dir_entry_frame,
            text="浏览",
            command=self._select_input_directory,
            width=80,
            height=35,
        )
        self.dir_button.pack(side="right")

    def _create_output_section(self):
        """创建输出区域"""
        output_frame = ctk.CTkFrame(self.scrollable_frame)
        output_frame.pack(fill="x", pady=(0, 20))

        # 标题
        output_title = ctk.CTkLabel(
            output_frame, text="输出设置", font=ctk.CTkFont(size=18, weight="bold")
        )
        output_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 输出文件选择
        file_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=20, pady=(0, 15))

        file_label = ctk.CTkLabel(
            file_frame, text="选择输出文件位置:", font=ctk.CTkFont(size=14)
        )
        file_label.pack(anchor="w", pady=(0, 5))

        file_entry_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_entry_frame.pack(fill="x")

        self.file_entry = ctk.CTkEntry(
            file_entry_frame,
            textvariable=self.output_file,
            placeholder_text="请选择输出文件位置...",
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.file_button = ctk.CTkButton(
            file_entry_frame,
            text="保存为",
            command=self._select_output_file,
            width=80,
            height=35,
        )
        self.file_button.pack(side="right")

    def _create_options_section(self):
        """创建选项区域"""
        options_frame = ctk.CTkFrame(self.scrollable_frame)
        options_frame.pack(fill="x", pady=(0, 20))

        # 标题
        options_title = ctk.CTkLabel(
            options_frame, text="合并选项", font=ctk.CTkFont(size=18, weight="bold")
        )
        options_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 命名策略选择
        naming_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        naming_frame.pack(fill="x", padx=20, pady=(0, 15))

        naming_label = ctk.CTkLabel(
            naming_frame, text="工作表命名策略:", font=ctk.CTkFont(size=14)
        )
        naming_label.pack(anchor="w", pady=(0, 5))

        self.naming_menu = ctk.CTkOptionMenu(
            naming_frame,
            values=["文件名", "目录名", "索引编号", "路径段", "第一层目录名"],
            variable=self.naming_strategy,
            width=200,
            height=35,
        )
        self.naming_menu.pack(anchor="w")

        # 文件过滤选项（可展开）
        filter_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 15))

        # 过滤选项开关
        self.filter_enabled = ctk.BooleanVar()
        self.filter_checkbox = ctk.CTkCheckBox(
            filter_frame,
            text="启用文件过滤",
            variable=self.filter_enabled,
            command=self._toggle_filter_options,
        )
        self.filter_checkbox.pack(anchor="w", pady=(0, 10))

        # 过滤选项区域（默认隐藏）
        self.filter_options_frame = ctk.CTkFrame(filter_frame)
        self.filter_options_frame.pack(fill="x", pady=(0, 10))

        # 文件名过滤模式选择
        mode_frame = ctk.CTkFrame(self.filter_options_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=5)

        mode_label = ctk.CTkLabel(
            mode_frame, text="文件名过滤模式:", font=ctk.CTkFont(size=12)
        )
        mode_label.pack(anchor="w", pady=(0, 5))

        self.filter_mode = ctk.StringVar(value="包含模式")
        self.filter_mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=["包含模式", "正则模式", "扩展名模式", "大小模式", "目录模式"],
            variable=self.filter_mode,
            width=150,
            height=30,
            command=self._on_filter_mode_change,
        )
        self.filter_mode_menu.pack(anchor="w")

        # 文件名模式过滤
        pattern_frame = ctk.CTkFrame(self.filter_options_frame, fg_color="transparent")
        pattern_frame.pack(fill="x", padx=10, pady=5)

        self.pattern_label = ctk.CTkLabel(
            pattern_frame, text="文件名包含:", font=ctk.CTkFont(size=12)
        )
        self.pattern_label.pack(anchor="w", pady=(0, 5))

        self.pattern_entry = ctk.CTkEntry(
            pattern_frame, placeholder_text="例如: data", height=30
        )
        self.pattern_entry.pack(fill="x")

        # 默认隐藏过滤选项
        self.filter_options_frame.pack_forget()

    def _create_control_section(self):
        """创建控制区域"""
        control_frame = ctk.CTkFrame(self.scrollable_frame)
        control_frame.pack(fill="x", pady=(0, 20))

        # 按钮区域
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        # 开始合并按钮
        self.merge_button = ctk.CTkButton(
            button_frame,
            text="开始合并",
            command=self._start_merge,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            width=150,
            fg_color=("blue", "blue"),
            hover_color=("darkblue", "darkblue"),
        )
        self.merge_button.pack(side="left", padx=(0, 10))

        # 清空日志按钮
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="清空日志",
            command=self._clear_log,
            font=ctk.CTkFont(size=14),
            height=35,
            width=100,
        )
        self.clear_button.pack(side="left")

    def _create_progress_section(self):
        """创建进度区域"""
        progress_frame = ctk.CTkFrame(self.scrollable_frame)
        progress_frame.pack(fill="x", pady=(0, 20))

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=20)
        self.progress_bar.set(0)

        # 进度标签
        self.progress_label = ctk.CTkLabel(
            progress_frame, text="准备就绪", font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=(0, 20))

    def _create_log_section(self):
        """创建日志区域"""
        log_frame = ctk.CTkFrame(self.scrollable_frame)
        log_frame.pack(fill="both", expand=True, pady=(0, 20))

        # 日志标题
        log_title = ctk.CTkLabel(
            log_frame, text="操作日志", font=ctk.CTkFont(size=16, weight="bold")
        )
        log_title.pack(pady=(15, 10), anchor="w", padx=20)

        # 日志文本框
        self.log_text = ctk.CTkTextbox(
            log_frame, height=200, font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _select_input_directory(self):
        """选择输入目录"""
        directory = filedialog.askdirectory(title="选择包含 Excel 文件的目录")
        if directory:
            self.input_dir.set(directory)
            self._log_message(f"已选择输入目录: {directory}")

    def _select_output_file(self):
        """选择输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件位置",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")],
        )
        if file_path:
            self.output_file.set(file_path)
            self._log_message(f"已选择输出文件: {file_path}")

    def _toggle_filter_options(self):
        """切换过滤选项显示"""
        if self.filter_enabled.get():
            self.filter_options_frame.pack(fill="x", pady=(0, 10))
        else:
            self.filter_options_frame.pack_forget()

    def _on_filter_mode_change(self, selected_mode):
        """文件名过滤模式改变时的回调"""
        # 更新标签和输入框的提示文本
        if selected_mode == "包含模式":
            self.pattern_label.configure(text="文件名包含:")
            self.pattern_entry.configure(placeholder_text="例如: data")
        elif selected_mode == "正则模式":
            self.pattern_label.configure(text="正则表达式:")
            self.pattern_entry.configure(placeholder_text="例如: .*_data.*")
        elif selected_mode == "扩展名模式":
            self.pattern_label.configure(text="文件扩展名:")
            self.pattern_entry.configure(placeholder_text="例如: xlsx,xls")
        elif selected_mode == "大小模式":
            self.pattern_label.configure(text="文件大小限制 (MB):")
            self.pattern_entry.configure(placeholder_text="例如: 1-10")
        elif selected_mode == "目录模式":
            self.pattern_label.configure(text="目录路径包含:")
            self.pattern_entry.configure(placeholder_text="例如: /data/")

    def _start_merge(self):
        """开始合并操作"""
        if self.controller.get_processing_status():
            return

        # 获取过滤选项
        filter_enabled = self.filter_enabled.get()
        filter_mode = self.filter_mode.get()
        pattern = self.pattern_entry.get().strip()

        # 更新UI状态
        self.merge_button.configure(text="处理中...", state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="开始处理...")

        # 开始合并
        self.controller.start_merge(
            input_dir=self.input_dir.get(),
            output_file=self.output_file.get(),
            naming_strategy=self.naming_strategy.get(),
            filter_enabled=filter_enabled,
            filter_mode=filter_mode,
            pattern=pattern,
        )

    def _on_progress_update(self, progress: float, message: str):
        """进度更新回调"""
        self.progress_bar.set(progress)
        self.progress_label.configure(text=message)

    def _on_log_message(self, message: str):
        """日志消息回调"""
        self._log_message(message)

    def _on_merge_complete(self, success: bool, message: str):
        """合并完成回调"""
        self.merge_button.configure(text="开始合并", state="normal")

        if success:
            self.progress_label.configure(text="处理完成")
            messagebox.showinfo("成功", message)
        else:
            self.progress_label.configure(text="处理失败")
            messagebox.showerror("错误", message)

    def _log_message(self, message: str):
        """添加日志消息"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")

    def _clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", "end")

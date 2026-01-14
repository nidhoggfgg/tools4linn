"""
文件提取功能页面
提供用户友好的界面来使用文件提取功能
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging

# 导入控制器
from ui.controllers.file_extractor_controller import FileExtractorController


class FileExtractorPage(ctk.CTkFrame):
    """文件提取功能页面"""

    def __init__(self, parent):
        super().__init__(parent)

        # 设置日志
        self.logger = self._setup_logger()

        # 状态变量
        self.input_dir = ctk.StringVar()
        self.output_dir = ctk.StringVar()
        self.organize_mode = ctk.StringVar(value="按第一层目录分组")
        self.naming_mode = ctk.StringVar(value="保持原文件名")
        self.custom_prefix = ctk.StringVar()
        self.custom_suffix = ctk.StringVar()

        # 创建控制器
        self.controller = FileExtractorController(self.logger)
        self.controller.set_callbacks(
            progress_callback=self._on_progress_update,
            log_callback=self._on_log_message,
            complete_callback=self._on_extraction_complete,
        )

        # 创建界面
        self._create_ui()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("file_extractor")
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
        self._create_naming_section()
        self._create_control_section()
        self._create_progress_section()
        self._create_log_section()

    def _create_header(self):
        """创建页面标题"""
        header_frame = ctk.CTkFrame(self.scrollable_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📂 文件提取工具",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.pack(pady=20)

        desc_label = ctk.CTkLabel(
            header_frame,
            text="从多层目录中提取符合条件的文件到指定目录，支持自定义文件过滤",
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
            dir_frame, text="选择要搜索的源目录:", font=ctk.CTkFont(size=14)
        )
        dir_label.pack(anchor="w", pady=(0, 5))

        dir_entry_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_entry_frame.pack(fill="x")

        self.dir_entry = ctk.CTkEntry(
            dir_entry_frame,
            textvariable=self.input_dir,
            placeholder_text="请选择要搜索的源目录...",
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

        # 输出目录选择
        dir_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        dir_frame.pack(fill="x", padx=20, pady=(0, 15))

        dir_label = ctk.CTkLabel(
            dir_frame, text="选择提取文件的目标目录:", font=ctk.CTkFont(size=14)
        )
        dir_label.pack(anchor="w", pady=(0, 5))

        dir_entry_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_entry_frame.pack(fill="x")

        self.output_entry = ctk.CTkEntry(
            dir_entry_frame,
            textvariable=self.output_dir,
            placeholder_text="请选择提取文件的目标目录...",
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.output_button = ctk.CTkButton(
            dir_entry_frame,
            text="浏览",
            command=self._select_output_directory,
            width=80,
            height=35,
        )
        self.output_button.pack(side="right")

    def _create_options_section(self):
        """创建选项区域"""
        options_frame = ctk.CTkFrame(self.scrollable_frame)
        options_frame.pack(fill="x", pady=(0, 20))

        # 标题
        options_title = ctk.CTkLabel(
            options_frame, text="提取选项", font=ctk.CTkFont(size=18, weight="bold")
        )
        options_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 文件组织方式选择
        organize_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        organize_frame.pack(fill="x", padx=20, pady=(0, 15))

        organize_label = ctk.CTkLabel(
            organize_frame, text="文件组织方式:", font=ctk.CTkFont(size=14)
        )
        organize_label.pack(anchor="w", pady=(0, 5))

        organize_desc_label = ctk.CTkLabel(
            organize_frame,
            text="选择如何组织提取的文件",
            font=ctk.CTkFont(size=11),
            text_color=("gray10", "gray90"),
        )
        organize_desc_label.pack(anchor="w", pady=(0, 5))

        self.organize_menu = ctk.CTkOptionMenu(
            organize_frame,
            values=["扁平化", "按第一层目录分组"],
            variable=self.organize_mode,
            width=200,
            height=35,
        )
        self.organize_menu.pack(anchor="w")

        # 文件过滤选项
        filter_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 15))

        filter_title = ctk.CTkLabel(
            filter_frame, text="文件过滤（必选）:", font=ctk.CTkFont(size=14)
        )
        filter_title.pack(anchor="w", pady=(0, 5))

        filter_desc_label = ctk.CTkLabel(
            filter_frame,
            text="设置过滤条件以选择要提取的文件",
            font=ctk.CTkFont(size=11),
            text_color=("gray10", "gray90"),
        )
        filter_desc_label.pack(anchor="w", pady=(0, 10))

        # 文件名过滤模式选择
        mode_label = ctk.CTkLabel(
            filter_frame, text="文件过滤模式:", font=ctk.CTkFont(size=12)
        )
        mode_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.filter_mode = ctk.StringVar(value="扩展名模式")
        self.filter_mode_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["包含模式", "正则模式", "扩展名模式", "大小模式", "目录模式"],
            variable=self.filter_mode,
            width=150,
            height=30,
            command=self._on_filter_mode_change,
        )
        self.filter_mode_menu.pack(anchor="w", padx=20, pady=(0, 10))

        # 文件名模式过滤
        self.pattern_label = ctk.CTkLabel(
            filter_frame, text="文件扩展名:", font=ctk.CTkFont(size=12)
        )
        self.pattern_label.pack(anchor="w", padx=20, pady=(0, 5))

        self.pattern_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="例如: xlsx,xls,pdf", height=30
        )
        self.pattern_entry.pack(fill="x", padx=20, pady=(0, 10))

        # 覆盖选项
        overwrite_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        overwrite_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.overwrite_enabled = ctk.BooleanVar()
        overwrite_checkbox = ctk.CTkCheckBox(
            overwrite_frame,
            text="覆盖已存在的文件（默认跳过）",
            variable=self.overwrite_enabled,
        )
        overwrite_checkbox.pack(anchor="w")

    def _create_naming_section(self):
        """创建文件命名模式区域"""
        naming_frame = ctk.CTkFrame(self.scrollable_frame)
        naming_frame.pack(fill="x", pady=(0, 20))

        # 标题
        naming_title = ctk.CTkLabel(
            naming_frame, text="文件命名模式", font=ctk.CTkFont(size=18, weight="bold")
        )
        naming_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 命名模式选择
        mode_frame = ctk.CTkFrame(naming_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 15))

        mode_label = ctk.CTkLabel(
            mode_frame, text="选择命名模式:", font=ctk.CTkFont(size=14)
        )
        mode_label.pack(anchor="w", pady=(0, 5))

        mode_desc_label = ctk.CTkLabel(
            mode_frame,
            text="选择如何命名提取的文件",
            font=ctk.CTkFont(size=11),
            text_color=("gray10", "gray90"),
        )
        mode_desc_label.pack(anchor="w", pady=(0, 5))

        self.naming_mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=[
                "保持原文件名",
                "添加序号",
                "使用时间戳",
                "添加自定义前缀",
                "添加自定义后缀",
                "使用第一层目录名",
            ],
            variable=self.naming_mode,
            width=250,
            height=35,
            command=self._on_naming_mode_change,
        )
        self.naming_mode_menu.pack(anchor="w")

        # 自定义前缀输入框（初始隐藏）
        self.prefix_frame = ctk.CTkFrame(naming_frame, fg_color="transparent")
        self.prefix_label = ctk.CTkLabel(
            self.prefix_frame, text="自定义前缀:", font=ctk.CTkFont(size=12)
        )
        self.prefix_label.pack(anchor="w", pady=(0, 5))

        self.prefix_entry = ctk.CTkEntry(
            self.prefix_frame,
            textvariable=self.custom_prefix,
            placeholder_text="例如: prefix_",
            height=30,
        )
        self.prefix_entry.pack(fill="x", pady=(0, 10))

        # 自定义后缀输入框（初始隐藏）
        self.suffix_frame = ctk.CTkFrame(naming_frame, fg_color="transparent")
        self.suffix_label = ctk.CTkLabel(
            self.suffix_frame, text="自定义后缀:", font=ctk.CTkFont(size=12)
        )
        self.suffix_label.pack(anchor="w", pady=(0, 5))

        self.suffix_entry = ctk.CTkEntry(
            self.suffix_frame,
            textvariable=self.custom_suffix,
            placeholder_text="例如: _backup",
            height=30,
        )
        self.suffix_entry.pack(fill="x", pady=(0, 10))

        # 模式说明标签
        self.naming_desc_label = ctk.CTkLabel(
            naming_frame,
            text="保持原文件名：不修改文件名",
            font=ctk.CTkFont(size=11),
            text_color=("gray10", "gray90"),
        )
        self.naming_desc_label.pack(anchor="w", padx=20, pady=(0, 10))

    def _create_control_section(self):
        """创建控制区域"""
        control_frame = ctk.CTkFrame(self.scrollable_frame)
        control_frame.pack(fill="x", pady=(0, 20))

        # 按钮区域
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        # 开始提取按钮
        self.extract_button = ctk.CTkButton(
            button_frame,
            text="开始提取",
            command=self._start_extraction,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            width=150,
            fg_color=("green", "green"),
            hover_color=("darkgreen", "darkgreen"),
        )
        self.extract_button.pack(side="left", padx=(0, 10))

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
        directory = filedialog.askdirectory(title="选择要搜索的源目录")
        if directory:
            self.input_dir.set(directory)
            self._log_message(f"已选择输入目录: {directory}")

    def _select_output_directory(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择提取文件的目标目录")
        if directory:
            self.output_dir.set(directory)
            self._log_message(f"已选择输出目录: {directory}")

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
            self.pattern_entry.configure(placeholder_text="例如: xlsx,xls,pdf")
        elif selected_mode == "大小模式":
            self.pattern_label.configure(text="文件大小限制 (MB):")
            self.pattern_entry.configure(placeholder_text="例如: 1-10 (最小1MB, 最大10MB)")
        elif selected_mode == "目录模式":
            self.pattern_label.configure(text="目录路径包含:")
            self.pattern_entry.configure(placeholder_text="例如: /data/ 或 /Documents/")

    def _on_naming_mode_change(self, selected_mode):
        """命名模式改变时的回调"""
        # 隐藏所有输入框
        self.prefix_frame.pack_forget()
        self.suffix_frame.pack_forget()

        # 更新说明文本
        descriptions = {
            "保持原文件名": "保持原文件名：不修改文件名",
            "添加序号": "添加序号：自动在文件名后添加序号（如 file_1.pdf, file_2.pdf）",
            "使用时间戳": "使用时间戳：在文件名后添加当前时间戳（如 file_20250114_143020.pdf）",
            "添加自定义前缀": "添加自定义前缀：在文件名前添加自定义前缀",
            "添加自定义后缀": "添加自定义后缀：在扩展名前添加自定义后缀",
            "使用第一层目录名": "使用第一层目录名：直接使用源文件的第一层目录名作为文件名（保留原扩展名）",
        }
        self.naming_desc_label.configure(text=descriptions.get(selected_mode, ""))

        # 显示相应的输入框
        if selected_mode == "添加自定义前缀":
            self.prefix_frame.pack(fill="x", padx=20, pady=(0, 10), after=self.naming_mode_menu.master)
        elif selected_mode == "添加自定义后缀":
            self.suffix_frame.pack(fill="x", padx=20, pady=(0, 10), after=self.naming_mode_menu.master)

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
            self.pattern_entry.configure(placeholder_text="例如: xlsx,xls,pdf")
        elif selected_mode == "大小模式":
            self.pattern_label.configure(text="文件大小限制 (MB):")
            self.pattern_entry.configure(placeholder_text="例如: 1-10 (最小1MB, 最大10MB)")
        elif selected_mode == "目录模式":
            self.pattern_label.configure(text="目录路径包含:")
            self.pattern_entry.configure(placeholder_text="例如: /data/ 或 /Documents/")
            self.pattern_label.configure(text="文件名包含:")
            self.pattern_entry.configure(placeholder_text="例如: data")
        elif selected_mode == "正则模式":
            self.pattern_label.configure(text="正则表达式:")
            self.pattern_entry.configure(placeholder_text="例如: .*_data.*")
        elif selected_mode == "扩展名模式":
            self.pattern_label.configure(text="文件扩展名:")
            self.pattern_entry.configure(placeholder_text="例如: xlsx,xls,pdf")
        elif selected_mode == "大小模式":
            self.pattern_label.configure(text="文件大小限制 (MB):")
            self.pattern_entry.configure(placeholder_text="例如: 1-10 (最小1MB, 最大10MB)")
        elif selected_mode == "目录模式":
            self.pattern_label.configure(text="目录路径包含:")
            self.pattern_entry.configure(placeholder_text="例如: /data/ 或 /Documents/")

    def _start_extraction(self):
        """开始提取操作"""
        if self.controller.get_processing_status():
            return

        # 获取过滤选项（过滤始终启用）
        filter_mode = self.filter_mode.get()
        pattern = self.pattern_entry.get().strip()
        overwrite = self.overwrite_enabled.get()
        naming_mode = self.naming_mode.get()
        custom_prefix = self.custom_prefix.get().strip()
        custom_suffix = self.custom_suffix.get().strip()

        # 验证过滤条件
        if not pattern:
            messagebox.showerror("错误", "请设置文件过滤条件！")
            return

        # 验证命名模式的必要参数
        if naming_mode == "添加自定义前缀" and not custom_prefix:
            messagebox.showerror("错误", "请输入自定义前缀！")
            return

        if naming_mode == "添加自定义后缀" and not custom_suffix:
            messagebox.showerror("错误", "请输入自定义后缀！")
            return

        # 更新UI状态
        self.extract_button.configure(text="处理中...", state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="开始处理...")

        # 开始提取（filter_enabled 始终为 True）
        self.controller.start_extraction(
            input_dir=self.input_dir.get(),
            output_dir=self.output_dir.get(),
            filter_enabled=True,  # 始终启用过滤
            filter_mode=filter_mode,
            pattern=pattern,
            overwrite=overwrite,
            organize_mode=self.organize_mode.get(),
            naming_mode=naming_mode,
            custom_prefix=custom_prefix,
            custom_suffix=custom_suffix,
        )

    def _on_progress_update(self, progress: float, message: str):
        """进度更新回调"""
        self.progress_bar.set(progress)
        self.progress_label.configure(text=message)

    def _on_log_message(self, message: str):
        """日志消息回调"""
        self._log_message(message)

    def _on_extraction_complete(self, success: bool, message: str):
        """提取完成回调"""
        self.extract_button.configure(text="开始提取", state="normal")

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

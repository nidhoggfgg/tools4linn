"""
文件格式转换功能页面
提供用户友好的界面来批量转换图片格式
"""

import customtkinter as ctk
from tkinter import filedialog
import logging
from typing import List, Optional
from pathlib import Path

# 导入控制器
from ui.controllers.file_converter_controller import FileConverterController


class FileConverterPage(ctk.CTkFrame):
    """文件格式转换功能页面"""

    def __init__(self, parent):
        super().__init__(parent)

        # 设置日志
        self.logger = self._setup_logger()

        # 状态变量
        self.input_dir = ctk.StringVar()
        self.output_dir = ctk.StringVar()
        self.match_mode = ctk.StringVar(value="扩展名匹配")
        self.match_pattern = ctk.StringVar()
        self.recursive_search = ctk.BooleanVar(value=True)
        self.output_mode = ctk.StringVar(value="same_dir")
        self.output_format = ctk.StringVar(value="JPEG")
        self.quality = ctk.IntVar(value=95)
        self.delete_original = ctk.BooleanVar(value=False)

        # 预览结果
        self.preview_files: List[Path] = []

        # 创建控制器
        self.controller = FileConverterController(self.logger)
        self.controller.set_callbacks(
            progress_callback=self._on_progress_update,
            log_callback=self._on_log_message,
            complete_callback=self._on_conversion_complete,
        )

        # 创建界面
        self._create_ui()

        # 初始化输出格式选项
        self._update_output_formats()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("file_converter")
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
        self._create_directory_section()
        self._create_match_mode_section()
        self._create_conversion_section()
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
            text="🔄 批量图片格式转换工具",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.pack(pady=20)

        desc_label = ctk.CTkLabel(
            header_frame,
            text="支持多种图片格式之间的批量转换，提供灵活的文件匹配和输出选项",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),
        )
        desc_label.pack(pady=(0, 20))

        # 支持格式说明
        formats_label = ctk.CTkLabel(
            header_frame,
            text="支持格式: PNG, JPEG, WEBP, BMP, TIFF, GIF",
            font=ctk.CTkFont(size=12),
            text_color=("gray20", "gray80"),
        )
        formats_label.pack(pady=(0, 20))

    def _create_directory_section(self):
        """创建目录设置区域"""
        dir_frame = ctk.CTkFrame(self.scrollable_frame)
        dir_frame.pack(fill="x", pady=(0, 20))

        # 标题
        dir_title = ctk.CTkLabel(
            dir_frame, text="📁 目录设置", font=ctk.CTkFont(size=18, weight="bold")
        )
        dir_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 输入目录选择
        input_dir_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        input_dir_frame.pack(fill="x", padx=20, pady=(0, 10))

        input_label = ctk.CTkLabel(
            input_dir_frame, text="选择要搜索的目录:", font=ctk.CTkFont(size=14)
        )
        input_label.pack(anchor="w", pady=(0, 5))

        input_entry_frame = ctk.CTkFrame(input_dir_frame, fg_color="transparent")
        input_entry_frame.pack(fill="x")

        self.input_dir_entry = ctk.CTkEntry(
            input_entry_frame,
            textvariable=self.input_dir,
            placeholder_text="请选择要搜索的目录...",
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.input_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.input_dir_button = ctk.CTkButton(
            input_entry_frame,
            text="浏览",
            command=self._select_input_directory,
            width=80,
            height=35,
        )
        self.input_dir_button.pack(side="right")

        # 递归搜索选项
        recursive_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        recursive_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.recursive_checkbox = ctk.CTkCheckBox(
            recursive_frame,
            text="递归搜索子目录",
            variable=self.recursive_search,
            font=ctk.CTkFont(size=13),
        )
        self.recursive_checkbox.pack(anchor="w")

    def _create_match_mode_section(self):
        """创建文件匹配区域"""
        match_frame = ctk.CTkFrame(self.scrollable_frame)
        match_frame.pack(fill="x", pady=(0, 20))

        # 标题
        match_title = ctk.CTkLabel(
            match_frame, text="🔍 文件匹配", font=ctk.CTkFont(size=18, weight="bold")
        )
        match_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 匹配模式选择
        mode_frame = ctk.CTkFrame(match_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 10))

        mode_label = ctk.CTkLabel(
            mode_frame, text="匹配模式:", font=ctk.CTkFont(size=14)
        )
        mode_label.pack(anchor="w", pady=(0, 5))

        self.match_mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=["扩展名匹配", "关键字匹配", "正则表达式匹配"],
            variable=self.match_mode,
            command=self._on_match_mode_change,
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.match_mode_menu.pack(fill="x")

        # 匹配条件输入
        pattern_frame = ctk.CTkFrame(match_frame, fg_color="transparent")
        pattern_frame.pack(fill="x", padx=20, pady=(0, 15))

        pattern_label = ctk.CTkLabel(
            pattern_frame, text="匹配条件:", font=ctk.CTkFont(size=14)
        )
        pattern_label.pack(anchor="w", pady=(0, 5))

        self.pattern_desc_label = ctk.CTkLabel(
            pattern_frame,
            text="例如: png,jpg (用逗号分隔多个扩展名)",
            font=ctk.CTkFont(size=11),
            text_color=("gray20", "gray80"),
        )
        self.pattern_desc_label.pack(anchor="w", pady=(0, 5))

        self.match_pattern_entry = ctk.CTkEntry(
            pattern_frame,
            textvariable=self.match_pattern,
            placeholder_text="请输入匹配条件...",
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.match_pattern_entry.pack(fill="x")

    def _create_conversion_section(self):
        """创建转换设置区域"""
        conversion_frame = ctk.CTkFrame(self.scrollable_frame)
        conversion_frame.pack(fill="x", pady=(0, 20))

        # 标题
        conversion_title = ctk.CTkLabel(
            conversion_frame, text="🎨 转换设置", font=ctk.CTkFont(size=18, weight="bold")
        )
        conversion_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 输出格式选择
        format_frame = ctk.CTkFrame(conversion_frame, fg_color="transparent")
        format_frame.pack(fill="x", padx=20, pady=(0, 10))

        format_label = ctk.CTkLabel(
            format_frame, text="输出格式:", font=ctk.CTkFont(size=14)
        )
        format_label.pack(anchor="w", pady=(0, 5))

        self.output_format_menu = ctk.CTkOptionMenu(
            format_frame,
            values=["JPEG"],
            variable=self.output_format,
            command=self._on_output_format_change,
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.output_format_menu.pack(fill="x")

        # 输出模式选择
        output_mode_frame = ctk.CTkFrame(conversion_frame, fg_color="transparent")
        output_mode_frame.pack(fill="x", padx=20, pady=(0, 10))

        output_mode_label = ctk.CTkLabel(
            output_mode_frame, text="输出模式:", font=ctk.CTkFont(size=14)
        )
        output_mode_label.pack(anchor="w", pady=(0, 5))

        # 输出模式单选按钮
        radio_frame = ctk.CTkFrame(output_mode_frame, fg_color="transparent")
        radio_frame.pack(fill="x", pady=(0, 5))

        self.same_dir_radio = ctk.CTkRadioButton(
            radio_frame,
            text="在原文件夹输出",
            variable=self.output_mode,
            value="same_dir",
            command=self._on_output_mode_change,
            font=ctk.CTkFont(size=13),
        )
        self.same_dir_radio.pack(side="left", padx=(0, 20))

        self.unified_dir_radio = ctk.CTkRadioButton(
            radio_frame,
            text="统一输出到指定目录",
            variable=self.output_mode,
            value="unified",
            command=self._on_output_mode_change,
            font=ctk.CTkFont(size=13),
        )
        self.unified_dir_radio.pack(side="left")

        # 输出目录选择（默认隐藏）
        self.output_dir_frame = ctk.CTkFrame(conversion_frame, fg_color="transparent")
        # 不 pack，根据输出模式动态显示

        output_dir_label_frame = ctk.CTkFrame(self.output_dir_frame, fg_color="transparent")
        output_dir_label_frame.pack(fill="x", pady=(0, 5))

        output_dir_label = ctk.CTkLabel(
            output_dir_label_frame, text="输出目录:", font=ctk.CTkFont(size=14)
        )
        output_dir_label.pack(anchor="w")

        output_dir_entry_frame = ctk.CTkFrame(self.output_dir_frame, fg_color="transparent")
        output_dir_entry_frame.pack(fill="x")

        self.output_dir_entry = ctk.CTkEntry(
            output_dir_entry_frame,
            textvariable=self.output_dir,
            placeholder_text="请选择输出目录...",
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.output_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.output_dir_button = ctk.CTkButton(
            output_dir_entry_frame,
            text="浏览",
            command=self._select_output_directory,
            width=80,
            height=35,
        )
        self.output_dir_button.pack(side="right")

    def _create_options_section(self):
        """创建转换选项区域"""
        options_frame = ctk.CTkFrame(self.scrollable_frame)
        options_frame.pack(fill="x", pady=(0, 20))

        # 标题
        options_title = ctk.CTkLabel(
            options_frame, text="⚙️ 转换选项", font=ctk.CTkFont(size=18, weight="bold")
        )
        options_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 质量选项
        self.quality_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        self.quality_frame.pack(fill="x", padx=20, pady=(0, 10))

        quality_label = ctk.CTkLabel(
            self.quality_frame, text="图片质量:", font=ctk.CTkFont(size=14)
        )
        quality_label.pack(anchor="w", pady=(0, 5))

        quality_control_frame = ctk.CTkFrame(self.quality_frame, fg_color="transparent")
        quality_control_frame.pack(fill="x")

        self.quality_slider = ctk.CTkSlider(
            quality_control_frame,
            from_=1,
            to=100,
            variable=self.quality,
            width=200,
            height=20,
        )
        self.quality_slider.pack(side="left", padx=(0, 10))

        self.quality_value_label = ctk.CTkLabel(
            quality_control_frame,
            textvariable=self.quality,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=30,
        )
        self.quality_value_label.pack(side="left", padx=(0, 10))

        quality_desc_label = ctk.CTkLabel(
            quality_control_frame,
            text="1-100，值越大质量越高",
            font=ctk.CTkFont(size=11),
            text_color=("gray20", "gray80"),
        )
        quality_desc_label.pack(side="left")

        # 删除原文件选项
        delete_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        delete_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.delete_checkbox = ctk.CTkCheckBox(
            delete_frame,
            text="删除原文件（谨慎使用）",
            variable=self.delete_original,
            font=ctk.CTkFont(size=13),
        )
        self.delete_checkbox.pack(anchor="w")

        # 警告标签
        warning_label = ctk.CTkLabel(
            delete_frame,
            text="⚠️ 删除后无法恢复，建议先备份重要文件",
            font=ctk.CTkFont(size=11),
            text_color=("red", "red"),
        )
        warning_label.pack(anchor="w", padx=(25, 0))

    def _create_control_section(self):
        """创建控制按钮区域"""
        control_frame = ctk.CTkFrame(self.scrollable_frame)
        control_frame.pack(fill="x", pady=(0, 20))

        # 标题
        control_title = ctk.CTkLabel(
            control_frame, text="🎮 控制", font=ctk.CTkFont(size=18, weight="bold")
        )
        control_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 按钮容器
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.preview_button = ctk.CTkButton(
            button_frame,
            text="🔍 预览文件",
            command=self._preview_files,
            height=40,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.preview_button.pack(side="left", padx=(0, 10))

        self.convert_button = ctk.CTkButton(
            button_frame,
            text="🔄 开始转换",
            command=self._start_conversion,
            height=40,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.convert_button.pack(side="left", padx=(0, 10))

        self.clear_log_button = ctk.CTkButton(
            button_frame,
            text="清空日志",
            command=self._clear_log,
            height=40,
            width=100,
        )
        self.clear_log_button.pack(side="left")

    def _create_progress_section(self):
        """创建进度显示区域"""
        progress_frame = ctk.CTkFrame(self.scrollable_frame)
        progress_frame.pack(fill="x", pady=(0, 20))

        # 标题
        progress_title = ctk.CTkLabel(
            progress_frame, text="📊 进度", font=ctk.CTkFont(size=18, weight="bold")
        )
        progress_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame, width=400, height=20
        )
        self.progress_bar.pack(padx=20, pady=(0, 10))
        self.progress_bar.set(0)

        # 进度标签
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="等待开始...",
            font=ctk.CTkFont(size=13),
            text_color=("gray20", "gray80"),
        )
        self.progress_label.pack(padx=20, pady=(0, 15))

    def _create_log_section(self):
        """创建日志显示区域"""
        log_frame = ctk.CTkFrame(self.scrollable_frame)
        log_frame.pack(fill="both", expand=True, pady=(0, 20))

        # 标题
        log_title = ctk.CTkLabel(
            log_frame, text="📝 操作日志", font=ctk.CTkFont(size=18, weight="bold")
        )
        log_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 日志文本框
        self.log_text = ctk.CTkTextbox(log_frame, height=200, font=ctk.CTkFont(size=11))
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_text.configure(state="disabled")

    def _update_output_formats(self):
        """更新输出格式列表"""
        supported = self.controller.get_supported_conversions()
        # 合并所有支持的输出格式
        all_formats = set()
        for formats in supported.values():
            all_formats.update(formats)

        # 更新下拉菜单
        format_list = sorted(list(all_formats))
        self.output_format_menu.configure(values=format_list)

        # 设置默认值
        if format_list:
            self.output_format.set(format_list[0])

    def _select_input_directory(self):
        """选择输入目录"""
        directory = filedialog.askdirectory(title="选择要搜索的目录")
        if directory:
            self.input_dir.set(directory)

    def _select_output_directory(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)

    def _on_match_mode_change(self, choice: str):
        """匹配模式改变事件"""
        # 更新提示文本
        if choice == "扩展名匹配":
            self.pattern_desc_label.configure(
                text="例如: png,jpg (用逗号分隔多个扩展名)"
            )
        elif choice == "关键字匹配":
            self.pattern_desc_label.configure(
                text="例如: photo (匹配文件名包含该关键字的文件)"
            )
        elif choice == "正则表达式匹配":
            self.pattern_desc_label.configure(
                text="例如: .*\\d{4}.* (匹配包含4位数字的文件)"
            )

    def _on_output_format_change(self, choice: str):
        """输出格式改变事件"""
        # 根据输出格式显示/隐藏相关选项
        if choice.upper() in ["JPEG", "JPG", "WEBP"]:
            # 显示质量选项
            self.quality_frame.pack(fill="x", padx=20, pady=(0, 10))
        else:
            # 隐藏质量选项
            self.quality_frame.pack_forget()

    def _on_output_mode_change(self):
        """输出模式改变事件"""
        if self.output_mode.get() == "unified":
            # 显示输出目录选择
            self.output_dir_frame.pack(fill="x", padx=20, pady=(0, 15))
        else:
            # 隐藏输出目录选择
            self.output_dir_frame.pack_forget()

    def _preview_files(self):
        """预览文件"""
        # 验证输入
        if not self.input_dir.get():
            self._log_message("❌ 请先选择要搜索的目录")
            return

        if not self.match_pattern.get():
            self._log_message("❌ 请输入匹配条件")
            return

        # 查找文件
        success, message, files = self.controller.find_files(
            root_dir=self.input_dir.get(),
            match_mode=self.match_mode.get(),
            pattern=self.match_pattern.get(),
            recursive=self.recursive_search.get(),
        )

        if success:
            self.preview_files = files
            self._log_message(f"✅ {message}")
        else:
            self._log_message(f"❌ {message}")

    def _start_conversion(self):
        """开始转换"""
        # 验证输入
        if not self.preview_files:
            self._log_message('❌ 请先点击"预览文件"查看要转换的文件')
            return

        if self.output_mode.get() == "unified" and not self.output_dir.get():
            self._log_message("❌ 请选择输出目录")
            return

        # 禁用按钮
        self.convert_button.configure(state="disabled")
        self.preview_button.configure(state="disabled")

        # 准备转换选项
        conversion_options = {}
        output_format = self.output_format.get().upper()

        # 添加质量参数（仅对 JPEG/WEBP 有效）
        if output_format in ["JPEG", "JPG", "WEBP"]:
            conversion_options["quality"] = self.quality.get()

        # 添加删除原文件选项
        conversion_options["delete_original"] = self.delete_original.get()

        # 执行转换
        success, message = self.controller.convert_files(
            files=self.preview_files,
            output_format=self.output_format.get(),
            output_mode=self.output_mode.get(),
            output_dir=self.output_dir.get() if self.output_mode.get() == "unified" else None,
            conversion_options=conversion_options,
        )

        if success:
            self._log_message(f"✅ {message}")
        else:
            self._log_message(f"❌ {message}")

        # 重新启用按钮
        self.convert_button.configure(state="normal")
        self.preview_button.configure(state="normal")

    def _on_progress_update(self, progress: float, message: str):
        """更新进度"""
        self.progress_bar.set(progress)
        self.progress_label.configure(text=message)

    def _on_log_message(self, message: str):
        """添加日志消息"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _on_conversion_complete(self, success: bool, message: str):
        """转换完成回调"""
        pass

    def _clear_log(self):
        """清空日志"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

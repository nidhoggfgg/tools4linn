"""
Excel 时间填充功能页面
支持填充时间数据、名称数据，保留格式，随机调整行数
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging

from ui.controllers.excel_time_filler_controller import ExcelTimeFillerController


class ExcelTimeFillerPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.logger = self._setup_logger()

        # 变量
        self.template_file = ctk.StringVar()
        self.human_file = ctk.StringVar()
        self.names_file = ctk.StringVar()
        self.output_dir = ctk.StringVar()
        self.auto_output = ctk.BooleanVar(value=True)

        # 列配置
        self.start_time_col = ctk.StringVar(value="C")
        self.end_time_col = ctk.StringVar(value="D")
        self.duration_col = ctk.StringVar(value="E")
        self.name_col = ctk.StringVar(value="")

        # 其他配置
        self.year = ctk.IntVar(value=2025)
        self.data_start_row = ctk.IntVar(value=2)
        self.time_offset_minutes = ctk.IntVar(value=15)
        self.row_adjust_min = ctk.IntVar(value=-1)
        self.row_adjust_max = ctk.IntVar(value=10)

        # 是否使用名称列
        self.use_name_col = ctk.BooleanVar(value=False)
        # 是否启用人名脱敏
        self.use_anonymize = ctk.BooleanVar(value=False)

        # 控制器
        self.controller = ExcelTimeFillerController(self, self.logger)
        self.controller.set_callbacks(
            progress_callback=self._on_progress,
            log_callback=self._on_log,
            complete_callback=self._on_complete,
        )

        self._create_ui()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("excel_time_filler")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        return logger

    def _create_ui(self):
        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True, padx=20, pady=20)

        self._create_header()
        self._create_input_section()
        self._create_column_config_section()
        self._create_time_config_section()
        self._create_name_config_section()
        self._create_output_section()
        self._create_controls()
        self._create_progress()
        self._create_log()

    def _create_header(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(
            frame, text="⏰ Excel 时间填充工具", font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=20)
        desc = ctk.CTkLabel(
            frame,
            text="根据人员信息自动填充 Excel 时间数据，支持随机时间范围和行数调整",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),
        )
        desc.pack()

    def _create_input_section(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(
            frame, text="输入文件", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 15), anchor="w", padx=20)

        # 模板文件
        self._create_file_selector(
            frame,
            "Excel 模板文件:",
            self.template_file,
            self._select_template,
            "请选择模板文件...",
        )

        # 人员信息文件
        self._create_file_selector(
            frame,
            "人员信息文件:",
            self.human_file,
            self._select_human_file,
            "请选择人员信息文件...",
        )

    def _create_column_config_section(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(
            frame, text="列配置", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 15), anchor="w", padx=20)

        # 网格布局
        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 第一行：开始时间列、结束时间列
        row1 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))

        self._create_column_input(row1, "开始时间列:", self.start_time_col, side="left")
        self._create_column_input(row1, "结束时间列:", self.end_time_col, side="left", padx=(20, 0))

        # 第二行：持续时间列、数据起始行
        row2 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        self._create_column_input(row2, "持续时间列:", self.duration_col, side="left")
        self._create_number_input(row2, "数据起始行:", self.data_start_row, side="left", padx=(20, 0))

    def _create_time_config_section(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(
            frame, text="时间配置", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 15), anchor="w", padx=20)

        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 年份设置
        row_year = ctk.CTkFrame(grid_frame, fg_color="transparent")
        row_year.pack(fill="x", pady=(0, 10))

        label_year = ctk.CTkLabel(row_year, text="年份:", width=150)
        label_year.pack(side="left")
        entry_year = ctk.CTkEntry(row_year, textvariable=self.year, width=100)
        entry_year.pack(side="left", padx=(10, 0))

        info_year = ctk.CTkLabel(
            row_year,
            text="(用于生成时间数据)",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        info_year.pack(side="left", padx=(10, 0))

        # 时间偏移范围
        row1 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))

        label = ctk.CTkLabel(row1, text="时间偏移范围 (分钟):", width=150)
        label.pack(side="left")
        entry = ctk.CTkEntry(row1, textvariable=self.time_offset_minutes, width=100)
        entry.pack(side="left", padx=(10, 0))

        info = ctk.CTkLabel(
            row1,
            text="(生成时间会在实际时间前后此范围内随机)",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        info.pack(side="left", padx=(10, 0))

        # 行数调整范围
        row2 = ctk.CTkFrame(grid_frame, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        label = ctk.CTkLabel(row2, text="行数随机调整:", width=150)
        label.pack(side="left")

        label_min = ctk.CTkLabel(row2, text="最小:")
        label_min.pack(side="left", padx=(10, 5))
        entry_min = ctk.CTkEntry(row2, textvariable=self.row_adjust_min, width=80)
        entry_min.pack(side="left")

        label_max = ctk.CTkLabel(row2, text="最大:")
        label_max.pack(side="left", padx=(20, 5))
        entry_max = ctk.CTkEntry(row2, textvariable=self.row_adjust_max, width=80)
        entry_max.pack(side="left")

        info = ctk.CTkLabel(
            row2,
            text="(负数表示删除行，正数表示增加行)",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
        )
        info.pack(side="left", padx=(10, 0))

    def _create_name_config_section(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(
            frame, text="名称配置 (可选)", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 15), anchor="w", padx=20)

        # 是否启用名称列
        toggle = ctk.CTkCheckBox(
            frame,
            text="启用名称列填充",
            variable=self.use_name_col,
            command=self._toggle_name_col,
        )
        toggle.pack(anchor="w", padx=20, pady=(0, 10))

        # 是否启用人名脱敏
        anonymize_toggle = ctk.CTkCheckBox(
            frame,
            text="启用人名脱敏 (2字保留首字，3字+保留首尾)",
            variable=self.use_anonymize,
        )
        anonymize_toggle.pack(anchor="w", padx=20, pady=(0, 10))

        # 名称列配置
        self.name_config_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.name_config_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 名称列
        row1 = ctk.CTkFrame(self.name_config_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        self._create_column_input(row1, "名称列:", self.name_col, side="left")

        # 名称文件
        self._create_file_selector(
            self.name_config_frame,
            "名称文件 (每行一个名称):",
            self.names_file,
            self._select_names_file,
            "请选择名称文件...",
        )

        # 初始禁用名称配置
        self._toggle_name_col()

    def _create_output_section(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(
            frame, text="输出设置", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 15), anchor="w", padx=20)

        toggle = ctk.CTkCheckBox(
            frame,
            text="自动生成输出目录 (使用 filled_excels)",
            variable=self.auto_output,
            command=self._toggle_output_mode,
        )
        toggle.pack(anchor="w", padx=20, pady=(0, 10))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 20))
        label = ctk.CTkLabel(row, text="输出目录:")
        label.pack(anchor="w", pady=(0, 5))

        line = ctk.CTkFrame(row, fg_color="transparent")
        line.pack(fill="x")
        self.output_entry = ctk.CTkEntry(
            line, textvariable=self.output_dir, placeholder_text="留空则自动生成", height=35
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.output_button = ctk.CTkButton(
            line, text="选择目录", width=100, height=35, command=self._select_output_dir
        )
        self.output_button.pack(side="right")

        # 初始根据自动模式禁用
        self._toggle_output_mode()

    def _create_controls(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=20)
        self.run_button = ctk.CTkButton(
            row,
            text="开始处理",
            command=self._start,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            width=150,
            fg_color=("blue", "blue"),
            hover_color=("darkblue", "darkblue"),
        )
        self.run_button.pack(side="left")

        self.clear_button = ctk.CTkButton(
            row, text="清空日志", command=self._clear_log, height=35, width=100
        )
        self.clear_button.pack(side="left", padx=(10, 0))

    def _create_progress(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        self.progress_bar = ctk.CTkProgressBar(frame)
        self.progress_bar.pack(fill="x", padx=20, pady=20)
        self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(frame, text="准备就绪")
        self.progress_label.pack(pady=(0, 10))

    def _create_log(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="both", expand=True, pady=(0, 20))
        title = ctk.CTkLabel(
            frame, text="操作日志", font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(15, 10), anchor="w", padx=20)
        self.log_text = ctk.CTkTextbox(
            frame, height=200, font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # 辅助方法
    def _create_file_selector(self, parent, label_text, variable, command, placeholder):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 10))
        label = ctk.CTkLabel(row, text=label_text)
        label.pack(anchor="w", pady=(0, 5))

        line = ctk.CTkFrame(row, fg_color="transparent")
        line.pack(fill="x")
        entry = ctk.CTkEntry(line, textvariable=variable, placeholder_text=placeholder, height=35)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        button = ctk.CTkButton(line, text="浏览", width=80, height=35, command=command)
        button.pack(side="right")

    def _create_column_input(self, parent, label_text, variable, side="left", padx=0):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side=side, padx=padx)

        label = ctk.CTkLabel(container, text=label_text, width=100)
        label.pack(side="left")
        entry = ctk.CTkEntry(container, textvariable=variable, width=80)
        entry.pack(side="left", padx=(5, 0))

    def _create_number_input(self, parent, label_text, variable, side="left", padx=0):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side=side, padx=padx)

        label = ctk.CTkLabel(container, text=label_text, width=100)
        label.pack(side="left")
        entry = ctk.CTkEntry(container, textvariable=variable, width=80)
        entry.pack(side="left", padx=(5, 0))

    # 交互逻辑
    def _select_template(self):
        file_path = filedialog.askopenfilename(
            title="选择 Excel 模板文件",
            filetypes=[("Excel 文件", "*.xlsx *.xlsm *.xltx *.xltm"), ("所有文件", "*.*")],
        )
        if file_path:
            self.template_file.set(file_path)
            self._log(f"已选择模板文件: {file_path}")

    def _select_human_file(self):
        file_path = filedialog.askopenfilename(
            title="选择人员信息文件",
            filetypes=[("Excel 文件", "*.xlsx *.xlsm *.xltx *.xltm"), ("所有文件", "*.*")],
        )
        if file_path:
            self.human_file.set(file_path)
            self._log(f"已选择人员信息文件: {file_path}")

    def _select_names_file(self):
        file_path = filedialog.askopenfilename(
            title="选择名称文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )
        if file_path:
            self.names_file.set(file_path)
            self._log(f"已选择名称文件: {file_path}")

    def _select_output_dir(self):
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir.set(dir_path)
            self._log(f"已选择输出目录: {dir_path}")

    def _toggle_output_mode(self):
        auto = self.auto_output.get()
        state = "disabled" if auto else "normal"
        self.output_entry.configure(state=state)
        self.output_button.configure(state=state)

    def _toggle_name_col(self):
        enabled = self.use_name_col.get()
        # 根据状态禁用或启用名称配置框中的所有子控件
        for child in self.name_config_frame.winfo_children():
            self._set_state_recursive(child, "normal" if enabled else "disabled")

    def _set_state_recursive(self, widget, state):
        """递归设置控件状态"""
        try:
            widget.configure(state=state)
        except:
            pass
        for child in widget.winfo_children():
            self._set_state_recursive(child, state)

    def _start(self):
        if self.controller.get_processing_status():
            return

        # 验证输入
        if not self.template_file.get():
            messagebox.showerror("错误", "请选择模板文件")
            return
        if not self.human_file.get():
            messagebox.showerror("错误", "请选择人员信息文件")
            return
        if self.use_name_col.get() and not self.names_file.get():
            messagebox.showerror("错误", "启用名称列时必须选择名称文件")
            return

        self.run_button.configure(text="处理中...", state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="开始处理...")

        # 准备配置
        config = {
            "year": self.year.get(),
            "template_file": self.template_file.get(),
            "human_file": self.human_file.get(),
            "start_time_col": self.start_time_col.get(),
            "end_time_col": self.end_time_col.get(),
            "duration_col": self.duration_col.get() if self.duration_col.get() else None,
            "data_start_row": self.data_start_row.get(),
            "time_offset_minutes": self.time_offset_minutes.get(),
            "row_adjust_min": self.row_adjust_min.get(),
            "row_adjust_max": self.row_adjust_max.get(),
            "use_name_col": self.use_name_col.get(),
            "name_col": self.name_col.get() if self.use_name_col.get() else None,
            "names_file": self.names_file.get() if self.use_name_col.get() else None,
            "use_anonymize": self.use_anonymize.get(),
            "output_dir": self.output_dir.get() if not self.auto_output.get() else None,
        }

        self.controller.start_fill(config)

    # 回调
    def _on_progress(self, progress: float, message: str):
        self.progress_bar.set(progress)
        self.progress_label.configure(text=message)

    def _on_log(self, message: str):
        self._log(message)

    def _on_complete(self, success: bool, message: str):
        self.run_button.configure(text="开始处理", state="normal")
        if success:
            self.progress_label.configure(text="处理完成")
            messagebox.showinfo("成功", message)
        else:
            self.progress_label.configure(text="处理失败")
            messagebox.showerror("错误", message)

    # 工具
    def _log(self, message: str):
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")

    def _clear_log(self):
        self.log_text.delete("1.0", "end")

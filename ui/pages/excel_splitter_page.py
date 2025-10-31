"""
Excel 拆分功能页面
按首列(A列)分组拆分工作表并在 H 列汇总金额
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging

from ui.controllers.excel_splitter_controller import ExcelSplitterController


class ExcelSplitterPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.logger = self._setup_logger()

        # 变量
        self.input_file = ctk.StringVar()
        self.output_file = ctk.StringVar()
        self.auto_output = ctk.BooleanVar(value=True)

        # 控制器
        self.controller = ExcelSplitterController(self, self.logger)
        self.controller.set_callbacks(
            progress_callback=self._on_progress,
            log_callback=self._on_log,
            complete_callback=self._on_complete,
        )

        self._create_ui()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("excel_splitter")
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
        self._create_output_section()
        self._create_controls()
        self._create_progress()
        self._create_log()

    def _create_header(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(frame, text="📑 Excel 拆分工具", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)
        desc = ctk.CTkLabel(
            frame,
            text="按首列(A列)分组拆分为多个工作表，并在 H 列汇总金额",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),
        )
        desc.pack()

    def _create_input_section(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(frame, text="输入设置", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(20, 15), anchor="w", padx=20)

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=20)
        label = ctk.CTkLabel(row, text="选择 Excel 文件:")
        label.pack(anchor="w", pady=(0, 5))

        line = ctk.CTkFrame(row, fg_color="transparent")
        line.pack(fill="x")
        self.input_entry = ctk.CTkEntry(line, textvariable=self.input_file, placeholder_text="请选择输入文件...", height=35)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_button = ctk.CTkButton(line, text="浏览", width=80, height=35, command=self._select_input)
        self.input_button.pack(side="right")

    def _create_output_section(self):
        frame = ctk.CTkFrame(self.scrollable)
        frame.pack(fill="x", pady=(0, 20))
        title = ctk.CTkLabel(frame, text="输出设置", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(20, 15), anchor="w", padx=20)

        toggle = ctk.CTkCheckBox(
            frame,
            text="自动生成输出文件名 (原名 + _split)",
            variable=self.auto_output,
            command=self._toggle_output_mode,
        )
        toggle.pack(anchor="w", padx=20, pady=(0, 10))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=20)
        label = ctk.CTkLabel(row, text="输出文件:")
        label.pack(anchor="w", pady=(0, 5))

        line = ctk.CTkFrame(row, fg_color="transparent")
        line.pack(fill="x")
        self.output_entry = ctk.CTkEntry(line, textvariable=self.output_file, placeholder_text="留空则自动生成", height=35)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.output_button = ctk.CTkButton(line, text="保存为", width=80, height=35, command=self._select_output)
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
            text="开始拆分",
            command=self._start,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            width=150,
            fg_color=("blue", "blue"),
            hover_color=("darkblue", "darkblue"),
        )
        self.run_button.pack(side="left")

        self.clear_button = ctk.CTkButton(row, text="清空日志", command=self._clear_log, height=35, width=100)
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
        title = ctk.CTkLabel(frame, text="操作日志", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=(15, 10), anchor="w", padx=20)
        self.log_text = ctk.CTkTextbox(frame, height=200, font=ctk.CTkFont(family="Consolas", size=11))
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # 交互逻辑
    def _select_input(self):
        file_path = filedialog.askopenfilename(
            title="选择 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx *.xlsm *.xltx *.xltm"), ("所有文件", "*.*")],
        )
        if file_path:
            self.input_file.set(file_path)
            self._log(f"已选择输入文件: {file_path}")

    def _select_output(self):
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件位置",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")],
        )
        if file_path:
            self.output_file.set(file_path)
            self._log(f"已选择输出文件: {file_path}")

    def _toggle_output_mode(self):
        auto = self.auto_output.get()
        state = "disabled" if auto else "normal"
        self.output_entry.configure(state=state)
        self.output_button.configure(state=state)

    def _start(self):
        if self.controller.get_processing_status():
            return
        self.run_button.configure(text="处理中...", state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="开始处理...")

        output = None if self.auto_output.get() or not self.output_file.get().strip() else self.output_file.get().strip()
        self.controller.start_split(self.input_file.get(), output)

    # 回调
    def _on_progress(self, progress: float, message: str):
        self.progress_bar.set(progress)
        self.progress_label.configure(text=message)

    def _on_log(self, message: str):
        self._log(message)

    def _on_complete(self, success: bool, message: str):
        self.run_button.configure(text="开始拆分", state="normal")
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



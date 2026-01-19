"""
文件删除功能页面
提供用户友好的界面来删除匹配的文件，删除前需要确认
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging
from typing import List, Optional
from pathlib import Path

# 导入控制器
from ui.controllers.file_deleter_controller import FileDeleterController


class FileDeleterPage(ctk.CTkFrame):
    """文件删除功能页面"""

    def __init__(self, parent):
        super().__init__(parent)

        # 设置日志
        self.logger = self._setup_logger()

        # 状态变量
        self.root_dir = ctk.StringVar()
        self.match_mode = ctk.StringVar(value="关键字匹配")
        self.pattern = ctk.StringVar()
        self.min_size = ctk.StringVar()
        self.max_size = ctk.StringVar()
        self.recursive_search = ctk.BooleanVar(value=True)

        # 预览结果
        self.preview_files: List[Path] = []

        # 创建控制器
        self.controller = FileDeleterController(self.logger)
        self.controller.set_callbacks(
            progress_callback=self._on_progress_update,
            log_callback=self._on_log_message,
            complete_callback=self._on_operation_complete,
        )

        # 创建界面
        self._create_ui()

    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("file_deleter")
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
        self._create_advanced_options_section()
        self._create_control_section()
        self._create_progress_section()
        self._create_log_section()

    def _create_header(self):
        """创建页面标题"""
        header_frame = ctk.CTkFrame(self.scrollable_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="🗑️ 批量文件删除工具",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.pack(pady=20)

        desc_label = ctk.CTkLabel(
            header_frame,
            text="根据匹配条件查找并删除文件，删除前需要确认，支持多种匹配模式",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),
        )
        desc_label.pack(pady=(0, 20))

        warning_label = ctk.CTkLabel(
            header_frame,
            text="⚠️ 警告：文件删除后无法恢复，请仔细确认！",
            font=ctk.CTkFont(size=12),
            text_color=("red", "red"),
        )
        warning_label.pack(pady=(0, 20))

    def _create_directory_section(self):
        """创建目录选择区域"""
        dir_frame = ctk.CTkFrame(self.scrollable_frame)
        dir_frame.pack(fill="x", pady=(0, 20))

        # 标题
        dir_title = ctk.CTkLabel(
            dir_frame, text="目录设置", font=ctk.CTkFont(size=18, weight="bold")
        )
        dir_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 目录选择
        dir_entry_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_entry_frame.pack(fill="x", padx=20, pady=(0, 15))

        dir_label = ctk.CTkLabel(
            dir_entry_frame, text="选择要搜索的目录:", font=ctk.CTkFont(size=14)
        )
        dir_label.pack(anchor="w", pady=(0, 5))

        dir_input_frame = ctk.CTkFrame(dir_entry_frame, fg_color="transparent")
        dir_input_frame.pack(fill="x")

        self.dir_entry = ctk.CTkEntry(
            dir_input_frame,
            textvariable=self.root_dir,
            placeholder_text="请选择要搜索的根目录...",
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.dir_button = ctk.CTkButton(
            dir_input_frame,
            text="浏览",
            command=self._select_directory,
            width=80,
            height=35,
        )
        self.dir_button.pack(side="right")

        # 递归搜索选项
        recursive_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        recursive_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.recursive_checkbox = ctk.CTkCheckBox(
            recursive_frame,
            text="递归搜索子目录",
            variable=self.recursive_search,
        )
        self.recursive_checkbox.pack(anchor="w")

    def _create_match_mode_section(self):
        """创建匹配模式区域"""
        match_frame = ctk.CTkFrame(self.scrollable_frame)
        match_frame.pack(fill="x", pady=(0, 20))

        # 标题
        match_title = ctk.CTkLabel(
            match_frame, text="匹配模式", font=ctk.CTkFont(size=18, weight="bold")
        )
        match_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 匹配模式选择
        mode_frame = ctk.CTkFrame(match_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 15))

        mode_label = ctk.CTkLabel(
            mode_frame, text="选择匹配模式:", font=ctk.CTkFont(size=14)
        )
        mode_label.pack(anchor="w", pady=(0, 5))

        self.match_mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=self.controller.get_match_modes(),
            variable=self.match_mode,
            width=200,
            height=35,
            command=self._on_match_mode_change,
        )
        self.match_mode_menu.pack(anchor="w")

        # 模式说明
        self.mode_desc_label = ctk.CTkLabel(
            mode_frame,
            text=self.controller.get_match_description(self.match_mode.get()),
            font=ctk.CTkFont(size=11),
            text_color=("gray10", "gray90"),
        )
        self.mode_desc_label.pack(anchor="w", pady=(5, 0))

        # 匹配模式输入
        pattern_frame = ctk.CTkFrame(match_frame, fg_color="transparent")
        pattern_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.pattern_label = ctk.CTkLabel(
            pattern_frame, text="匹配关键字:", font=ctk.CTkFont(size=14)
        )
        self.pattern_label.pack(anchor="w", pady=(0, 5))

        self.pattern_entry = ctk.CTkEntry(
            pattern_frame,
            textvariable=self.pattern,
            placeholder_text="例如: temp",
            height=35,
            font=ctk.CTkFont(size=12),
        )
        self.pattern_entry.pack(fill="x")

    def _create_advanced_options_section(self):
        """创建高级选项区域"""
        advanced_frame = ctk.CTkFrame(self.scrollable_frame)
        advanced_frame.pack(fill="x", pady=(0, 20))

        # 标题
        advanced_title = ctk.CTkLabel(
            advanced_frame, text="高级选项（可选）", font=ctk.CTkFont(size=18, weight="bold")
        )
        advanced_title.pack(pady=(20, 15), anchor="w", padx=20)

        # 文件大小限制
        size_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        size_frame.pack(fill="x", padx=20, pady=(0, 15))

        size_label = ctk.CTkLabel(
            size_frame, text="文件大小限制 (MB):", font=ctk.CTkFont(size=14)
        )
        size_label.pack(anchor="w", pady=(0, 5))

        size_input_frame = ctk.CTkFrame(size_frame, fg_color="transparent")
        size_input_frame.pack(fill="x")

        min_label = ctk.CTkLabel(size_input_frame, text="最小:")
        min_label.pack(side="left", padx=(0, 5))

        self.min_size_entry = ctk.CTkEntry(
            size_input_frame,
            textvariable=self.min_size,
            placeholder_text="例如: 1",
            width=100,
            height=30,
        )
        self.min_size_entry.pack(side="left", padx=(0, 20))

        max_label = ctk.CTkLabel(size_input_frame, text="最大:")
        max_label.pack(side="left", padx=(0, 5))

        self.max_size_entry = ctk.CTkEntry(
            size_input_frame,
            textvariable=self.max_size,
            placeholder_text="例如: 100",
            width=100,
            height=30,
        )
        self.max_size_entry.pack(side="left")

        size_hint_label = ctk.CTkLabel(
            size_frame,
            text="提示：只设置最小值或最大值，或两者都设置以限制文件大小范围",
            font=ctk.CTkFont(size=11),
            text_color=("gray10", "gray90"),
        )
        size_hint_label.pack(anchor="w", pady=(5, 0))

    def _create_control_section(self):
        """创建控制按钮区域"""
        control_frame = ctk.CTkFrame(self.scrollable_frame)
        control_frame.pack(fill="x", pady=(0, 20))

        # 按钮区域
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        # 预览按钮
        self.preview_button = ctk.CTkButton(
            button_frame,
            text="🔍 预览匹配文件",
            command=self._preview_files,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            width=180,
            fg_color=("blue", "blue"),
            hover_color=("darkblue", "darkblue"),
        )
        self.preview_button.pack(side="left", padx=(0, 10))

        # 删除按钮（初始禁用）
        self.delete_button = ctk.CTkButton(
            button_frame,
            text="🗑️ 删除选中文件",
            command=self._delete_files,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            width=180,
            fg_color=("red", "red"),
            hover_color=("darkred", "darkred"),
            state="disabled",
        )
        self.delete_button.pack(side="left", padx=(0, 10))

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

    def _select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(title="选择要搜索的根目录")
        if directory:
            self.root_dir.set(directory)
            self._log_message(f"已选择目录: {directory}")

    def _on_match_mode_change(self, selected_mode):
        """匹配模式改变时的回调"""
        # 更新模式说明
        self.mode_desc_label.configure(
            text=self.controller.get_match_description(selected_mode)
        )

        # 更新标签和输入框的提示文本
        if selected_mode == "关键字匹配":
            self.pattern_label.configure(text="匹配关键字:")
            self.pattern_entry.configure(placeholder_text="例如: temp")
        elif selected_mode == "前缀匹配":
            self.pattern_label.configure(text="匹配前缀:")
            self.pattern_entry.configure(placeholder_text="例如: tmp_")
        elif selected_mode == "后缀匹配":
            self.pattern_label.configure(text="匹配后缀:")
            self.pattern_entry.configure(placeholder_text="例如: _backup (不含扩展名)")
        elif selected_mode == "扩展名匹配":
            self.pattern_label.configure(text="文件扩展名:")
            self.pattern_entry.configure(placeholder_text="例如: tmp,bak,old")
        elif selected_mode == "正则表达式匹配":
            self.pattern_label.configure(text="正则表达式:")
            self.pattern_entry.configure(placeholder_text="例如: .*\\.tmp$")

    def _preview_files(self):
        """预览匹配的文件"""
        if self.controller.get_processing_status():
            return

        # 获取参数
        root_dir = self.root_dir.get()
        match_mode = self.match_mode.get()
        pattern = self.pattern.get().strip()

        # 解析大小参数
        min_size = None
        max_size = None
        if self.min_size.get().strip():
            try:
                min_size = float(self.min_size.get().strip())
            except ValueError:
                messagebox.showerror("错误", "最小文件大小必须是数字！")
                return
        if self.max_size.get().strip():
            try:
                max_size = float(self.max_size.get().strip())
            except ValueError:
                messagebox.showerror("错误", "最大文件大小必须是数字！")
                return

        # 验证大小范围
        if min_size is not None and max_size is not None and min_size > max_size:
            messagebox.showerror("错误", "最小文件大小不能大于最大文件大小！")
            return

        # 验证输入
        if not root_dir:
            messagebox.showerror("错误", "请选择要搜索的目录！")
            return

        if not pattern:
            messagebox.showerror("错误", "请输入匹配模式！")
            return

        # 更新UI状态
        self.preview_button.configure(text="扫描中...", state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="开始扫描...")

        # 执行预览
        success, message, matched_files, errors = self.controller.preview_files(
            root_dir=root_dir,
            match_mode=match_mode,
            pattern=pattern,
            min_size=min_size,
            max_size=max_size,
            recursive=self.recursive_search.get(),
        )

        # 恢复UI状态
        self.preview_button.configure(text="🔍 预览匹配文件", state="normal")

        if success:
            if len(matched_files) > 0:
                self.delete_button.configure(state="normal")
                # 显示预览对话框
                self._show_preview_dialog(matched_files)
            else:
                self.delete_button.configure(state="disabled")
                messagebox.showinfo("预览完成", "未找到匹配的文件")
        else:
            self.delete_button.configure(state="disabled")
            messagebox.showerror("错误", message)

    def _delete_files(self):
        """删除文件"""
        if not self.preview_files:
            messagebox.showerror("错误", "没有可删除的文件，请先执行预览！")
            return

        # 确认对话框
        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除 {len(self.preview_files)} 个文件吗？\n\n此操作无法撤销！",
            icon="warning",
        )

        if not confirm:
            self._log_message("用户取消删除操作")
            return

        # 二次确认
        confirm2 = messagebox.askyesno(
            "再次确认",
            f"真的要删除这些文件吗？\n\n文件数量: {len(self.preview_files)}",
            icon="warning",
        )

        if not confirm2:
            self._log_message("用户在二次确认中取消删除操作")
            return

        # 更新UI状态
        self.delete_button.configure(text="删除中...", state="disabled")
        self.preview_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="开始删除...")

        # 执行删除
        success, message = self.controller.delete_files(self.preview_files)

        # 恢复UI状态
        self.delete_button.configure(text="🗑️ 删除选中文件", state="disabled")
        self.preview_button.configure(state="normal")

        if success:
            # 清空预览
            self.preview_files = []
            for widget in self.preview_list_frame.winfo_children():
                widget.destroy()
            self.preview_count_label.configure(text="删除完成")
            messagebox.showinfo("删除完成", message)
        else:
            messagebox.showerror("删除失败", message)

    def _on_progress_update(self, progress: float, message: str):
        """进度更新回调"""
        self.progress_bar.set(progress)
        self.progress_label.configure(text=message)

    def _on_log_message(self, message: str):
        """日志消息回调"""
        self._log_message(message)

    def _on_operation_complete(self, success: bool, message: str):
        """操作完成回调"""
        if success:
            self.progress_label.configure(text="操作完成")
        else:
            self.progress_label.configure(text="操作失败")

    def _show_preview_dialog(self, files: List[Path]):
        """显示预览对话框"""
        # 保存预览文件列表
        self.preview_files = files

        # 创建预览窗口
        preview_window = ctk.CTkToplevel(self.winfo_toplevel())
        preview_window.title("匹配文件预览")
        preview_window.geometry("800x600")

        # 设置窗口为模态
        preview_window.transient(self.winfo_toplevel())
        preview_window.grab_set()

        # 标题和统计信息
        header_frame = ctk.CTkFrame(preview_window, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="匹配文件预览",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(side="left")

        count_label = ctk.CTkLabel(
            header_frame,
            text=f"共找到 {len(files)} 个匹配文件",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),
        )
        count_label.pack(side="right")

        # 警告信息
        warning_frame = ctk.CTkFrame(preview_window, fg_color=("red", "darkred"))
        warning_frame.pack(fill="x", padx=20, pady=(0, 10))

        warning_label = ctk.CTkLabel(
            warning_frame,
            text="⚠️ 请仔细检查以下文件，确认删除后将无法恢复！",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
        )
        warning_label.pack(pady=10)

        # 文件列表
        list_frame = ctk.CTkScrollableFrame(preview_window, fg_color=("gray95", "gray10"))
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 显示文件列表
        for idx, file_path in enumerate(files, 1):
            file_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
            file_frame.pack(fill="x", pady=2, padx=5)

            # 序号
            num_label = ctk.CTkLabel(
                file_frame,
                text=f"{idx}.",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=40,
                anchor="w",
            )
            num_label.pack(side="left")

            # 文件路径
            path_label = ctk.CTkLabel(
                file_frame,
                text=str(file_path),
                font=ctk.CTkFont(size=11),
                anchor="w",
            )
            path_label.pack(side="left", fill="x", expand=True)

        # 按钮区域
        button_frame = ctk.CTkFrame(preview_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 关闭按钮
        close_button = ctk.CTkButton(
            button_frame,
            text="关闭",
            command=preview_window.destroy,
            width=120,
            height=35,
        )
        close_button.pack(side="right")

        # 导出列表按钮
        export_button = ctk.CTkButton(
            button_frame,
            text="导出列表",
            command=lambda: self._export_file_list(files),
            width=120,
            height=35,
        )
        export_button.pack(side="right", padx=(0, 10))

    def _export_file_list(self, files: List[Path]):
        """导出文件列表到文本文件"""
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            title="导出文件列表",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"匹配文件列表 - 共 {len(files)} 个文件\n")
                    f.write("=" * 80 + "\n\n")
                    for idx, path in enumerate(files, 1):
                        f.write(f"{idx}. {path}\n")
                messagebox.showinfo("导出成功", f"文件列表已导出到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("导出失败", f"导出文件列表时出错:\n{str(e)}")

    def _log_message(self, message: str):
        """添加日志消息"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")

    def _clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", "end")

"""
目录创建器页面
提供目录创建的用户界面
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path

from ui.controllers.directory_creator_controller import DirectoryCreatorController


class DirectoryCreatorPage(ctk.CTkFrame):
    """目录创建器页面"""

    def __init__(self, parent):
        super().__init__(parent)
        self.controller = DirectoryCreatorController()
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        title_label = ctk.CTkLabel(
            self, text="📁 批量创建文件夹", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # 创建滚动区域
        scrollable_frame = ctk.CTkScrollableFrame(self)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 基础设置区域
        self.setup_base_settings(scrollable_frame)

        # 创建模式选择
        self.setup_mode_selection(scrollable_frame)

        # 输入区域容器（用于管理列表和树状模式的切换）
        self.input_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        self.input_container.pack(fill="both", expand=True, padx=0, pady=0)

        # 列表模式输入区域
        self.list_frame = ctk.CTkFrame(self.input_container)
        self.setup_list_mode(self.list_frame)

        # 树状模式输入区域
        self.template_frame = ctk.CTkFrame(self.input_container)
        self.setup_template_mode(self.template_frame)

        # 默认显示列表模式
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 结果显示区域（最后pack，确保在最底部）
        self.setup_result_area(scrollable_frame)

    def setup_base_settings(self, parent):
        """设置基础设置区域"""
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            settings_frame, text="选择保存位置", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 基础路径设置
        base_path_frame = ctk.CTkFrame(settings_frame)
        base_path_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(base_path_frame, text="保存到:", width=80).pack(
            side="left", padx=5
        )
        self.base_path_entry = ctk.CTkEntry(
            base_path_frame, placeholder_text="选择文件夹位置"
        )
        self.base_path_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.base_path_entry.insert(0, ".")

        ctk.CTkButton(
            base_path_frame, text="选择文件夹", command=self.browse_base_path, width=100
        ).pack(side="right", padx=5)

        # 隐藏技术选项，默认设置
        self.exist_ok_var = ctk.BooleanVar(value=True)

    def setup_mode_selection(self, parent):
        """设置模式选择区域"""
        mode_frame = ctk.CTkFrame(parent)
        mode_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            mode_frame, text="输入方式", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        mode_buttons_frame = ctk.CTkFrame(mode_frame)
        mode_buttons_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.mode_var = ctk.StringVar(value="list")

        ctk.CTkRadioButton(
            mode_buttons_frame,
            text="📝 简单模式（每行一个路径）",
            variable=self.mode_var,
            value="list",
            command=self.on_mode_change,
        ).pack(side="left", padx=20, pady=5)

        ctk.CTkRadioButton(
            mode_buttons_frame,
            text="🌲 树状模式（层级结构）",
            variable=self.mode_var,
            value="template",
            command=self.on_mode_change,
        ).pack(side="left", padx=20, pady=5)

    def setup_list_mode(self, parent):
        """设置列表模式输入区域"""
        ctk.CTkLabel(
            parent,
            text="💡 提示：每行输入一个文件夹路径，可以包含多层（如：项目/源代码/工具）",
            font=ctk.CTkFont(size=13),
            text_color=("gray10", "gray70"),
        ).pack(pady=(10, 5))

        # 输入文本框
        self.list_input = ctk.CTkTextbox(parent, height=280)
        self.list_input.pack(fill="both", expand=True, padx=10, pady=10)

        # 默认示例
        example_text = """项目/源代码
项目/文档
项目/测试/单元测试
项目/测试/集成测试
数据/原始数据
数据/处理结果"""
        self.list_input.insert("1.0", example_text)

        # 快速操作按钮
        quick_buttons_frame = ctk.CTkFrame(parent)
        quick_buttons_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            quick_buttons_frame, text="清空", command=self.clear_list_input, width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            quick_buttons_frame,
            text="查看示例",
            command=self.load_list_example,
            width=80,
        ).pack(side="left", padx=5)

        # 创建按钮
        ctk.CTkButton(
            parent,
            text="✨ 开始创建",
            command=self.create_from_list,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=15)

    def setup_template_mode(self, parent):
        """设置树状模式输入区域"""
        ctk.CTkLabel(
            parent,
            text="💡 提示：用缩进（2个空格）表示层级，# 开头是注释，末尾 / 表示文件夹",
            font=ctk.CTkFont(size=13),
            text_color=("gray10", "gray70"),
        ).pack(pady=(10, 5))

        # 文件创建选项
        options_frame = ctk.CTkFrame(parent)
        options_frame.pack(fill="x", padx=10, pady=5)

        self.create_files_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_frame,
            text="📄 同时创建文件（自动识别带扩展名的项目）",
            variable=self.create_files_var,
            command=self.on_create_files_change,
        ).pack(side="left", padx=10, pady=5)

        # 输入文本框
        self.template_input = ctk.CTkTextbox(parent, height=250)
        self.template_input.pack(fill="both", expand=True, padx=10, pady=10)

        # 默认示例（不包含文件）
        example_text = """# 我的项目
我的项目/
  # 源代码
  源代码/
    组件/
      按钮/
      输入框/
      卡片/
    工具/
    服务/
      接口/
      认证/
  # 测试
  测试/
    单元测试/
    集成测试/
  # 文档
  文档/"""
        self.template_input.insert("1.0", example_text)

        # 快速操作按钮
        quick_buttons_frame = ctk.CTkFrame(parent)
        quick_buttons_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            quick_buttons_frame,
            text="清空",
            command=self.clear_template_input,
            width=80,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            quick_buttons_frame,
            text="文件夹示例",
            command=self.load_template_example_indent,
            width=90,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            quick_buttons_frame,
            text="文件+文件夹示例",
            command=self.load_template_example_with_files,
            width=110,
        ).pack(side="left", padx=5)

        # 创建按钮
        ctk.CTkButton(
            parent,
            text="✨ 开始创建",
            command=self.create_from_template,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=15)

    def setup_result_area(self, parent):
        """设置结果显示区域"""
        result_frame = ctk.CTkFrame(parent)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            result_frame, text="📋 创建结果", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 结果文本框
        self.result_text = ctk.CTkTextbox(result_frame, height=200)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)

        # 操作按钮
        button_frame = ctk.CTkFrame(result_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame, text="清空", command=self.clear_results, width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="复制", command=self.copy_results, width=80
        ).pack(side="left", padx=5)

    def browse_base_path(self):
        """浏览选择保存位置"""
        path = filedialog.askdirectory(title="选择文件夹保存位置")
        if path:
            self.base_path_entry.delete(0, "end")
            self.base_path_entry.insert(0, path)

    def on_exist_ok_change(self):
        """处理 exist_ok 选项变化"""
        self.controller.set_exist_ok(self.exist_ok_var.get())

    def on_create_files_change(self):
        """处理 create_files 选项变化"""
        self.controller.set_create_files(self.create_files_var.get())

    def on_mode_change(self):
        """处理模式切换"""
        mode = self.mode_var.get()
        if mode == "list":
            self.template_frame.pack_forget()
            self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            self.list_frame.pack_forget()
            self.template_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def clear_list_input(self):
        """清空列表输入"""
        self.list_input.delete("1.0", "end")

    def load_list_example(self):
        """加载简单模式示例"""
        example_text = """项目/源代码/组件
项目/源代码/工具
项目/源代码/服务/接口
项目/源代码/服务/认证
项目/测试/单元测试
项目/测试/集成测试
项目/文档"""
        self.list_input.delete("1.0", "end")
        self.list_input.insert("1.0", example_text)

    def clear_template_input(self):
        """清空模板输入"""
        self.template_input.delete("1.0", "end")

    def load_template_example_indent(self):
        """加载树状模式示例（缩进格式，仅文件夹）"""
        example_text = """# 我的项目结构
我的项目/
  # 源代码
  源代码/
    组件/
      按钮/
      输入框/
      卡片/
    工具/
    服务/
      接口/
      认证/
  # 测试
  测试/
    单元测试/
    集成测试/
  # 文档
  文档/"""
        self.template_input.delete("1.0", "end")
        self.template_input.insert("1.0", example_text)

    def load_template_example_with_files(self):
        """加载包含文件的树状示例"""
        example_text = """# 网站项目（包含文件和文件夹）
网站项目/
  # 源代码
  源代码/
    # 组件
    组件/
      头部.tsx
      底部.tsx
      侧边栏.tsx
    # 页面
    页面/
      首页.tsx
      关于.tsx
      联系.tsx
    # 工具
    工具/
      接口.ts
      帮助函数.ts
    # 样式
    样式/
      全局.css
      主题.css
    # 入口
    应用.tsx
    主文件.tsx
  # 公共资源
  公共资源/
    首页.html
    图标.ico
  # 配置
  配置.json
  # 说明文档
  说明文档.md"""
        self.template_input.delete("1.0", "end")
        self.template_input.insert("1.0", example_text)
        # 自动启用文件创建选项
        self.create_files_var.set(True)
        self.controller.set_create_files(True)

    def create_from_list(self):
        """从列表创建文件夹"""
        # 获取保存路径
        base_path = self.base_path_entry.get().strip()
        if not base_path:
            messagebox.showerror("提示", "请选择保存位置")
            return

        # 设置保存路径
        if not self.controller.set_base_path(base_path):
            messagebox.showerror("提示", self.controller.get_last_error())
            return

        # 设置允许已存在
        self.controller.set_exist_ok(self.exist_ok_var.get())

        # 获取路径列表
        content = self.list_input.get("1.0", "end").strip()
        if not content:
            messagebox.showerror("提示", "请输入要创建的文件夹路径")
            return

        paths = [line.strip() for line in content.split("\n") if line.strip()]

        # 创建文件夹
        if self.controller.create_from_list(paths):
            self.show_success_result()
        else:
            messagebox.showerror("提示", self.controller.get_last_error())

    def create_from_template(self):
        """从树状结构创建文件夹"""
        # 获取保存路径
        base_path = self.base_path_entry.get().strip()
        if not base_path:
            messagebox.showerror("提示", "请选择保存位置")
            return

        # 设置保存路径
        if not self.controller.set_base_path(base_path):
            messagebox.showerror("提示", self.controller.get_last_error())
            return

        # 设置选项
        self.controller.set_exist_ok(self.exist_ok_var.get())
        self.controller.set_create_files(self.create_files_var.get())

        # 获取树状结构内容
        template = self.template_input.get("1.0", "end").strip()
        if not template:
            messagebox.showerror("提示", "请输入树状结构")
            return

        # 创建文件夹
        if self.controller.create_from_template(template):
            self.show_success_result()
        else:
            messagebox.showerror("提示", self.controller.get_last_error())

    def show_success_result(self):
        """显示成功结果"""
        summary = self.controller.get_summary()
        tree_structure = self.controller.get_tree_structure(show_files=True)

        # 构建结果文本
        result_text = "✅ 创建成功！\n\n"
        result_text += f"📊 创建数量：\n"
        result_text += f"  - 文件夹: {summary['directories']} 个\n"
        result_text += f"  - 文件: {summary['files']} 个\n"
        result_text += f"  - 总计: {summary['total']} 个\n\n"
        result_text += tree_structure

        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", result_text)

        # 构建提示消息
        if summary['files'] > 0:
            msg = f"成功创建 {summary['directories']} 个文件夹和 {summary['files']} 个文件！"
        else:
            msg = f"成功创建 {summary['directories']} 个文件夹！"

        messagebox.showinfo("完成", msg)

    def clear_results(self):
        """清空结果"""
        self.result_text.delete("1.0", "end")

    def copy_results(self):
        """复制结果到剪贴板"""
        content = self.result_text.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("提示", "没有可复制的内容")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("完成", "已复制到剪贴板")


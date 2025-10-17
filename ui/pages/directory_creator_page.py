"""
目录创建器页面
提供目录创建的用户界面
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from tkinter import END, BOTH, LEFT, RIGHT, TOP, BOTTOM
from pathlib import Path

from ui.controllers.directory_creator_controller import DirectoryCreatorController
from toolkits.file.directory_creator import _expand_braces


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
        """设置树状模式输入区域（可视化方式）"""
        ctk.CTkLabel(
            parent,
            text="💡 提示：使用可视化树形结构构建目录，点击按钮添加文件夹或文件",
            font=ctk.CTkFont(size=13),
            text_color=("gray10", "gray70"),
        ).pack(pady=(10, 5))

        # 主容器：左侧树形视图 + 右侧操作按钮
        main_container = ctk.CTkFrame(parent)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 左侧：树形视图
        tree_container = ctk.CTkFrame(main_container)
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # 树形视图标题
        ctk.CTkLabel(
            tree_container,
            text="📁 目录结构",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(5, 5))

        # 创建树形视图（使用ttk.Treeview）
        tree_frame = ctk.CTkFrame(tree_container)
        tree_frame.pack(fill="both", expand=True)

        # 滚动条
        tree_scroll_y = ctk.CTkScrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        tree_scroll_x = ctk.CTkScrollbar(tree_frame, orientation="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        # 树形控件
        self.tree_view = ttk.Treeview(
            tree_frame,
            selectmode="browse",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
        )
        self.tree_view.pack(fill="both", expand=True)

        tree_scroll_y.configure(command=self.tree_view.yview)
        tree_scroll_x.configure(command=self.tree_view.xview)

        # 配置树形视图列
        self.tree_view["columns"] = ("type",)
        self.tree_view.column("#0", width=300, minwidth=200)
        self.tree_view.column("type", width=80, minwidth=60)
        self.tree_view.heading("#0", text="名称", anchor="w")
        self.tree_view.heading("type", text="类型", anchor="center")

        # 设置树形视图样式
        style = ttk.Style()
        style.theme_use("default")
        
        # 根据当前主题设置颜色
        bg_color = parent._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = parent._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = parent._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        
        style.configure(
            "Treeview",
            background=bg_color,
            foreground=text_color,
            fieldbackground=bg_color,
            borderwidth=0,
            font=("Microsoft YaHei UI", 10),
        )
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 10, "bold"))
        style.map("Treeview", background=[("selected", selected_color)])

        # 初始化根节点
        self.tree_view.insert("", "end", "root", text="根目录", values=("📁",), open=True)

        # 右侧：操作按钮区
        button_container = ctk.CTkFrame(main_container)
        button_container.pack(side="right", fill="y", padx=(0, 0))

        ctk.CTkLabel(
            button_container,
            text="🛠️ 操作",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(5, 10))

        # 添加操作按钮
        btn_width = 140

        ctk.CTkButton(
            button_container,
            text="➕ 添加文件夹",
            command=self.add_folder_node,
            width=btn_width,
        ).pack(pady=5)

        ctk.CTkButton(
            button_container,
            text="📄 添加文件",
            command=self.add_file_node,
            width=btn_width,
        ).pack(pady=5)

        ctk.CTkButton(
            button_container,
            text="✏️ 重命名",
            command=self.rename_node,
            width=btn_width,
        ).pack(pady=5)

        ctk.CTkButton(
            button_container,
            text="🗑️ 删除",
            command=self.delete_node,
            width=btn_width,
            fg_color=("#d32f2f", "#c62828"),
            hover_color=("#c62828", "#b71c1c"),
        ).pack(pady=5)

        # 分隔线
        ctk.CTkFrame(button_container, height=2, fg_color="gray50").pack(
            fill="x", pady=15, padx=10
        )

        ctk.CTkButton(
            button_container,
            text="⬆️ 上移",
            command=self.move_node_up,
            width=btn_width,
        ).pack(pady=5)

        ctk.CTkButton(
            button_container,
            text="⬇️ 下移",
            command=self.move_node_down,
            width=btn_width,
        ).pack(pady=5)

        # 分隔线
        ctk.CTkFrame(button_container, height=2, fg_color="gray50").pack(
            fill="x", pady=15, padx=10
        )

        ctk.CTkButton(
            button_container,
            text="🧹 清空全部",
            command=self.clear_tree,
            width=btn_width,
        ).pack(pady=5)

        ctk.CTkButton(
            button_container,
            text="📦 加载示例",
            command=self.load_tree_example,
            width=btn_width,
        ).pack(pady=5)

        # 创建按钮
        ctk.CTkButton(
            parent,
            text="✨ 开始创建",
            command=self.create_from_tree,
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

    # ==================== 树形视图操作方法 ====================

    def _create_multiline_input_dialog(self, title, prompt, placeholder=""):
        """创建多行输入对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # 提示文本
        ctk.CTkLabel(
            dialog,
            text=prompt,
            font=ctk.CTkFont(size=13),
            wraplength=360
        ).pack(pady=(20, 10), padx=20)
        
        # 文本输入框
        text_input = ctk.CTkTextbox(dialog, height=150)
        text_input.pack(fill="both", expand=True, padx=20, pady=10)
        if placeholder:
            text_input.insert("1.0", placeholder)
        
        # 按钮区域
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        result = {"value": None}
        
        def on_confirm():
            result["value"] = text_input.get("1.0", "end").strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame,
            text="确定",
            command=on_confirm,
            width=100
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="取消",
            command=on_cancel,
            width=100,
            fg_color="gray50",
            hover_color="gray40"
        ).pack(side="right", padx=5)
        
        # 等待对话框关闭
        dialog.wait_window()
        return result["value"]

    def _parse_input(self, input_text):
        """
        解析输入文本，支持多种格式：
        1. 花括号语法：{a,b,c} 或 {\na\nb\nc\n} - 作为一个节点（延迟展开）
        2. 纯列表：a\nb\nc - 批量添加多个节点
        
        Returns:
            list: 解析后的名称列表
        """
        if not input_text:
            return []
        
        input_text = input_text.strip()
        
        # 检测是否包含花括号
        if '{' in input_text and '}' in input_text:
            # 花括号模式：作为单个节点（延迟展开）
            # 标准化多行花括号格式为逗号分隔（更简洁）
            if '\n' in input_text:
                # 多行花括号：提取内容并转换为逗号分隔
                lines = input_text.split('\n')
                items = []
                in_brace = False
                for line in lines:
                    line = line.strip()
                    if line == '{':
                        in_brace = True
                    elif line == '}':
                        in_brace = False
                    elif in_brace and line:
                        items.append(line)
                
                if items:
                    # 返回标准化的花括号格式
                    return ['{' + ','.join(items) + '}']
                else:
                    # 保留原始输入
                    return [input_text]
            else:
                # 单行花括号：直接使用
                return [input_text]
        else:
            # 纯列表模式：按行分割，批量添加
            lines = input_text.split('\n')
            return [line.strip() for line in lines if line.strip()]

    def add_folder_node(self):
        """添加文件夹节点（支持多行和花括号展开）"""
        selected = self.tree_view.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个节点作为父节点")
            return

        # 弹出多行输入对话框
        folder_names = self._create_multiline_input_dialog(
            title="添加文件夹",
            prompt="支持两种模式:\n• 纯列表: 每行一个，批量添加\n• 花括号: {a,b,c} 或 {\\n  a\\n  b\\n}，添加为单个节点，可继续添加子目录",
            placeholder="模式1（批量添加）：\n组件\n服务\n工具\n\n模式2（延迟展开）：\n{组件,服务,工具}\n\n或多行花括号：\n{\n  组件\n  服务\n  工具\n}"
        )

        if folder_names:
            # 处理输入：支持花括号语法或纯列表
            names = self._parse_input(folder_names)
            
            if names:
                # 批量添加到树形视图
                added_count = 0
                for name in names:
                    self.tree_view.insert(
                        selected[0], "end", text=name, values=("📁",)
                    )
                    added_count += 1
                
                # 展开父节点
                self.tree_view.item(selected[0], open=True)
                
                # 显示添加结果
                if added_count > 1:
                    messagebox.showinfo("完成", f"成功批量添加 {added_count} 个文件夹")
                elif added_count == 1 and '{' in names[0]:
                    messagebox.showinfo("完成", f"已添加花括号节点: {names[0]}\n创建时将自动展开")

    def add_file_node(self):
        """添加文件节点（支持多行和花括号展开）"""
        selected = self.tree_view.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个节点作为父节点")
            return

        # 检查选中的节点是否为文件
        node_type = self.tree_view.item(selected[0])["values"][0]
        if node_type == "📄":
            messagebox.showwarning("提示", "不能在文件下添加子项，请选择文件夹")
            return

        # 弹出多行输入对话框
        file_names = self._create_multiline_input_dialog(
            title="添加文件",
            prompt="支持两种模式:\n• 纯列表: 每行一个，批量添加\n• 花括号: {a,b}.txt，添加为单个节点（可在其父级添加子目录）",
            placeholder="模式1（批量添加）：\nREADME.md\nconfig.json\nmain.py\n\n模式2（延迟展开）：\n{main,test,utils}.py\n\n或多行花括号：\n{\n  README.md\n  package.json\n  .gitignore\n}"
        )

        if file_names:
            # 处理输入：支持花括号语法或纯列表
            names = self._parse_input(file_names)
            
            if names:
                # 批量添加到树形视图
                added_count = 0
                for name in names:
                    self.tree_view.insert(
                        selected[0], "end", text=name, values=("📄",)
                    )
                    added_count += 1
                
                # 展开父节点
                self.tree_view.item(selected[0], open=True)
                
                # 显示添加结果
                if added_count > 1:
                    messagebox.showinfo("完成", f"成功批量添加 {added_count} 个文件")
                elif added_count == 1 and '{' in names[0]:
                    messagebox.showinfo("完成", f"已添加花括号节点: {names[0]}\n创建时将自动展开")

    def rename_node(self):
        """重命名节点"""
        selected = self.tree_view.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要重命名的节点")
            return

        if selected[0] == "root":
            messagebox.showwarning("提示", "不能重命名根目录")
            return

        current_name = self.tree_view.item(selected[0])["text"]
        node_type = self.tree_view.item(selected[0])["values"][0]

        # 弹出输入对话框
        dialog = ctk.CTkInputDialog(
            text=f"请输入新名称:\n当前: {current_name}",
            title="重命名",
        )
        new_name = dialog.get_input()

        if new_name:
            new_name = new_name.strip()
            if new_name:
                self.tree_view.item(selected[0], text=new_name)

    def delete_node(self):
        """删除节点"""
        selected = self.tree_view.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的节点")
            return

        if selected[0] == "root":
            messagebox.showwarning("提示", "不能删除根目录")
            return

        node_name = self.tree_view.item(selected[0])["text"]
        if messagebox.askyesno("确认删除", f"确定要删除 '{node_name}' 及其所有子项吗？"):
            self.tree_view.delete(selected[0])

    def move_node_up(self):
        """上移节点"""
        selected = self.tree_view.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要移动的节点")
            return

        if selected[0] == "root":
            messagebox.showwarning("提示", "不能移动根目录")
            return

        item = selected[0]
        parent = self.tree_view.parent(item)
        index = self.tree_view.index(item)

        if index > 0:
            self.tree_view.move(item, parent, index - 1)

    def move_node_down(self):
        """下移节点"""
        selected = self.tree_view.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要移动的节点")
            return

        if selected[0] == "root":
            messagebox.showwarning("提示", "不能移动根目录")
            return

        item = selected[0]
        parent = self.tree_view.parent(item)
        children = self.tree_view.get_children(parent)
        index = self.tree_view.index(item)

        if index < len(children) - 1:
            self.tree_view.move(item, parent, index + 1)

    def clear_tree(self):
        """清空树形视图"""
        if messagebox.askyesno("确认清空", "确定要清空所有内容吗？"):
            # 删除root的所有子节点
            for child in self.tree_view.get_children("root"):
                self.tree_view.delete(child)

    def load_tree_example(self):
        """加载树形示例"""
        # 清空现有内容
        for child in self.tree_view.get_children("root"):
            self.tree_view.delete(child)

        # 创建示例结构
        project = self.tree_view.insert("root", "end", text="我的项目", values=("📁",))

        # 源代码
        src = self.tree_view.insert(project, "end", text="源代码", values=("📁",))
        components = self.tree_view.insert(src, "end", text="组件", values=("📁",))
        self.tree_view.insert(components, "end", text="按钮", values=("📁",))
        self.tree_view.insert(components, "end", text="输入框", values=("📁",))
        self.tree_view.insert(components, "end", text="卡片", values=("📁",))

        utils = self.tree_view.insert(src, "end", text="工具", values=("📁",))
        services = self.tree_view.insert(src, "end", text="服务", values=("📁",))
        self.tree_view.insert(services, "end", text="接口", values=("📁",))
        self.tree_view.insert(services, "end", text="认证", values=("📁",))

        # 测试
        tests = self.tree_view.insert(project, "end", text="测试", values=("📁",))
        self.tree_view.insert(tests, "end", text="单元测试", values=("📁",))
        self.tree_view.insert(tests, "end", text="集成测试", values=("📁",))

        # 文档
        docs = self.tree_view.insert(project, "end", text="文档", values=("📁",))

        # 展开所有节点
        self.tree_view.item("root", open=True)
        self.tree_view.item(project, open=True)
        self.tree_view.item(src, open=True)
        self.tree_view.item(components, open=True)

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

    def create_from_tree(self):
        """从树形视图创建文件夹"""
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
        self.controller.set_create_files(True)  # 树形视图支持文件和文件夹

        # 检查是否有内容
        root_children = self.tree_view.get_children("root")
        if not root_children:
            messagebox.showerror("提示", "请先添加文件夹或文件")
            return

        # 将树形结构转换为模板字符串
        template = self._tree_to_template()

        # 创建文件夹
        if self.controller.create_from_template(template):
            self.show_success_result()
        else:
            messagebox.showerror("提示", self.controller.get_last_error())

    def _tree_to_template(self, parent="root", indent=0):
        """递归将树形结构转换为模板字符串"""
        lines = []
        children = self.tree_view.get_children(parent)

        for child in children:
            item = self.tree_view.item(child)
            name = item["text"]
            node_type = item["values"][0]

            # 添加缩进
            prefix = "  " * indent

            # 文件夹添加 /，文件不添加
            if node_type == "📁":
                lines.append(f"{prefix}{name}/")
                # 递归处理子节点
                child_lines = self._tree_to_template(child, indent + 1)
                if child_lines:
                    lines.append(child_lines)
            else:  # 文件
                lines.append(f"{prefix}{name}")

        return "\n".join(lines)

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


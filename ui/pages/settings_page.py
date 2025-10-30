"""设置页面

提供应用程序设置界面，包括 API Key 配置和其他设置选项。
"""

import customtkinter as ctk
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from ui.controllers.settings_controller import SettingsController


class SettingsPage(ctk.CTkFrame):
    """设置页面类"""

    def __init__(self, parent):
        super().__init__(parent)

        # 初始化控制器
        self.controller = SettingsController(log_callback=self._add_log)

        # 创建主布局
        self._create_layout()

        # 加载当前设置
        self._load_current_settings()

    def _create_layout(self):
        """创建页面布局"""
        # 创建滚动区域
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True)

        # 页面标题
        title_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            title_frame,
            text="⚙️ 设置",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="配置应用程序的基本设置和 API 密钥",
            font=ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # API 设置区域
        self._create_api_settings_section()

        # 其他设置区域
        self._create_other_settings_section()

        # 操作按钮区域
        self._create_action_buttons()

        # 日志区域
        self._create_log_section()

    def _create_api_settings_section(self):
        """创建 API 设置区域"""
        api_frame = ctk.CTkFrame(self.scrollable_frame)
        api_frame.pack(fill="x", padx=20, pady=10)

        # 区域标题
        section_title = ctk.CTkLabel(
            api_frame,
            text="API 配置",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        section_title.pack(anchor="w", padx=20, pady=(20, 15))

        # API Key 输入
        api_key_label = ctk.CTkLabel(
            api_frame,
            text="API Key:",
            font=ctk.CTkFont(size=14),
        )
        api_key_label.pack(anchor="w", padx=20, pady=(5, 5))

        self.api_key_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="请输入您的 API Key",
            width=600,
            height=40,
            show="*",  # 隐藏输入内容
        )
        self.api_key_entry.pack(anchor="w", padx=20, pady=(0, 15))

        # 显示/隐藏 API Key 按钮
        show_key_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        show_key_frame.pack(anchor="w", padx=20, pady=(0, 15))

        self.show_key_var = ctk.BooleanVar(value=False)
        self.show_key_checkbox = ctk.CTkCheckBox(
            show_key_frame,
            text="显示 API Key",
            variable=self.show_key_var,
            command=self._toggle_api_key_visibility,
        )
        self.show_key_checkbox.pack(side="left")

        # API Base URL 输入
        base_url_label = ctk.CTkLabel(
            api_frame,
            text="API Base URL:",
            font=ctk.CTkFont(size=14),
        )
        base_url_label.pack(anchor="w", padx=20, pady=(5, 5))

        self.base_url_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="例如: https://api.deepseek.com",
            width=600,
            height=40,
        )
        self.base_url_entry.pack(anchor="w", padx=20, pady=(0, 15))

        # 模型选择
        model_label = ctk.CTkLabel(
            api_frame,
            text="模型:",
            font=ctk.CTkFont(size=14),
        )
        model_label.pack(anchor="w", padx=20, pady=(5, 5))

        self.model_entry = ctk.CTkEntry(
            api_frame,
            placeholder_text="例如: deepseek-chat",
            width=600,
            height=40,
        )
        self.model_entry.pack(anchor="w", padx=20, pady=(0, 20))

    def _create_other_settings_section(self):
        """创建其他设置区域"""
        other_frame = ctk.CTkFrame(self.scrollable_frame)
        other_frame.pack(fill="x", padx=20, pady=10)

        # 区域标题
        section_title = ctk.CTkLabel(
            other_frame,
            text="其他设置",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        section_title.pack(anchor="w", padx=20, pady=(20, 15))

        # 配置文件路径显示
        config_path_label = ctk.CTkLabel(
            other_frame,
            text="配置文件路径:",
            font=ctk.CTkFont(size=14),
        )
        config_path_label.pack(anchor="w", padx=20, pady=(5, 5))

        config_path = self.controller.get_config_file_path()
        self.config_path_text = ctk.CTkLabel(
            other_frame,
            text=config_path,
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray70"),
        )
        self.config_path_text.pack(anchor="w", padx=20, pady=(0, 20))

    def _create_action_buttons(self):
        """创建操作按钮区域"""
        button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)

        # 保存按钮
        self.save_button = ctk.CTkButton(
            button_frame,
            text="💾 保存设置",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=150,
            command=self._save_settings,
        )
        self.save_button.pack(side="left", padx=(0, 10))

        # 测试连接按钮
        self.test_button = ctk.CTkButton(
            button_frame,
            text="🔗 测试连接",
            font=ctk.CTkFont(size=14),
            height=40,
            width=150,
            command=self._test_connection,
            fg_color=("gray70", "gray30"),
        )
        self.test_button.pack(side="left", padx=(0, 10))

        # 重置按钮
        self.reset_button = ctk.CTkButton(
            button_frame,
            text="🔄 重置默认",
            font=ctk.CTkFont(size=14),
            height=40,
            width=150,
            command=self._reset_settings,
            fg_color=("orange", "darkorange"),
        )
        self.reset_button.pack(side="left")

    def _create_log_section(self):
        """创建日志区域"""
        log_frame = ctk.CTkFrame(self.scrollable_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 日志标题
        log_title = ctk.CTkLabel(
            log_frame,
            text="操作日志",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        log_title.pack(anchor="w", padx=20, pady=(20, 10))

        # 日志文本框
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            height=200,
            font=ctk.CTkFont(family="Courier New", size=12),
        )
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_textbox.configure(state="disabled")

        # 清空日志按钮
        clear_log_button = ctk.CTkButton(
            log_frame,
            text="清空日志",
            command=self._clear_log,
            width=100,
            height=30,
        )
        clear_log_button.pack(anchor="e", padx=20, pady=(0, 20))

    def _toggle_api_key_visibility(self):
        """切换 API Key 可见性"""
        if self.show_key_var.get():
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="*")

    def _load_current_settings(self):
        """加载当前设置"""
        try:
            settings = self.controller.load_settings()

            # 填充表单
            self.api_key_entry.delete(0, "end")
            self.api_key_entry.insert(0, settings.get("api_key", ""))

            self.base_url_entry.delete(0, "end")
            self.base_url_entry.insert(0, settings.get("api_base_url", ""))

            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, settings.get("model", ""))

            self._add_log("INFO", "设置加载成功")
        except Exception as e:
            self._add_log("ERROR", f"加载设置失败: {str(e)}")

    def _save_settings(self):
        """保存设置"""
        try:
            # 禁用按钮
            self._set_buttons_state("disabled")

            # 获取表单数据
            settings = {
                "api_key": self.api_key_entry.get(),
                "api_base_url": self.base_url_entry.get(),
                "model": self.model_entry.get(),
            }

            # 保存设置
            if self.controller.save_all_settings(settings):
                self._add_log("SUCCESS", "✅ 所有设置已成功保存")
            else:
                self._add_log("ERROR", "❌ 保存设置失败，请检查输入")

        except Exception as e:
            self._add_log("ERROR", f"保存设置时发生错误: {str(e)}")
        finally:
            # 重新启用按钮
            self._set_buttons_state("normal")

    def _test_connection(self):
        """测试 API 连接"""
        try:
            # 禁用按钮
            self._set_buttons_state("disabled")

            # 测试连接
            self.controller.test_api_connection()

        except Exception as e:
            self._add_log("ERROR", f"测试连接时发生错误: {str(e)}")
        finally:
            # 重新启用按钮
            self._set_buttons_state("normal")

    def _reset_settings(self):
        """重置为默认设置"""
        # 确认对话框
        dialog = ctk.CTkInputDialog(
            text="确定要重置为默认设置吗？\n这将清空所有自定义配置。\n\n输入 'YES' 确认:",
            title="重置确认",
        )
        result = dialog.get_input()

        if result and result.upper() == "YES":
            try:
                # 禁用按钮
                self._set_buttons_state("disabled")

                # 重置设置
                if self.controller.reset_settings():
                    # 重新加载设置
                    self._load_current_settings()
                    self._add_log("SUCCESS", "✅ 设置已重置为默认值")
                else:
                    self._add_log("ERROR", "❌ 重置设置失败")

            except Exception as e:
                self._add_log("ERROR", f"重置设置时发生错误: {str(e)}")
            finally:
                # 重新启用按钮
                self._set_buttons_state("normal")
        else:
            self._add_log("INFO", "已取消重置操作")

    def _set_buttons_state(self, state: str):
        """设置按钮状态

        Args:
            state: 状态 ("normal" 或 "disabled")
        """
        self.save_button.configure(state=state)
        self.test_button.configure(state=state)
        self.reset_button.configure(state=state)

    def _add_log(self, level: str, message: str):
        """添加日志

        Args:
            level: 日志级别 (INFO, SUCCESS, WARNING, ERROR)
            message: 日志消息
        """
        self.log_textbox.configure(state="normal")

        # 根据级别设置颜色
        color_map = {
            "INFO": "blue",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red",
        }
        color = color_map.get(level, "black")

        # 添加时间戳
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        # 插入日志
        self.log_textbox.insert("end", log_entry)
        self.log_textbox.see("end")  # 滚动到底部

        self.log_textbox.configure(state="disabled")

    def _clear_log(self):
        """清空日志"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")


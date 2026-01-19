import customtkinter as ctk
from typing import Optional, Dict
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from ui.pages.home_page import HomePage
from ui.pages.excel_merger_page import ExcelMergerPage
from ui.pages.excel_splitter_page import ExcelSplitterPage
from ui.pages.excel_time_filler_page import ExcelTimeFillerPage
from ui.pages.time_generator_page import TimeGeneratorPage
from ui.pages.directory_creator_page import DirectoryCreatorPage
from ui.pages.document_reviewer_page import DocumentReviewerPage
from ui.pages.file_extractor_page import FileExtractorPage
from ui.pages.file_deleter_page import FileDeleterPage
from ui.pages.file_converter_page import FileConverterPage
from ui.pages.settings_page import SettingsPage


class MainWindow:
    """主窗口类，管理整个应用的界面布局"""

    def __init__(self):
        # 设置 CustomTkinter 主题
        ctk.set_appearance_mode("system")  # 跟随系统主题
        ctk.set_default_color_theme("blue")  # 蓝色主题

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("Tools4Linn - 多功能工具集")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass  # 如果没有图标文件就忽略

        # 当前页面
        self.current_page: Optional[ctk.CTkFrame] = None
        self.pages: Dict[str, ctk.CTkFrame] = {}

        # 创建界面
        self._create_sidebar()
        self._create_main_content()
        self._load_home_page()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_sidebar(self):
        """创建侧边栏导航"""
        # 侧边栏容器
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Logo 区域
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(20, 10))

        logo_label = ctk.CTkLabel(
            logo_frame, text="🛠️ Tools4Linn", font=ctk.CTkFont(size=24, weight="bold")
        )
        logo_label.pack(pady=10)

        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="多功能工具集",
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90"),
        )
        subtitle_label.pack()

        # 导航按钮区域
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=10)

        # 导航按钮
        self.nav_buttons = {}

        # 首页按钮
        self._create_nav_button(nav_frame, "home", "🏠 首页", self._show_home_page)

        # Excel 合并按钮
        self._create_nav_button(
            nav_frame, "excel_merger", "📊 Excel 合并", self._show_excel_merger_page
        )

        # Excel 拆分按钮
        self._create_nav_button(
            nav_frame, "excel_splitter", "📑 Excel 拆分", self._show_excel_splitter_page
        )

        # Excel 时间填充按钮
        self._create_nav_button(
            nav_frame, "excel_time_filler", "⏰ Excel 时间填充", self._show_excel_time_filler_page
        )

        # 时间生成器按钮
        self._create_nav_button(
            nav_frame, "time_generator", "🕐 时间生成器", self._show_time_generator_page
        )

        # 目录创建器按钮
        self._create_nav_button(
            nav_frame,
            "directory_creator",
            "📁 目录创建器",
            self._show_directory_creator_page,
        )

        # 文档审查按钮
        self._create_nav_button(
            nav_frame,
            "document_reviewer",
            "📄 文档审查",
            self._show_document_reviewer_page,
        )

        # 文件提取按钮
        self._create_nav_button(
            nav_frame,
            "file_extractor",
            "📂 文件提取",
            self._show_file_extractor_page,
        )

        # 文件删除按钮
        self._create_nav_button(
            nav_frame,
            "file_deleter",
            "🗑️ 批量文件删除",
            self._show_file_deleter_page,
        )

        # 文件格式转换按钮
        self._create_nav_button(
            nav_frame,
            "file_converter",
            "🔄 文件格式转换",
            self._show_file_converter_page,
        )

        # 分隔线
        separator = ctk.CTkFrame(nav_frame, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", pady=20)

        # 设置按钮
        self._create_nav_button(
            nav_frame, "settings", "⚙️ 设置", self._show_settings_page
        )

        # 关于按钮
        self._create_nav_button(nav_frame, "about", "ℹ️ 关于", self._show_about_page)

        # 底部区域 - 主题切换
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        # 主题切换按钮
        theme_label = ctk.CTkLabel(bottom_frame, text="主题模式:")
        theme_label.pack(anchor="w", pady=(0, 5))

        self.theme_menu = ctk.CTkOptionMenu(
            bottom_frame,
            values=["系统", "浅色", "深色"],
            command=self._change_theme,
            width=200,
        )
        self.theme_menu.pack(fill="x")
        self.theme_menu.set("系统")

    def _create_nav_button(self, parent, key: str, text: str, command):
        """创建导航按钮"""
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=40,
            font=ctk.CTkFont(size=14),
            anchor="w",
            fg_color="transparent",
            hover_color=("gray80", "gray20"),
        )
        button.pack(fill="x", pady=2)
        self.nav_buttons[key] = button

    def _create_main_content(self):
        """创建主内容区"""
        # 主内容区容器
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        # 内容区域
        self.content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _load_home_page(self):
        """加载首页"""
        if "home" not in self.pages:
            self.pages["home"] = HomePage(self.content_frame)
        self._show_page("home")

    def _show_home_page(self):
        """显示首页"""
        self._show_page("home")
        self._update_nav_button("home")

    def _show_excel_merger_page(self):
        """显示 Excel 合并页面"""
        if "excel_merger" not in self.pages:
            self.pages["excel_merger"] = ExcelMergerPage(self.content_frame)
        self._show_page("excel_merger")
        self._update_nav_button("excel_merger")

    def _show_excel_splitter_page(self):
        """显示 Excel 拆分页面"""
        if "excel_splitter" not in self.pages:
            self.pages["excel_splitter"] = ExcelSplitterPage(self.content_frame)
        self._show_page("excel_splitter")
        self._update_nav_button("excel_splitter")

    def _show_excel_time_filler_page(self):
        """显示 Excel 时间填充页面"""
        if "excel_time_filler" not in self.pages:
            self.pages["excel_time_filler"] = ExcelTimeFillerPage(self.content_frame)
        self._show_page("excel_time_filler")
        self._update_nav_button("excel_time_filler")

    def _show_time_generator_page(self):
        """显示时间生成器页面"""
        if "time_generator" not in self.pages:
            self.pages["time_generator"] = TimeGeneratorPage(self.content_frame)
        self._show_page("time_generator")
        self._update_nav_button("time_generator")

    def _show_directory_creator_page(self):
        """显示目录创建器页面"""
        if "directory_creator" not in self.pages:
            self.pages["directory_creator"] = DirectoryCreatorPage(self.content_frame)
        self._show_page("directory_creator")
        self._update_nav_button("directory_creator")

    def _show_document_reviewer_page(self):
        """显示文档审查页面"""
        if "document_reviewer" not in self.pages:
            self.pages["document_reviewer"] = DocumentReviewerPage(self.content_frame)
        self._show_page("document_reviewer")
        self._update_nav_button("document_reviewer")

    def _show_file_extractor_page(self):
        """显示文件提取页面"""
        if "file_extractor" not in self.pages:
            self.pages["file_extractor"] = FileExtractorPage(self.content_frame)
        self._show_page("file_extractor")
        self._update_nav_button("file_extractor")

    def _show_file_deleter_page(self):
        """显示文件删除页面"""
        if "file_deleter" not in self.pages:
            self.pages["file_deleter"] = FileDeleterPage(self.content_frame)
        self._show_page("file_deleter")
        self._update_nav_button("file_deleter")

    def _show_file_converter_page(self):
        """显示文件格式转换页面"""
        if "file_converter" not in self.pages:
            self.pages["file_converter"] = FileConverterPage(self.content_frame)
        self._show_page("file_converter")
        self._update_nav_button("file_converter")

    def _show_settings_page(self):
        """显示设置页面"""
        if "settings" not in self.pages:
            self.pages["settings"] = SettingsPage(self.content_frame)
        self._show_page("settings")
        self._update_nav_button("settings")

    def _show_about_page(self):
        """显示关于页面"""
        about_text = """
        Tools4Linn v0.1.0
        
        一个现代化的多功能桌面工具集
        
        功能特性：
        • Excel 文件合并
        • Excel 按首列拆分
        • Excel 时间填充（根据人员信息自动生成时间数据）
        • 时间点生成器（支持固定步长和随机步长模式）
        • 目录创建器（支持列表和树状模板模式）
        • 文档审查（AI驱动的文档数据提取与对比）
        • 文件提取（从多层目录中提取符合条件的文件）
        • 批量文件删除（支持多种匹配模式删除文件，删除前确认）
        • 文件格式转换（支持多种图片格式的批量转换）
        • 更多功能即将推出...
        
        开发者：nidhoggfgg
        """
        self._show_info_dialog("关于", about_text)

    def _show_page(self, page_key: str):
        """显示指定页面"""
        # 隐藏当前页面
        if self.current_page:
            self.current_page.pack_forget()

        # 显示新页面
        if page_key in self.pages:
            self.current_page = self.pages[page_key]
            self.current_page.pack(fill="both", expand=True)

    def _update_nav_button(self, active_key: str):
        """更新导航按钮状态"""
        for key, button in self.nav_buttons.items():
            if key == active_key:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color="transparent")

    def _change_theme(self, choice: str):
        """切换主题"""
        theme_map = {"系统": "system", "浅色": "light", "深色": "dark"}
        ctk.set_appearance_mode(theme_map[choice])

    def _show_info_dialog(self, title: str, message: str):
        """显示信息对话框"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.geometry(
            "+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50)
        )

        # 内容
        text_widget = ctk.CTkTextbox(dialog, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", message)
        text_widget.configure(state="disabled")

        # 关闭按钮
        close_button = ctk.CTkButton(
            dialog, text="关闭", command=dialog.destroy, width=100
        )
        close_button.pack(pady=(0, 20))

    def _on_closing(self):
        """窗口关闭事件处理"""
        self.root.quit()
        self.root.destroy()

    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()

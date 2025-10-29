import customtkinter as ctk


class HomePage(ctk.CTkFrame):
    """首页类，显示欢迎信息和功能概览"""

    def __init__(self, parent):
        super().__init__(parent)

        # 创建滚动区域
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True)

        self._create_welcome_section()
        self._create_features_section()
        self._create_quick_start_section()

    def _create_welcome_section(self):
        """创建欢迎区域"""
        welcome_frame = ctk.CTkFrame(self.scrollable_frame)
        welcome_frame.pack(fill="x", padx=20, pady=20)

        # 主标题
        title_label = ctk.CTkLabel(
            welcome_frame,
            text="欢迎使用 Tools4Linn",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        title_label.pack(pady=(30, 10))

        # 副标题
        subtitle_label = ctk.CTkLabel(
            welcome_frame,
            text="一个现代化的多功能桌面工具集",
            font=ctk.CTkFont(size=16),
            text_color=("gray10", "gray90"),
        )
        subtitle_label.pack(pady=(0, 20))

        # 描述文本
        description_text = """
        Tools4Linn 全称 tools for linn，是一个专为 linn 设计并开发的工具集，主要用于自动化处理。
        """

        description_label = ctk.CTkLabel(
            welcome_frame,
            text=description_text.strip(),
            font=ctk.CTkFont(size=14),
            justify="center",
            wraplength=600,
        )
        description_label.pack(pady=(0, 30))

    def _create_features_section(self):
        """创建功能特性区域"""
        features_frame = ctk.CTkFrame(self.scrollable_frame)
        features_frame.pack(fill="x", padx=20, pady=20)

        # 功能标题
        features_title = ctk.CTkLabel(
            features_frame, text="功能特性", font=ctk.CTkFont(size=24, weight="bold")
        )
        features_title.pack(pady=(20, 20))

        # 功能卡片容器
        cards_frame = ctk.CTkFrame(features_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=(0, 20))

        # 功能卡片
        features = [
            {
                "icon": "📊",
                "title": "Excel 合并",
                "description": "快速合并多个 Excel 文件，支持自定义命名策略和文件过滤",
                "status": "可用",
            },
            {
                "icon": "⏰",
                "title": "时间生成器",
                "description": "生成时间点序列，支持固定步长和随机步长模式",
                "status": "可用",
            },
            {
                "icon": "📁",
                "title": "目录创建器",
                "description": "批量创建多层目录结构，支持列表和树状模板模式",
                "status": "可用",
            },
            {
                "icon": "🎨",
                "title": "图像处理",
                "description": "图片格式转换和批量处理工具",
                "status": "计划中",
            },
        ]

        # 创建功能卡片网格
        for i, feature in enumerate(features):
            row = i // 2
            col = i % 2

            card = self._create_feature_card(cards_frame, feature)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        # 配置网格权重
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)

    def _create_feature_card(self, parent, feature: dict) -> ctk.CTkFrame:
        """创建功能卡片"""
        card = ctk.CTkFrame(parent, height=150)
        card.pack_propagate(False)

        # 图标
        icon_label = ctk.CTkLabel(card, text=feature["icon"], font=ctk.CTkFont(size=32))
        icon_label.pack(pady=(15, 5))

        # 标题
        title_label = ctk.CTkLabel(
            card, text=feature["title"], font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 5))

        # 描述
        desc_label = ctk.CTkLabel(
            card,
            text=feature["description"],
            font=ctk.CTkFont(size=12),
            text_color=("gray10", "gray90"),
            wraplength=200,
        )
        desc_label.pack(pady=(0, 10))

        # 状态标签
        status_color = "green" if feature["status"] == "可用" else "orange"
        status_label = ctk.CTkLabel(
            card,
            text=feature["status"],
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=status_color,
        )
        status_label.pack()

        return card

    def _create_quick_start_section(self):
        """创建快速开始区域"""
        quick_start_frame = ctk.CTkFrame(self.scrollable_frame)
        quick_start_frame.pack(fill="x", padx=20, pady=20)

        # 快速开始标题
        quick_start_title = ctk.CTkLabel(
            quick_start_frame, text="快速开始", font=ctk.CTkFont(size=24, weight="bold")
        )
        quick_start_title.pack(pady=(20, 20))

        # 快速开始内容
        quick_start_text = """
        1. 使用左侧导航栏选择您需要的功能
        2. 按照界面提示完成操作
        3. 查看实时日志了解处理进度
        
        当前可用功能：
        • Excel 合并：合并多个 Excel 文件为一个
        • 时间生成器：生成时间点序列
        • 目录创建器：批量创建目录结构
        """

        quick_start_label = ctk.CTkLabel(
            quick_start_frame,
            text=quick_start_text.strip(),
            font=ctk.CTkFont(size=14),
            justify="left",
            wraplength=600,
        )
        quick_start_label.pack(pady=(0, 20))

        # 开始使用按钮
        start_button = ctk.CTkButton(
            quick_start_frame,
            text="开始使用 Excel 合并",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=200,
        )
        start_button.pack(pady=(0, 20))

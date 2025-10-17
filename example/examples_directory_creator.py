"""
目录创建器使用示例
演示三种不同的创建方式
"""

from toolkits.file import (
    DirectoryCreator,
    create_directories,
    create_directories_from_template,
)
from pathlib import Path

# 创建示例输出目录
example_base = Path("./example_output")
example_base.mkdir(exist_ok=True)


def example1_list_syntax():
    """示例1：使用列表语法（最简单）"""
    print("\n" + "=" * 60)
    print("示例1：列表语法 - 适合创建简单的目录结构")
    print("=" * 60)

    creator = DirectoryCreator(base_path=example_base / "example1")

    # 创建一个简单的项目结构
    paths = creator.create_from_list(
        [
            "src/components",
            "src/utils",
            "src/services",
            "tests/unit",
            "tests/integration",
            "docs",
        ]
    )

    print(f"\n✓ 成功创建 {len(paths)} 个目录")
    creator.print_tree()


def example2_dict_syntax():
    """示例2：使用字典语法（推荐，最直观）"""
    print("\n" + "=" * 60)
    print("示例2：字典语法 - 适合创建复杂的嵌套结构（推荐）")
    print("=" * 60)

    creator = DirectoryCreator(base_path=example_base / "example2")

    # 创建一个完整的 Web 项目结构
    paths = creator.create_from_dict(
        {
            "my_web_app": {
                "frontend": {
                    "src": {
                        "components": ["Header", "Footer", "Sidebar"],
                        "pages": ["Home", "About", "Contact"],
                        "assets": {"images": None, "styles": None, "scripts": None},
                        "utils": None,
                    },
                    "public": None,
                },
                "backend": {
                    "api": {
                        "routes": ["users", "posts", "auth"],
                        "middleware": None,
                        "models": None,
                    },
                    "services": None,
                    "config": None,
                },
                "tests": {"unit": None, "integration": None, "e2e": None},
                "docs": ["api", "setup", "deployment"],
            }
        }
    )

    print(f"\n✓ 成功创建 {len(paths)} 个目录")
    creator.print_tree(max_depth=3)


def example3_template_syntax():
    """示例3：使用模板字符串语法（可视化）"""
    print("\n" + "=" * 60)
    print("示例3：模板字符串语法 - 适合从已有的目录树复制结构")
    print("=" * 60)

    creator = DirectoryCreator(base_path=example_base / "example3")

    # 使用简单缩进格式（支持注释）
    template = """
    # 数据处理管道项目
    data_pipeline/
      # 原始数据目录
      raw/
        csv/
        json/
        xml/
      # 处理后的数据
      processed/
        cleaned/
        normalized/
        aggregated/
      output/
        reports/
        visualizations/
      scripts/
        etl/
        analysis/
      logs/
    """

    paths = creator.create_from_template(template)

    print(f"\n✓ 成功创建 {len(paths)} 个目录")
    creator.print_tree()


def example4_convenience_functions():
    """示例4：使用便捷函数（快速创建）"""
    print("\n" + "=" * 60)
    print("示例4：便捷函数 - 不需要实例化类，直接创建")
    print("=" * 60)

    # 方式1：使用列表
    print("\n使用 create_directories() 和列表：")
    paths1 = create_directories(
        ["app/models", "app/views", "app/controllers"],
        base_path=example_base / "example4a",
    )
    print(f"✓ 创建了 {len(paths1)} 个目录")

    # 方式2：使用字典
    print("\n使用 create_directories() 和字典：")
    paths2 = create_directories(
        {
            "game": {
                "assets": ["sprites", "sounds", "music"],
                "scripts": ["player", "enemy", "ui"],
                "scenes": None,
            }
        },
        base_path=example_base / "example4b",
    )
    print(f"✓ 创建了 {len(paths2)} 个目录")

    # 方式3：使用模板
    print("\n使用 create_directories_from_template()：")
    paths3 = create_directories_from_template(
        """
        ml_project/
          data/
            train/
            test/
            val/
          models/
          notebooks/
        """,
        base_path=example_base / "example4c",
    )
    print(f"✓ 创建了 {len(paths3)} 个目录")


def example5_real_world():
    """示例5：真实世界的应用场景"""
    print("\n" + "=" * 60)
    print("示例5：真实场景 - 创建一个完整的 Python 包结构")
    print("=" * 60)

    # 创建一个标准的 Python 包结构
    package_structure = {
        "my_package": {
            "src": {
                "my_package": {"core": None, "utils": None, "models": None, "api": None}
            },
            "tests": {"unit": None, "integration": None, "fixtures": None},
            "docs": {"source": None, "build": None, "images": None},
            "examples": None,
            "scripts": None,
        }
    }

    paths = create_directories(package_structure, base_path=example_base / "example5")

    print(f"\n✓ 成功创建 {len(paths)} 个目录")
    print("\n完整的 Python 包结构已创建！")

    # 使用 DirectoryCreator 来打印树状结构
    creator = DirectoryCreator(base_path=example_base / "example5")
    creator.created_dirs = paths
    creator.print_tree(max_depth=4)


def example6_template_with_files():
    """示例6：模板语法增强功能 - 同时创建目录和文件"""
    print("\n" + "=" * 60)
    print("示例6：增强模板功能 - 支持创建文件和目录")
    print("=" * 60)

    creator = DirectoryCreator(base_path=example_base / "example6")

    # 使用模板同时创建目录和文件
    template = """
    # Web 应用项目
    web_app/
      # 前端源码
      src/
        # 组件目录
        components/
          Header.tsx
          Footer.tsx
          Sidebar.tsx
        # 页面
        pages/
          index.tsx
          about.tsx
          contact.tsx
        # 工具函数
        utils/
          api.ts
          helpers.ts
          constants.ts
        # 样式文件
        styles/
          global.css
          theme.css
        # 入口文件
        App.tsx
        main.tsx
      # 公共资源
      public/
        index.html
        favicon.ico
      # 配置文件
      package.json
      tsconfig.json
      vite.config.ts
      # 文档
      README.md
    """

    paths = creator.create_from_template(template, create_files=True)

    # 获取统计信息
    summary = creator.get_summary()
    
    print(f"\n✓ 创建成功！")
    print(f"  - 目录数量: {summary['directories']}")
    print(f"  - 文件数量: {summary['files']}")
    print(f"  - 总计: {summary['total']}")
    
    print("\n创建的目录和文件：")
    creator.print_tree(show_files=True)


if __name__ == "__main__":
    print("\n" + "🎯 " * 20)
    print("目录创建器 (DirectoryCreator) 使用示例")
    print("🎯 " * 20)

    # 运行所有示例
    example1_list_syntax()
    example2_dict_syntax()
    example3_template_syntax()
    example4_convenience_functions()
    example5_real_world()
    example6_template_with_files()

    print("\n" + "=" * 60)
    print("✨ 所有示例运行完成！")
    print(f"📁 查看创建的目录：{example_base.absolute()}")
    print("=" * 60)

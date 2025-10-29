"""
测试花括号展开语法的示例。

演示如何使用新的扩展语法快速创建大量多层目录。
"""

from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkits.file.directory_creator import DirectoryCreator

# 设置输出目录
base_output = Path(__file__).parent.parent / "example_output"


def example1_simple_braces():
    """示例1：简单的花括号列表展开"""
    print("\n" + "=" * 60)
    print("示例1：简单的花括号列表展开")
    print("=" * 60)

    output_dir = base_output / "brace_expansion_1"
    creator = DirectoryCreator(base_path=output_dir)

    template = """
project/
  src/
    {components,services,utils,models}/
  tests/
    {unit,integration,e2e}/
  docs/
    {api,guides,tutorials}/
"""

    print(f"\n使用的模板：")
    print(template)

    creator.create_from_template(template)
    creator.print_tree()

    summary = creator.get_summary()
    print(f"\n总共创建了 {summary['directories']} 个目录")


def example2_numeric_ranges():
    """示例2：数字范围展开"""
    print("\n" + "=" * 60)
    print("示例2：数字范围展开")
    print("=" * 60)

    output_dir = base_output / "brace_expansion_2"
    creator = DirectoryCreator(base_path=output_dir)

    template = """
courses/
  week_{1..12}/
    day_{1..7}/
      {morning,afternoon,evening}/
"""

    print(f"\n使用的模板：")
    print(template)
    print("这将创建 12 周 × 7 天 × 3 个时段 = 252 个叶子目录！")

    creator.create_from_template(template)

    summary = creator.get_summary()
    print(f"\n总共创建了 {summary['directories']} 个目录")
    print("\n显示前 3 周的结构：")
    # 只显示部分目录结构
    for path in creator.get_created_paths()[:30]:
        relative = path.relative_to(output_dir)
        indent = "  " * len(relative.parts)
        print(f"{indent}{relative.parts[-1]}/")


def example3_padded_numbers():
    """示例3：补零的数字范围"""
    print("\n" + "=" * 60)
    print("示例3：补零的数字范围")
    print("=" * 60)

    output_dir = base_output / "brace_expansion_3"
    creator = DirectoryCreator(base_path=output_dir)

    template = """
data/
  batch_{001..100}/
    {raw,processed,validated}/
"""

    print(f"\n使用的模板：")
    print(template)
    print("batch_001, batch_002, ..., batch_100")

    creator.create_from_template(template)

    summary = creator.get_summary()
    print(f"\n总共创建了 {summary['directories']} 个目录")
    print("\n显示前 10 个批次：")
    for path in creator.get_created_paths()[:33]:
        relative = path.relative_to(output_dir)
        indent = "  " * (len(relative.parts) - 1)
        print(f"{indent}{relative.parts[-1]}/")


def example4_letter_ranges():
    """示例4：字母范围展开"""
    print("\n" + "=" * 60)
    print("示例4：字母范围展开")
    print("=" * 60)

    output_dir = base_output / "brace_expansion_4"
    creator = DirectoryCreator(base_path=output_dir)

    template = """
sections/
  section_{A..Z}/
    subsection_{a..c}/
"""

    print(f"\n使用的模板：")
    print(template)

    creator.create_from_template(template)
    creator.print_tree(max_depth=2)

    summary = creator.get_summary()
    print(f"\n总共创建了 {summary['directories']} 个目录 (26 × 3 个子节 = 78 个子目录)")


def example5_nested_expansion():
    """示例5：嵌套展开"""
    print("\n" + "=" * 60)
    print("示例5：嵌套展开（极致的批量创建）")
    print("=" * 60)

    output_dir = base_output / "brace_expansion_5"
    creator = DirectoryCreator(base_path=output_dir)

    template = """
microservices/
  {user,product,order,payment}-service/
    {src,tests}/
      {models,views,controllers,services}/
    {docs,config}/
"""

    print(f"\n使用的模板：")
    print(template)
    print("4 个微服务 × 每个有相同的目录结构")

    creator.create_from_template(template)

    summary = creator.get_summary()
    print(f"\n总共创建了 {summary['directories']} 个目录")

    # 显示一个完整的服务结构
    print("\n显示 user-service 的完整结构：")
    for path in creator.get_created_paths():
        relative = path.relative_to(output_dir)
        if relative.parts[0] == "user-service":
            indent = "  " * (len(relative.parts) - 1)
            print(f"{indent}{relative.parts[-1]}/")


def example6_with_files():
    """示例6：结合文件创建"""
    print("\n" + "=" * 60)
    print("示例6：结合文件创建")
    print("=" * 60)

    output_dir = base_output / "brace_expansion_6"
    creator = DirectoryCreator(base_path=output_dir)

    template = """
app/
  {frontend,backend,mobile}/
    src/
      {components,utils,services}/
        __init__.py
    tests/
      {unit,integration}/
        __init__.py
    README.md
    requirements.txt
"""

    print(f"\n使用的模板：")
    print(template)

    creator.create_from_template(template, create_files=True)

    summary = creator.get_summary()
    print(f"\n总共创建了 {summary['directories']} 个目录，{summary['files']} 个文件")
    creator.print_tree(max_depth=3)


def example7_complex_project():
    """示例7：复杂项目结构（真实场景）"""
    print("\n" + "=" * 60)
    print("示例7：复杂项目结构（真实场景）")
    print("=" * 60)

    output_dir = base_output / "brace_expansion_7"
    creator = DirectoryCreator(base_path=output_dir)

    template = """
full_stack_app/
  # 前端部分
  frontend/
    src/
      pages/
        {Home,About,Contact,Dashboard,Profile}/
      components/
        {common,layout,forms,widgets}/
      {assets,styles,utils}/
    public/
    tests/
      {unit,e2e}/
  
  # 后端部分
  backend/
    api/
      v{1..3}/
        {users,posts,comments,auth}/
    {models,services,middleware,utils}/
    tests/
      {unit,integration}/
  
  # 基础设施
  {docker,kubernetes,terraform}/
  
  # 文档
  docs/
    {api,architecture,deployment,guides}/
"""

    print(f"\n使用的模板：")
    print(template)

    creator.create_from_template(template)

    summary = creator.get_summary()
    print(f"\n总共创建了 {summary['directories']} 个目录")
    creator.print_tree(max_depth=3)


def example8_year_month_structure():
    """示例8：年月日结构（日志、备份等场景）"""
    print("\n" + "=" * 60)
    print("示例8：年月日结构（适合日志、备份等场景）")
    print("=" * 60)

    output_dir = base_output / "brace_expansion_8"
    creator = DirectoryCreator(base_path=output_dir)

    template = """
logs/
  {2023..2024}/
    {01..12}/
      {01..31}/
"""

    print(f"\n使用的模板：")
    print(template)
    print("2 年 × 12 月 × 31 天 = 744 个目录（一次性创建所有日期目录）")

    creator.create_from_template(template)

    summary = creator.get_summary()
    print(f"\n总共创建了 {summary['directories']} 个目录")
    print("\n显示 2024年1月的部分结构：")
    count = 0
    for path in creator.get_created_paths():
        relative = path.relative_to(output_dir)
        if (
            len(relative.parts) >= 2
            and relative.parts[0] == "2024"
            and relative.parts[1] == "01"
        ):
            indent = "  " * (len(relative.parts) - 1)
            print(f"{indent}{relative.parts[-1]}/")
            count += 1
            if count >= 10:
                print(f"  ... 还有 21 天")
                break


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("花括号展开语法测试示例")
    print("=" * 60)
    print("\n这些示例展示了如何使用新的扩展语法快速创建大量目录")

    try:
        example1_simple_braces()
        example2_numeric_ranges()
        example3_padded_numbers()
        example4_letter_ranges()
        example5_nested_expansion()
        example6_with_files()
        example7_complex_project()
        example8_year_month_structure()

        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)
        print(f"\n所有输出文件位于：{base_output.absolute()}")

    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback

        traceback.print_exc()

"""
快速开始 - 花括号展开语法示例

展示最常用的几个场景。
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkits.file.directory_creator import DirectoryCreator

# 输出目录
output = Path(__file__).parent.parent / "example_output" / "quick_start"

print("=" * 60)
print("花括号展开语法 - 快速开始")
print("=" * 60)

# 示例 1：创建多个同级目录
print("\n1. 创建多个同级目录")
print("   模板: project/ src/ {components,utils,services}/")

creator = DirectoryCreator(base_path=output / "example1")
creator.create_from_template("""
project/
  src/
    {components,utils,services}/
""")
print(f"   [OK] 创建了 {creator.get_summary()['directories']} 个目录")

# 示例 2：创建带编号的目录
print("\n2. 创建带编号的目录")
print("   模板: week_{1..4}/")

creator = DirectoryCreator(base_path=output / "example2")
creator.create_from_template("""
courses/
  week_{1..4}/
""")
print(f"   [OK] 创建了 {creator.get_summary()['directories']} 个目录")

# 示例 3：嵌套展开（笛卡尔积）
print("\n3. 嵌套展开 - 为多个服务创建相同结构")
print("   模板: {user,product}-service/ {src,tests}/")

creator = DirectoryCreator(base_path=output / "example3")
creator.create_from_template("""
{user,product}-service/
  {src,tests}/
""")
print(f"   [OK] 创建了 {creator.get_summary()['directories']} 个目录")

# 示例 4：复杂的实际项目
print("\n4. 完整的微服务结构")
print("   组合使用多种展开模式")

creator = DirectoryCreator(base_path=output / "example4")
creator.create_from_template("""
microservices/
  {user,product,order}-service/
    src/
      {models,views,controllers}/
    tests/
      {unit,integration}/
    config/
""")
print(f"   [OK] 创建了 {creator.get_summary()['directories']} 个目录")

# 示例 5：结合文件创建
print("\n5. 结合文件创建")
print("   为每个服务创建配置文件")

creator = DirectoryCreator(base_path=output / "example5")
creator.create_from_template(
    """
services/
  {api,web,worker}/
    src/
      __init__.py
    README.md
    Dockerfile
""",
    create_files=True,
)
summary = creator.get_summary()
print(f"   [OK] 创建了 {summary['directories']} 个目录和 {summary['files']} 个文件")

print("\n" + "=" * 60)
print("完成！所有示例已创建")
print(f"输出目录: {output.absolute()}")
print("=" * 60)

print("\n提示：")
print("- 使用 {a,b,c} 创建多个同级目录")
print("- 使用 {1..10} 创建数字范围")
print("- 使用 {01..10} 创建补零的数字范围")
print("- 可以任意嵌套组合使用")
print(f"\n查看完整指南: {Path(__file__).parent / 'BRACE_EXPANSION_GUIDE.md'}")

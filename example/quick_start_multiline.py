"""
多行花括号语法 - 快速开始示例
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from toolkits.file.directory_creator import DirectoryCreator


def example1_basic():
    """示例1: 基本多行语法"""
    print("示例 1: 基本多行语法")
    print("-" * 50)
    
    creator = DirectoryCreator(base_path="./example_output/quick_multiline1")
    creator.create_from_template('''
my_app/
  {
    frontend
    backend
    mobile
  }/
''')
    
    creator.print_tree()
    print()


def example2_nested():
    """示例2: 嵌套多行语法"""
    print("示例 2: 嵌套多行语法")
    print("-" * 50)
    
    creator = DirectoryCreator(base_path="./example_output/quick_multiline2")
    creator.create_from_template('''
project/
  src/
    {
      components
      services
      utils
    }/
  tests/
    {
      unit
      integration
    }/
''')
    
    creator.print_tree()
    print()


def example3_mixed():
    """示例3: 多行与其他语法混合"""
    print("示例 3: 多行与范围展开混合")
    print("-" * 50)
    
    creator = DirectoryCreator(base_path="./example_output/quick_multiline3")
    creator.create_from_template('''
courses/
  {
    math
    science
    history
  }/
    week_{1..4}/
      day_{1..5}/
''')
    
    creator.print_tree(max_depth=3)
    summary = creator.get_summary()
    print(f"\n总计创建了 {summary['directories']} 个目录")
    print()


def example4_microservices():
    """示例4: 微服务架构"""
    print("示例 4: 微服务架构")
    print("-" * 50)
    
    creator = DirectoryCreator(base_path="./example_output/quick_multiline4")
    creator.create_from_template('''
microservices/
  {
    user-service
    order-service
    payment-service
  }/
    {
      src
      tests
      docs
    }/
''')
    
    creator.print_tree()
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("多行花括号语法 - 快速开始")
    print("=" * 50)
    print()
    
    example1_basic()
    example2_nested()
    example3_mixed()
    example4_microservices()
    
    print("=" * 50)
    print("所有示例运行完成！")
    print("=" * 50)


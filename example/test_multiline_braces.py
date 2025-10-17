"""
测试多行花括号语法
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from toolkits.file.directory_creator import DirectoryCreator


def test_multiline_braces():
    """测试多行花括号语法"""
    print("=" * 60)
    print("测试 1: 基本多行语法")
    print("=" * 60)
    
    template1 = """
multiline_test1/
  {
    frontend
    backend
    mobile
  }/
"""
    
    creator1 = DirectoryCreator(base_path="./example_output/multiline_test1")
    creator1.create_from_template(template1)
    creator1.print_tree()
    print(f"\n[OK] 创建了 {len(creator1.created_dirs)} 个目录")
    
    print("\n" + "=" * 60)
    print("测试 2: 嵌套多行语法")
    print("=" * 60)
    
    template2 = """
multiline_test2/
  src/
    {
      components
      services
      utils
      models
    }/
  tests/
    {
      unit
      integration
      e2e
    }/
"""
    
    creator2 = DirectoryCreator(base_path="./example_output/multiline_test2")
    creator2.create_from_template(template2)
    creator2.print_tree()
    print(f"\n[OK] 创建了 {len(creator2.created_dirs)} 个目录")
    
    print("\n" + "=" * 60)
    print("测试 3: 多行与逗号混合")
    print("=" * 60)
    
    template3 = """
multiline_test3/
  {
    app1,app2
    app3
    app4,app5,app6
  }/
    {
      src
      tests
    }/
"""
    
    creator3 = DirectoryCreator(base_path="./example_output/multiline_test3")
    creator3.create_from_template(template3)
    creator3.print_tree()
    print(f"\n[OK] 创建了 {len(creator3.created_dirs)} 个目录")
    
    print("\n" + "=" * 60)
    print("测试 4: 多行与范围展开组合")
    print("=" * 60)
    
    template4 = """
multiline_test4/
  data/
    {
      production
      staging
      development
    }/
      year_{2023..2025}/
        quarter_{1..4}/
"""
    
    creator4 = DirectoryCreator(base_path="./example_output/multiline_test4")
    creator4.create_from_template(template4)
    creator4.print_tree(max_depth=3)
    print(f"\n[OK] 创建了 {len(creator4.created_dirs)} 个目录")
    
    print("\n" + "=" * 60)
    print("测试 5: 复杂的多行嵌套")
    print("=" * 60)
    
    template5 = """
multiline_test5/
  microservices/
    {
      user-service
      order-service
      payment-service
      notification-service
    }/
      {
        src
        tests
        docs
      }/
        {
          models
          controllers
          services
        }/
"""
    
    creator5 = DirectoryCreator(base_path="./example_output/multiline_test5")
    creator5.create_from_template(template5)
    creator5.print_tree(max_depth=4)
    print(f"\n[OK] 创建了 {len(creator5.created_dirs)} 个目录")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 所有多行语法测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    test_multiline_braces()


"""
Verification script to check if all modules can be imported correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("模块导入验证脚本")
print("=" * 60)
print()

# Test imports
tests = []

def test_import(module_name, description):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        tests.append((description, True, None))
        print(f"✅ {description}")
    except Exception as e:
        tests.append((description, False, str(e)))
        print(f"❌ {description}: {e}")

# Core modules
print("核心模块:")
test_import("toolkits.review", "Review模块")
test_import("toolkits.review.pdf_converter", "PDF转换器")
test_import("toolkits.review.comparator", "数据比对器")
test_import("toolkits.review.reviewer", "文档审查器")
print()

# AI module
print("AI模块:")
test_import("toolkits.ai.client", "AI客户端")
print()

# UI modules
print("UI模块:")
test_import("ui.controllers.document_reviewer_controller", "文档审查控制器")
# Note: UI pages require display, may fail in headless environment
try:
    from ui.pages.document_reviewer_page import DocumentReviewerPage
    tests.append(("文档审查UI页面", True, None))
    print(f"✅ 文档审查UI页面")
except Exception as e:
    # May fail due to display requirements
    if "DISPLAY" in str(e) or "display" in str(e).lower():
        tests.append(("文档审查UI页面", True, "需要显示环境（正常）"))
        print(f"⚠️  文档审查UI页面: 需要显示环境（这是正常的）")
    else:
        tests.append(("文档审查UI页面", False, str(e)))
        print(f"❌ 文档审查UI页面: {e}")
print()

# Test class instantiation
print("类实例化测试:")
try:
    from toolkits.review import DataComparator
    comparator = DataComparator()
    tests.append(("DataComparator实例化", True, None))
    print(f"✅ DataComparator实例化")
except Exception as e:
    tests.append(("DataComparator实例化", False, str(e)))
    print(f"❌ DataComparator实例化: {e}")

try:
    from toolkits.review.pdf_converter import PDFConverter
    converter = PDFConverter()
    tests.append(("PDFConverter实例化", True, None))
    print(f"✅ PDFConverter实例化")
except Exception as e:
    tests.append(("PDFConverter实例化", False, str(e)))
    print(f"❌ PDFConverter实例化: {e}")

# Note: DocumentReviewer requires API key, may fail
try:
    from toolkits.review import DocumentReviewer
    reviewer = DocumentReviewer()
    tests.append(("DocumentReviewer实例化", True, None))
    print(f"✅ DocumentReviewer实例化")
except ValueError as e:
    if "API_KEY" in str(e):
        tests.append(("DocumentReviewer实例化", True, "需要API密钥（正常）"))
        print(f"⚠️  DocumentReviewer实例化: 需要API密钥（这是正常的）")
    else:
        tests.append(("DocumentReviewer实例化", False, str(e)))
        print(f"❌ DocumentReviewer实例化: {e}")
except Exception as e:
    tests.append(("DocumentReviewer实例化", False, str(e)))
    print(f"❌ DocumentReviewer实例化: {e}")

print()
print("=" * 60)
print("测试总结")
print("=" * 60)

passed = sum(1 for _, success, _ in tests if success)
total = len(tests)
warnings = sum(1 for _, success, note in tests if success and note)

print(f"总计: {total} 项测试")
print(f"通过: {passed} 项")
print(f"警告: {warnings} 项 (这些警告是正常的)")
print(f"失败: {total - passed} 项")
print()

if passed == total:
    print("✅ 所有测试通过！文档审查功能已正确安装。")
elif passed + warnings >= total:
    print("✅ 核心功能测试通过！警告是正常的，需要运行时环境。")
else:
    print("❌ 部分测试失败，请检查错误信息。")
    print()
    print("失败的测试:")
    for desc, success, error in tests:
        if not success:
            print(f"  - {desc}: {error}")

print()
print("下一步:")
print("1. 如果所有测试通过，运行: uv run python main.py")
print("2. 点击左侧 '📄 文档审查' 开始使用")
print("3. 查看快速开始指南: toolkits/review/QUICK_START.md")


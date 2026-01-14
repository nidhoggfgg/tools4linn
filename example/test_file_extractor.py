"""
文件提取功能测试脚本
"""

import logging
import tempfile
from pathlib import Path

# 添加项目根目录到路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

from toolkits.file.file_extractor import FileExtractor
from toolkits.utils.file_filter import NameIncludeStrategy, ExtensionStrategy


def setup_test_environment():
    """创建测试环境"""
    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())
    print(f"创建临时测试目录: {temp_dir}")

    # 创建目录结构
    (temp_dir / "level1").mkdir()
    (temp_dir / "level1" / "level2a").mkdir()
    (temp_dir / "level1" / "level2b").mkdir()

    # 创建测试文件
    test_files = [
        temp_dir / "test1.txt",
        temp_dir / "test2.doc",
        temp_dir / "level1" / "test3.txt",
        temp_dir / "level1" / "test4.xlsx",
        temp_dir / "level1" / "level2a" / "test5.txt",
        temp_dir / "level1" / "level2a" / "test6.pdf",
        temp_dir / "level1" / "level2b" / "test7.txt",
        temp_dir / "level1" / "level2b" / "test8.docx",
    ]

    for file_path in test_files:
        file_path.write_text(f"测试文件: {file_path.name}")
        print(f"创建测试文件: {file_path.relative_to(temp_dir)}")

    return temp_dir


def test_basic_extraction():
    """测试基本文件提取（不过滤）"""
    print("\n" + "="*60)
    print("测试 1: 基本文件提取（不过滤）")
    print("="*60)

    temp_dir = setup_test_environment()
    output_dir = temp_dir / "output_basic"

    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger("test_basic")

    # 创建提取器
    extractor = FileExtractor(
        logger=logger,
        input_dir=temp_dir,
        output_dir=output_dir,
        file_filter_strategy=None,
        overwrite=False,
    )

    # 提取文件
    result = extractor.extract_files()

    print(f"\n结果: 总计={result['total_count']}, 成功={result['success_count']}, "
          f"跳过={result['skipped_count']}, 失败={result['error_count']}")

    # 列出提取的文件
    extracted_files = list(output_dir.iterdir())
    print(f"\n提取的文件列表 (共 {len(extracted_files)} 个):")
    for f in sorted(extracted_files):
        print(f"  - {f.name}")

    return temp_dir


def test_with_extension_filter():
    """测试扩展名过滤"""
    print("\n" + "="*60)
    print("测试 2: 扩展名过滤（仅提取 .txt 文件）")
    print("="*60)

    temp_dir = setup_test_environment()
    output_dir = temp_dir / "output_extension"

    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger("test_extension")

    # 创建过滤策略
    filter_strategy = ExtensionStrategy(["txt"])

    # 创建提取器
    extractor = FileExtractor(
        logger=logger,
        input_dir=temp_dir,
        output_dir=output_dir,
        file_filter_strategy=filter_strategy,
        overwrite=False,
    )

    # 提取文件
    result = extractor.extract_files()

    print(f"\n结果: 总计={result['total_count']}, 成功={result['success_count']}, "
          f"跳过={result['skipped_count']}, 失败={result['error_count']}")

    # 列出提取的文件
    extracted_files = list(output_dir.iterdir())
    print(f"\n提取的文件列表 (共 {len(extracted_files)} 个):")
    for f in sorted(extracted_files):
        print(f"  - {f.name}")

    return temp_dir


def test_with_name_filter():
    """测试文件名过滤"""
    print("\n" + "="*60)
    print("测试 3: 文件名过滤（仅提取包含 'test5' 或 'test6' 的文件）")
    print("="*60)

    temp_dir = setup_test_environment()
    output_dir = temp_dir / "output_name"

    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger("test_name")

    # 创建过滤策略 - 使用复合策略
    from toolkits.utils.file_filter import CompositeStrategy, NameIncludeStrategy

    filter1 = NameIncludeStrategy("test5")
    filter2 = NameIncludeStrategy("test6")
    filter_strategy = CompositeStrategy([filter1, filter2], mode="OR")

    # 创建提取器
    extractor = FileExtractor(
        logger=logger,
        input_dir=temp_dir,
        output_dir=output_dir,
        file_filter_strategy=filter_strategy,
        overwrite=False,
    )

    # 提取文件
    result = extractor.extract_files()

    print(f"\n结果: 总计={result['total_count']}, 成功={result['success_count']}, "
          f"跳过={result['skipped_count']}, 失败={result['error_count']}")

    # 列出提取的文件
    extracted_files = list(output_dir.iterdir())
    print(f"\n提取的文件列表 (共 {len(extracted_files)} 个):")
    for f in sorted(extracted_files):
        print(f"  - {f.name}")

    return temp_dir


def main():
    """运行所有测试"""
    print("文件提取功能测试")
    print("="*60)

    try:
        test_basic_extraction()
        test_with_extension_filter()
        test_with_name_filter()

        print("\n" + "="*60)
        print("✓ 所有测试完成!")
        print("="*60)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

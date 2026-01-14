"""
测试文件提取功能 - 按第一层目录分组
"""

import logging
import tempfile
from pathlib import Path

# 添加项目根目录到路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

from toolkits.file.file_extractor import FileExtractor


def setup_test_environment():
    """创建测试环境"""
    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())
    print(f"创建临时测试目录: {temp_dir}")

    # 创建目录结构: 顶层有 a, b, c 三个目录
    for dir_name in ["a", "b", "c"]:
        top_dir = temp_dir / dir_name
        top_dir.mkdir()

        # 在每个目录下创建子目录和文件
        (top_dir / "sub1").mkdir()
        (top_dir / "sub2").mkdir()

        # 创建测试文件
        test_files = [
            top_dir / f"{dir_name}_1.txt",
            top_dir / f"{dir_name}_2.doc",
            top_dir / "sub1" / f"{dir_name}_sub1_1.txt",
            top_dir / "sub1" / f"{dir_name}_sub1_2.xlsx",
            top_dir / "sub2" / f"{dir_name}_sub2_1.pdf",
        ]

        for file_path in test_files:
            file_path.write_text(f"测试文件: {file_path.name}")
            print(f"  创建: {file_path.relative_to(temp_dir)}")

    # 在顶层创建一些文件
    (temp_dir / "root_1.txt").write_text("根目录文件1")
    (temp_dir / "root_2.doc").write_text("根目录文件2")
    print(f"  创建: root_1.txt")
    print(f"  创建: root_2.doc")

    return temp_dir


def test_flat_mode():
    """测试扁平化模式"""
    print("\n" + "="*60)
    print("测试 1: 扁平化模式")
    print("="*60)

    temp_dir = setup_test_environment()
    output_dir = temp_dir / "output_flat"

    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger("test_flat")

    # 创建提取器
    extractor = FileExtractor(
        logger=logger,
        input_dir=temp_dir,
        output_dir=output_dir,
        file_filter_strategy=None,
        overwrite=False,
        organize_by="flat",
    )

    # 提取文件
    result = extractor.extract_files()

    print(f"\n结果: 总计={result['total_count']}, 成功={result['success_count']}, "
          f"跳过={result['skipped_count']}, 失败={result['error_count']}")

    # 列出提取的文件结构
    print(f"\n输出目录结构:")
    if output_dir.exists():
        for f in sorted(output_dir.rglob("*")):
            if f.is_file():
                print(f"  {f.relative_to(output_dir)}")

    return temp_dir


def test_first_dir_mode():
    """测试按第一层目录分组模式"""
    print("\n" + "="*60)
    print("测试 2: 按第一层目录分组模式")
    print("="*60)

    temp_dir = setup_test_environment()
    output_dir = temp_dir / "output_first_dir"

    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger("test_first_dir")

    # 创建提取器
    extractor = FileExtractor(
        logger=logger,
        input_dir=temp_dir,
        output_dir=output_dir,
        file_filter_strategy=None,
        overwrite=False,
        organize_by="first_dir",
    )

    # 提取文件
    result = extractor.extract_files()

    print(f"\n结果: 总计={result['total_count']}, 成功={result['success_count']}, "
          f"跳过={result['skipped_count']}, 失败={result['error_count']}")

    # 列出提取的文件结构
    print(f"\n输出目录结构:")
    if output_dir.exists():
        # 列出子目录
        for subdir in sorted(output_dir.iterdir()):
            if subdir.is_dir():
                print(f"  目录: {subdir.name}/")
                # 列出该目录下的文件
                for f in sorted(subdir.iterdir()):
                    if f.is_file():
                        print(f"    {f.name}")
        # 列出根目录的文件
        print(f"  根目录文件:")
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                print(f"    {f.name}")

    return temp_dir


def test_first_dir_with_filter():
    """测试按第一层目录分组 + 文件过滤"""
    print("\n" + "="*60)
    print("测试 3: 按第一层目录分组 + 仅提取 .txt 文件")
    print("="*60)

    temp_dir = setup_test_environment()
    output_dir = temp_dir / "output_filtered"

    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger("test_filtered")

    # 创建过滤策略
    from toolkits.utils.file_filter import ExtensionStrategy
    filter_strategy = ExtensionStrategy(["txt"])

    # 创建提取器
    extractor = FileExtractor(
        logger=logger,
        input_dir=temp_dir,
        output_dir=output_dir,
        file_filter_strategy=filter_strategy,
        overwrite=False,
        organize_by="first_dir",
    )

    # 提取文件
    result = extractor.extract_files()

    print(f"\n结果: 总计={result['total_count']}, 成功={result['success_count']}, "
          f"跳过={result['skipped_count']}, 失败={result['error_count']}")

    # 列出提取的文件结构
    print(f"\n输出目录结构 (仅 .txt 文件):")
    if output_dir.exists():
        for subdir in sorted(output_dir.iterdir()):
            if subdir.is_dir():
                print(f"  目录: {subdir.name}/")
                for f in sorted(subdir.iterdir()):
                    if f.is_file():
                        print(f"    {f.name}")
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                print(f"  根目录: {f.name}")

    return temp_dir


def main():
    """运行所有测试"""
    print("文件提取功能测试 - 按目录分组")
    print("="*60)

    try:
        test_flat_mode()
        test_first_dir_mode()
        test_first_dir_with_filter()

        print("\n" + "="*60)
        print("✓ 所有测试完成!")
        print("="*60)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

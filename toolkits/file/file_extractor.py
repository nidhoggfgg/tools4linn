import shutil
from logging import Logger
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from collections import defaultdict

from toolkits.utils.file_filter import FileFilterStrategy


class FileExtractor:
    """文件提取器 - 从目录树中提取符合条件的文件到指定目录"""

    def __init__(
        self,
        logger: Logger,
        input_dir: Path,
        output_dir: Path,
        file_filter_strategy: Optional[FileFilterStrategy] = None,
        overwrite: bool = False,
        organize_by: str = "flat",
        naming_mode: str = "original",
        custom_prefix: str = "",
        custom_suffix: str = "",
        extract_target: str = "files",
    ):
        """
        初始化文件提取器

        Args:
            logger: 日志记录器
            input_dir: 输入目录（搜索源目录）
            output_dir: 输出目录（提取文件的目标目录）
            file_filter_strategy: 文件过滤策略，None 表示包含所有文件
            overwrite: 是否覆盖已存在的文件
            organize_by: 文件组织方式
                - "flat": 扁平化，所有文件放在输出目录根目录
                - "first_dir": 按第一层目录分组
            naming_mode: 文件命名模式
                - "original": 保持原文件名
                - "sequence": 添加序号（处理冲突）
                - "timestamp": 使用时间戳
                - "prefix": 添加自定义前缀
                - "suffix": 添加自定义后缀
                - "use_first_dir": 使用第一层目录名作为文件名（保留扩展名）
            custom_prefix: 自定义前缀（当 naming_mode="prefix" 时使用）
            custom_suffix: 自定义后缀（当 naming_mode="suffix" 时使用）
            extract_target: 提取目标类型
                - "files": 提取文件
                - "dirs": 提取文件夹
        """
        self.logger = logger
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.file_filter_strategy = file_filter_strategy
        self.overwrite = overwrite
        self.organize_by = organize_by
        self.naming_mode = naming_mode
        self.custom_prefix = custom_prefix
        self.custom_suffix = custom_suffix
        self.extract_target = extract_target

        # 用于序号模式的文件计数器
        self.file_counters = defaultdict(int)

    def find_all_files(
        self, input_dir: Path, extensions: Optional[List[str]] = None
    ) -> List[Path]:
        """
        查找目录中所有符合条件的文件

        Args:
            input_dir: 要搜索的目录
            extensions: 文件扩展名列表，None 表示所有文件

        Returns:
            符合条件的文件路径列表
        """
        if not input_dir.exists():
            self.logger.error(f"输入目录不存在: {input_dir}")
            return []

        if not input_dir.is_dir():
            self.logger.error(f"输入路径不是目录: {input_dir}")
            return []

        # 查找所有文件
        if extensions:
            # 查找指定扩展名的文件
            all_files = []
            for ext in extensions:
                if not ext.startswith("."):
                    ext = "." + ext
                all_files.extend(list(input_dir.rglob(f"*{ext}")))
        else:
            # 查找所有文件
            all_files = list(input_dir.rglob("*"))
            all_files = [f for f in all_files if f.is_file()]

        # 应用过滤策略
        filtered_files = []
        for file_path in all_files:
            if self.file_filter_strategy is None:
                filtered_files.append(file_path)
            elif self.file_filter_strategy.should_include(file_path):
                filtered_files.append(file_path)

        return filtered_files

    def find_all_directories(self, input_dir: Path) -> List[Path]:
        """
        查找目录中所有符合条件的子目录

        Args:
            input_dir: 要搜索的目录

        Returns:
            符合条件的目录路径列表
        """
        if not input_dir.exists():
            self.logger.error(f"输入目录不存在: {input_dir}")
            return []

        if not input_dir.is_dir():
            self.logger.error(f"输入路径不是目录: {input_dir}")
            return []

        all_dirs = [p for p in input_dir.rglob("*") if p.is_dir()]

        filtered_dirs = []
        for dir_path in all_dirs:
            if self.file_filter_strategy is None:
                filtered_dirs.append(dir_path)
            elif self.file_filter_strategy.should_include(dir_path):
                filtered_dirs.append(dir_path)

        return filtered_dirs

    def extract_files(self, extensions: Optional[List[str]] = None) -> dict:
        """
        提取文件到输出目录

        Args:
            extensions: 要提取的文件扩展名列表，None 表示所有文件

        Returns:
            包含提取结果的字典:
            - success_count: 成功提取的文件数
            - skipped_count: 跳过的文件数
            - error_count: 出错的文件数
            - total_count: 总文件数
        """
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 查找所有符合条件的目标
        extract_target = self._normalize_extract_target()
        if extract_target == "dirs":
            all_targets = self.find_all_directories(self.input_dir)
        else:
            all_targets = self.find_all_files(self.input_dir, extensions)

        # 排除输出目录自身及其内容（避免递归复制）
        all_targets = [
            p for p in all_targets if not self._is_within_output_dir(p)
        ]

        self.logger.info(
            f"找到 {len(all_targets)} 个{self._get_extract_target_name(extract_target)}"
        )
        self.logger.info(f"组织方式: {self._get_organize_mode_name()}")
        self.logger.info(f"命名模式: {self._get_naming_mode_name()}")

        success_count = 0
        skipped_count = 0
        error_count = 0

        for target_path in all_targets:
            try:
                # 计算目标文件路径
                dest_path = self._get_destination_path(target_path)

                # 应用命名模式
                dest_path = self._apply_naming_mode(dest_path, target_path)

                # 检查文件是否已存在
                if dest_path.exists():
                    if self.overwrite:
                        if dest_path.is_dir():
                            shutil.rmtree(dest_path)
                        else:
                            dest_path.unlink()
                        self.logger.warning(f"覆盖已存在的目标: {dest_path}")
                    else:
                        self.logger.info(f"跳过已存在的目标: {dest_path}")
                        skipped_count += 1
                        continue

                # 创建目标目录（如果需要）
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # 复制文件/目录
                if target_path.is_dir():
                    shutil.copytree(target_path, dest_path, copy_function=shutil.copy2)
                else:
                    shutil.copy2(target_path, dest_path)
                self.logger.info(
                    f"已复制: {target_path.relative_to(self.input_dir)}"
                )
                success_count += 1

            except Exception as e:
                self.logger.error(f"复制失败 {target_path}: {e}")
                error_count += 1

        result = {
            "success_count": success_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "total_count": len(all_targets),
        }

        self.logger.info(
            f"提取完成: 成功={success_count}, 跳过={skipped_count}, 失败={error_count}"
        )

        return result

    def _get_destination_path(self, file_path: Path) -> Path:
        """
        根据组织模式计算目标文件路径

        Args:
            file_path: 源文件路径

        Returns:
            目标文件路径
        """
        if self.organize_by == "flat":
            # 扁平化：直接放在输出目录根目录
            return self.output_dir / file_path.name

        elif self.organize_by == "first_dir":
            # 按第一层目录分组
            try:
                relative_path = file_path.relative_to(self.input_dir)
                parts = relative_path.parts

                if len(parts) > 1:
                    # 文件在子目录中，使用第一层目录名
                    first_dir = parts[0]
                    return self.output_dir / first_dir / file_path.name
                else:
                    # 文件在输入目录根目录，直接放在输出目录
                    return self.output_dir / file_path.name
            except ValueError:
                # 如果无法计算相对路径，直接使用文件名
                return self.output_dir / file_path.name

        else:
            # 默认扁平化
            return self.output_dir / file_path.name

    def _get_organize_mode_name(self) -> str:
        """获取组织模式的名称"""
        if self.organize_by == "flat":
            return "扁平化"
        elif self.organize_by == "first_dir":
            return "按第一层目录分组"
        else:
            return "未知"

    def _get_naming_mode_name(self) -> str:
        """获取命名模式的名称"""
        naming_mode_names = {
            "original": "保持原文件名",
            "sequence": "添加序号",
            "timestamp": "使用时间戳",
            "prefix": "添加自定义前缀",
            "suffix": "添加自定义后缀",
            "use_first_dir": "使用第一层目录名",
        }
        return naming_mode_names.get(self.naming_mode, "未知")

    def _normalize_extract_target(self) -> str:
        """规范化提取目标类型"""
        if self.extract_target not in ("files", "dirs"):
            self.logger.warning(f"未知的提取目标类型: {self.extract_target}, 默认使用 files")
            return "files"
        return self.extract_target

    def _get_extract_target_name(self, extract_target: str) -> str:
        """获取提取目标的名称"""
        if extract_target == "dirs":
            return "文件夹"
        return "文件"

    def _is_within_output_dir(self, path: Path) -> bool:
        """判断路径是否位于输出目录内"""
        try:
            path.relative_to(self.output_dir)
            return True
        except ValueError:
            return False

    def _apply_naming_mode(self, dest_path: Path, file_path: Path) -> Path:
        """
        应用命名模式生成最终目标路径

        Args:
            dest_path: 原始目标路径
            file_path: 源文件路径

        Returns:
            应用命名模式后的目标路径
        """
        if self.naming_mode == "original":
            # 保持原文件名
            return dest_path

        elif self.naming_mode == "sequence":
            # 添加序号处理冲突
            return self._add_sequence_suffix(dest_path)

        elif self.naming_mode == "timestamp":
            # 使用时间戳
            return self._add_timestamp(dest_path)

        elif self.naming_mode == "prefix":
            # 添加自定义前缀
            return self._add_custom_prefix(dest_path)

        elif self.naming_mode == "suffix":
            # 添加自定义后缀
            return self._add_custom_suffix(dest_path)

        elif self.naming_mode == "use_first_dir":
            # 使用第一层目录名作为文件名
            return self._use_first_dir_as_name(dest_path, file_path)

        else:
            return dest_path

    def _add_sequence_suffix(self, dest_path: Path) -> Path:
        """添加序号后缀来处理文件名冲突"""
        base_name = dest_path.stem
        extension = dest_path.suffix
        parent = dest_path.parent

        # 使用计数器
        counter_key = str(parent / base_name)
        self.file_counters[counter_key] += 1
        sequence = self.file_counters[counter_key]

        new_name = f"{base_name}_{sequence}{extension}"
        return parent / new_name

    def _add_timestamp(self, dest_path: Path) -> Path:
        """添加时间戳到文件名"""
        base_name = dest_path.stem
        extension = dest_path.suffix
        parent = dest_path.parent

        # 使用当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{base_name}_{timestamp}{extension}"
        return parent / new_name

    def _add_custom_prefix(self, dest_path: Path) -> Path:
        """添加自定义前缀到文件名"""
        base_name = dest_path.stem
        extension = dest_path.suffix
        parent = dest_path.parent

        new_name = f"{self.custom_prefix}{base_name}{extension}"
        return parent / new_name

    def _add_custom_suffix(self, dest_path: Path) -> Path:
        """添加自定义后缀到文件名（在扩展名之前）"""
        base_name = dest_path.stem
        extension = dest_path.suffix
        parent = dest_path.parent

        new_name = f"{base_name}{self.custom_suffix}{extension}"
        return parent / new_name

    def _use_first_dir_as_name(self, dest_path: Path, file_path: Path) -> Path:
        """使用第一层目录名作为文件名（保留原文件扩展名）"""
        extension = dest_path.suffix
        parent = dest_path.parent

        # 获取第一层目录名
        try:
            relative_path = file_path.relative_to(self.input_dir)
            parts = relative_path.parts
            if len(parts) > 1:
                # 文件在子目录中，使用第一层目录名作为文件名
                first_dir = parts[0]
                new_name = f"{first_dir}{extension}"
            else:
                # 文件在输入目录根目录，保持原名
                new_name = dest_path.name
        except ValueError:
            # 如果无法计算相对路径，保持原名
            new_name = dest_path.name

        return parent / new_name

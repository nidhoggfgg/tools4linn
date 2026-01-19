"""
文件删除工具
支持多种匹配模式删除文件，删除前需要确认
"""

from pathlib import Path
from typing import List, Optional, Callable, Tuple
import re
import logging


class FileDeleter:
    """文件删除器，支持多种匹配模式"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化文件删除器

        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.match_modes = [
            "关键字匹配",
            "前缀匹配",
            "后缀匹配",
            "扩展名匹配",
            "正则表达式匹配",
        ]

    def find_files(
        self,
        root_dir: str,
        match_mode: str,
        pattern: str,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        recursive: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Tuple[List[Path], List[str]]:
        """
        查找符合条件的文件

        Args:
            root_dir: 根目录
            match_mode: 匹配模式
            pattern: 匹配模式（关键字/前缀/后缀/扩展名/正则表达式）
            min_size: 最小文件大小（MB）
            max_size: 最大文件大小（MB）
            recursive: 是否递归搜索子目录
            progress_callback: 进度回调函数 (current, total)

        Returns:
            (匹配的文件列表, 错误信息列表)
        """
        root_path = Path(root_dir)
        if not root_path.exists():
            raise ValueError(f"目录不存在: {root_dir}")

        if not root_path.is_dir():
            raise ValueError(f"路径不是目录: {root_dir}")

        matched_files = []
        errors = []

        # 获取所有文件
        if recursive:
            all_files = list(root_path.rglob("*"))
        else:
            all_files = list(root_path.glob("*"))

        # 过滤出文件（排除目录）
        all_files = [f for f in all_files if f.is_file()]

        total = len(all_files)

        self.logger.info(f"开始扫描，共找到 {total} 个文件")

        for idx, file_path in enumerate(all_files):
            try:
                # 进度回调
                if progress_callback:
                    progress_callback(idx + 1, total)

                # 检查文件是否匹配
                if self._matches(file_path, match_mode, pattern, min_size, max_size):
                    matched_files.append(file_path)
                    self.logger.debug(f"匹配文件: {file_path}")

            except Exception as e:
                error_msg = f"处理文件 {file_path} 时出错: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)

        self.logger.info(f"扫描完成，共找到 {len(matched_files)} 个匹配文件")

        return matched_files, errors

    def _matches(
        self,
        file_path: Path,
        match_mode: str,
        pattern: str,
        min_size: Optional[int],
        max_size: Optional[int],
    ) -> bool:
        """
        检查文件是否匹配条件

        Args:
            file_path: 文件路径
            match_mode: 匹配模式
            pattern: 匹配模式
            min_size: 最小文件大小（MB）
            max_size: 最大文件大小（MB）

        Returns:
            是否匹配
        """
        # 大小检查（所有模式都支持）
        if min_size is not None or max_size is not None:
            try:
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                if min_size is not None and file_size_mb < min_size:
                    return False
                if max_size is not None and file_size_mb > max_size:
                    return False
            except Exception as e:
                self.logger.warning(f"无法获取文件大小 {file_path}: {e}")
                return False

        # 根据匹配模式检查
        if match_mode == "关键字匹配":
            return self._match_keyword(file_path, pattern)
        elif match_mode == "前缀匹配":
            return self._match_prefix(file_path, pattern)
        elif match_mode == "后缀匹配":
            return self._match_suffix(file_path, pattern)
        elif match_mode == "扩展名匹配":
            return self._match_extension(file_path, pattern)
        elif match_mode == "正则表达式匹配":
            return self._match_regex(file_path, pattern)
        else:
            self.logger.warning(f"未知的匹配模式: {match_mode}")
            return False

    def _match_keyword(self, file_path: Path, keyword: str) -> bool:
        """关键字匹配"""
        return keyword.lower() in file_path.name.lower()

    def _match_prefix(self, file_path: Path, prefix: str) -> bool:
        """前缀匹配"""
        return file_path.name.lower().startswith(prefix.lower())

    def _match_suffix(self, file_path: Path, suffix: str) -> bool:
        """后缀匹配（不包含扩展名）"""
        # 如果后缀以点开头，从完整文件名匹配
        if suffix.startswith("."):
            return file_path.name.lower().endswith(suffix.lower())
        # 否则从文件名（不含扩展名）匹配
        return file_path.stem.lower().endswith(suffix.lower())

    def _match_extension(self, file_path: Path, extensions: str) -> bool:
        """扩展名匹配"""
        ext_list = [ext.strip().lower() for ext in extensions.split(",")]
        file_ext = file_path.suffix.lower()

        # 标准化扩展名（确保有点号）
        for ext in ext_list:
            if not ext.startswith("."):
                ext = "." + ext
            if file_ext == ext:
                return True
        return False

    def _match_regex(self, file_path: Path, pattern: str) -> bool:
        """正则表达式匹配"""
        try:
            regex = re.compile(pattern)
            return bool(regex.search(file_path.name))
        except re.error as e:
            self.logger.error(f"无效的正则表达式 '{pattern}': {e}")
            return False

    def delete_files(
        self,
        files: List[Path],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Tuple[int, List[str]]:
        """
        删除文件列表

        Args:
            files: 要删除的文件列表
            progress_callback: 进度回调函数 (current, total)

        Returns:
            (成功删除的文件数, 错误信息列表)
        """
        success_count = 0
        errors = []

        total = len(files)
        self.logger.info(f"开始删除 {total} 个文件")

        for idx, file_path in enumerate(files):
            try:
                # 进度回调
                if progress_callback:
                    progress_callback(idx + 1, total)

                # 删除文件
                file_path.unlink()
                success_count += 1
                self.logger.info(f"已删除: {file_path}")

            except Exception as e:
                error_msg = f"删除文件 {file_path} 失败: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)

        self.logger.info(f"删除完成，成功删除 {success_count} 个文件，失败 {len(errors)} 个")

        return success_count, errors

    def get_match_description(self, match_mode: str) -> str:
        """
        获取匹配模式的说明

        Args:
            match_mode: 匹配模式

        Returns:
            模式说明
        """
        descriptions = {
            "关键字匹配": "文件名包含指定关键字（不区分大小写）",
            "前缀匹配": "文件名以指定文本开头（不区分大小写）",
            "后缀匹配": "文件名以指定文本结尾（不区分大小写，不含扩展名）",
            "扩展名匹配": "文件扩展名匹配，多个扩展名用逗号分隔（如: pdf,doc,txt）",
            "正则表达式匹配": "使用正则表达式匹配文件名",
        }
        return descriptions.get(match_mode, "未知模式")

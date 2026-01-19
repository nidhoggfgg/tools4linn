"""
文件删除工具控制器
处理UI与核心逻辑之间的交互
"""

import logging
from typing import Optional, Callable, List, Tuple
from pathlib import Path

from toolkits.file.file_deleter import FileDeleter


class FileDeleterController:
    """文件删除工具控制器"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化控制器

        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.deleter = FileDeleter(logger)
        self.processing = False

        # 回调函数
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self.log_callback: Optional[Callable[[str], None]] = None
        self.complete_callback: Optional[Callable[[bool, str], None]] = None

    def set_callbacks(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        complete_callback: Optional[Callable[[bool, str], None]] = None,
    ):
        """
        设置回调函数

        Args:
            progress_callback: 进度回调 (progress, message)
            log_callback: 日志回调 (message)
            complete_callback: 完成回调 (success, message)
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.complete_callback = complete_callback

    def get_processing_status(self) -> bool:
        """
        获取处理状态

        Returns:
            是否正在处理
        """
        return self.processing

    def get_match_modes(self) -> List[str]:
        """
        获取支持的匹配模式

        Returns:
            匹配模式列表
        """
        return self.deleter.match_modes

    def get_match_description(self, match_mode: str) -> str:
        """
        获取匹配模式说明

        Args:
            match_mode: 匹配模式

        Returns:
            模式说明
        """
        return self.deleter.get_match_description(match_mode)

    def preview_files(
        self,
        root_dir: str,
        match_mode: str,
        pattern: str,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        recursive: bool = True,
    ) -> Tuple[bool, str, List[Path], List[str]]:
        """
        预览将要删除的文件

        Args:
            root_dir: 根目录
            match_mode: 匹配模式
            pattern: 匹配模式
            min_size: 最小文件大小（MB）
            max_size: 最大文件大小（MB）
            recursive: 是否递归搜索

        Returns:
            (success, message, matched_files, errors)
        """
        try:
            # 验证输入
            if not root_dir:
                return False, "请选择要搜索的目录", [], []

            if not pattern:
                return False, "请输入匹配模式", [], []

            # 更新进度
            if self.progress_callback:
                self.progress_callback(0, "开始扫描文件...")

            if self.log_callback:
                self.log_message(f"开始扫描目录: {root_dir}")
                self.log_message(f"匹配模式: {match_mode}")
                self.log_message(f"匹配条件: {pattern}")

            # 查找文件
            def progress_func(current, total):
                if self.progress_callback:
                    progress = current / total if total > 0 else 0
                    self.progress_callback(progress, f"扫描中... {current}/{total}")

            matched_files, errors = self.deleter.find_files(
                root_dir=root_dir,
                match_mode=match_mode,
                pattern=pattern,
                min_size=min_size,
                max_size=max_size,
                recursive=recursive,
                progress_callback=progress_func,
            )

            # 日志输出
            if self.log_callback:
                if matched_files:
                    self.log_message(f"找到 {len(matched_files)} 个匹配文件:")
                    for file_path in matched_files[:20]:  # 只显示前20个
                        self.log_message(f"  - {file_path}")
                    if len(matched_files) > 20:
                        self.log_message(f"  ... 还有 {len(matched_files) - 20} 个文件")
                else:
                    self.log_message("未找到匹配的文件")

                if errors:
                    self.log_message(f"扫描过程中发生 {len(errors)} 个错误:")
                    for error in errors[:5]:  # 只显示前5个错误
                        self.log_message(f"  错误: {error}")

            # 完成回调
            if self.progress_callback:
                self.progress_callback(1.0, "扫描完成")

            message = f"找到 {len(matched_files)} 个匹配文件"
            if errors:
                message += f"，{len(errors)} 个错误"

            return True, message, matched_files, errors

        except ValueError as e:
            error_msg = f"参数错误: {str(e)}"
            if self.log_callback:
                self.log_message(error_msg)
            return False, error_msg, [], []
        except Exception as e:
            error_msg = f"扫描失败: {str(e)}"
            if self.log_callback:
                self.log_message(error_msg)
            self.logger.exception("预览文件时发生错误")
            return False, error_msg, [], []

    def delete_files(
        self,
        files: List[Path],
    ) -> Tuple[bool, str]:
        """
        删除文件

        Args:
            files: 要删除的文件列表

        Returns:
            (success, message)
        """
        try:
            if not files:
                return False, "没有要删除的文件"

            self.processing = True

            # 更新进度
            if self.progress_callback:
                self.progress_callback(0, "开始删除文件...")

            if self.log_callback:
                self.log_message(f"开始删除 {len(files)} 个文件...")

            # 删除文件
            def progress_func(current, total):
                if self.progress_callback:
                    progress = current / total if total > 0 else 0
                    self.progress_callback(progress, f"删除中... {current}/{total}")

            success_count, errors = self.deleter.delete_files(
                files=files,
                progress_callback=progress_func,
            )

            # 日志输出
            if self.log_callback:
                self.log_message(f"成功删除 {success_count} 个文件")
                if errors:
                    self.log_message(f"删除失败的文件:")
                    for error in errors[:5]:  # 只显示前5个错误
                        self.log_message(f"  错误: {error}")

            # 完成回调
            if self.progress_callback:
                self.progress_callback(1.0, "删除完成")

            message = f"成功删除 {success_count} 个文件"
            if errors:
                message += f"，{len(errors)} 个文件删除失败"

            return True, message

        except Exception as e:
            error_msg = f"删除失败: {str(e)}"
            if self.log_callback:
                self.log_message(error_msg)
            self.logger.exception("删除文件时发生错误")
            return False, error_msg
        finally:
            self.processing = False

    def log_message(self, message: str):
        """发送日志消息"""
        if self.log_callback:
            self.log_callback(message)

import logging
from pathlib import Path
from typing import Optional, Callable, List
import re

from toolkits.file.file_extractor import FileExtractor
from toolkits.utils.file_filter import (
    FileFilterStrategy,
    NameIncludeStrategy,
    NamePatternStrategy,
    ExtensionStrategy,
    SizeStrategy,
    DirectoryStrategy,
)


class FileExtractorController:
    """文件提取器控制器 - 处理业务逻辑"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.processing = False
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self.log_callback: Optional[Callable[[str], None]] = None
        self.complete_callback: Optional[Callable[[bool, str], None]] = None

    def set_callbacks(
        self,
        progress_callback: Callable[[float, str], None],
        log_callback: Callable[[str], None],
        complete_callback: Callable[[bool, str], None],
    ):
        """设置回调函数"""
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.complete_callback = complete_callback

    def get_processing_status(self) -> bool:
        """获取处理状态"""
        return self.processing

    def _log(self, message: str):
        """发送日志消息"""
        if self.log_callback:
            self.log_callback(message)
        self.logger.info(message)

    def _update_progress(self, progress: float, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(progress, message)

    def _complete(self, success: bool, message: str):
        """完成处理"""
        self.processing = False
        if self.complete_callback:
            self.complete_callback(success, message)

    def start_extraction(
        self,
        input_dir: str,
        output_dir: str,
        filter_enabled: bool,
        filter_mode: str,
        pattern: str,
        overwrite: bool,
        organize_mode: str = "扁平化",
        naming_mode: str = "保持原文件名",
        custom_prefix: str = "",
        custom_suffix: str = "",
    ):
        """开始提取文件"""
        if self.processing:
            self._log("已有任务在处理中")
            return

        self.processing = True
        self._update_progress(0, "准备处理...")

        try:
            # 验证输入
            input_path = Path(input_dir)
            output_path = Path(output_dir)

            if not input_path.exists():
                self._complete(False, f"输入目录不存在: {input_dir}")
                return

            if not output_path.parent.exists():
                self._complete(False, f"输出目录的父目录不存在: {output_dir}")
                return

            # 创建文件过滤策略
            filter_strategy = None
            if filter_enabled:
                filter_strategy = self._create_filter_strategy(filter_mode, pattern)
                if filter_strategy is None:
                    self._complete(False, f"无效的过滤模式或参数: {filter_mode}")
                    return

            self._update_progress(0.1, "创建提取器...")

            # 映射组织模式
            organize_by_map = {
                "扁平化": "flat",
                "按第一层目录分组": "first_dir",
            }
            organize_by = organize_by_map.get(organize_mode, "flat")

            # 映射命名模式
            naming_mode_map = {
                "保持原文件名": "original",
                "添加序号": "sequence",
                "使用时间戳": "timestamp",
                "添加自定义前缀": "prefix",
                "添加自定义后缀": "suffix",
                "使用第一层目录名": "use_first_dir",
            }
            naming_mode = naming_mode_map.get(naming_mode, "original")

            # 创建提取器
            extractor = FileExtractor(
                logger=self.logger,
                input_dir=input_path,
                output_dir=output_path,
                file_filter_strategy=filter_strategy,
                overwrite=overwrite,
                organize_by=organize_by,
                naming_mode=naming_mode,
                custom_prefix=custom_prefix,
                custom_suffix=custom_suffix,
            )

            self._update_progress(0.2, "开始提取文件...")

            # 提取文件
            result = extractor.extract_files()

            # 构建结果消息
            message = (
                f"提取完成!\n"
                f"总计: {result['total_count']} 个文件\n"
                f"成功: {result['success_count']} 个文件\n"
                f"跳过: {result['skipped_count']} 个文件\n"
                f"失败: {result['error_count']} 个文件"
            )

            self._update_progress(1.0, "提取完成!")
            self._complete(True, message)

        except Exception as e:
            self._log(f"处理过程中发生错误: {str(e)}")
            self._complete(False, f"处理失败: {str(e)}")

    def _create_filter_strategy(
        self, filter_mode: str, pattern: str
    ) -> Optional[FileFilterStrategy]:
        """根据模式和模式字符串创建过滤策略"""
        if not pattern:
            return None

        try:
            if filter_mode == "包含模式":
                return NameIncludeStrategy(pattern)

            elif filter_mode == "正则模式":
                return NamePatternStrategy(pattern)

            elif filter_mode == "扩展名模式":
                extensions = [ext.strip() for ext in pattern.split(",")]
                return ExtensionStrategy(extensions)

            elif filter_mode == "大小模式":
                # 解析大小限制，格式: "min-max" 或 "min" 或 "-max"
                min_size = None
                max_size = None

                if "-" in pattern:
                    parts = pattern.split("-")
                    if parts[0]:
                        min_size = int(float(parts[0]) * 1024 * 1024)  # MB to bytes
                    if parts[1]:
                        max_size = int(float(parts[1]) * 1024 * 1024)  # MB to bytes
                elif pattern.startswith("-"):
                    max_size = int(float(pattern[1:]) * 1024 * 1024)
                else:
                    min_size = int(float(pattern) * 1024 * 1024)

                return SizeStrategy(min_size=min_size, max_size=max_size)

            elif filter_mode == "目录模式":
                # 目录路径包含模式
                return DirectoryStrategy(include_dirs=[pattern])

            else:
                return None

        except Exception as e:
            self._log(f"创建过滤策略失败: {str(e)}")
            return None

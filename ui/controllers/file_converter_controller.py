"""
文件格式转换工具控制器
处理UI与核心逻辑之间的交互
"""

import logging
from typing import Optional, Callable, List, Tuple, Dict
from pathlib import Path

from toolkits.file.converter import ConverterManager, ConversionResult
from toolkits.utils.file_filter import (
    FileFilterStrategy,
    ExtensionStrategy,
    NameIncludeStrategy,
    NamePatternStrategy,
)


class FileConverterController:
    """文件格式转换工具控制器"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化控制器

        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.manager = ConverterManager(logger)
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

    def get_supported_conversions(self) -> Dict[str, List[str]]:
        """
        获取支持的转换类型

        Returns:
            {输入格式: [输出格式列表]}
        """
        return self.manager.get_supported_conversions()

    def get_conversion_options(self, input_format: str, output_format: str) -> Dict[str, any]:
        """
        获取转换选项（用于 UI 动态显示）

        Args:
            input_format: 输入格式
            output_format: 输出格式

        Returns:
            选项字典
        """
        options = {}

        # 图片转换选项
        input_fmt = input_format.upper().lstrip(".")
        output_fmt = output_format.upper().lstrip(".")

        if output_fmt in ["JPEG", "JPG", "WEBP"]:
            options["quality"] = {
                "type": "int",
                "label": "图片质量",
                "default": 95,
                "min": 1,
                "max": 100,
                "description": "1-100，值越大质量越高",
            }

        return options

    def find_files(
        self,
        root_dir: str,
        match_mode: str,
        pattern: str,
        recursive: bool = True,
    ) -> Tuple[bool, str, List[Path]]:
        """
        查找符合条件的文件

        Args:
            root_dir: 根目录
            match_mode: 匹配模式
            pattern: 匹配条件
            recursive: 是否递归搜索

        Returns:
            (success, message, matched_files)
        """
        try:
            # 验证输入
            if not root_dir:
                return False, "请选择要搜索的目录", []

            if not pattern:
                return False, "请输入匹配条件", []

            # 更新进度
            if self.progress_callback:
                self.progress_callback(0, "开始扫描文件...")

            if self.log_callback:
                self._log_message(f"开始扫描目录: {root_dir}")
                self._log_message(f"匹配模式: {match_mode}")
                self._log_message(f"匹配条件: {pattern}")

            # 创建过滤策略
            filter_strategy = self._create_filter_strategy(match_mode, pattern)

            # 查找文件
            root_path = Path(root_dir)
            if recursive:
                all_files = list(root_path.rglob("*"))
            else:
                all_files = list(root_path.glob("*"))

            # 过滤文件
            matched_files = []
            for file_path in all_files:
                if file_path.is_file():
                    if filter_strategy is None or filter_strategy.should_include(
                        file_path
                    ):
                        matched_files.append(file_path)

            # 日志输出
            if self.log_callback:
                if matched_files:
                    self._log_message(f"找到 {len(matched_files)} 个匹配文件:")
                    for file_path in matched_files[:20]:  # 只显示前20个
                        self._log_message(f"  - {file_path}")
                    if len(matched_files) > 20:
                        self._log_message(f"  ... 还有 {len(matched_files) - 20} 个文件")
                else:
                    self._log_message("未找到匹配的文件")

            # 完成回调
            if self.progress_callback:
                self.progress_callback(1.0, "扫描完成")

            message = f"找到 {len(matched_files)} 个匹配文件"

            return True, message, matched_files

        except ValueError as e:
            error_msg = f"参数错误: {str(e)}"
            if self.log_callback:
                self._log_message(error_msg)
            return False, error_msg, []
        except Exception as e:
            error_msg = f"扫描失败: {str(e)}"
            if self.log_callback:
                self._log_message(error_msg)
            self.logger.exception("扫描文件时发生错误")
            return False, error_msg, []

    def convert_files(
        self,
        files: List[Path],
        output_format: str,
        output_mode: str = "same_dir",
        output_dir: Optional[str] = None,
        conversion_options: Optional[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        转换文件

        Args:
            files: 要转换的文件列表
            output_format: 输出格式
            output_mode: 输出模式
            output_dir: 输出目录（output_mode="unified" 时使用）
            conversion_options: 转换选项

        Returns:
            (success, message)
        """
        try:
            if not files:
                return False, "没有要转换的文件"

            if output_mode == "unified" and not output_dir:
                return False, "请指定输出目录"

            self.processing = True

            # 更新进度
            if self.progress_callback:
                self.progress_callback(0, "开始转换文件...")

            if self.log_callback:
                self._log_message(f"开始转换 {len(files)} 个文件...")
                self._log_message(f"目标格式: {output_format}")
                self._log_message(f"输出模式: {output_mode}")

            # 准备转换选项
            options = conversion_options or {}

            # 转换文件
            def progress_func(current, total):
                if self.progress_callback:
                    progress = current / total if total > 0 else 0
                    self.progress_callback(progress, f"转换中... {current}/{total}")

            output_path = Path(output_dir) if output_dir else None
            results, errors = self.manager.batch_convert(
                files=files,
                output_format=output_format,
                output_dir=output_path,
                output_mode=output_mode,
                progress_callback=progress_func,
                **options,
            )

            # 统计结果
            success_count = sum(1 for r in results if r.success)

            # 日志输出
            if self.log_callback:
                self._log_message(f"成功转换 {success_count} 个文件")
                if errors:
                    self._log_message(f"转换失败的文件:")
                    for error in errors[:5]:  # 只显示前5个错误
                        self._log_message(f"  错误: {error}")

            # 完成回调
            if self.progress_callback:
                self.progress_callback(1.0, "转换完成")

            message = f"成功转换 {success_count} 个文件"
            if errors:
                message += f"，{len(errors)} 个文件转换失败"

            return True, message

        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            if self.log_callback:
                self._log_message(error_msg)
            self.logger.exception("转换文件时发生错误")
            return False, error_msg
        finally:
            self.processing = False

    def _create_filter_strategy(
        self, match_mode: str, pattern: str
    ) -> Optional[FileFilterStrategy]:
        """根据模式和模式字符串创建过滤策略"""
        if not pattern:
            return None

        try:
            if match_mode == "扩展名匹配":
                extensions = [ext.strip() for ext in pattern.split(",")]
                return ExtensionStrategy(extensions)

            elif match_mode == "关键字匹配":
                return NameIncludeStrategy(pattern)

            elif match_mode == "正则表达式匹配":
                return NamePatternStrategy(pattern)

            else:
                return None

        except Exception as e:
            self._log_message(f"创建过滤策略失败: {str(e)}")
            return None

    def _log_message(self, message: str):
        """发送日志消息"""
        if self.log_callback:
            self.log_callback(message)

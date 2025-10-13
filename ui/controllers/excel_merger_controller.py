"""
Excel 合并控制器
处理 UI 与后端逻辑的连接，管理异步操作和状态更新
"""

import threading
import queue
import logging
from pathlib import Path
from typing import Optional, Callable, Any

from toolkits.excel.merge_excel import ExcelMerger
from toolkits.utils.naming import (
    FILENAME_STRATEGY,
    DIRECTORY_STRATEGY,
    INDEXED_STRATEGY,
    LAST_TWO_SEGMENTS_STRATEGY,
    NamingStrategy,
    PathSegmentsStrategy,
)
from toolkits.utils.file_filter import (
    NamePatternStrategy,
    SizeStrategy,
    FileFilterStrategy,
)


class ExcelMergerController:
    """Excel 合并控制器类"""

    def __init__(self, ui_page, logger: Optional[logging.Logger] = None):
        """
        初始化控制器

        Args:
            ui_page: Excel 合并页面实例
            logger: 日志记录器
        """
        self.ui_page = ui_page
        self.logger = logger or self._create_logger()

        # 状态管理
        self.is_processing = False
        self.current_merger: Optional[ExcelMerger] = None

        # 消息队列用于线程间通信
        self.message_queue = queue.Queue()

        # 回调函数
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self.log_callback: Optional[Callable[[str], None]] = None
        self.complete_callback: Optional[Callable[[bool, str], None]] = None

    def _create_logger(self) -> logging.Logger:
        """创建日志记录器"""
        logger = logging.getLogger("excel_merger_controller")
        logger.setLevel(logging.INFO)

        # 创建处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def set_callbacks(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        complete_callback: Optional[Callable[[bool, str], None]] = None,
    ):
        """设置回调函数"""
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.complete_callback = complete_callback

    def validate_inputs(self, input_dir: str, output_file: str) -> tuple[bool, str]:
        """
        验证用户输入

        Returns:
            (是否有效, 错误消息)
        """
        # 检查输入目录
        if not input_dir:
            return False, "请选择输入目录"

        input_path = Path(input_dir)
        if not input_path.exists():
            return False, "输入目录不存在"

        if not input_path.is_dir():
            return False, "输入路径不是目录"

        # 检查输出文件
        if not output_file:
            return False, "请选择输出文件位置"

        output_path = Path(output_file)
        if output_path.exists() and not output_path.is_file():
            return False, "输出路径已存在且不是文件"

        # 检查输出目录是否存在
        output_dir = output_path.parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"无法创建输出目录: {e}"

        return True, ""

    def get_naming_strategy(
        self, strategy_name: str, input_dir: Optional[str]
    ) -> NamingStrategy:
        """获取命名策略"""
        if input_dir is not None:
            cwd = Path(input_dir)
        else:
            cwd = None
        strategy_map = {
            "文件名": FILENAME_STRATEGY,
            "目录名": DIRECTORY_STRATEGY,
            "索引编号": INDEXED_STRATEGY,
            "第一层目录名": PathSegmentsStrategy(segments=[0], cwd=cwd),
        }
        return strategy_map.get(strategy_name, FILENAME_STRATEGY)

    def get_filter_strategy(
        self,
        enabled: bool,
        pattern: str = "",
    ) -> Optional[FileFilterStrategy]:
        if not enabled:
            return None

        if pattern.strip():
            try:
                return NamePatternStrategy(pattern.strip())
            except Exception as e:
                self._log_message(f"文件名模式过滤设置错误: {e}")
                return None

    def start_merge(
        self,
        input_dir: str,
        output_file: str,
        naming_strategy: str,
        filter_enabled: bool = False,
        pattern: str = "",
    ):
        """开始合并操作"""
        if self.is_processing:
            self._log_message("合并操作正在进行中，请等待...")
            return

        # 验证输入
        is_valid, error_msg = self.validate_inputs(input_dir, output_file)
        if not is_valid:
            self._log_message(f"输入验证失败: {error_msg}")
            if self.complete_callback:
                self.complete_callback(False, error_msg)
            return

        # 获取策略
        naming_strat = self.get_naming_strategy(naming_strategy, input_dir)
        filter_strat = self.get_filter_strategy(filter_enabled, pattern)

        # 在后台线程中执行合并
        self.is_processing = True
        self._log_message("开始合并 Excel 文件...")

        thread = threading.Thread(
            target=self._merge_excel_files,
            args=(input_dir, output_file, naming_strat, filter_strat),
        )
        thread.daemon = True
        thread.start()

    def _merge_excel_files(
        self,
        input_dir: str,
        output_file: str,
        naming_strategy: NamingStrategy,
        filter_strategy: Optional[FileFilterStrategy],
    ):
        """在后台线程中执行 Excel 合并"""
        try:
            # 创建 Excel 合并器
            self.current_merger = ExcelMerger(
                logger=self.logger,
                input_dir=Path(input_dir),
                output_file=Path(output_file),
                sheet_naming_strategy=naming_strategy,
                file_filter_strategy=filter_strategy,
            )

            # 更新进度
            self._update_progress(0.1, "正在扫描 Excel 文件...")

            # 执行合并
            success_count = self.current_merger.merge_excel()

            # 更新进度
            self._update_progress(1.0, "合并完成！")
            self._log_message(f"成功合并 {success_count} 个文件")

            # 完成回调
            if self.complete_callback:
                self.complete_callback(True, f"成功合并 {success_count} 个文件")

        except Exception as e:
            error_msg = f"合并过程中发生错误: {str(e)}"
            self._log_message(error_msg)
            self.logger.error(error_msg, exc_info=True)

            # 错误回调
            if self.complete_callback:
                self.complete_callback(False, error_msg)

        finally:
            self.is_processing = False
            self.current_merger = None

    def cancel_merge(self):
        """取消合并操作"""
        if self.is_processing and self.current_merger:
            # 这里可以实现取消逻辑
            self._log_message("正在取消合并操作...")
            self.is_processing = False
            self.current_merger = None
            self._log_message("合并操作已取消")

    def _update_progress(self, progress: float, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(progress, message)

    def _log_message(self, message: str):
        """记录日志消息"""
        if self.log_callback:
            self.log_callback(message)
        self.logger.info(message)

    def get_processing_status(self) -> bool:
        """获取处理状态"""
        return self.is_processing

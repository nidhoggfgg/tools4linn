"""
Excel 拆分控制器
管理 UI 与拆分逻辑的衔接、线程与回调
"""

import threading
import logging
from pathlib import Path
from typing import Optional, Callable

from toolkits.excel.split_excel import ExcelSplitter


class ExcelSplitterController:
    """Excel 拆分控制器类"""

    def __init__(self, ui_page, logger: Optional[logging.Logger] = None):
        self.ui_page = ui_page
        self.logger = logger or self._create_logger()

        self.is_processing = False
        self.splitter: Optional[ExcelSplitter] = None

        # 回调
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self.log_callback: Optional[Callable[[str], None]] = None
        self.complete_callback: Optional[Callable[[bool, str], None]] = None

    def _create_logger(self) -> logging.Logger:
        logger = logging.getLogger("excel_splitter_controller")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        return logger

    def set_callbacks(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        complete_callback: Optional[Callable[[bool, str], None]] = None,
    ):
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.complete_callback = complete_callback

    def validate_inputs(self, input_file: str, output_file: Optional[str]) -> tuple[bool, str]:
        if not input_file:
            return False, "请选择输入文件"
        input_path = Path(input_file)
        if not input_path.exists() or not input_path.is_file():
            return False, "输入文件不存在或不是文件"

        if output_file:
            output_path = Path(output_file)
            parent = output_path.parent
            if not parent.exists():
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    return False, f"无法创建输出目录: {e}"
        return True, ""

    def start_split(self, input_file: str, output_file: Optional[str] = None):
        if self.is_processing:
            self._log_message("拆分操作正在进行中，请等待...")
            return

        is_valid, err = self.validate_inputs(input_file, output_file)
        if not is_valid:
            self._log_message(f"输入验证失败: {err}")
            if self.complete_callback:
                self.complete_callback(False, err)
            return

        self.is_processing = True
        self._update_progress(0.05, "开始处理...")

        thread = threading.Thread(
            target=self._do_split,
            args=(input_file, output_file),
        )
        thread.daemon = True
        thread.start()

    def _do_split(self, input_file: str, output_file: Optional[str]):
        try:
            self._update_progress(0.2, "加载工作簿...")
            self.splitter = ExcelSplitter(self.logger)
            out_path = self.splitter.split_by_first_column(input_file, output_file)
            self._update_progress(1.0, "拆分完成！")
            if self.complete_callback:
                self.complete_callback(True, f"处理完成，输出: {out_path}")
        except Exception as e:
            msg = f"拆分过程中发生错误: {e}"
            self._log_message(msg)
            self.logger.error(msg, exc_info=True)
            if self.complete_callback:
                self.complete_callback(False, msg)
        finally:
            self.is_processing = False
            self.splitter = None

    def _update_progress(self, progress: float, message: str):
        if self.progress_callback:
            self.progress_callback(progress, message)

    def _log_message(self, message: str):
        if self.log_callback:
            self.log_callback(message)
        self.logger.info(message)

    def get_processing_status(self) -> bool:
        return self.is_processing



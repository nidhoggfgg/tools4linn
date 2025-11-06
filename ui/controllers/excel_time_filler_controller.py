"""
Excel 时间填充控制器
管理 UI 与时间填充逻辑的衔接、线程与回调
"""

import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable, Dict, Any

from toolkits.excel import ExcelTimeFiller, ExcelHumanLoader
from toolkits.utils import NameGenerator


class ExcelTimeFillerController:
    """Excel 时间填充控制器类"""

    def __init__(self, ui_page, logger: Optional[logging.Logger] = None):
        self.ui_page = ui_page
        self.logger = logger or self._create_logger()

        self.is_processing = False
        self.time_filler: Optional[ExcelTimeFiller] = None
        self.human_loader: Optional[ExcelHumanLoader] = None

        # 回调
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self.log_callback: Optional[Callable[[str], None]] = None
        self.complete_callback: Optional[Callable[[bool, str], None]] = None

    def _create_logger(self) -> logging.Logger:
        logger = logging.getLogger("excel_time_filler_controller")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
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

    def validate_inputs(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """验证输入配置"""
        # 验证模板文件
        if not config.get("template_file"):
            return False, "请选择模板文件"
        template_path = Path(config["template_file"])
        if not template_path.exists() or not template_path.is_file():
            return False, "模板文件不存在或不是文件"

        # 验证人员信息文件
        if not config.get("human_file"):
            return False, "请选择人员信息文件"
        human_path = Path(config["human_file"])
        if not human_path.exists() or not human_path.is_file():
            return False, "人员信息文件不存在或不是文件"

        # 验证名称文件（如果启用）
        if config.get("use_name_col") and config.get("names_file"):
            names_path = Path(config["names_file"])
            if not names_path.exists() or not names_path.is_file():
                return False, "名称文件不存在或不是文件"

        # 验证列配置
        if not config.get("start_time_col"):
            return False, "请指定开始时间列"
        if not config.get("end_time_col"):
            return False, "请指定结束时间列"

        # 验证数字配置
        try:
            data_start_row = int(config.get("data_start_row", 2))
            if data_start_row < 1:
                return False, "数据起始行必须大于等于 1"

            time_offset = int(config.get("time_offset_minutes", 15))
            if time_offset < 0:
                return False, "时间偏移范围不能为负数"

            row_adjust_min = int(config.get("row_adjust_min", -1))
            row_adjust_max = int(config.get("row_adjust_max", 10))
            if row_adjust_min > row_adjust_max:
                return False, "行数调整最小值不能大于最大值"
        except ValueError as e:
            return False, f"数字配置格式错误: {e}"

        return True, ""

    def start_fill(self, config: Dict[str, Any]):
        """开始填充处理"""
        if self.is_processing:
            self._log_message("填充操作正在进行中，请等待...")
            return

        is_valid, err = self.validate_inputs(config)
        if not is_valid:
            self._log_message(f"输入验证失败: {err}")
            if self.complete_callback:
                self.complete_callback(False, err)
            return

        self.is_processing = True
        self._update_progress(0.05, "开始处理...")

        thread = threading.Thread(
            target=self._do_fill,
            args=(config,),
        )
        thread.daemon = True
        thread.start()

    def _do_fill(self, config: Dict[str, Any]):
        """执行填充操作"""
        try:
            # 初始化
            self._update_progress(0.1, "初始化工具...")
            self.time_filler = ExcelTimeFiller(self.logger)
            self.human_loader = ExcelHumanLoader(self.logger)

            # 加载人员信息
            self._update_progress(0.2, "加载人员信息...")
            humans = self.human_loader.load_humans_from_excel(config["human_file"])
            self._log_message(f"加载了 {len(humans)} 条人员信息")

            if not humans:
                raise ValueError("人员信息文件为空")

            # 加载名称生成器（如果需要）
            name_generator = None
            if config.get("use_name_col") and config.get("names_file"):
                self._update_progress(0.3, "加载名称文件...")
                name_generator = NameGenerator(names_file=config["names_file"])
                self._log_message(
                    f"加载了 {name_generator.get_name_count()} 个名称"
                )

            # 准备输出目录
            output_dir = self._prepare_output_dir(config)
            self._log_message(f"输出目录: {output_dir}")

            # 获取时间偏移
            time_offset = config.get("time_offset_minutes", 15)

            # 处理每个人员信息
            total = len(humans)
            for idx, item in enumerate(humans):
                progress = 0.3 + (0.6 * (idx / total))
                self._update_progress(
                    progress, f"处理 {idx + 1}/{total}: {item['human']}..."
                )

                # 计算时间范围
                start_time = datetime.fromisoformat(
                    f"2025-{item['date']} {item['start_time']}:00"
                )
                start_time_range_start = start_time - timedelta(minutes=time_offset)
                start_time_range_end = start_time + timedelta(minutes=time_offset)

                end_time = datetime.fromisoformat(
                    f"2025-{item['date']} {item['end_time']}:00"
                )
                end_time_range_start = end_time - timedelta(minutes=time_offset)
                end_time_range_end = end_time + timedelta(minutes=time_offset)

                # 生成输出文件名
                output_file = output_dir / f"{item['date']}_{item['human']}.xlsx"

                # 填充时间数据
                self.time_filler.fill_time_columns(
                    excel_file=config["template_file"],
                    start_time_col=config["start_time_col"],
                    end_time_col=config["end_time_col"],
                    duration_col=config.get("duration_col"),
                    start_time_range_start_str=start_time_range_start.isoformat(),
                    start_time_range_end_str=start_time_range_end.isoformat(),
                    end_time_range_start_str=end_time_range_start.isoformat(),
                    end_time_range_end_str=end_time_range_end.isoformat(),
                    data_start_row=config.get("data_start_row", 2),
                    name_col=config.get("name_col"),
                    name_generator=name_generator,
                    random_row_adjustment=(
                        config.get("row_adjust_min", -1),
                        config.get("row_adjust_max", 10),
                    ),
                    output_file=output_file,
                )

                self._log_message(f"已生成: {output_file.name}")

            self._update_progress(1.0, "处理完成！")
            self._log_message(f"所有文件已生成到 {output_dir}")

            if self.complete_callback:
                self.complete_callback(
                    True, f"成功处理 {total} 个文件，输出到: {output_dir}"
                )

        except Exception as e:
            msg = f"填充过程中发生错误: {e}"
            self._log_message(msg)
            self.logger.error(msg, exc_info=True)
            if self.complete_callback:
                self.complete_callback(False, msg)
        finally:
            self.is_processing = False
            self.time_filler = None
            self.human_loader = None

    def _prepare_output_dir(self, config: Dict[str, Any]) -> Path:
        """准备输出目录"""
        if config.get("output_dir"):
            output_dir = Path(config["output_dir"])
        else:
            output_dir = Path("filled_excels")

        output_dir.mkdir(exist_ok=True)
        return output_dir

    def _update_progress(self, progress: float, message: str):
        if self.progress_callback:
            self.progress_callback(progress, message)

    def _log_message(self, message: str):
        if self.log_callback:
            self.log_callback(message)
        self.logger.info(message)

    def get_processing_status(self) -> bool:
        return self.is_processing

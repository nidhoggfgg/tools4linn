"""
时间生成器控制器
处理时间生成器的业务逻辑和UI交互
"""

import customtkinter as ctk
from datetime import datetime
from typing import List, Optional

from toolkits.time import TimeGenerator, TimeMode


class TimeGeneratorController:
    """时间生成器控制器"""

    def __init__(self):
        self.generator = TimeGenerator()
        self.result_time_points: List[datetime] = []

    def set_time_range(self, start_time_str: str, end_time_str: str) -> bool:
        """
        设置时间范围

        Args:
            start_time_str: 开始时间字符串
            end_time_str: 结束时间字符串

        Returns:
            是否设置成功
        """
        try:
            # 尝试解析时间字符串
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)

            self.generator.set_time_range(start_time, end_time)
            return True
        except ValueError as e:
            print(f"时间格式错误: {e}")
            return False

    def set_mode(self, mode: str) -> None:
        """
        设置生成模式

        Args:
            mode: 模式字符串 ("fixed_step" 或 "random_step")
        """
        if mode == "fixed_step":
            self.generator.set_mode(TimeMode.FIXED_STEP)
        elif mode == "random_step":
            self.generator.set_mode(TimeMode.RANDOM_STEP)
        else:
            raise ValueError(f"不支持的模式: {mode}")

    def set_point_count(self, count: int) -> bool:
        """
        设置时间点数量

        Args:
            count: 时间点数量

        Returns:
            是否设置成功
        """
        try:
            self.generator.set_point_count(count)
            return True
        except ValueError as e:
            print(f"参数错误: {e}")
            return False

    def set_step_range(self, min_seconds: int, max_seconds: int) -> bool:
        """
        设置步长范围

        Args:
            min_seconds: 最小步长（秒）
            max_seconds: 最大步长（秒）

        Returns:
            是否设置成功
        """
        try:
            self.generator.set_step_range(min_seconds, max_seconds)
            return True
        except ValueError as e:
            print(f"参数错误: {e}")
            return False

    def generate_time_points(self) -> bool:
        """
        生成时间点

        Returns:
            是否生成成功
        """
        try:
            self.result_time_points = self.generator.generate()
            return True
        except Exception as e:
            print(f"生成时间点失败: {e}")
            return False

    def get_formatted_results(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> List[str]:
        """
        获取格式化的结果

        Args:
            format_str: 时间格式字符串，特殊值 "timestamp" 表示Unix时间戳

        Returns:
            格式化的时间点字符串列表
        """
        if not self.result_time_points:
            return []

        if format_str == "timestamp":
            return [str(int(dt.timestamp())) for dt in self.result_time_points]
        else:
            return [dt.strftime(format_str) for dt in self.result_time_points]

    def get_duration_info(self) -> dict:
        """
        获取时间范围信息

        Returns:
            时间范围信息字典
        """
        return self.generator.get_duration_info()

    def export_to_text(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        导出结果为文本格式

        Args:
            format_str: 时间格式字符串

        Returns:
            格式化的文本结果
        """
        if not self.result_time_points:
            return "没有生成的时间点"

        info = self.get_duration_info()
        result_lines = [
            f"时间范围: {info.get('start_time', 'N/A')} 到 {info.get('end_time', 'N/A')}",
            f"总时长: {info.get('total_duration_seconds', 0):.0f} 秒 ({info.get('total_duration_hours', 0):.2f} 小时)",
            f"生成模式: {info.get('mode', 'N/A')}",
            f"时间点数量: {info.get('point_count', 0)}",
            f"输出格式: {format_str}",
            "",
            "生成的时间点:",
            "-" * 50,
        ]

        if format_str == "timestamp":
            for time_point in self.result_time_points:
                result_lines.append(str(int(time_point.timestamp())))
        else:
            for time_point in self.result_time_points:
                result_lines.append(time_point.strftime(format_str))

        return "\n".join(result_lines)

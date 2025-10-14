import random
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Union


class TimeMode(Enum):
    FIXED_STEP = "fixed_step"  # 固定步长模式
    RANDOM_STEP = "random_step"  # 随机步长模式


class TimeGenerator:
    def __init__(
        self,
        start_time: Union[str, datetime, None] = None,
        end_time: Union[str, datetime, None] = None,
        mode: TimeMode = TimeMode.FIXED_STEP,
        point_count: int = 10,
        min_step_seconds: int = 60,
        max_step_seconds: int = 3600,
    ):
        """
        初始化时间生成器

        Args:
            start_time: 开始时间，可以是字符串格式或datetime对象
            end_time: 结束时间，可以是字符串格式或datetime对象
            mode: 时间生成模式
            point_count: 生成的时间点数量
            min_step_seconds: 最小步长（秒）
            max_step_seconds: 最大步长（秒）
        """
        self.mode: TimeMode = mode
        self.point_count: int = point_count
        self.min_step_seconds: int = min_step_seconds  # 最小步长（秒）
        self.max_step_seconds: int = max_step_seconds  # 最大步长（秒）
        if start_time is not None and end_time is not None:
            self.set_time_range(start_time, end_time)
        elif start_time is not None:
            self.set_start_time(start_time)
        elif end_time is not None:
            self.set_end_time(end_time)

    def set_time_range(
        self, start_time: Union[str, datetime], end_time: Union[str, datetime]
    ) -> None:
        """
        设置时间范围

        Args:
            start_time: 开始时间，可以是字符串格式或datetime对象
            end_time: 结束时间，可以是字符串格式或datetime对象
        """
        self.set_start_time(start_time)
        self.set_end_time(end_time)

        if self.start_time is None or self.end_time is None:
            raise ValueError("开始时间或结束时间不能为空")

        if self.start_time >= self.end_time:
            raise ValueError("开始时间必须早于结束时间")

    def set_start_time(self, start_time: Union[str, datetime, None]) -> None:
        """
        设置开始时间
        """
        if isinstance(start_time, str):
            self.start_time = datetime.fromisoformat(start_time)
        else:
            self.start_time = start_time

    def set_end_time(self, end_time: Union[str, datetime, None]) -> None:
        """
        设置结束时间
        """
        if isinstance(end_time, str):
            self.end_time = datetime.fromisoformat(end_time)
        else:
            self.end_time = end_time

    def set_mode(self, mode: TimeMode) -> None:
        """
        设置生成模式

        Args:
            mode: 时间生成模式
        """
        self.mode = mode

    def set_point_count(self, count: int) -> None:
        """
        设置生成的时间点数量

        Args:
            count: 时间点数量
        """
        if count <= 0:
            raise ValueError("时间点数量必须大于0")
        self.point_count = count

    def set_step_range(self, min_seconds: int, max_seconds: int) -> None:
        """
        设置步长范围（仅用于随机步长模式）

        Args:
            min_seconds: 最小步长（秒）
            max_seconds: 最大步长（秒）
        """
        if min_seconds <= 0 or max_seconds <= 0:
            raise ValueError("步长必须大于0")
        if min_seconds > max_seconds:
            raise ValueError("最小步长不能大于最大步长")
        self.min_step_seconds = min_seconds
        self.max_step_seconds = max_seconds

    def generate_fixed_step(self) -> List[datetime]:
        """
        生成固定步长的时间点

        Returns:
            时间点列表
        """
        if not self.start_time or not self.end_time:
            raise ValueError("请先设置时间范围")

        total_duration = self.end_time - self.start_time
        step_duration = total_duration / (self.point_count - 1)

        time_points = []
        current_time = self.start_time

        for _ in range(self.point_count):
            time_points.append(current_time)
            current_time += step_duration

        # 确保最后一个点正好是结束时间
        time_points[-1] = self.end_time

        return time_points

    def generate_random_step(self) -> List[datetime]:
        """
        生成随机步长的时间点

        Returns:
            时间点列表
        """
        if not self.start_time or not self.end_time:
            raise ValueError("请先设置时间范围")

        time_points = [self.start_time]
        current_time = self.start_time

        # 生成前n-1个点
        for i in range(self.point_count - 2):
            # 计算剩余时间和剩余点数
            remaining_time = self.end_time - current_time
            remaining_points = self.point_count - i - 1

            # 计算最大可能的步长
            max_possible_step = remaining_time.total_seconds() / remaining_points
            max_step = min(self.max_step_seconds, max_possible_step)

            # 确保最小步长不超过最大步长
            min_step = min(self.min_step_seconds, max_step)

            # 生成随机步长
            step_seconds = random.uniform(min_step, max_step)
            current_time += timedelta(seconds=step_seconds)
            time_points.append(current_time)

        # 添加结束时间点
        time_points.append(self.end_time)

        return time_points

    def generate(self) -> List[datetime]:
        """
        根据当前设置生成时间点

        Returns:
            时间点列表
        """
        if self.mode == TimeMode.FIXED_STEP:
            return self.generate_fixed_step()
        elif self.mode == TimeMode.RANDOM_STEP:
            return self.generate_random_step()
        else:
            raise ValueError(f"不支持的模式: {self.mode}")

    def generate_with_format(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> List[str]:
        """
        生成格式化的时间点字符串

        Args:
            format_str: 时间格式字符串

        Returns:
            格式化的时间点字符串列表
        """
        time_points = self.generate()
        return [dt.strftime(format_str) for dt in time_points]

    def get_duration_info(self) -> dict:
        """
        获取时间范围信息

        Returns:
            包含时间范围信息的字典
        """
        if not self.start_time or not self.end_time:
            return {}

        duration = self.end_time - self.start_time
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration_seconds": duration.total_seconds(),
            "total_duration_minutes": duration.total_seconds() / 60,
            "total_duration_hours": duration.total_seconds() / 3600,
            "total_duration_days": duration.days,
            "point_count": self.point_count,
            "mode": self.mode.value,
        }

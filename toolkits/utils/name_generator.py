import random
from pathlib import Path
from typing import List, Optional


class NameGenerator:
    """随机名称生成器"""

    def __init__(self, names_file: Optional[Path | str] = None, names: Optional[List[str]] = None):
        """
        初始化名称生成器

        Args:
            names_file: 名称文件路径，每行一个名称
            names: 名称列表，如果提供则不从文件读取
        """
        self.all_names: List[str] = []

        if names is not None:
            self.all_names = names
        elif names_file is not None:
            self.load_names_from_file(names_file)

    def load_names_from_file(self, file_path: Path | str) -> None:
        """
        从文件加载名称列表

        Args:
            file_path: 名称文件路径
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"名称文件不存在: {file_path}")

        self.all_names = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:  # 跳过空行
                    self.all_names.append(name)

        if not self.all_names:
            raise ValueError(f"名称文件为空: {file_path}")

    def generate_names(self, nums: int) -> List[str]:
        """
        生成指定数量的不重复随机名称

        Args:
            nums: 需要生成的名称数量

        Returns:
            名称列表
        """
        if not self.all_names:
            raise ValueError("名称列表为空，请先加载名称")

        if nums <= 0:
            return []

        # 如果需要的数量超过可用名称数量，则重复使用
        if nums > len(self.all_names):
            # 计算需要重复多少次
            repeat_times = (nums // len(self.all_names)) + 1
            # 复制并随机打乱
            extended_names = self.all_names * repeat_times
            random.shuffle(extended_names)
            return extended_names[:nums]

        # 使用 set 确保不重复
        names = set()
        available_names = self.all_names.copy()
        random.shuffle(available_names)

        for name in available_names:
            if len(names) >= nums:
                break
            names.add(name)

        return list(names)

    def add_names(self, names: List[str]) -> None:
        """
        添加名称到列表

        Args:
            names: 要添加的名称列表
        """
        self.all_names.extend(names)

    def get_all_names(self) -> List[str]:
        """获取所有可用的名称"""
        return self.all_names.copy()

    def get_name_count(self) -> int:
        """获取可用名称的数量"""
        return len(self.all_names)

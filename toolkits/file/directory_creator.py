from pathlib import Path
from typing import Union, List, Dict, Optional
import re


class DirectoryCreator:
    """
    一键创建多个多层目录的工具类。

    支持多种易用的语法：
    1. 列表语法：传入路径列表
    2. 字典语法：支持嵌套结构，更直观地表示层级关系
    3. 模板字符串：类似 tree 命令的可视化结构

    Examples:
        >>> creator = DirectoryCreator(base_path="./my_project")

        # 方式1：列表语法
        >>> creator.create_from_list([
        ...     "src/components",
        ...     "src/utils",
        ...     "tests/unit"
        ... ])

        # 方式2：字典语法（推荐，最直观）
        >>> creator.create_from_dict({
        ...     "src": {
        ...         "components": ["Button", "Input"],
        ...         "utils": None,
        ...         "services": ["api", "auth"]
        ...     },
        ...     "tests": ["unit", "integration"]
        ... })

        # 方式3：模板字符串
        >>> creator.create_from_template('''
        ... project/
        ...   src/
        ...     components/
        ...     utils/
        ...   tests/
        ...     unit/
        ... ''')
    """

    def __init__(self, base_path: Union[str, Path] = ".", exist_ok: bool = True):
        """
        初始化目录创建器。

        Args:
            base_path: 基础路径，所有目录都将在此路径下创建
            exist_ok: 如果目录已存在，是否继续（True 不报错，False 会抛出异常）
        """
        self.base_path = Path(base_path)
        self.exist_ok = exist_ok
        self.created_dirs: List[Path] = []

    def create_from_list(self, paths: List[str]) -> List[Path]:
        """
        从路径列表创建目录（最简单的方式）。

        Args:
            paths: 目录路径列表，支持多层路径（如 "a/b/c"）

        Returns:
            创建的目录路径列表

        Examples:
            >>> creator = DirectoryCreator()
            >>> creator.create_from_list([
            ...     "project/src/components",
            ...     "project/src/utils",
            ...     "project/tests/unit",
            ...     "project/tests/integration"
            ... ])
        """
        self.created_dirs = []

        for path_str in paths:
            full_path = self.base_path / path_str
            full_path.mkdir(parents=True, exist_ok=self.exist_ok)
            self.created_dirs.append(full_path)

        return self.created_dirs

    def create_from_dict(
        self,
        structure: Dict[str, Union[None, List, Dict]],
        parent: Optional[Path] = None,
    ) -> List[Path]:
        """
        从字典结构创建目录（推荐方式，最直观）。

        Args:
            structure: 目录结构字典
                - key: 目录名
                - value: None（创建空目录）、List（子目录列表）或 Dict（嵌套结构）
            parent: 父目录路径（递归使用，通常不需要手动指定）

        Returns:
            创建的目录路径列表

        Examples:
            >>> creator = DirectoryCreator()
            >>> creator.create_from_dict({
            ...     "project": {
            ...         "src": {
            ...             "components": ["Button", "Input", "Card"],
            ...             "utils": None,
            ...             "services": {
            ...                 "api": ["users", "posts"],
            ...                 "auth": None
            ...             }
            ...         },
            ...         "tests": ["unit", "integration", "e2e"],
            ...         "docs": None
            ...     }
            ... })
        """
        if parent is None:
            parent = self.base_path
            self.created_dirs = []

        for name, children in structure.items():
            current_path = parent / name
            current_path.mkdir(parents=True, exist_ok=self.exist_ok)
            self.created_dirs.append(current_path)

            if children is None:
                # 空目录，不创建子目录
                continue
            elif isinstance(children, list):
                # 子目录列表
                for child_name in children:
                    child_path = current_path / child_name
                    child_path.mkdir(parents=True, exist_ok=self.exist_ok)
                    self.created_dirs.append(child_path)
            elif isinstance(children, dict):
                # 嵌套字典结构，递归创建
                self.create_from_dict(children, parent=current_path)

        return self.created_dirs

    def create_from_template(self, template: str) -> List[Path]:
        """
        从模板字符串创建目录（可视化方式）。

        支持多种格式：
        - 简单格式：使用缩进表示层级
        - Tree 格式：使用 tree 命令的输出格式（├──, └──, │等）

        Args:
            template: 目录结构模板字符串

        Returns:
            创建的目录路径列表

        Examples:
            >>> creator = DirectoryCreator()

            # 简单缩进格式
            >>> creator.create_from_template('''
            ... project/
            ...   src/
            ...     components/
            ...     utils/
            ...   tests/
            ...     unit/
            ... ''')

            # Tree 命令格式
            >>> creator.create_from_template('''
            ... project/
            ... ├── src/
            ... │   ├── components/
            ... │   └── utils/
            ... └── tests/
            ...     ├── unit/
            ...     └── integration/
            ... ''')
        """
        self.created_dirs = []
        lines = template.strip().split("\n")

        # 解析每一行的缩进级别和目录名
        path_stack: List[str] = []
        last_indent = -1

        for line in lines:
            if not line.strip():
                continue

            # 清理 tree 格式的特殊字符
            cleaned_line = re.sub(r"[├└│─]", "", line)

            # 计算缩进级别（空格或制表符数量）
            indent = len(line) - len(line.lstrip())

            # 提取目录名（去掉末尾的 /）
            dir_name = cleaned_line.strip().rstrip("/")
            if not dir_name:
                continue

            # 根据缩进级别调整路径栈
            if indent > last_indent:
                # 更深一层
                pass
            elif indent == last_indent:
                # 同一层，移除上一个同级目录
                if path_stack:
                    path_stack.pop()
            else:
                # 回到更浅的层级
                # 计算需要回退的层数
                indent_diff = (last_indent - indent) // 2 + 1
                for _ in range(indent_diff):
                    if path_stack:
                        path_stack.pop()

            # 添加当前目录到栈
            path_stack.append(dir_name)

            # 创建完整路径
            full_path = self.base_path / Path(*path_stack)
            full_path.mkdir(parents=True, exist_ok=self.exist_ok)
            self.created_dirs.append(full_path)

            last_indent = indent

        return self.created_dirs

    def get_created_paths(self) -> List[Path]:
        """
        获取已创建的目录路径列表。

        Returns:
            已创建的目录路径列表
        """
        return self.created_dirs.copy()

    def print_tree(self, max_depth: Optional[int] = None):
        """
        以树状结构打印已创建的目录。

        Args:
            max_depth: 最大显示深度，None 表示显示所有层级
        """
        if not self.created_dirs:
            print("未创建任何目录")
            return

        # 按路径排序
        sorted_dirs = sorted(self.created_dirs)

        print(f"\n已创建的目录结构（基于 {self.base_path}）：")
        print(self.base_path)

        for path in sorted_dirs:
            try:
                relative_path = path.relative_to(self.base_path)
                parts = relative_path.parts

                if max_depth is not None and len(parts) > max_depth:
                    continue

                if not parts:
                    continue

                # 计算缩进
                indent = "  " * (len(parts) - 1)
                prefix = "├── "
                print(f"{indent}{prefix}{parts[-1]}/")
            except ValueError:
                # 如果路径不在 base_path 下
                print(f"  {path}/")


# 便捷函数：快速创建目录而不需要实例化类


def create_directories(
    structure: Union[List[str], Dict],
    base_path: Union[str, Path] = ".",
    exist_ok: bool = True,
) -> List[Path]:
    """
    便捷函数：快速创建多个多层目录。

    Args:
        structure: 目录结构，可以是：
            - List[str]: 路径列表
            - Dict: 嵌套字典结构
        base_path: 基础路径
        exist_ok: 目录存在时是否报错

    Returns:
        创建的目录路径列表

    Examples:
        >>> # 使用列表
        >>> create_directories([
        ...     "project/src",
        ...     "project/tests"
        ... ])

        >>> # 使用字典（推荐）
        >>> create_directories({
        ...     "project": {
        ...         "src": ["components", "utils"],
        ...         "tests": None
        ...     }
        ... })
    """
    creator = DirectoryCreator(base_path=base_path, exist_ok=exist_ok)

    if isinstance(structure, list):
        return creator.create_from_list(structure)
    elif isinstance(structure, dict):
        return creator.create_from_dict(structure)
    else:
        raise TypeError(
            f"structure 必须是 list 或 dict 类型，但得到了 {type(structure)}"
        )


def create_directories_from_template(
    template: str, base_path: Union[str, Path] = ".", exist_ok: bool = True
) -> List[Path]:
    """
    便捷函数：从模板字符串创建目录。

    Args:
        template: 目录结构模板字符串
        base_path: 基础路径
        exist_ok: 目录存在时是否报错

    Returns:
        创建的目录路径列表

    Examples:
        >>> create_directories_from_template('''
        ... project/
        ...   src/
        ...     components/
        ...   tests/
        ... ''')
    """
    creator = DirectoryCreator(base_path=base_path, exist_ok=exist_ok)
    return creator.create_from_template(template)

"""
目录创建器控制器
处理目录创建器的业务逻辑和UI交互
"""

from pathlib import Path
from typing import List, Dict, Union, Optional
from toolkits.file.directory_creator import DirectoryCreator


class DirectoryCreatorController:
    """目录创建器控制器"""

    def __init__(self):
        self.creator: Optional[DirectoryCreator] = None
        self.base_path: str = "."
        self.exist_ok: bool = True
        self.create_files: bool = False
        self.created_dirs: List[Path] = []
        self.created_files: List[Path] = []
        self.last_error: Optional[str] = None

    def set_base_path(self, base_path: str) -> bool:
        """
        设置基础路径

        Args:
            base_path: 基础路径字符串

        Returns:
            是否设置成功
        """
        try:
            path = Path(base_path)
            if not path.exists():
                self.last_error = f"路径不存在: {base_path}"
                return False
            if not path.is_dir():
                self.last_error = f"路径不是目录: {base_path}"
                return False
            self.base_path = base_path
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = f"设置路径失败: {e}"
            return False

    def set_exist_ok(self, exist_ok: bool) -> None:
        """
        设置是否允许目录已存在

        Args:
            exist_ok: 是否允许目录已存在
        """
        self.exist_ok = exist_ok

    def set_create_files(self, create_files: bool) -> None:
        """
        设置是否创建文件

        Args:
            create_files: 是否创建文件（在模板模式下）
        """
        self.create_files = create_files

    def create_from_list(self, paths: List[str]) -> bool:
        """
        从路径列表创建目录

        Args:
            paths: 目录路径列表

        Returns:
            是否创建成功
        """
        try:
            if not paths:
                self.last_error = "路径列表为空"
                return False

            self.creator = DirectoryCreator(
                base_path=self.base_path, exist_ok=self.exist_ok
            )
            self.created_dirs = self.creator.create_from_list(paths)
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = f"创建目录失败: {e}"
            return False

    def create_from_template(self, template: str) -> bool:
        """
        从模板字符串创建目录

        Args:
            template: 模板字符串

        Returns:
            是否创建成功
        """
        try:
            if not template.strip():
                self.last_error = "模板字符串为空"
                return False

            self.creator = DirectoryCreator(
                base_path=self.base_path, exist_ok=self.exist_ok
            )
            self.created_dirs = self.creator.create_from_template(
                template, create_files=self.create_files
            )
            self.created_files = self.creator.get_created_files()
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = f"创建目录失败: {e}"
            return False

    def get_created_dirs(self) -> List[str]:
        """
        获取已创建的目录列表

        Returns:
            目录路径字符串列表
        """
        return [str(path) for path in self.created_dirs]

    def get_created_files(self) -> List[str]:
        """
        获取已创建的文件列表

        Returns:
            文件路径字符串列表
        """
        return [str(path) for path in self.created_files]

    def get_summary(self) -> Dict[str, int]:
        """
        获取创建的目录和文件统计信息

        Returns:
            包含统计信息的字典
        """
        return {
            "directories": len(self.created_dirs),
            "files": len(self.created_files),
            "total": len(self.created_dirs) + len(self.created_files),
        }

    def get_last_error(self) -> Optional[str]:
        """
        获取最后一次错误信息

        Returns:
            错误信息，如果没有错误则返回 None
        """
        return self.last_error

    def get_tree_structure(
        self, max_depth: Optional[int] = None, show_files: bool = True
    ) -> str:
        """
        获取已创建目录和文件的树状结构字符串

        Args:
            max_depth: 最大显示深度
            show_files: 是否显示文件

        Returns:
            树状结构字符串
        """
        if not self.created_dirs and not self.created_files:
            return "未创建任何目录或文件"

        # 合并目录和文件列表
        all_paths = []
        for path in self.created_dirs:
            all_paths.append((path, True))  # True 表示是目录

        if show_files:
            for path in self.created_files:
                all_paths.append((path, False))  # False 表示是文件

        # 按路径排序
        all_paths.sort(key=lambda x: x[0])
        base = Path(self.base_path)

        lines = [f"已创建的目录结构（基于 {self.base_path}）：", str(base)]

        for path, is_dir in all_paths:
            try:
                relative_path = path.relative_to(base)
                parts = relative_path.parts

                if max_depth is not None and len(parts) > max_depth:
                    continue

                if not parts:
                    continue

                # 计算缩进
                indent = "  " * (len(parts) - 1)
                prefix = "├── "
                suffix = "/" if is_dir else ""
                lines.append(f"{indent}{prefix}{parts[-1]}{suffix}")
            except ValueError:
                # 如果路径不在 base_path 下
                suffix = "/" if is_dir else ""
                lines.append(f"  {path}{suffix}")

        return "\n".join(lines)

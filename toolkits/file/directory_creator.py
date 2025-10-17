from pathlib import Path
from typing import Union, List, Dict, Optional
import re


def _expand_braces(pattern: str) -> List[str]:
    """
    展开花括号表达式，支持多种模式：
    
    1. 逗号分隔: {a,b,c} -> ['a', 'b', 'c']
    2. 多行分隔: {
                   a
                   b
                   c
                 } -> ['a', 'b', 'c']
    3. 数字范围: {1..5} -> ['1', '2', '3', '4', '5']
    4. 数字范围(补零): {01..10} -> ['01', '02', ..., '10']
    5. 字母范围: {a..z} -> ['a', 'b', ..., 'z']
    6. 嵌套/组合: src/{a,b}/{1..3} -> ['src/a/1', 'src/a/2', ...]
    
    Args:
        pattern: 包含花括号表达式的字符串
        
    Returns:
        展开后的字符串列表
    """
    # 如果没有花括号，直接返回
    if '{' not in pattern or '}' not in pattern:
        return [pattern]
    
    # 找到第一个花括号对
    start = pattern.find('{')
    if start == -1:
        return [pattern]
    
    # 找到匹配的右花括号（需要处理嵌套）
    depth = 0
    end = -1
    for i in range(start, len(pattern)):
        if pattern[i] == '{':
            depth += 1
        elif pattern[i] == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    
    if end == -1:
        # 没有匹配的右花括号，返回原字符串
        return [pattern]
    
    # 提取花括号内容
    prefix = pattern[:start]
    content = pattern[start + 1:end]
    suffix = pattern[end + 1:]
    
    # 如果内容为空，不展开
    if not content:
        return [pattern]
    
    # 检测是否是范围表达式
    range_match = re.match(r'^(\d+|[a-zA-Z])\.\.(\d+|[a-zA-Z])$', content)
    
    if range_match:
        # 范围表达式
        start_val, end_val = range_match.groups()
        
        if start_val.isdigit() and end_val.isdigit():
            # 数字范围
            start_num = int(start_val)
            end_num = int(end_val)
            
            # 检测是否需要补零
            width = len(start_val) if start_val.startswith('0') else 0
            
            if start_num <= end_num:
                if width > 0:
                    expanded = [str(i).zfill(width) for i in range(start_num, end_num + 1)]
                else:
                    expanded = [str(i) for i in range(start_num, end_num + 1)]
            else:
                # 逆序
                if width > 0:
                    expanded = [str(i).zfill(width) for i in range(start_num, end_num - 1, -1)]
                else:
                    expanded = [str(i) for i in range(start_num, end_num - 1, -1)]
        elif start_val.isalpha() and end_val.isalpha() and len(start_val) == 1 and len(end_val) == 1:
            # 字母范围
            if start_val <= end_val:
                expanded = [chr(i) for i in range(ord(start_val), ord(end_val) + 1)]
            else:
                # 逆序
                expanded = [chr(i) for i in range(ord(start_val), ord(end_val) - 1, -1)]
        else:
            # 无法识别的范围，不展开
            expanded = [content]
    else:
        # 逗号分隔的列表或多行列表
        # 需要处理嵌套的花括号
        parts = []
        current = []
        depth = 0
        
        for char in content:
            if char == '{':
                depth += 1
                current.append(char)
            elif char == '}':
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0:
                # 逗号分隔
                part = ''.join(current).strip()
                if part:  # 忽略空白部分
                    parts.append(part)
                current = []
            elif char == '\n' and depth == 0:
                # 换行分隔（支持多行语法）
                part = ''.join(current).strip()
                if part:  # 忽略空白部分
                    parts.append(part)
                current = []
            else:
                current.append(char)
        
        # 处理最后一个部分
        if current:
            part = ''.join(current).strip()
            if part:
                parts.append(part)
        
        expanded = parts
    
    # 生成结果
    results = []
    for item in expanded:
        new_pattern = prefix + item + suffix
        # 递归处理剩余的花括号
        results.extend(_expand_braces(new_pattern))
    
    return results


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
        self.created_files: List[Path] = []

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

    def _merge_multiline_braces(self, template: str) -> str:
        """
        将多行花括号语法合并为单行，以便后续处理。
        
        将类似：
        {
          a
          b
        }
        
        转换为：
        {a
b
c}
        
        Args:
            template: 原始模板字符串
            
        Returns:
            合并后的模板字符串
        """
        lines = template.split("\n")
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 检测是否包含未闭合的花括号
            if '{' in line:
                # 检查这一行的 { 和 } 是否配对
                open_count = line.count('{')
                close_count = line.count('}')
                
                if open_count > close_count:
                    # 有未闭合的花括号，需要收集后续行
                    indent = len(line) - len(line.lstrip())
                    
                    # 找到 { 的位置，提取前缀和后缀
                    brace_start = line.index('{')
                    prefix = line[:brace_start]
                    first_content = line[brace_start + 1:].strip()
                    
                    # 收集花括号内容
                    brace_content = []
                    if first_content and first_content != '}':
                        brace_content.append(first_content)
                    
                    # 继续收集后续行
                    depth = open_count - close_count
                    j = i + 1
                    suffix = ""
                    
                    while j < len(lines) and depth > 0:
                        next_line = lines[j]
                        next_stripped = next_line.strip()
                        
                        # 计算本行的括号变化
                        line_open = next_line.count('{')
                        line_close = next_line.count('}')
                        
                        # 如果这行包含闭合括号
                        if line_close > 0:
                            # 找到最后一个 } 的位置
                            close_pos = next_line.rfind('}')
                            
                            # 提取 } 之前的内容
                            before_close = next_line[:close_pos].strip()
                            if before_close:
                                brace_content.append(before_close)
                            
                            # 提取 } 之后的内容（如 /）
                            suffix = next_line[close_pos + 1:].strip()
                            
                            depth += line_open - line_close
                            
                            if depth <= 0:
                                j += 1
                                break
                        else:
                            # 没有闭合括号，添加整行内容
                            if next_stripped:
                                brace_content.append(next_stripped)
                            depth += line_open
                        
                        j += 1
                    
                    # 重构为单行（用逗号连接，而不是换行符）
                    merged_content = ','.join(brace_content)
                    merged_line = ' ' * indent + prefix + '{' + merged_content + '}' + suffix
                    result_lines.append(merged_line)
                    i = j
                    continue
            
            result_lines.append(line)
            i += 1
        
        return '\n'.join(result_lines)

    def create_from_template(
        self, template: str, create_files: bool = False, expand_braces: bool = True
    ) -> List[Path]:
        """
        从模板字符串创建目录（可视化方式）。

        使用缩进表示层级关系，支持以下特性：
        - 自动检测缩进类型（空格或制表符）
        - 支持注释（# 开头的行）
        - 可选创建文件（带扩展名的条目）
        - 忽略空行
        - 末尾 / 表示强制为目录
        - 花括号展开语法（类似 bash）：
          * {a,b,c} - 逗号分隔列表
          * {           - 多行列表（换行分隔）
              a
              b
            }
          * {1..10} - 数字范围
          * {01..10} - 补零数字范围
          * {a..z} - 字母范围
          * 支持嵌套：src/{a,b}/{1..3}

        Args:
            template: 目录结构模板字符串
            create_files: 是否创建文件（True 时会创建带扩展名的文件，False 时所有条目都作为目录）
            expand_braces: 是否启用花括号展开语法（默认 True）

        Returns:
            创建的目录路径列表（不包含文件）

        Examples:
            >>> creator = DirectoryCreator()

            # 基本缩进格式
            >>> creator.create_from_template('''
            ... project/
            ...   src/
            ...     components/
            ...     utils/
            ...   tests/
            ...     unit/
            ... ''')

            # 支持注释和文件
            >>> creator.create_from_template('''
            ... # 这是项目根目录
            ... project/
            ...   src/
            ...     components/
            ...       Button/
            ...       Input/
            ...     utils/
            ...       helpers.py
            ...       constants.py
            ...   tests/
            ...     # 测试目录
            ...     unit/
            ...     integration/
            ...   README.md
            ... ''', create_files=True)

            # 花括号展开语法 - 快速创建多个同级目录
            >>> creator.create_from_template('''
            ... project/
            ...   src/
            ...     {components,services,utils}/
            ...   tests/
            ...     {unit,integration,e2e}/
            ... ''')
            
            # 多行花括号语法 - 更清晰的可读性
            >>> creator.create_from_template('''
            ... project/
            ...   {
            ...     frontend
            ...     backend
            ...     mobile
            ...   }/
            ...     {src,tests,docs}/
            ... ''')

            # 数字范围展开 - 创建带编号的目录
            >>> creator.create_from_template('''
            ... courses/
            ...   week_{1..12}/
            ...     day_{1..7}/
            ... ''')

            # 补零范围 - 保持统一位数
            >>> creator.create_from_template('''
            ... data/
            ...   batch_{001..100}/
            ... ''')

            # 字母范围
            >>> creator.create_from_template('''
            ... sections/
            ...   section_{A..Z}/
            ... ''')

            # 组合使用 - 创建复杂结构
            >>> creator.create_from_template('''
            ... project/
            ...   {frontend,backend}/
            ...     {src,tests}/
            ...       {models,views,controllers}/
            ... ''')
        """
        self.created_dirs = []
        self.created_files: List[Path] = []
        
        # 预处理：合并多行花括号为单行
        template = self._merge_multiline_braces(template)
        
        lines = template.strip().split("\n")

        # 第一步：解析模板结构，构建带缩进的条目列表
        entries = []  # [(indent, name, is_directory, is_file_ext)]
        for line in lines:
            # 跳过空行和注释行
            if not line.strip() or line.strip().startswith("#"):
                continue

            # 计算缩进级别
            indent = len(line) - len(line.lstrip())
            name = line.strip()
            
            if not name:
                continue

            # 判断是目录还是文件
            is_directory = name.endswith("/")
            name = name.rstrip("/")
            
            # 检测是否有文件扩展名
            has_extension = "." in name and not name.startswith(".")
            
            entries.append((indent, name, is_directory, has_extension))

        # 第二步：递归展开花括号并构建完整路径
        def expand_tree(entries_list, start_idx=0, parent_indent=-1, parent_paths=None):
            """
            递归展开树形结构，处理花括号展开。
            
            Args:
                entries_list: 条目列表
                start_idx: 开始索引
                parent_indent: 父节点的缩进级别
                parent_paths: 父节点的所有路径（考虑展开后的多个路径）
            
            Returns:
                (next_idx, all_paths) - 下一个要处理的索引和所有生成的路径
            """
            if parent_paths is None:
                parent_paths = [[]]
            
            all_generated_paths = []
            idx = start_idx
            
            while idx < len(entries_list):
                indent, name, is_dir_marker, has_ext = entries_list[idx]
                
                # 如果缩进不是子级，返回
                if indent <= parent_indent:
                    break
                
                # 展开当前名称
                if expand_braces and '{' in name and '}' in name:
                    expanded_names = _expand_braces(name)
                else:
                    expanded_names = [name]
                
                # 为每个展开的名称创建路径
                current_level_paths = []
                for parent_path in parent_paths:
                    for expanded_name in expanded_names:
                        new_path = parent_path + [expanded_name]
                        current_level_paths.append(new_path)
                        all_generated_paths.append((new_path, is_dir_marker, has_ext))
                
                # 查看下一行，判断是否有子节点
                if idx + 1 < len(entries_list):
                    next_indent = entries_list[idx + 1][0]
                    if next_indent > indent:
                        # 有子节点，递归处理
                        idx, child_paths = expand_tree(entries_list, idx + 1, indent, current_level_paths)
                        all_generated_paths.extend(child_paths)
                        continue
                
                idx += 1
            
            return idx, all_generated_paths

        # 执行展开
        _, all_paths_info = expand_tree(entries)

        # 第三步：创建目录和文件
        created_paths_set = set()  # 使用集合去重
        
        for path_parts, is_dir_marker, has_ext in all_paths_info:
            if not path_parts:
                continue
            
            # 检测是否为文件
            is_file = create_files and not is_dir_marker and has_ext
            
            full_path = self.base_path / Path(*path_parts)
            
            # 避免重复创建
            if full_path in created_paths_set:
                continue
            created_paths_set.add(full_path)
            
            if is_file:
                # 创建文件
                full_path.parent.mkdir(parents=True, exist_ok=self.exist_ok)
                full_path.touch(exist_ok=self.exist_ok)
                self.created_files.append(full_path)
                # 确保父目录在创建列表中
                if full_path.parent not in self.created_dirs and full_path.parent != self.base_path:
                    self.created_dirs.append(full_path.parent)
            else:
                # 创建目录
                full_path.mkdir(parents=True, exist_ok=self.exist_ok)
                self.created_dirs.append(full_path)

        return self.created_dirs

    def get_created_paths(self) -> List[Path]:
        """
        获取已创建的目录路径列表。

        Returns:
            已创建的目录路径列表
        """
        return self.created_dirs.copy()

    def get_created_files(self) -> List[Path]:
        """
        获取已创建的文件路径列表。

        Returns:
            已创建的文件路径列表
        """
        return self.created_files.copy()

    def get_summary(self) -> Dict[str, int]:
        """
        获取创建的目录和文件统计信息。

        Returns:
            包含统计信息的字典，包括 'directories' 和 'files' 键
        """
        return {
            "directories": len(self.created_dirs),
            "files": len(self.created_files),
            "total": len(self.created_dirs) + len(self.created_files),
        }

    def print_tree(self, max_depth: Optional[int] = None, show_files: bool = True):
        """
        以树状结构打印已创建的目录和文件。

        Args:
            max_depth: 最大显示深度，None 表示显示所有层级
            show_files: 是否显示文件
        """
        if not self.created_dirs and not self.created_files:
            print("未创建任何目录或文件")
            return

        # 合并目录和文件列表
        all_paths = []
        for path in self.created_dirs:
            all_paths.append((path, True))  # True 表示是目录

        if show_files:
            for path in self.created_files:
                all_paths.append((path, False))  # False 表示是文件

        # 按路径排序
        all_paths.sort(key=lambda x: x[0])

        print(f"\n已创建的目录结构（基于 {self.base_path}）：")
        print(self.base_path)

        for path, is_dir in all_paths:
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
                suffix = "/" if is_dir else ""
                print(f"{indent}{prefix}{parts[-1]}{suffix}")
            except ValueError:
                # 如果路径不在 base_path 下
                suffix = "/" if is_dir else ""
                print(f"  {path}{suffix}")


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
    template: str,
    base_path: Union[str, Path] = ".",
    exist_ok: bool = True,
    create_files: bool = False,
    expand_braces: bool = True,
) -> List[Path]:
    """
    便捷函数：从模板字符串创建目录。

    Args:
        template: 目录结构模板字符串
        base_path: 基础路径
        exist_ok: 目录存在时是否报错
        create_files: 是否创建文件（True 时会创建带扩展名的文件）
        expand_braces: 是否启用花括号展开语法（默认 True）

    Returns:
        创建的目录路径列表

    Examples:
        >>> create_directories_from_template('''
        ... project/
        ...   src/
        ...     components/
        ...   tests/
        ... ''')

        >>> create_directories_from_template('''
        ... # 项目结构
        ... project/
        ...   src/
        ...     main.py
        ...     utils.py
        ...   tests/
        ...     test_main.py
        ...   README.md
        ... ''', create_files=True)

        >>> # 使用花括号展开快速创建多个目录
        >>> create_directories_from_template('''
        ... project/
        ...   src/
        ...     {components,services,utils}/
        ...   tests/
        ...     {unit,integration,e2e}/
        ... ''')

        >>> # 使用数字范围创建大量目录
        >>> create_directories_from_template('''
        ... data/
        ...   year_{2020..2024}/
        ...     month_{01..12}/
        ... ''')
    """
    creator = DirectoryCreator(base_path=base_path, exist_ok=exist_ok)
    return creator.create_from_template(template, create_files=create_files, expand_braces=expand_braces)

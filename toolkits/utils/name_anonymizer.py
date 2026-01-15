"""人名脱敏工具"""


def anonymize_name(name: str) -> str:
    """
    对人名进行脱敏处理

    规则：
    - 2个字的名字：保留第一个字，第二个字替换为*
    - 3个字及以上：保留第一个和最后一个字，中间替换为*

    Args:
        name: 原始名字

    Returns:
        脱敏后的名字

    Examples:
        >>> anonymize_name("张三")
        '张*'
        >>> anonymize_name("王小明")
        '王*明'
        >>> anonymize_name("欧阳修明")
        '欧**明'
    """
    if not name or not isinstance(name, str):
        return name

    name = name.strip()
    length = len(name)

    if length == 0:
        return name
    elif length == 1:
        # 单个字，直接返回
        return name
    elif length == 2:
        # 两个字：保留第一个，第二个替换为*
        return name[0] + "*"
    else:
        # 3个字及以上：保留首尾，中间全部替换为*
        return name[0] + "*" * (length - 2) + name[-1]


def anonymize_names(names: list[str]) -> list[str]:
    """
    批量对人名进行脱敏处理

    Args:
        names: 名字列表

    Returns:
        脱敏后的名字列表
    """
    return [anonymize_name(name) for name in names]

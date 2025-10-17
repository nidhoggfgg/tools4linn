"""
测试花括号展开函数的单元测试。
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkits.file.directory_creator import _expand_braces


def test_comma_separated():
    """测试逗号分隔的列表展开"""
    print("\n测试：逗号分隔列表")
    
    tests = [
        ("{a,b,c}", ["a", "b", "c"]),
        ("prefix_{x,y,z}", ["prefix_x", "prefix_y", "prefix_z"]),
        ("{one,two,three}_suffix", ["one_suffix", "two_suffix", "three_suffix"]),
        ("a{1,2,3}b", ["a1b", "a2b", "a3b"]),
    ]
    
    for pattern, expected in tests:
        result = _expand_braces(pattern)
        status = "OK" if result == expected else "FAIL"
        print(f"[{status}] {pattern} -> {result}")
        if result != expected:
            print(f"   期望: {expected}")


def test_numeric_ranges():
    """测试数字范围展开"""
    print("\n测试：数字范围")
    
    tests = [
        ("{1..5}", ["1", "2", "3", "4", "5"]),
        ("file_{1..3}", ["file_1", "file_2", "file_3"]),
        ("v{10..12}", ["v10", "v11", "v12"]),
        ("{5..1}", ["5", "4", "3", "2", "1"]),  # 逆序
    ]
    
    for pattern, expected in tests:
        result = _expand_braces(pattern)
        status = "OK" if result == expected else "FAIL"
        print(f"[{status}] {pattern} -> {result}")
        if result != expected:
            print(f"   期望: {expected}")


def test_padded_numeric_ranges():
    """测试补零数字范围"""
    print("\n测试：补零数字范围")
    
    tests = [
        ("{01..05}", ["01", "02", "03", "04", "05"]),
        ("batch_{001..003}", ["batch_001", "batch_002", "batch_003"]),
        ("{00..10}", ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]),
    ]
    
    for pattern, expected in tests:
        result = _expand_braces(pattern)
        status = "OK" if result == expected else "FAIL"
        print(f"[{status}] {pattern} -> {result}")
        if result != expected:
            print(f"   期望: {expected}")


def test_letter_ranges():
    """测试字母范围展开"""
    print("\n测试：字母范围")
    
    tests = [
        ("{a..e}", ["a", "b", "c", "d", "e"]),
        ("section_{A..C}", ["section_A", "section_B", "section_C"]),
        ("{z..x}", ["z", "y", "x"]),  # 逆序
    ]
    
    for pattern, expected in tests:
        result = _expand_braces(pattern)
        status = "OK" if result == expected else "FAIL"
        print(f"[{status}] {pattern} -> {result}")
        if result != expected:
            print(f"   期望: {expected}")


def test_nested_expansion():
    """测试嵌套展开"""
    print("\n测试：嵌套展开")
    
    tests = [
        ("{a,b}/{1,2}", ["a/1", "a/2", "b/1", "b/2"]),
        ("{x,y}_{1..3}", ["x_1", "x_2", "x_3", "y_1", "y_2", "y_3"]),
        ("{A,B}/{a,b}/{1,2}", [
            "A/a/1", "A/a/2", "A/b/1", "A/b/2",
            "B/a/1", "B/a/2", "B/b/1", "B/b/2"
        ]),
    ]
    
    for pattern, expected in tests:
        result = _expand_braces(pattern)
        status = "OK" if result == expected else "FAIL"
        print(f"[{status}] {pattern} -> {result}")
        if result != expected:
            print(f"   期望: {expected}")
            print(f"   差异: {set(expected) - set(result)} 缺失")


def test_no_expansion():
    """测试不需要展开的情况"""
    print("\n测试：不展开")
    
    tests = [
        ("simple", ["simple"]),
        ("no-braces-here", ["no-braces-here"]),
        ("path/to/dir", ["path/to/dir"]),
    ]
    
    for pattern, expected in tests:
        result = _expand_braces(pattern)
        status = "OK" if result == expected else "FAIL"
        print(f"[{status}] {pattern} -> {result}")
        if result != expected:
            print(f"   期望: {expected}")


def test_complex_examples():
    """测试复杂的实际案例"""
    print("\n测试：复杂案例")
    
    # 微服务命名
    pattern = "{user,product,order}-service"
    result = _expand_braces(pattern)
    expected = ["user-service", "product-service", "order-service"]
    status = "OK" if result == expected else "FAIL"
    print(f"[{status}] 微服务: {pattern}")
    print(f"   结果: {result}")
    
    # API 版本
    pattern = "api/v{1..3}/{users,posts}"
    result = _expand_braces(pattern)
    expected = [
        "api/v1/users", "api/v1/posts",
        "api/v2/users", "api/v2/posts",
        "api/v3/users", "api/v3/posts"
    ]
    status = "OK" if result == expected else "FAIL"
    print(f"[{status}] API 版本: api/v{{1..3}}/{{users,posts}}")
    print(f"   结果: {result}")
    
    # 日期结构（小范围）
    pattern = "{2023..2024}/{01..02}"
    result = _expand_braces(pattern)
    expected = ["2023/01", "2023/02", "2024/01", "2024/02"]
    status = "OK" if result == expected else "FAIL"
    print(f"[{status}] 日期: {{2023..2024}}/{{01..02}}")
    print(f"   结果: {result}")


def test_edge_cases():
    """测试边界情况"""
    print("\n测试：边界情况")
    
    tests = [
        # 单元素
        ("{a}", ["a"]),
        # 空花括号（不展开，保持原样）
        ("{}", ["{}"]),
        # 不匹配的花括号（不展开）
        ("{a,b", ["{a,b"]),
        ("a,b}", ["a,b}"]),
        # 单数字范围
        ("{1..1}", ["1"]),
        # 单字母范围
        ("{a..a}", ["a"]),
    ]
    
    for pattern, expected in tests:
        result = _expand_braces(pattern)
        status = "OK" if result == expected else "FAIL"
        print(f"[{status}] {pattern} -> {result}")
        if result != expected:
            print(f"   期望: {expected}")


if __name__ == "__main__":
    print("=" * 60)
    print("花括号展开函数单元测试")
    print("=" * 60)
    
    test_comma_separated()
    test_numeric_ranges()
    test_padded_numeric_ranges()
    test_letter_ranges()
    test_nested_expansion()
    test_no_expansion()
    test_complex_examples()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


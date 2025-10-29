"""
测试延迟花括号展开功能（树状模式）
"""

import sys
from pathlib import Path

# 设置输出编码
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def simulate_parse_input(input_text):
    """模拟 _parse_input 方法"""
    if not input_text:
        return []

    input_text = input_text.strip()

    # 检测是否包含花括号
    if "{" in input_text and "}" in input_text:
        # 花括号模式：作为单个节点（延迟展开）
        # 标准化多行花括号格式为逗号分隔（更简洁）
        if "\n" in input_text:
            # 多行花括号：提取内容并转换为逗号分隔
            lines = input_text.split("\n")
            items = []
            in_brace = False
            for line in lines:
                line = line.strip()
                if line == "{":
                    in_brace = True
                elif line == "}":
                    in_brace = False
                elif in_brace and line:
                    items.append(line)

            if items:
                # 返回标准化的花括号格式
                return ["{" + ",".join(items) + "}"]
            else:
                # 保留原始输入
                return [input_text]
        else:
            # 单行花括号：直接使用
            return [input_text]
    else:
        # 纯列表模式：按行分割，批量添加
        lines = input_text.split("\n")
        return [line.strip() for line in lines if line.strip()]


def test_delayed_expansion():
    """测试延迟展开模式"""

    print("🎯 测试延迟花括号展开功能\n")
    print("=" * 60)

    # 场景1：多行花括号 -> 单个节点
    print("\n【场景1】多行花括号 -> 单个节点（延迟展开）")
    input1 = """{
a
b
c
}"""
    print(f"输入:\n{input1}")
    result1 = simulate_parse_input(input1)
    print(f"树形视图中的节点: {result1}")
    print(f"节点数量: {len(result1)}")
    assert len(result1) == 1, f"应该返回1个节点，实际返回{len(result1)}个"
    assert result1[0] == "{a,b,c}", f"期望 '{{a,b,c}}', 得到 '{result1[0]}'"
    print("✓ 正确：在树形视图中显示为一个节点 '{a,b,c}'")
    print("  可以在此节点下继续添加子目录，创建时会展开为 a/, b/, c/\n")

    # 场景2：单行花括号 -> 单个节点
    print("【场景2】单行花括号 -> 单个节点（延迟展开）")
    input2 = "{组件,服务,工具}"
    print(f"输入: {input2}")
    result2 = simulate_parse_input(input2)
    print(f"树形视图中的节点: {result2}")
    print(f"节点数量: {len(result2)}")
    assert len(result2) == 1, f"应该返回1个节点，实际返回{len(result2)}个"
    assert result2[0] == "{组件,服务,工具}", (
        f"期望 '{{组件,服务,工具}}', 得到 '{result2[0]}'"
    )
    print("✓ 正确：在树形视图中显示为一个节点 '{组件,服务,工具}'\n")

    # 场景3：纯列表 -> 多个节点
    print("【场景3】纯列表 -> 多个节点（批量添加）")
    input3 = """组件
服务
工具"""
    print(f"输入:\n{input3}")
    result3 = simulate_parse_input(input3)
    print(f"树形视图中的节点: {result3}")
    print(f"节点数量: {len(result3)}")
    assert len(result3) == 3, f"应该返回3个节点，实际返回{len(result3)}个"
    assert result3 == ["组件", "服务", "工具"], (
        f"期望 ['组件', '服务', '工具'], 得到 {result3}"
    )
    print("✓ 正确：在树形视图中创建3个独立节点\n")

    # 场景4：带扩展名的花括号 -> 单个节点
    print("【场景4】带扩展名的花括号 -> 单个节点（延迟展开）")
    input4 = "{main,test,utils}.py"
    print(f"输入: {input4}")
    result4 = simulate_parse_input(input4)
    print(f"树形视图中的节点: {result4}")
    print(f"节点数量: {len(result4)}")
    assert len(result4) == 1, f"应该返回1个节点，实际返回{len(result4)}个"
    assert result4[0] == "{main,test,utils}.py", (
        f"期望 '{{main,test,utils}}.py', 得到 '{result4[0]}'"
    )
    print("✓ 正确：在树形视图中显示为一个节点 '{main,test,utils}.py'\n")

    # 场景5：范围花括号 -> 单个节点
    print("【场景5】范围花括号 -> 单个节点（延迟展开）")
    input5 = "week_{1..5}"
    print(f"输入: {input5}")
    result5 = simulate_parse_input(input5)
    print(f"树形视图中的节点: {result5}")
    print(f"节点数量: {len(result5)}")
    assert len(result5) == 1, f"应该返回1个节点，实际返回{len(result5)}个"
    assert result5[0] == "week_{1..5}", f"期望 'week_{{1..5}}', 得到 '{result5[0]}'"
    print("✓ 正确：在树形视图中显示为一个节点 'week_{1..5}'\n")

    # 场景6：多行花括号（带空行） -> 单个节点
    print("【场景6】多行花括号（带空行）-> 单个节点")
    input6 = """{
README.md

package.json

.gitignore
}"""
    print(f"输入:\n{input6}")
    result6 = simulate_parse_input(input6)
    print(f"树形视图中的节点: {result6}")
    print(f"节点数量: {len(result6)}")
    assert len(result6) == 1, f"应该返回1个节点，实际返回{len(result6)}个"
    print(f"✓ 正确：在树形视图中显示为一个节点 '{result6[0]}'\n")

    print("=" * 60)
    print("✅ 所有测试通过！\n")

    # 使用示例
    print("📖 使用示例：")
    print("-" * 60)
    print("\n示例场景：创建多个微服务，每个都有相同的结构\n")
    print("步骤1: 选择根节点，添加文件夹，输入：")
    print("  {user-service,order-service,product-service}")
    print("\n步骤2: 在树形视图中看到一个节点：")
    print("  📁 {user-service,order-service,product-service}")
    print("\n步骤3: 选择这个节点，继续添加子目录：")
    print("  📁 {user-service,order-service,product-service}/")
    print("    📁 src")
    print("    📁 tests")
    print("    📄 README.md")
    print("\n步骤4: 点击创建，最终生成：")
    print("  📁 user-service/")
    print("    📁 src")
    print("    📁 tests")
    print("    📄 README.md")
    print("  📁 order-service/")
    print("    📁 src")
    print("    📁 tests")
    print("    📄 README.md")
    print("  📁 product-service/")
    print("    📁 src")
    print("    📁 tests")
    print("    📄 README.md")
    print("\n💡 这样就不需要重复创建相同的结构了！")


if __name__ == "__main__":
    test_delayed_expansion()

"""测试设置功能

演示如何使用配置管理器
"""

from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from toolkits.utils.config import get_config_manager


def test_config_manager():
    """测试配置管理器"""
    print("=" * 60)
    print("测试配置管理器")
    print("=" * 60)
    
    # 获取配置管理器实例
    config_manager = get_config_manager()
    
    # 显示配置文件路径
    print(f"\n配置文件路径: {config_manager.config_file}")
    
    # 显示当前配置
    print("\n当前配置:")
    current_config = config_manager.get_all()
    for key, value in current_config.items():
        if key == "api_key" and value:
            # 隐藏 API Key 的大部分内容
            masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
    
    # 测试设置 API Key
    print("\n测试设置 API Key...")
    test_api_key = "sk-test-1234567890abcdef"
    if config_manager.set_api_key(test_api_key):
        print("✅ API Key 设置成功")
        print(f"  保存的 API Key: {test_api_key[:4]}...{test_api_key[-4:]}")
    else:
        print("❌ API Key 设置失败")
    
    # 测试获取 API Key
    print("\n测试获取 API Key...")
    retrieved_key = config_manager.get_api_key()
    if retrieved_key == test_api_key:
        print("✅ API Key 读取成功")
    else:
        print("❌ API Key 读取失败")
    
    # 测试设置其他配置
    print("\n测试批量更新配置...")
    test_config = {
        "api_key": "sk-real-api-key-here",
        "api_base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    }
    if config_manager.update(test_config):
        print("✅ 批量更新配置成功")
    else:
        print("❌ 批量更新配置失败")
    
    # 显示更新后的配置
    print("\n更新后的配置:")
    updated_config = config_manager.get_all()
    for key, value in updated_config.items():
        if key == "api_key" and value:
            masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("- 配置文件会自动保存在用户主目录的 .tools4linn 文件夹中")
    print("- 您可以在应用的设置页面中修改这些配置")
    print("- 所有配置都会自动持久化保存")


if __name__ == "__main__":
    test_config_manager()


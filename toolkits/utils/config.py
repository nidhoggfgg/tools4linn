"""配置管理工具

提供配置文件的读取、保存和管理功能，支持持久化存储。
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """配置管理器类"""

    def __init__(self, config_dir: Optional[Path] = None):
        """初始化配置管理器

        Args:
            config_dir: 配置文件目录，如果为None则使用默认目录
        """
        if config_dir is None:
            # 默认配置文件目录：用户主目录下的 .tools4linn
            self.config_dir = Path.home() / ".tools4linn"
        else:
            self.config_dir = Path(config_dir)

        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self.config_file = self.config_dir / "config.json"

        # 加载配置
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """从文件加载配置

        Returns:
            配置字典
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置文件失败: {e}")
                return self._get_default_config()
        else:
            # 如果配置文件不存在，创建默认配置
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置到文件

        Args:
            config: 配置字典

        Returns:
            保存是否成功
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"保存配置文件失败: {e}")
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置

        Returns:
            默认配置字典
        """
        return {
            "api_key": "",
            "api_base_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
            "theme": "system",
            "language": "zh_CN",
        }

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """设置配置项

        Args:
            key: 配置键
            value: 配置值

        Returns:
            设置是否成功
        """
        self._config[key] = value
        return self._save_config(self._config)

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置

        Returns:
            配置字典
        """
        return self._config.copy()

    def update(self, config: Dict[str, Any]) -> bool:
        """批量更新配置

        Args:
            config: 配置字典

        Returns:
            更新是否成功
        """
        self._config.update(config)
        return self._save_config(self._config)

    def reset(self) -> bool:
        """重置为默认配置

        Returns:
            重置是否成功
        """
        self._config = self._get_default_config()
        return self._save_config(self._config)

    def get_api_key(self) -> str:
        """获取 API Key

        Returns:
            API Key 字符串
        """
        return self.get("api_key", "")

    def set_api_key(self, api_key: str) -> bool:
        """设置 API Key

        Args:
            api_key: API Key 字符串

        Returns:
            设置是否成功
        """
        return self.set("api_key", api_key)

    def get_api_base_url(self) -> str:
        """获取 API Base URL

        Returns:
            API Base URL 字符串
        """
        return self.get("api_base_url", "https://api.deepseek.com")

    def set_api_base_url(self, base_url: str) -> bool:
        """设置 API Base URL

        Args:
            base_url: API Base URL 字符串

        Returns:
            设置是否成功
        """
        return self.set("api_base_url", base_url)

    def get_model(self) -> str:
        """获取模型名称

        Returns:
            模型名称字符串
        """
        return self.get("model", "deepseek-chat")

    def set_model(self, model: str) -> bool:
        """设置模型名称

        Args:
            model: 模型名称字符串

        Returns:
            设置是否成功
        """
        return self.set("model", model)


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例

    Returns:
        ConfigManager 实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

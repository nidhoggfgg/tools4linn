"""设置页面控制器

处理设置页面的业务逻辑，包括配置的读取、保存和验证。
"""

from pathlib import Path
import sys
from typing import Callable, Optional

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from toolkits.utils.config import get_config_manager, ConfigManager


class SettingsController:
    """设置页面控制器类"""

    def __init__(
        self,
        log_callback: Optional[Callable[[str, str], None]] = None,
    ):
        """初始化设置控制器

        Args:
            log_callback: 日志回调函数，接收 (level, message) 参数
        """
        self.config_manager: ConfigManager = get_config_manager()
        self.log_callback = log_callback

    def _log(self, level: str, message: str):
        """输出日志

        Args:
            level: 日志级别 (INFO, SUCCESS, WARNING, ERROR)
            message: 日志消息
        """
        if self.log_callback:
            self.log_callback(level, message)

    def load_settings(self) -> dict:
        """加载所有设置

        Returns:
            设置字典
        """
        try:
            settings = self.config_manager.get_all()
            self._log("INFO", "设置加载成功")
            return settings
        except Exception as e:
            self._log("ERROR", f"加载设置失败: {str(e)}")
            return {}

    def save_api_key(self, api_key: str) -> bool:
        """保存 API Key

        Args:
            api_key: API Key 字符串

        Returns:
            保存是否成功
        """
        try:
            # 验证 API Key（基本验证）
            if not api_key or not api_key.strip():
                self._log("WARNING", "API Key 不能为空")
                return False

            # 保存 API Key
            if self.config_manager.set_api_key(api_key.strip()):
                self._log("SUCCESS", "API Key 保存成功")
                return True
            else:
                self._log("ERROR", "API Key 保存失败")
                return False
        except Exception as e:
            self._log("ERROR", f"保存 API Key 时发生错误: {str(e)}")
            return False

    def get_api_key(self) -> str:
        """获取 API Key

        Returns:
            API Key 字符串
        """
        try:
            return self.config_manager.get_api_key()
        except Exception as e:
            self._log("ERROR", f"获取 API Key 时发生错误: {str(e)}")
            return ""

    def save_api_base_url(self, base_url: str) -> bool:
        """保存 API Base URL

        Args:
            base_url: API Base URL 字符串

        Returns:
            保存是否成功
        """
        try:
            # 验证 URL（基本验证）
            if not base_url or not base_url.strip():
                self._log("WARNING", "API Base URL 不能为空")
                return False

            if not base_url.startswith(("http://", "https://")):
                self._log("WARNING", "API Base URL 必须以 http:// 或 https:// 开头")
                return False

            # 保存 Base URL
            if self.config_manager.set_api_base_url(base_url.strip()):
                self._log("SUCCESS", "API Base URL 保存成功")
                return True
            else:
                self._log("ERROR", "API Base URL 保存失败")
                return False
        except Exception as e:
            self._log("ERROR", f"保存 API Base URL 时发生错误: {str(e)}")
            return False

    def get_api_base_url(self) -> str:
        """获取 API Base URL

        Returns:
            API Base URL 字符串
        """
        try:
            return self.config_manager.get_api_base_url()
        except Exception as e:
            self._log("ERROR", f"获取 API Base URL 时发生错误: {str(e)}")
            return ""

    def save_model(self, model: str) -> bool:
        """保存模型名称

        Args:
            model: 模型名称字符串

        Returns:
            保存是否成功
        """
        try:
            # 验证模型名称
            if not model or not model.strip():
                self._log("WARNING", "模型名称不能为空")
                return False

            # 保存模型名称
            if self.config_manager.set_model(model.strip()):
                self._log("SUCCESS", "模型名称保存成功")
                return True
            else:
                self._log("ERROR", "模型名称保存失败")
                return False
        except Exception as e:
            self._log("ERROR", f"保存模型名称时发生错误: {str(e)}")
            return False

    def get_model(self) -> str:
        """获取模型名称

        Returns:
            模型名称字符串
        """
        try:
            return self.config_manager.get_model()
        except Exception as e:
            self._log("ERROR", f"获取模型名称时发生错误: {str(e)}")
            return ""

    def save_all_settings(self, settings: dict) -> bool:
        """批量保存所有设置

        Args:
            settings: 设置字典

        Returns:
            保存是否成功
        """
        try:
            # 验证必要的字段
            api_key = settings.get("api_key", "").strip()
            base_url = settings.get("api_base_url", "").strip()
            model = settings.get("model", "").strip()

            # 验证 API Key
            if not api_key:
                self._log("WARNING", "API Key 不能为空")
                return False

            # 验证 Base URL
            if not base_url:
                self._log("WARNING", "API Base URL 不能为空")
                return False

            if not base_url.startswith(("http://", "https://")):
                self._log("WARNING", "API Base URL 必须以 http:// 或 https:// 开头")
                return False

            # 验证模型名称
            if not model:
                self._log("WARNING", "模型名称不能为空")
                return False

            # 批量更新配置
            if self.config_manager.update(settings):
                self._log("SUCCESS", "所有设置保存成功")
                return True
            else:
                self._log("ERROR", "保存设置失败")
                return False
        except Exception as e:
            self._log("ERROR", f"保存设置时发生错误: {str(e)}")
            return False

    def reset_settings(self) -> bool:
        """重置为默认设置

        Returns:
            重置是否成功
        """
        try:
            if self.config_manager.reset():
                self._log("SUCCESS", "设置已重置为默认值")
                return True
            else:
                self._log("ERROR", "重置设置失败")
                return False
        except Exception as e:
            self._log("ERROR", f"重置设置时发生错误: {str(e)}")
            return False

    def test_api_connection(self) -> bool:
        """测试 API 连接

        Returns:
            连接是否成功
        """
        try:
            api_key = self.get_api_key()
            base_url = self.get_api_base_url()

            if not api_key:
                self._log("WARNING", "请先设置 API Key")
                return False

            if not base_url:
                self._log("WARNING", "请先设置 API Base URL")
                return False

            # 这里可以添加实际的 API 连接测试逻辑
            # 目前只做基本验证
            self._log("INFO", "开始测试 API 连接...")
            self._log("INFO", f"Base URL: {base_url}")
            self._log("INFO", f"API Key: {api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "API Key: ***")

            # TODO: 实现实际的 API 连接测试
            self._log("SUCCESS", "API 配置验证通过（未进行实际连接测试）")
            return True

        except Exception as e:
            self._log("ERROR", f"测试 API 连接时发生错误: {str(e)}")
            return False

    def get_config_file_path(self) -> str:
        """获取配置文件路径

        Returns:
            配置文件路径字符串
        """
        return str(self.config_manager.config_file)


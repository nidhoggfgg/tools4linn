"""
Controller for document review functionality.
"""

import json
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from toolkits.review import DocumentReviewer
from toolkits.ai.client import AIChatClient
from toolkits.utils.config import get_config_manager


class DocumentReviewerController:
    """Controller for managing document review operations."""

    def __init__(self):
        """Initialize the controller."""
        self.reviewer: Optional[DocumentReviewer] = None
        self._init_reviewer()

    def _init_reviewer(self):
        """Initialize the document reviewer."""
        try:
            config = get_config_manager()
            api_key = config.get_api_key()
            base_url = config.get_api_base_url()

            if not api_key or not base_url:
                raise ValueError("API 配置不完整，请在设置页面配置 API Key 和 Base URL")

            ai_client = AIChatClient(api_key=api_key, base_url=base_url)
            self.reviewer = DocumentReviewer(
                ai_client=ai_client, model="qwen-vl-max-latest", pdf_dpi=300
            )
        except ValueError as e:
            # API key not configured
            print(f"Failed to initialize DocumentReviewer: {e}")
            self.reviewer = None

    def review_document(
        self,
        file_path: str,
        prompt_path: str,
        reference_data: Dict[str, Any],
        on_success: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_progress: Optional[Callable[[str], None]] = None,
        cleanup_images: bool = True,
    ):
        """
        Review document and compare with reference data.

        Args:
            file_path: Path to image or PDF file
            prompt_path: Path to prompt file
            reference_data: Reference data dictionary
            on_success: Callback for successful completion
            on_error: Callback for errors
            on_progress: Callback for progress updates
            cleanup_images: Whether to cleanup generated images
        """
        if self.reviewer is None:
            if on_error:
                on_error("AI客户端未初始化，请检查API密钥配置")
            return

        def run_review():
            try:
                if on_progress:
                    on_progress("开始处理文档...")

                # Check if files exist
                if not Path(file_path).exists():
                    raise FileNotFoundError(f"文档文件不存在: {file_path}")

                if not Path(prompt_path).exists():
                    raise FileNotFoundError(f"提示词文件不存在: {prompt_path}")

                if on_progress:
                    on_progress("正在分析文档...")

                # Perform review
                if self.reviewer is None:
                    raise ValueError("AI客户端未初始化，请检查API密钥配置")

                result = self.reviewer.review_and_compare(
                    file_path=file_path,
                    prompt_path=prompt_path,
                    reference_data=reference_data,
                    cleanup_images=cleanup_images,
                )

                if on_progress:
                    on_progress("分析完成")

                if on_success:
                    on_success(result)

            except Exception as e:
                if on_error:
                    on_error(str(e))

        # Run in background thread
        thread = threading.Thread(target=run_review, daemon=True)
        thread.start()

    def load_reference_from_json(self, json_path: str) -> Optional[Dict[str, Any]]:
        """
        Load reference data from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            Reference data dictionary or None if error
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load JSON: {e}")
            return None

    def save_result_to_json(self, result: Dict[str, Any], output_path: str) -> bool:
        """
        Save review result to JSON file.

        Args:
            result: Review result dictionary
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for saving
            data = {
                "extracted_data": result.get("extracted_data", {}),
                "differences": result.get("differences", []),
                "formatted_differences": result.get("formatted_differences", ""),
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Failed to save result: {e}")
            return False

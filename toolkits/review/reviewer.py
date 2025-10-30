"""
Document reviewer for extracting and comparing data.
"""

import base64
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from toolkits.ai.client import AIChatClient
from .pdf_converter import PDFConverter
from .comparator import DataComparator


class DocumentReviewer:
    """
    Review documents (images/PDFs) using AI model and compare extracted data.
    """

    def __init__(
        self,
        ai_client: AIChatClient,
        model: str = "qwen-vl-max-latest",
        pdf_dpi: int = 300,
    ):
        """
        Initialize the document reviewer.

        Args:
            ai_client: AI client instance (required).
            model: Model name to use for vision tasks
            pdf_dpi: DPI for PDF to image conversion
        """
        self.ai_client = ai_client
        self.model = model
        self.pdf_converter = PDFConverter(dpi=pdf_dpi)
        self.comparator = DataComparator()

    def review_and_compare(
        self,
        file_path: Union[str, Path],
        prompt_path: Union[str, Path],
        reference_data: Dict[str, Any],
        cleanup_images: bool = True,
    ) -> Dict[str, Any]:
        """
        Review a document and compare extracted data with reference data.

        Args:
            file_path: Path to image or PDF file
            prompt_path: Path to prompt file
            reference_data: Reference data dictionary to compare against
            cleanup_images: Whether to cleanup generated images from PDFs

        Returns:
            Dictionary containing:
            - extracted_data: Data extracted from document
            - differences: List of differences
            - formatted_differences: Human-readable differences
        """
        file_path = Path(file_path)

        # Convert PDF to images if needed
        image_paths = []
        if PDFConverter.is_pdf(file_path):
            image_paths = self.pdf_converter.convert_to_images(file_path)
        else:
            image_paths = [str(file_path)]

        try:
            # Read prompt
            prompt = self._read_prompt(prompt_path)

            # Process all images
            extracted_data = None
            for image_path in image_paths:
                # Extract data from image using AI
                page_data = self._extract_data_from_image(image_path, prompt)

                # For now, use the first page's data
                # You can modify this to handle multi-page logic
                if extracted_data is None:
                    extracted_data = page_data
                else:
                    # Merge data from multiple pages if needed
                    extracted_data.update(page_data)

            if extracted_data is None:
                raise ValueError("No data extracted from document")

            # Compare with reference data
            differences = self.comparator.compare(extracted_data, reference_data)
            formatted_diff = self.comparator.format_differences(differences)

            return {
                "extracted_data": extracted_data,
                "differences": differences,
                "formatted_differences": formatted_diff,
            }

        finally:
            # Cleanup generated images if requested
            if cleanup_images and PDFConverter.is_pdf(file_path):
                self._cleanup_images(image_paths)

    def _read_prompt(self, prompt_path: Union[str, Path]) -> str:
        """Read prompt from file."""
        prompt_path = Path(prompt_path)
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _extract_data_from_image(
        self, image_path: Union[str, Path], prompt: str
    ) -> Dict[str, Any]:
        """
        Extract structured data from image using AI model.

        Args:
            image_path: Path to image file
            prompt: Prompt text

        Returns:
            Extracted data as dictionary
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Read and encode image
        image_url = self._encode_image_to_url(image_path)

        # Prepare messages for vision model
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        # Call AI model
        result = self.ai_client.chat(messages=messages, model=self.model, stream=False)

        # Extract JSON from response
        json_data = self._extract_json_from_response(result.answer)

        return json_data

    def _encode_image_to_url(self, image_path: Path) -> str:
        """
        Encode image to base64 data URL.

        Args:
            image_path: Path to image file

        Returns:
            Data URL string
        """
        with open(image_path, "rb") as f:
            image_data = f.read()

        base64_image = base64.b64encode(image_data).decode("utf-8")

        # Detect image format
        suffix = image_path.suffix.lower()
        mime_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }.get(suffix, "image/png")

        return f"data:{mime_type};base64,{base64_image}"

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON data from AI response.

        The response may contain JSON wrapped in ```json ``` code blocks.

        Args:
            response: AI model response text

        Returns:
            Parsed JSON data
        """
        # Try to find JSON in code blocks
        json_pattern = r"```json\s*\n(.*?)\n```"
        matches = re.findall(json_pattern, response, re.DOTALL)

        if matches:
            # Use the first JSON block found
            json_text = matches[0]
        else:
            # Try to find JSON without code blocks
            json_pattern = r"\{.*\}"
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                json_text = matches[0]
            else:
                raise ValueError(f"No JSON found in AI response: {response}")

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}\nJSON text: {json_text}")

    def _cleanup_images(self, image_paths: List[str]) -> None:
        """
        Clean up generated image files and their parent folder.

        Args:
            image_paths: List of image paths to delete
        """
        import shutil

        if not image_paths:
            return

        # Delete all image files
        for image_path in image_paths:
            path = Path(image_path)
            if path.exists():
                path.unlink()

        # Try to delete the parent folder if it's empty
        parent_folder = Path(image_paths[0]).parent
        try:
            if parent_folder.exists() and not any(parent_folder.iterdir()):
                parent_folder.rmdir()
        except Exception:
            # Ignore errors when cleaning up folder
            pass

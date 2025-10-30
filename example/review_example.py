"""
Example usage of the document review functionality.
"""

from pathlib import Path
from toolkits.review import DocumentReviewer
from toolkits.ai.client import AIChatClient
from toolkits.utils.config import get_config_manager


def main():
    """Run document review example."""

    # Get configuration
    config = get_config_manager()
    api_key = config.get_api_key()
    base_url = config.get_api_base_url()

    # Initialize AI client with required parameters
    ai_client = AIChatClient(api_key=api_key, base_url=base_url)

    # Initialize reviewer
    reviewer = DocumentReviewer(
        ai_client=ai_client,
        model="qwen-vl-max-latest",  # Vision model for image analysis
        pdf_dpi=300,  # DPI for PDF conversion
    )

    # Example: Review a document and compare with reference data

    # 1. Prepare file paths
    document_path = "path/to/your/document.pdf"  # or .jpg, .png
    prompt_path = "path/to/your/prompt.txt"

    # 2. Prepare reference data to compare against
    reference_data = {"name": "张三", "age": 30, "city": "北京", "phone": "13800138000"}

    # 3. Review and compare
    try:
        result = reviewer.review_and_compare(
            file_path=document_path,
            prompt_path=prompt_path,
            reference_data=reference_data,
            cleanup_images=True,  # Auto cleanup generated images from PDFs
        )

        print("=== Extracted Data ===")
        print(result["extracted_data"])
        print()

        print("=== Comparison Results ===")
        print(result["formatted_differences"])
        print()

        # Access raw differences for programmatic processing
        for diff in result["differences"]:
            field = diff["field"]
            status = diff["status"]
            value1 = diff["value1"]
            value2 = diff["value2"]

            if status == "different":
                print(f"Field '{field}' differs:")
                print(f"  Extracted: {value1}")
                print(f"  Reference: {value2}")

    except Exception as e:
        print(f"Error during review: {e}")


def example_with_json_reference():
    """Example using JSON file as reference data."""
    import json

    # Get configuration
    config = get_config_manager()
    api_key = config.get_api_key()
    base_url = config.get_api_base_url()

    ai_client = AIChatClient(api_key=api_key, base_url=base_url)
    reviewer = DocumentReviewer(ai_client=ai_client)

    # Load reference data from JSON file
    with open("reference_data.json", "r", encoding="utf-8") as f:
        reference_data = json.load(f)

    # Review document
    result = reviewer.review_and_compare(
        file_path="document.pdf",
        prompt_path="prompt.txt",
        reference_data=reference_data,
    )

    # Save results
    with open("review_results.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "extracted_data": result["extracted_data"],
                "differences": result["differences"],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(result["formatted_differences"])


def example_prompt_content():
    """
    Example prompt that you might use.

    Save this to a .txt file and use it as your prompt_path.
    """
    prompt = """
请仔细分析这张图片中的信息，并提取以下字段的数据。
请以JSON格式返回结果，确保JSON被```json ```包裹。

需要提取的字段：
- name: 姓名
- age: 年龄
- city: 城市
- phone: 电话号码
- address: 地址（如果有）

请确保：
1. 如果某个字段在图片中不存在，请设置为null
2. 数字类型的字段（如年龄）请返回数字而非字符串
3. 电话号码保持字符串格式

返回格式示例：
```json
{
  "name": "张三",
  "age": 30,
  "city": "北京",
  "phone": "13800138000",
  "address": "朝阳区xxx街道"
}
```
"""
    return prompt


if __name__ == "__main__":
    # Print example prompt
    print("=== Example Prompt ===")
    print(example_prompt_content())
    print()

    # Uncomment to run the actual review
    # main()

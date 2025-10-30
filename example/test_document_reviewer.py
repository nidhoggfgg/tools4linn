"""
Simple test script for document reviewer functionality.
"""

import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkits.review import DocumentReviewer, DataComparator


def test_comparator():
    """Test the data comparator with sample data."""
    print("=" * 60)
    print("Testing DataComparator")
    print("=" * 60)

    # Sample data
    data1 = {"name": "张三", "age": 30, "city": "北京", "phone": "13800138000"}

    data2 = {
        "name": "李四",
        "age": 30,
        "city": "北京",
        "phone": "13900139000",
        "email": "lisi@example.com",
    }

    # Compare
    comparator = DataComparator()
    differences = comparator.compare(data1, data2)

    print("\nData 1:")
    print(json.dumps(data1, ensure_ascii=False, indent=2))

    print("\nData 2:")
    print(json.dumps(data2, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("Comparison Results:")
    print("=" * 60)
    print(comparator.format_differences(differences))


def test_nested_comparator():
    """Test the comparator with nested data."""
    print("\n" + "=" * 60)
    print("Testing DataComparator with Nested Data")
    print("=" * 60)

    data1 = {
        "user": {
            "name": "张三",
            "contact": {"phone": "13800138000", "email": "zhangsan@example.com"},
        },
        "status": "active",
    }

    data2 = {
        "user": {
            "name": "李四",
            "contact": {"phone": "13800138000", "email": "lisi@example.com"},
        },
        "status": "active",
    }

    comparator = DataComparator()
    differences = comparator.compare(data1, data2)

    print("\nData 1:")
    print(json.dumps(data1, ensure_ascii=False, indent=2))

    print("\nData 2:")
    print(json.dumps(data2, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("Comparison Results:")
    print("=" * 60)
    print(comparator.format_differences(differences))


def test_reviewer_with_real_document():
    """
    Test document reviewer with a real document.

    Note: This requires:
    1. DASHSCOPE_API_KEY environment variable set
    2. A sample document file (PDF or image)
    3. A prompt file
    """
    print("\n" + "=" * 60)
    print("Testing DocumentReviewer")
    print("=" * 60)
    print("\nNote: This test requires:")
    print("1. DASHSCOPE_API_KEY environment variable")
    print("2. Sample document (PDF/image)")
    print("3. Prompt file")
    print("\nSkipping this test. Please use the UI or example/review_example.py")
    print("with actual documents to test the full functionality.")

    # Uncomment and modify the following code to test with real documents:
    """
    try:
        reviewer = DocumentReviewer()
        
        result = reviewer.review_and_compare(
            file_path="path/to/your/document.pdf",
            prompt_path="example/sample_prompt.txt",
            reference_data={
                "name": "张三",
                "age": 30,
                "city": "北京"
            }
        )
        
        print("\nExtracted Data:")
        print(json.dumps(result["extracted_data"], ensure_ascii=False, indent=2))
        
        print("\nComparison Results:")
        print(result["formatted_differences"])
        
    except Exception as e:
        print(f"\nError: {e}")
    """


if __name__ == "__main__":
    print("\n" + "🔍 Document Reviewer Test Suite 🔍".center(60))
    print()

    # Test comparator
    test_comparator()

    # Test nested comparator
    test_nested_comparator()

    # Test reviewer (informational only)
    test_reviewer_with_real_document()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

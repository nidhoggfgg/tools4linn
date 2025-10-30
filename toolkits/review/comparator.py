"""
Data comparison utilities.
"""

from typing import Any, Dict, List, Tuple


class DataComparator:
    """Compare two JSON-like data structures and find differences."""

    @staticmethod
    def compare(data1: Dict[str, Any], data2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compare two dictionaries and return differences.

        Args:
            data1: First dictionary (e.g., from AI model)
            data2: Second dictionary (e.g., reference data)

        Returns:
            List of dictionaries containing field differences:
            [
                {
                    "field": "field_name",
                    "value1": value_from_data1,
                    "value2": value_from_data2,
                    "status": "different" | "missing_in_data1" | "missing_in_data2"
                }
            ]
        """
        differences = []

        # Get all unique keys from both dictionaries
        all_keys = set(data1.keys()) | set(data2.keys())

        for key in sorted(all_keys):
            if key not in data1:
                differences.append(
                    {
                        "field": key,
                        "value1": None,
                        "value2": data2[key],
                        "status": "missing_in_data1",
                    }
                )
            elif key not in data2:
                differences.append(
                    {
                        "field": key,
                        "value1": data1[key],
                        "value2": None,
                        "status": "missing_in_data2",
                    }
                )
            else:
                # Both keys exist, compare values
                value1 = data1[key]
                value2 = data2[key]

                # Handle nested dictionaries recursively
                if isinstance(value1, dict) and isinstance(value2, dict):
                    nested_diffs = DataComparator._compare_nested(value1, value2, key)
                    differences.extend(nested_diffs)
                elif value1 != value2:
                    differences.append(
                        {
                            "field": key,
                            "value1": value1,
                            "value2": value2,
                            "status": "different",
                        }
                    )

        return differences

    @staticmethod
    def _compare_nested(
        dict1: Dict[str, Any], dict2: Dict[str, Any], parent_key: str
    ) -> List[Dict[str, Any]]:
        """
        Compare nested dictionaries recursively.

        Args:
            dict1: First nested dictionary
            dict2: Second nested dictionary
            parent_key: Parent key path

        Returns:
            List of differences with nested field paths
        """
        differences = []
        all_keys = set(dict1.keys()) | set(dict2.keys())

        for key in sorted(all_keys):
            full_key = f"{parent_key}.{key}"

            if key not in dict1:
                differences.append(
                    {
                        "field": full_key,
                        "value1": None,
                        "value2": dict2[key],
                        "status": "missing_in_data1",
                    }
                )
            elif key not in dict2:
                differences.append(
                    {
                        "field": full_key,
                        "value1": dict1[key],
                        "value2": None,
                        "status": "missing_in_data2",
                    }
                )
            else:
                value1 = dict1[key]
                value2 = dict2[key]

                if isinstance(value1, dict) and isinstance(value2, dict):
                    nested_diffs = DataComparator._compare_nested(
                        value1, value2, full_key
                    )
                    differences.extend(nested_diffs)
                elif value1 != value2:
                    differences.append(
                        {
                            "field": full_key,
                            "value1": value1,
                            "value2": value2,
                            "status": "different",
                        }
                    )

        return differences

    @staticmethod
    def format_differences(differences: List[Dict[str, Any]]) -> str:
        """
        Format differences into a readable string.

        Args:
            differences: List of differences from compare()

        Returns:
            Formatted string representation
        """
        if not differences:
            return "No differences found."

        lines = [f"Found {len(differences)} difference(s):\n"]

        for i, diff in enumerate(differences, 1):
            field = diff["field"]
            status = diff["status"]
            value1 = diff["value1"]
            value2 = diff["value2"]

            lines.append(f"{i}. Field: {field}")
            if status == "missing_in_data1":
                lines.append(f"   Status: Missing in first data")
                lines.append(f"   Value in second data: {value2}")
            elif status == "missing_in_data2":
                lines.append(f"   Status: Missing in second data")
                lines.append(f"   Value in first data: {value1}")
            else:
                lines.append(f"   Status: Different values")
                lines.append(f"   Value in first data: {value1}")
                lines.append(f"   Value in second data: {value2}")
            lines.append("")

        return "\n".join(lines)

from pathlib import Path
from typing import Callable, Optional, List


class NamingStrategy:
    """Base class for naming strategies."""

    def generate_name(self, file_path: Path, index: int = 0) -> str:
        """Generate a name from the file path."""
        raise NotImplementedError


class FileNameStrategy(NamingStrategy):
    """Use the file name (without extension) as name."""

    def generate_name(self, file_path: Path, index: int = 0) -> str:
        return file_path.stem


class DirectoryNameStrategy(NamingStrategy):
    """Use the parent directory name as name."""

    def generate_name(self, file_path: Path, index: int = 0) -> str:
        return file_path.parent.name


class PathSegmentsStrategy(NamingStrategy):
    """Use specific path segments as name."""

    def __init__(self, segments: Optional[List[int]] = None, separator: str = "_"):
        """
        Args:
            segments: List of segment indices to use (0-based, negative for reverse indexing)
            separator: String to join segments with
        """
        self.segments = segments or [-2, -1]  # Default: last two segments
        self.separator = separator

    def generate_name(self, file_path: Path, index: int = 0) -> str:
        parts = file_path.parts
        selected_parts = []

        for seg in self.segments:
            if 0 <= seg < len(parts):
                selected_parts.append(parts[seg])
            elif seg < 0 and abs(seg) <= len(parts):
                selected_parts.append(parts[seg])

        return self.separator.join(selected_parts)


class IndexedStrategy(NamingStrategy):
    """Use index-based naming with optional prefix."""

    def __init__(self, prefix: str = "Name", start_index: int = 1):
        self.prefix = prefix
        self.start_index = start_index

    def generate_name(self, file_path: Path, index: int = 0) -> str:
        return f"{self.prefix}_{self.start_index + index}"


class CustomFunctionStrategy(NamingStrategy):
    """Use a custom function to generate names."""

    def __init__(self, func: Callable[[Path, int], str]):
        self.func = func

    def generate_name(self, file_path: Path, index: int = 0) -> str:
        return self.func(file_path, index)


# Predefined strategy instances for common use cases
FILENAME_STRATEGY = FileNameStrategy()
DIRECTORY_STRATEGY = DirectoryNameStrategy()
LAST_TWO_SEGMENTS_STRATEGY = PathSegmentsStrategy([-2, -1])
INDEXED_STRATEGY = IndexedStrategy()

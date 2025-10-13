from pathlib import Path
from typing import Callable, Optional, List
import re


class FileFilterStrategy:
    """Base class for file filtering strategies."""

    def should_include(self, file_path: Path) -> bool:
        """Determine if a file should be included based on the filtering strategy."""
        raise NotImplementedError


class NameIncludeStrategy(FileFilterStrategy):
    """Filter files based on name inclusion."""

    def __init__(self, name: str):
        """
        Args:
            name: Name to include
        """
        self.name = name

    def should_include(self, file_path: Path) -> bool:
        return self.name in file_path.stem


class NamePatternStrategy(FileFilterStrategy):
    """Filter files based on name pattern matching."""

    def __init__(self, pattern: str):
        """
        Args:
            pattern: Regex pattern to match against file name (without extension)
        """
        self.pattern = re.compile(pattern)

    def should_include(self, file_path: Path) -> bool:
        return bool(self.pattern.search(file_path.stem))


class ExtensionStrategy(FileFilterStrategy):
    """Filter files based on specific extensions."""

    def __init__(self, extensions: List[str]):
        """
        Args:
            extensions: List of extensions to include (with or without dot)
        """
        # Normalize extensions (ensure they start with dot)
        self.extensions = []
        for ext in extensions:
            if not ext.startswith("."):
                ext = "." + ext
            self.extensions.append(ext)

    def should_include(self, file_path: Path) -> bool:
        file_ext = file_path.suffix
        return file_ext in self.extensions


class SizeStrategy(FileFilterStrategy):
    """Filter files based on file size."""

    def __init__(self, min_size: Optional[int] = None, max_size: Optional[int] = None):
        """
        Args:
            min_size: Minimum file size in bytes (inclusive)
            max_size: Maximum file size in bytes (inclusive)
        """
        self.min_size = min_size
        self.max_size = max_size

    def should_include(self, file_path: Path) -> bool:
        if not file_path.exists():
            return False

        file_size = file_path.stat().st_size

        if self.min_size is not None and file_size < self.min_size:
            return False

        if self.max_size is not None and file_size > self.max_size:
            return False

        return True


class DirectoryStrategy(FileFilterStrategy):
    """Filter files based on directory patterns."""

    def __init__(
        self,
        include_dirs: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
    ):
        """
        Args:
            include_dirs: List of directory patterns to include (regex)
            exclude_dirs: List of directory patterns to exclude (regex)
        """
        self.include_patterns = []
        if include_dirs:
            for pattern in include_dirs:
                self.include_patterns.append(re.compile(pattern))

        self.exclude_patterns = []
        if exclude_dirs:
            for pattern in exclude_dirs:
                self.exclude_patterns.append(re.compile(pattern))

    def should_include(self, file_path: Path) -> bool:
        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if pattern.search(str(file_path.parent)):
                return False

        # If no include patterns, include all (after exclusions)
        if not self.include_patterns:
            return True

        # Check include patterns
        for pattern in self.include_patterns:
            if pattern.search(str(file_path.parent)):
                return True

        return False


class CustomFunctionStrategy(FileFilterStrategy):
    """Use a custom function to filter files."""

    def __init__(self, func: Callable[[Path], bool]):
        self.func = func

    def should_include(self, file_path: Path) -> bool:
        return self.func(file_path)


class CompositeStrategy(FileFilterStrategy):
    """Combine multiple filtering strategies with AND/OR logic."""

    def __init__(self, strategies: List[FileFilterStrategy], mode: str = "AND"):
        """
        Args:
            strategies: List of filtering strategies to combine
            mode: "AND" (all must pass) or "OR" (any can pass)
        """
        self.strategies = strategies
        self.mode = mode.upper()

    def should_include(self, file_path: Path) -> bool:
        if not self.strategies:
            return True

        results = [strategy.should_include(file_path) for strategy in self.strategies]

        if self.mode == "AND":
            return all(results)
        elif self.mode == "OR":
            return any(results)
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Must be 'AND' or 'OR'.")

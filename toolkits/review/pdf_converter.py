"""
PDF to image converter utilities.
"""

import os
from pathlib import Path
from typing import List, Union

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


class PDFConverter:
    """Convert PDF files to images."""
    
    def __init__(self, dpi: int = 300):
        """
        Initialize the PDF converter.
        
        Args:
            dpi: DPI for image conversion (default: 300)
        """
        if not PDF2IMAGE_AVAILABLE:
            raise ImportError(
                "pdf2image is not installed. Please install it with: pip install pdf2image"
            )
        self.dpi = dpi
    
    def convert_to_images(
        self, 
        pdf_path: Union[str, Path],
        output_folder: Union[str, Path, None] = None,
        fmt: str = "png"
    ) -> List[str]:
        """
        Convert PDF to images.
        
        Args:
            pdf_path: Path to the PDF file
            output_folder: Optional output folder for images. If None, creates temp folder
            fmt: Image format (default: "png")
            
        Returns:
            List of paths to generated images
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Create output folder if specified
        if output_folder:
            output_folder = Path(output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)
        else:
            # Use temp folder in the same directory as PDF
            output_folder = pdf_path.parent / f"{pdf_path.stem}_images"
            output_folder.mkdir(parents=True, exist_ok=True)
        
        # Convert PDF to images
        images = convert_from_path(str(pdf_path), dpi=self.dpi)
        
        # Save images and collect paths
        image_paths = []
        for i, image in enumerate(images, start=1):
            image_path = output_folder / f"{pdf_path.stem}_page_{i}.{fmt}"
            image.save(str(image_path), fmt.upper())
            image_paths.append(str(image_path))
        
        return image_paths
    
    @staticmethod
    def is_pdf(file_path: Union[str, Path]) -> bool:
        """Check if a file is a PDF."""
        return Path(file_path).suffix.lower() == ".pdf"


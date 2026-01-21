"""
文件格式转换工具
支持多种文件格式之间的批量转换
"""

from pathlib import Path
from typing import List, Optional, Callable, Dict, Tuple, Any
from abc import ABC, abstractmethod
import logging
import platform
import subprocess

# 可用性检查
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

# Windows 特定转换器可用性检查
WINDOWS_DOC_CONVERTER_AVAILABLE = platform.system() == "Windows"


class ConversionResult:
    """转换结果数据类"""

    def __init__(
        self,
        success: bool,
        input_path: Path,
        output_path: Optional[Path],
        error_message: Optional[str] = None,
    ):
        self.success = success
        self.input_path = input_path
        self.output_path = output_path
        self.error_message = error_message


class BaseConverter(ABC):
    """转换器抽象基类"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.supported_input_formats: List[str] = []
        self.supported_output_formats: List[str] = []

    @abstractmethod
    def convert(
        self, input_path: Path, output_path: Path, **options
    ) -> ConversionResult:
        """
        执行转换

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            **options: 转换选项（如质量、DPI等）

        Returns:
            ConversionResult: 转换结果
        """
        pass

    @abstractmethod
    def is_supported(self, input_format: str, output_format: str) -> bool:
        """检查是否支持该转换"""
        pass

    def get_output_path(
        self, input_path: Path, output_dir: Optional[Path], output_format: str
    ) -> Path:
        """
        计算输出文件路径

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录，None 表示与输入文件同目录
            output_format: 输出格式（不含点）

        Returns:
            输出文件路径
        """
        if output_dir is None:
            # 与输入文件同目录
            return input_path.parent / f"{input_path.stem}.{output_format}"
        else:
            # 统一输出到指定目录
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir / f"{input_path.stem}.{output_format}"


class ImageConverter(BaseConverter):
    """图片格式转换器"""

    # 支持的格式映射
    FORMAT_EXTENSIONS = {
        "PNG": "png",
        "JPEG": "jpg",
        "JPG": "jpg",
        "WEBP": "webp",
        "BMP": "bmp",
        "TIFF": "tiff",
        "GIF": "gif",
    }

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__(logger)

        if not PILLOW_AVAILABLE:
            raise ImportError("PIL/Pillow is not installed")

        self.supported_input_formats = list(self.FORMAT_EXTENSIONS.keys())
        self.supported_output_formats = list(self.FORMAT_EXTENSIONS.keys())

    def is_supported(self, input_format: str, output_format: str) -> bool:
        """检查是否支持该转换"""
        input_format = input_format.upper().lstrip(".")
        output_format = output_format.upper().lstrip(".")

        return (
            input_format in self.supported_input_formats
            and output_format in self.supported_output_formats
        )

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        quality: int = 95,
        maintain_aspect_ratio: bool = True,
        delete_original: bool = False,
        **options,
    ) -> ConversionResult:
        """
        转换图片格式

        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            quality: 图片质量（1-100），用于 JPEG/WEBP
            maintain_aspect_ratio: 保持宽高比
            delete_original: 是否删除原文件
            **options: 其他选项
        """
        try:
            if not input_path.exists():
                return ConversionResult(
                    success=False,
                    input_path=input_path,
                    output_path=None,
                    error_message=f"输入文件不存在: {input_path}",
                )

            # 打开图片
            with Image.open(input_path) as img:
                # 处理 RGBA 模式（JPEG 不支持透明）
                output_format = output_path.suffix.lstrip(".").upper()
                if output_format in ["JPEG", "JPG"] and img.mode == "RGBA":
                    # 创建白色背景
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # 使用 alpha 通道
                    img = background
                elif img.mode not in ["RGB", "RGBA", "L", "LA", "P"]:
                    # 转换为 RGB
                    img = img.convert("RGB")

                # 保存参数
                save_kwargs = {}
                if output_format in ["JPEG", "JPG", "WEBP"]:
                    save_kwargs["quality"] = quality
                elif output_format == "PNG":
                    save_kwargs["optimize"] = True

                # 确保输出目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # 保存图片
                img.save(str(output_path), **save_kwargs)

            # 删除原文件（如果要求）
            if delete_original:
                try:
                    input_path.unlink()
                    self.logger.info(f"已删除原文件: {input_path}")
                except Exception as e:
                    self.logger.warning(f"删除原文件失败: {e}")

            self.logger.info(f"图片转换成功: {input_path} -> {output_path}")

            return ConversionResult(
                success=True, input_path=input_path, output_path=output_path
            )

        except Exception as e:
            error_msg = f"图片转换失败: {str(e)}"
            self.logger.error(f"{error_msg} - 文件: {input_path}")
            return ConversionResult(
                success=False, input_path=input_path, output_path=None, error_message=error_msg
            )


class WindowsDocumentConverter(BaseConverter):
    """Windows 文档转换器 (Word/PPTX 转 PDF)"""

    # 支持的格式映射
    FORMAT_EXTENSIONS = {
        "DOCX": "docx",
        "DOC": "doc",
        "PPTX": "pptx",
        "PPT": "ppt",
        "PDF": "pdf",
    }

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__(logger)

        if not WINDOWS_DOC_CONVERTER_AVAILABLE:
            raise ImportError("Windows document converter only available on Windows")

        # Word 支持的输入/输出格式
        self.word_input_formats = ["DOCX", "DOC"]
        self.word_output_formats = ["PDF"]

        # PowerPoint 支持的输入/输出格式
        self.ppt_input_formats = ["PPTX", "PPT"]
        self.ppt_output_formats = ["PDF"]

        self.supported_input_formats = (
            self.word_input_formats + self.ppt_input_formats
        )
        self.supported_output_formats = ["PDF"]

    def is_supported(self, input_format: str, output_format: str) -> bool:
        """检查是否支持该转换"""
        input_format = input_format.upper().lstrip(".")
        output_format = output_format.upper().lstrip(".")

        # 仅支持转换为 PDF
        if output_format != "PDF":
            return False

        return input_format in self.supported_input_formats

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        delete_original: bool = False,
        **options,
    ) -> ConversionResult:
        """
        转换文档格式为 PDF

        Args:
            input_path: 输入文档路径
            output_path: 输出 PDF 路径
            delete_original: 是否删除原文件
            **options: 其他选项
        """
        try:
            if not input_path.exists():
                return ConversionResult(
                    success=False,
                    input_path=input_path,
                    output_path=None,
                    error_message=f"输入文件不存在: {input_path}",
                )

            input_format = input_path.suffix.lstrip(".").upper()

            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 根据文件类型选择转换方法
            if input_format in self.word_input_formats:
                success = self._convert_word_to_pdf(input_path, output_path)
            elif input_format in self.ppt_input_formats:
                success = self._convert_ppt_to_pdf(input_path, output_path)
            else:
                return ConversionResult(
                    success=False,
                    input_path=input_path,
                    output_path=None,
                    error_message=f"不支持的输入格式: {input_format}",
                )

            if not success:
                return ConversionResult(
                    success=False,
                    input_path=input_path,
                    output_path=None,
                    error_message="文档转换失败",
                )

            # 删除原文件（如果要求）
            if delete_original:
                try:
                    input_path.unlink()
                    self.logger.info(f"已删除原文件: {input_path}")
                except Exception as e:
                    self.logger.warning(f"删除原文件失败: {e}")

            self.logger.info(f"文档转换成功: {input_path} -> {output_path}")

            return ConversionResult(
                success=True, input_path=input_path, output_path=output_path
            )

        except Exception as e:
            error_msg = f"文档转换失败: {str(e)}"
            self.logger.error(f"{error_msg} - 文件: {input_path}")
            return ConversionResult(
                success=False, input_path=input_path, output_path=None, error_message=error_msg
            )

    def _convert_word_to_pdf(self, input_path: Path, output_path: Path) -> bool:
        """使用 Word COM 接口转换文档为 PDF"""
        try:
            import win32com.client

            # 创建 Word 应用程序对象
            word = win32com.client.Dispatch("Word.Application")
            try:
                word.Visible = False
            except Exception:
                # 某些系统不允许隐藏窗口，忽略此错误
                self.logger.debug("无法隐藏 Word 窗口，将继续转换")

            try:
                # 打开文档
                doc = word.Documents.Open(str(input_path.absolute()))

                # 保存为 PDF (16 = wdFormatPDF)
                doc.SaveAs(str(output_path.absolute()), FileFormat=16)

                # 关闭文档
                doc.Close(SaveChanges=0)
                return True

            except Exception as e:
                # 确保文档被关闭
                try:
                    doc.Close(SaveChanges=0)
                except:
                    pass
                raise

            finally:
                # 退出 Word 应用程序
                try:
                    word.Quit(SaveChanges=0)
                except:
                    pass

        except Exception as e:
            self.logger.error(f"Word 转 PDF 失败: {e}")
            return False

    def _convert_ppt_to_pdf(self, input_path: Path, output_path: Path) -> bool:
        """使用 PowerPoint COM 接口转换演示文稿为 PDF"""
        try:
            import win32com.client

            # 创建 PowerPoint 应用程序对象
            ppt = win32com.client.Dispatch("PowerPoint.Application")
            try:
                ppt.Visible = False
            except Exception:
                # 某些系统不允许隐藏窗口，忽略此错误
                self.logger.debug("无法隐藏 PowerPoint 窗口，将继续转换")

            try:
                # 打开演示文稿
                presentation = ppt.Presentations.Open(str(input_path.absolute()))

                # 保存为 PDF (32 = ppSaveAsPDF)
                presentation.SaveAs(str(output_path.absolute()), 32)

                # 关闭演示文稿
                presentation.Close()
                return True

            except Exception as e:
                # 确保演示文稿被关闭
                try:
                    presentation.Close()
                except:
                    pass
                raise

            finally:
                # 退出 PowerPoint 应用程序
                try:
                    ppt.Quit()
                except:
                    pass

        except Exception as e:
            self.logger.error(f"PowerPoint 转 PDF 失败: {e}")
            return False


class ConverterManager:
    """转换器管理器 - 负责选择合适的转换器并执行批量转换"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.converters: List[BaseConverter] = []

        # 注册可用的转换器
        self._register_converters()

    def _register_converters(self):
        """注册所有可用的转换器"""
        # 注册图片转换器
        try:
            self.converters.append(ImageConverter(self.logger))
            self.logger.info("图片转换器已注册")
        except ImportError as e:
            self.logger.warning(f"图片转换器不可用: {e}")

        # 注册 Windows 文档转换器
        try:
            self.converters.append(WindowsDocumentConverter(self.logger))
            self.logger.info("Windows 文档转换器已注册")
        except ImportError as e:
            self.logger.info(f"Windows 文档转换器不可用 (仅支持 Windows): {e}")

    def get_supported_conversions(self) -> Dict[str, List[str]]:
        """
        获取所有支持的转换类型

        Returns:
            {输入格式: [输出格式1, 输出格式2, ...]}
        """
        supported = {}
        for converter in self.converters:
            for input_fmt in converter.supported_input_formats:
                if input_fmt not in supported:
                    supported[input_fmt] = set()
                for output_fmt in converter.supported_output_formats:
                    if converter.is_supported(input_fmt, output_fmt):
                        supported[input_fmt].add(output_fmt)

        # 转换为列表并排序
        return {k: sorted(list(v)) for k, v in sorted(supported.items())}

    def find_converter(
        self, input_format: str, output_format: str
    ) -> Optional[BaseConverter]:
        """
        查找支持该转换的转换器

        Args:
            input_format: 输入格式
            output_format: 输出格式

        Returns:
            匹配的转换器，None 表示不支持
        """
        input_format = input_format.upper().lstrip(".")
        output_format = output_format.upper().lstrip(".")

        for converter in self.converters:
            if converter.is_supported(input_format, output_format):
                return converter

        return None

    def batch_convert(
        self,
        files: List[Path],
        output_format: str,
        output_dir: Optional[Path] = None,
        output_mode: str = "same_dir",
        progress_callback: Optional[Callable[[int, int], None]] = None,
        **options,
    ) -> Tuple[List[ConversionResult], List[str]]:
        """
        批量转换文件

        Args:
            files: 文件路径列表
            output_format: 目标格式
            output_dir: 输出目录（output_mode="unified" 时使用）
            output_mode: 输出模式
                - "same_dir": 在原文件夹输出
                - "unified": 统一输出到指定目录
            progress_callback: 进度回调 (current, total)
            **options: 转换选项

        Returns:
            (转换结果列表, 错误信息列表)
        """
        results = []
        errors = []

        total = len(files)
        self.logger.info(f"开始批量转换，共 {total} 个文件")

        for idx, file_path in enumerate(files):
            try:
                # 进度回调
                if progress_callback:
                    progress_callback(idx + 1, total)

                # 获取输入格式
                input_format = file_path.suffix.lstrip(".")

                # 查找转换器
                converter = self.find_converter(input_format, output_format)
                if converter is None:
                    error_msg = f"不支持的转换: {input_format} -> {output_format}"
                    errors.append(f"{file_path}: {error_msg}")
                    results.append(
                        ConversionResult(
                            success=False,
                            input_path=file_path,
                            output_path=None,
                            error_message=error_msg,
                        )
                    )
                    continue

                # 计算输出路径
                if output_mode == "same_dir":
                    output_path = converter.get_output_path(
                        file_path, None, output_format
                    )
                else:  # unified
                    output_path = converter.get_output_path(
                        file_path, output_dir, output_format
                    )

                # 执行转换
                result = converter.convert(file_path, output_path, **options)
                results.append(result)

                if not result.success:
                    errors.append(f"{file_path}: {result.error_message}")

            except Exception as e:
                error_msg = f"处理文件 {file_path} 时出错: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
                results.append(
                    ConversionResult(
                        success=False, input_path=file_path, output_path=None, error_message=error_msg
                    )
                )

        # 统计结果
        success_count = sum(1 for r in results if r.success)
        self.logger.info(
            f"批量转换完成: 成功 {success_count}/{total}, 失败 {len(errors)}"
        )

        return results, errors

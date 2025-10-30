"""
Document reviewer page UI.
"""

import json
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox

from ui.controllers.document_reviewer_controller import DocumentReviewerController


class DocumentReviewerPage(ctk.CTkFrame):
    """Document reviewer page for reviewing and comparing documents."""
    
    def __init__(self, parent):
        """Initialize the page."""
        super().__init__(parent)
        self.controller = DocumentReviewerController()
        
        # State
        self.document_path = None
        self.prompt_path = None
        self.reference_data = {}
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="文档审查与对比",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Document file selection
        doc_frame = ctk.CTkFrame(self)
        doc_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            doc_frame,
            text="1. 选择文档文件（图片或PDF）:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=10, pady=5)
        
        doc_select_frame = ctk.CTkFrame(doc_frame)
        doc_select_frame.pack(fill="x", padx=10, pady=5)
        
        self.doc_path_entry = ctk.CTkEntry(
            doc_select_frame,
            placeholder_text="请选择文档文件"
        )
        self.doc_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            doc_select_frame,
            text="浏览",
            width=100,
            command=self._select_document
        ).pack(side="right")
        
        # Prompt file selection
        prompt_frame = ctk.CTkFrame(self)
        prompt_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            prompt_frame,
            text="2. 选择提示词文件:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=10, pady=5)
        
        prompt_select_frame = ctk.CTkFrame(prompt_frame)
        prompt_select_frame.pack(fill="x", padx=10, pady=5)
        
        self.prompt_path_entry = ctk.CTkEntry(
            prompt_select_frame,
            placeholder_text="请选择提示词文件（.txt）"
        )
        self.prompt_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            prompt_select_frame,
            text="浏览",
            width=100,
            command=self._select_prompt
        ).pack(side="right")
        
        # Reference data section
        ref_frame = ctk.CTkFrame(self)
        ref_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ref_header = ctk.CTkFrame(ref_frame)
        ref_header.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            ref_header,
            text="3. 参考数据（JSON格式）:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", anchor="w")
        
        ctk.CTkButton(
            ref_header,
            text="从文件加载",
            width=120,
            command=self._load_reference_json
        ).pack(side="right", padx=5)
        
        self.reference_text = ctk.CTkTextbox(
            ref_frame,
            height=150
        )
        self.reference_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.reference_text.insert("1.0", '{\n  "name": "示例",\n  "value": "数据"\n}')
        
        # Action buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        self.review_button = ctk.CTkButton(
            button_frame,
            text="开始审查",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self._start_review
        )
        self.review_button.pack(side="left", expand=True, fill="x", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="清空",
            height=40,
            command=self._clear_form
        ).pack(side="right", padx=5)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=5)
        
        # Results section
        result_frame = ctk.CTkFrame(self)
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        result_header = ctk.CTkFrame(result_frame)
        result_header.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            result_header,
            text="审查结果:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", anchor="w")
        
        ctk.CTkButton(
            result_header,
            text="保存结果",
            width=100,
            command=self._save_results
        ).pack(side="right", padx=5)
        
        self.result_text = ctk.CTkTextbox(
            result_frame,
            height=200
        )
        self.result_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Store result for saving
        self.current_result = None
    
    def _select_document(self):
        """Open file dialog to select document."""
        file_path = filedialog.askopenfilename(
            title="选择文档文件",
            filetypes=[
                ("所有支持的文件", "*.pdf *.png *.jpg *.jpeg *.gif *.webp"),
                ("PDF文件", "*.pdf"),
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.document_path = file_path
            self.doc_path_entry.delete(0, "end")
            self.doc_path_entry.insert(0, file_path)
    
    def _select_prompt(self):
        """Open file dialog to select prompt file."""
        file_path = filedialog.askopenfilename(
            title="选择提示词文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.prompt_path = file_path
            self.prompt_path_entry.delete(0, "end")
            self.prompt_path_entry.insert(0, file_path)
    
    def _load_reference_json(self):
        """Load reference data from JSON file."""
        file_path = filedialog.askopenfilename(
            title="选择参考数据JSON文件",
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Display in text box
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                self.reference_text.delete("1.0", "end")
                self.reference_text.insert("1.0", json_str)
                
                messagebox.showinfo("成功", "参考数据加载成功")
            
            except Exception as e:
                messagebox.showerror("错误", f"加载JSON文件失败: {e}")
    
    def _start_review(self):
        """Start the document review process."""
        # Validate inputs
        if not self.document_path or not Path(self.document_path).exists():
            messagebox.showerror("错误", "请选择有效的文档文件")
            return
        
        if not self.prompt_path or not Path(self.prompt_path).exists():
            messagebox.showerror("错误", "请选择有效的提示词文件")
            return
        
        # Parse reference data
        try:
            reference_text = self.reference_text.get("1.0", "end").strip()
            self.reference_data = json.loads(reference_text)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"参考数据JSON格式错误: {e}")
            return
        
        # Disable button during processing
        self.review_button.configure(state="disabled")
        self.result_text.delete("1.0", "end")
        
        # Start review
        self.controller.review_document(
            file_path=self.document_path,
            prompt_path=self.prompt_path,
            reference_data=self.reference_data,
            on_success=self._on_review_success,
            on_error=self._on_review_error,
            on_progress=self._on_progress,
            cleanup_images=True
        )
    
    def _on_progress(self, message: str):
        """Handle progress updates."""
        self.progress_label.configure(text=message)
    
    def _on_review_success(self, result: dict):
        """Handle successful review completion."""
        self.current_result = result
        self.review_button.configure(state="normal")
        self.progress_label.configure(text="审查完成！")
        
        # Display results
        output = []
        output.append("=" * 50)
        output.append("提取的数据:")
        output.append("=" * 50)
        output.append(json.dumps(result["extracted_data"], ensure_ascii=False, indent=2))
        output.append("\n")
        output.append("=" * 50)
        output.append("对比结果:")
        output.append("=" * 50)
        output.append(result["formatted_differences"])
        
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "\n".join(output))
        
        # Show notification
        diff_count = len(result["differences"])
        if diff_count == 0:
            messagebox.showinfo("完成", "审查完成！数据完全匹配，没有发现差异。")
        else:
            messagebox.showinfo("完成", f"审查完成！发现 {diff_count} 处差异。")
    
    def _on_review_error(self, error: str):
        """Handle review errors."""
        self.review_button.configure(state="normal")
        self.progress_label.configure(text="审查失败")
        
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", f"错误: {error}")
        
        messagebox.showerror("错误", f"审查过程中发生错误:\n{error}")
    
    def _save_results(self):
        """Save review results to file."""
        if not self.current_result:
            messagebox.showwarning("警告", "没有可保存的结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".json",
            filetypes=[
                ("JSON文件", "*.json"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith(".json"):
                    # Save as JSON
                    success = self.controller.save_result_to_json(
                        self.current_result,
                        file_path
                    )
                else:
                    # Save as text
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(self.result_text.get("1.0", "end"))
                    success = True
                
                if success:
                    messagebox.showinfo("成功", f"结果已保存到: {file_path}")
                else:
                    messagebox.showerror("错误", "保存结果失败")
            
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {e}")
    
    def _clear_form(self):
        """Clear the form."""
        self.document_path = None
        self.prompt_path = None
        self.reference_data = {}
        self.current_result = None
        
        self.doc_path_entry.delete(0, "end")
        self.prompt_path_entry.delete(0, "end")
        self.reference_text.delete("1.0", "end")
        self.reference_text.insert("1.0", '{\n  "name": "示例",\n  "value": "数据"\n}')
        self.result_text.delete("1.0", "end")
        self.progress_label.configure(text="")


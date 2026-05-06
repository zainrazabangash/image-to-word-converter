"""
Image-to-Word Converter (MVP)
A desktop application that extracts text from images while preserving basic formatting.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from image_preprocessor import ImagePreprocessor
from ocr_engine import OCREngine
from formatting_detector import FormattingDetector
from docx_generator import DOCXGenerator


class ImageToWordConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Word Converter")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        self.current_image_path = None
        self.processed_data = None
        
        self.preprocessor = ImagePreprocessor()
        self.ocr_engine = OCREngine()
        self.formatting_detector = FormattingDetector()
        self.docx_generator = DOCXGenerator()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="Image to Word Converter", 
            font=("Helvetica", 20, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Image display
        left_frame = tk.LabelFrame(main_frame, text="Image Preview", font=("Helvetica", 12), bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.image_label = tk.Label(left_frame, bg="#e0e0e0", text="No image selected")
        self.image_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Right panel - Controls
        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # File selection
        file_frame = tk.LabelFrame(right_frame, text="File Selection", font=("Helvetica", 12), bg="#f0f0f0")
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=40, state="readonly")
        file_entry.pack(padx=10, pady=5, fill=tk.X)
        
        browse_btn = tk.Button(
            file_frame, 
            text="Browse Image", 
            command=self.browse_image,
            bg="#3498db",
            fg="white",
            font=("Helvetica", 10, "bold"),
            width=15
        )
        browse_btn.pack(pady=5)
        
        # Options
        options_frame = tk.LabelFrame(right_frame, text="Processing Options", font=("Helvetica", 12), bg="#f0f0f0")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.preprocess_var = tk.BooleanVar(value=True)
        preprocess_cb = tk.Checkbutton(
            options_frame, 
            text="Apply Image Preprocessing", 
            variable=self.preprocess_var,
            bg="#f0f0f0",
            font=("Helvetica", 10)
        )
        preprocess_cb.pack(anchor=tk.W, padx=10, pady=2)
        
        self.detect_formatting_var = tk.BooleanVar(value=True)
        formatting_cb = tk.Checkbutton(
            options_frame, 
            text="Detect Formatting (Bold/Italic)", 
            variable=self.detect_formatting_var,
            bg="#f0f0f0",
            font=("Helvetica", 10)
        )
        formatting_cb.pack(anchor=tk.W, padx=10, pady=2)
        
        # Language selection
        lang_frame = tk.Frame(options_frame, bg="#f0f0f0")
        lang_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(lang_frame, text="Language:", bg="#f0f0f0", font=("Helvetica", 10)).pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value="eng")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, values=["eng", "eng+deu", "eng+fra"], width=15, state="readonly")
        lang_combo.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = tk.Frame(right_frame, bg="#f0f0f0")
        action_frame.pack(fill=tk.X, pady=20)
        
        self.convert_btn = tk.Button(
            action_frame, 
            text="Convert to Word", 
            command=self.convert_image,
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 12, "bold"),
            width=18,
            height=2,
            state="disabled"
        )
        self.convert_btn.pack(pady=5)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(right_frame, variable=self.progress_var, maximum=100, length=250)
        self.progress_bar.pack(pady=10)
        
        self.status_label = tk.Label(right_frame, text="Ready", font=("Helvetica", 10), bg="#f0f0f0", fg="#7f8c8d")
        self.status_label.pack(pady=5)
        
        # Preview text
        preview_frame = tk.LabelFrame(self.root, text="Extracted Text Preview", font=("Helvetica", 12), bg="#f0f0f0")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.preview_text = tk.Text(preview_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=scrollbar.set)
    
    def browse_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(
            title="Select an image",
            filetypes=filetypes
        )
        
        if filename:
            self.current_image_path = filename
            self.file_path_var.set(filename)
            self.display_image(filename)
            self.convert_btn.config(state="normal")
            self.preview_text.delete(1.0, tk.END)
            self.status_label.config(text="Image loaded. Ready to convert.", fg="#27ae60")
    
    def display_image(self, image_path):
        try:
            image = Image.open(image_path)
            # Resize for display
            max_size = (400, 400)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {str(e)}")
    
    def update_progress(self, value, status_text):
        self.progress_var.set(value)
        self.status_label.config(text=status_text)
        self.root.update_idletasks()
    
    def convert_image(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please select an image first.")
            return
        
        try:
            self.convert_btn.config(state="disabled")
            
            # Step 1: Image preprocessing
            self.update_progress(10, "Preprocessing image...")
            if self.preprocess_var.get():
                processed_image = self.preprocessor.preprocess(self.current_image_path)
            else:
                processed_image = Image.open(self.current_image_path)
            
            # Step 2: OCR
            self.update_progress(40, "Performing OCR...")
            ocr_data = self.ocr_engine.extract_text(processed_image, self.language_var.get())
            
            # Step 3: Formatting detection
            self.update_progress(70, "Detecting formatting...")
            if self.detect_formatting_var.get():
                formatted_data = self.formatting_detector.detect_formatting(ocr_data, processed_image)
            else:
                formatted_data = ocr_data
            
            # Display preview
            self.update_progress(85, "Generating preview...")
            self.preview_text.delete(1.0, tk.END)
            preview_content = self.formatting_detector.get_text_preview(formatted_data)
            self.preview_text.insert(tk.END, preview_content)
            
            # Step 4: Generate Word document
            self.update_progress(95, "Saving document...")
            output_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word Document", "*.docx")],
                title="Save Word Document"
            )
            
            if output_path:
                self.docx_generator.create_document(formatted_data, output_path)
                self.update_progress(100, "Conversion complete!")
                messagebox.showinfo("Success", f"Document saved successfully!\n\nLocation: {output_path}")
            else:
                self.update_progress(0, "Save cancelled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
            self.update_progress(0, "Error occurred")
        finally:
            self.convert_btn.config(state="normal")


def main():
    root = tk.Tk()
    app = ImageToWordConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()

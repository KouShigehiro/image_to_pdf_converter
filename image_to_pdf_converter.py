import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import threading

class ImageToPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("批量图片转PDF工具")
        self.root.geometry("750x500")
        self.root.resizable(True, True)
        
        # 设置变量
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.selected_format = tk.StringVar(value="PDF")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="就绪")
        
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 输入文件夹选择
        input_frame = ttk.LabelFrame(main_frame, text="输入设置", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(input_frame, text="图片文件夹:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(input_frame, textvariable=self.input_folder, width=50).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(input_frame, text="浏览", command=self.select_input_folder).grid(row=0, column=2)
        
        # 输出文件夹选择
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="10")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(output_frame, text="输出文件夹:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(output_frame, textvariable=self.output_folder, width=50).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(output_frame, text="浏览", command=self.select_output_folder).grid(row=0, column=2)
        
        # 输出格式选择
        format_frame = ttk.LabelFrame(main_frame, text="输出格式", padding="10")
        format_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        formats = ["PDF"]
        for fmt in formats:
            ttk.Radiobutton(format_frame, text=fmt, variable=self.selected_format, value=fmt).pack(side=tk.LEFT, padx=(0, 20))
        
        # 文件列表显示
        files_frame = ttk.LabelFrame(main_frame, text="待转换文件", padding="10")
        files_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 创建滚动文本框
        self.files_text = tk.Text(files_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_text.yview)
        self.files_text.configure(yscrollcommand=scrollbar.set)
        
        self.files_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 进度条
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.progress_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.progress_label.grid(row=0, column=1)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        self.convert_btn = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="清空列表", command=self.clear_list)
        self.clear_btn.pack(side=tk.LEFT)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
    
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="选择图片文件夹")
        if folder:
            self.input_folder.set(folder)
            self.update_file_list()
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_folder.set(folder)
    
    def update_file_list(self):
        self.files_text.delete(1.0, tk.END)
        folder_path = self.input_folder.get()
        if not folder_path:
            return
        
        # 支持的图片格式
        supported_formats = ('.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp')
        image_files = []
        
        for file in os.listdir(folder_path):
            if file.lower().endswith(supported_formats):
                image_files.append(file)
        
        # 按文件名排序
        image_files.sort()
        
        # 显示文件列表
        if image_files:
            self.files_text.insert(tk.END, f"找到 {len(image_files)} 个支持的图片文件:\n\n")
            for i, file in enumerate(image_files, 1):
                self.files_text.insert(tk.END, f"{i}. {file}\n")
        else:
            self.files_text.insert(tk.END, "未找到支持的图片文件\n")
    
    def clear_list(self):
        self.input_folder.set("")
        self.output_folder.set("")
        self.files_text.delete(1.0, tk.END)
        self.status_var.set("就绪")
        self.progress_var.set(0)
    
    def start_conversion(self):
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()
        
        if not input_folder:
            messagebox.showerror("错误", "请选择输入文件夹")
            return
        
        if not output_folder:
            messagebox.showerror("错误", "请选择输出文件夹")
            return
        
        # 在新线程中执行转换
        conversion_thread = threading.Thread(target=self.convert_images_to_pdf, args=(input_folder, output_folder))
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def convert_images_to_pdf(self, input_folder, output_folder):
        try:
            # 支持的图片格式
            supported_formats = ('.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp')
            
            # 获取所有图片文件并按名称排序
            image_files = []
            for file in os.listdir(input_folder):
                if file.lower().endswith(supported_formats):
                    image_files.append(file)
            
            image_files.sort()
            
            if not image_files:
                self.status_var.set("没有找到支持的图片文件")
                return
            
            total_files = len(image_files)
            
            for i, filename in enumerate(image_files):
                try:
                    # 更新状态
                    self.status_var.set(f"正在转换: {filename} ({i+1}/{total_files})")
                    self.progress_var.set((i / total_files) * 100)
                    
                    # 打开图片
                    img_path = os.path.join(input_folder, filename)
                    img = Image.open(img_path)
                    
                    # 转换模式（如果是RGBA或P模式）
                    if img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGB")
                    
                    # 生成PDF文件名
                    base_name = os.path.splitext(filename)[0]
                    pdf_filename = f"{base_name}.pdf"
                    pdf_path = os.path.join(output_folder, pdf_filename)
                    
                    # 保存为PDF
                    img.save(pdf_path, "PDF", resolution=100.0, save_all=True)
                    
                except Exception as e:
                    print(f"转换 {filename} 时出错: {str(e)}")
                    continue
            
            # 转换完成
            self.progress_var.set(100)
            self.status_var.set(f"转换完成! 共转换 {total_files} 个文件")
            messagebox.showinfo("完成", f"转换完成!\n共转换 {total_files} 个文件\n输出路径: {output_folder}")
            
        except Exception as e:
            self.status_var.set(f"转换失败: {str(e)}")
            messagebox.showerror("错误", f"转换过程中发生错误:\n{str(e)}")

def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToPDFConverter(root)
    
    # 设置窗口图标（如果有的话）
    try:
        icon_path = resource_path('icon.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass
    
    root.mainloop()

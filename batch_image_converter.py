import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import pillow_heif  # <-- Required for HEIC support

# Register HEIF opener to enable Pillow to read and write HEIC/HEIF files
pillow_heif.register_heif_opener()

class BatchImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Converter")
        # Increased height to accommodate the new slider
        self.root.geometry("450x300") 
        self.root.resizable(False, False)

        # Variables
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.target_format = tk.StringVar(value="JPEG")
        self.quality_var = tk.IntVar(value=100) # Default quality set to 100
        
        # Supported formats (HEIC added)
        self.formats = ["JPEG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "HEIC"]

        self.create_widgets()

    def create_widgets(self):
        # Source Directory Row
        tk.Label(self.root, text="Source Folder:").grid(row=0, column=0, padx=10, pady=15, sticky="e")
        tk.Entry(self.root, textvariable=self.source_dir, width=35).grid(row=0, column=1, padx=5, pady=15)
        tk.Button(self.root, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=10, pady=15)

        # Destination Directory Row
        tk.Label(self.root, text="Destination Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.dest_dir, width=35).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_dest).grid(row=1, column=2, padx=10, pady=5)

        # Format Selection Row
        tk.Label(self.root, text="Convert to:").grid(row=2, column=0, padx=10, pady=15, sticky="e")
        format_dropdown = ttk.Combobox(self.root, textvariable=self.target_format, values=self.formats, state="readonly", width=10)
        format_dropdown.grid(row=2, column=1, sticky="w", padx=5)

        # Quality Slider Row
        tk.Label(self.root, text="Quality (1-100):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        quality_slider = tk.Scale(self.root, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.quality_var, length=200)
        quality_slider.grid(row=3, column=1, columnspan=2, sticky="w", padx=5)

        # Convert Button (Moved to row 4)
        convert_btn = tk.Button(self.root, text="Start Batch Conversion", command=self.convert_images, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        convert_btn.grid(row=4, column=0, columnspan=3, pady=25)

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_dir.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_dir.set(folder)

    def convert_images(self):
        src = self.source_dir.get()
        dest = self.dest_dir.get()
        ext = self.target_format.get().lower()
        quality_val = self.quality_var.get()

        if not src or not dest:
            messagebox.showwarning("Missing Information", "Please select both source and destination folders.")
            return

        if not os.path.exists(dest):
            try:
                os.makedirs(dest)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create destination folder:\n{e}")
                return

        # Common image extensions to look for (Added .heic and .heif)
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif', '.heic', '.heif')
        files_to_convert = [f for f in os.listdir(src) if f.lower().endswith(valid_extensions)]

        if not files_to_convert:
            messagebox.showinfo("No Images", "No supported image files found in the source folder.")
            return

        success_count = 0
        error_count = 0

        for filename in files_to_convert:
            try:
                img_path = os.path.join(src, filename)
                img = Image.open(img_path)

                # Handle RGBA to JPEG/BMP conversion (JPEG/BMP doesn't support transparency)
                if ext in ['jpeg', 'jpg', 'bmp'] and img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[3]) # 3 is the alpha channel
                    img = background

                # Create new filename
                name_without_ext = os.path.splitext(filename)[0]
                new_filename = f"{name_without_ext}.{ext}"
                dest_path = os.path.join(dest, new_filename)

                # Save the image with quality settings if applicable
                if ext in ['jpeg', 'jpg', 'webp', 'heic']:
                    # Pillow uses the string "HEIF" to save HEIC files
                    save_format = "HEIF" if ext == 'heic' else ext.upper()
                    img.save(dest_path, format=save_format, quality=quality_val)
                else:
                    # Other formats like PNG or BMP don't use this parameter in the same way
                    img.save(dest_path, format=ext.upper())
                    
                success_count += 1
                
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")
                error_count += 1

        # Final Status Message
        msg = f"Conversion complete!\n\nSuccessfully converted: {success_count} files."
        if error_count > 0:
            msg += f"\nFailed to convert: {error_count} files (check console for details)."
        messagebox.showinfo("Done", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchImageConverter(root)
    root.mainloop()
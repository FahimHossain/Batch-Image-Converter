import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import pillow_heif

# Register HEIF opener to enable Pillow to read and write HEIC/HEIF files
pillow_heif.register_heif_opener()

# Set overall appearance and theme for CustomTkinter
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class BatchImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Converter (HEIC Supported)")
        # Increased dimensions slightly to accommodate modern widget padding
        self.root.geometry("550x350")
        self.root.resizable(False, False)

        # Determine default directories
        default_source = os.getcwd()
        default_dest = os.path.join(default_source, "converted")

        # Variables
        self.source_dir = tk.StringVar(value=default_source)
        self.dest_dir = tk.StringVar(value=default_dest)
        self.target_format = tk.StringVar(value="JPEG")
        self.quality_var = tk.IntVar(value=100)
        
        # Supported formats
        self.formats = ["JPEG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "HEIC"]

        self.create_widgets()

    def create_widgets(self):
        # Configure grid weight for better alignment
        self.root.grid_columnconfigure(1, weight=1)

        # Source Directory Row
        ctk.CTkLabel(self.root, text="Source Folder:").grid(row=0, column=0, padx=15, pady=(20, 10), sticky="e")
        ctk.CTkEntry(self.root, textvariable=self.source_dir).grid(row=0, column=1, padx=5, pady=(20, 10), sticky="ew")
        ctk.CTkButton(self.root, text="Browse", width=80, command=self.browse_source).grid(row=0, column=2, padx=15, pady=(20, 10))

        # Destination Directory Row
        ctk.CTkLabel(self.root, text="Destination Folder:").grid(row=1, column=0, padx=15, pady=10, sticky="e")
        ctk.CTkEntry(self.root, textvariable=self.dest_dir).grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        ctk.CTkButton(self.root, text="Browse", width=80, command=self.browse_dest).grid(row=1, column=2, padx=15, pady=10)

        # Format Selection Row
        ctk.CTkLabel(self.root, text="Convert to:").grid(row=2, column=0, padx=15, pady=10, sticky="e")
        format_dropdown = ctk.CTkComboBox(self.root, variable=self.target_format, values=self.formats, state="readonly", width=120)
        format_dropdown.grid(row=2, column=1, sticky="w", padx=5, pady=10)

        # Quality Slider Row
        # Note: CTkSlider uses floats, so we update a text label to show the exact integer value
        self.quality_label_text = tk.StringVar(value="Quality (100):")
        ctk.CTkLabel(self.root, textvariable=self.quality_label_text).grid(row=3, column=0, padx=15, pady=10, sticky="e")
        
        quality_slider = ctk.CTkSlider(self.root, from_=1, to=100, variable=self.quality_var, command=self.update_quality_label)
        quality_slider.grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=10)
        quality_slider.set(100) # Ensure slider visually starts at 100

        # Convert Button
        convert_btn = ctk.CTkButton(self.root, text="Start Batch Conversion", command=self.convert_images, 
                                    fg_color="#2FA572", hover_color="#1D7952", font=("Arial", 14, "bold"), height=40)
        convert_btn.grid(row=4, column=0, columnspan=3, pady=(25, 15))

    def update_quality_label(self, value):
        # Update the label text dynamically as the slider moves
        self.quality_label_text.set(f"Quality ({int(value)}):")

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder", initialdir=self.source_dir.get())
        if folder:
            self.source_dir.set(folder)
            # Automatically update destination to "converted" inside the new source folder
            self.dest_dir.set(os.path.join(folder, "converted"))

    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select Destination Folder", initialdir=self.dest_dir.get())
        if folder:
            self.dest_dir.set(folder)

    def convert_images(self):
        src = self.source_dir.get()
        dest = self.dest_dir.get()
        ext = self.target_format.get().lower()
        # CustomTkinter slider returns floats, cast to int
        quality_val = int(self.quality_var.get())

        if not src or not dest:
            messagebox.showwarning("Missing Information", "Please select both source and destination folders.")
            return

        if not os.path.exists(dest):
            try:
                os.makedirs(dest)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create destination folder:\n{e}")
                return

        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif', '.heic', '.heif')
        files_to_convert = [f for f in os.listdir(src) if f.lower().endswith(valid_extensions)]

        if not files_to_convert:
            messagebox.showinfo("No Images", f"No supported image files found in:\n{src}")
            return

        success_count = 0
        error_count = 0

        for filename in files_to_convert:
            try:
                img_path = os.path.join(src, filename)
                img = Image.open(img_path)

                # Handle RGBA to JPEG/BMP conversion
                if ext in ['jpeg', 'jpg', 'bmp'] and img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[3])
                    img = background

                name_without_ext = os.path.splitext(filename)[0]
                new_filename = f"{name_without_ext}.{ext}"
                dest_path = os.path.join(dest, new_filename)

                # Save logic
                if ext in ['jpeg', 'jpg', 'webp', 'heic']:
                    save_format = "HEIF" if ext == 'heic' else ext.upper()
                    img.save(dest_path, format=save_format, quality=quality_val)
                else:
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
    # Initialize the CustomTkinter window instead of standard tk.Tk()
    root = ctk.CTk()
    app = BatchImageConverter(root)
    root.mainloop()
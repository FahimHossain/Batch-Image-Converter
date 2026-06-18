import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import pillow_heif

# Register HEIF opener to enable Pillow to read and write HEIC/HEIF files
pillow_heif.register_heif_opener()

# Set overall appearance and theme for CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BatchImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Converter - Zenothermic")
        # Increased height slightly to fit the new footer comfortably
        self.root.geometry("600x480")
        # Made window resizable
        self.root.resizable(True, True)

        # Determine default directories and enforce Windows backslashes
        default_source = os.path.normpath(os.getcwd())
        default_dest = os.path.normpath(os.path.join(default_source, "converted"))

        # Variables (Default changed to JPG)
        self.source_dir = tk.StringVar(value=default_source)
        self.dest_dir = tk.StringVar(value=default_dest)
        self.target_format = tk.StringVar(value="JPG")
        self.quality_var = tk.IntVar(value=100)
        
        # Supported formats (JPEG changed to JPG)
        self.formats = ["JPG", "PNG", "WEBP", "BMP", "GIF", "TIFF", "HEIC"]

        self.create_widgets()

    def create_widgets(self):
        # Allow the middle column and bottom row to expand when the window is resized
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(6, weight=1)

        # Source Directory Row
        ctk.CTkLabel(self.root, text="Source Folder:").grid(row=0, column=0, padx=15, pady=(15, 10), sticky="e")
        ctk.CTkEntry(self.root, textvariable=self.source_dir).grid(row=0, column=1, padx=5, pady=(15, 10), sticky="ew")
        ctk.CTkButton(self.root, text="Browse", width=80, command=self.browse_source).grid(row=0, column=2, padx=15, pady=(15, 10))

        # Destination Directory Row
        ctk.CTkLabel(self.root, text="Destination Folder:").grid(row=1, column=0, padx=15, pady=5, sticky="e")
        ctk.CTkEntry(self.root, textvariable=self.dest_dir).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(self.root, text="Browse", width=80, command=self.browse_dest).grid(row=1, column=2, padx=15, pady=5)

        # Format Selection Row
        ctk.CTkLabel(self.root, text="Convert to:").grid(row=2, column=0, padx=15, pady=5, sticky="e")
        format_dropdown = ctk.CTkComboBox(self.root, variable=self.target_format, values=self.formats, state="readonly", width=120)
        format_dropdown.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Quality Slider Row
        self.quality_label_text = tk.StringVar(value="Quality (100):")
        ctk.CTkLabel(self.root, textvariable=self.quality_label_text).grid(row=3, column=0, padx=15, pady=5, sticky="e")
        
        # Quality Slider with fixed width
        quality_slider = ctk.CTkSlider(self.root, from_=1, to=100, width=300, variable=self.quality_var, command=self.update_quality_label)
        quality_slider.grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        quality_slider.set(100)

        # Convert Button
        self.convert_btn = ctk.CTkButton(self.root, text="Start Batch Conversion", command=self.convert_images, 
                                         fg_color="#2FA572", hover_color="#1D7952", font=("Arial", 14, "bold"), height=40)
        self.convert_btn.grid(row=4, column=0, columnspan=3, pady=(15, 10))

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.root)
        self.progress_bar.grid(row=5, column=0, columnspan=3, padx=15, pady=(5, 15), sticky="ew")
        self.progress_bar.set(0)

        # Live Activity Log TextBox
        self.log_box = ctk.CTkTextbox(self.root, state="disabled")
        self.log_box.grid(row=6, column=0, columnspan=3, padx=15, pady=(0, 15), sticky="nsew")

        # --- Footer Area (Row 7) ---
        footer_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        footer_frame.grid(row=7, column=0, columnspan=3, padx=15, pady=(0, 10), sticky="ew")
        footer_frame.grid_columnconfigure(1, weight=1) # Push footer text to the right

        # Dark Mode Toggle
        self.mode_switch = ctk.CTkSwitch(footer_frame, text="🌙", command=self.toggle_appearance)
        self.mode_switch.grid(row=0, column=0, sticky="w")
        self.mode_switch.select() # Turn the switch ON by default

        # Credits Footer
        footer_label = ctk.CTkLabel(footer_frame, text="Developed by Fahim Hossain", font=("Arial", 11, "italic"), text_color="gray")
        footer_label.grid(row=0, column=1, sticky="e")

    def toggle_appearance(self):
        """Toggles the UI between Dark and Light mode."""
        if self.mode_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def update_quality_label(self, value):
        self.quality_label_text.set(f"Quality ({int(value)}):")

    def log_message(self, message):
        """Helper method to insert text into the log box and auto-scroll."""
        self.log_box.configure(state="normal") 
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end") 
        self.log_box.configure(state="disabled") 
        self.root.update_idletasks() 

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder", initialdir=self.source_dir.get())
        if folder:
            win_path = os.path.normpath(folder)
            self.source_dir.set(win_path)
            self.dest_dir.set(os.path.normpath(os.path.join(win_path, "converted")))

    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select Destination Folder", initialdir=self.dest_dir.get())
        if folder:
            self.dest_dir.set(os.path.normpath(folder))

    def convert_images(self):
        src = self.source_dir.get()
        dest = self.dest_dir.get()
        ext = self.target_format.get().lower()
        quality_val = int(self.quality_var.get())

        if not src or not dest:
            messagebox.showwarning("Missing Information", "Please select both source and destination folders.")
            return

        self.convert_btn.configure(state="disabled")
        self.progress_bar.set(0)
        
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        if not os.path.exists(dest):
            try:
                os.makedirs(dest)
                self.log_message(f"Created destination folder: {dest}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create destination folder:\n{e}")
                self.convert_btn.configure(state="normal")
                return

        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif', '.heic', '.heif')
        files_to_convert = [f for f in os.listdir(src) if f.lower().endswith(valid_extensions)]
        total_files = len(files_to_convert)

        if total_files == 0:
            self.log_message("No supported image files found in the source folder.")
            messagebox.showinfo("No Images", f"No supported image files found in:\n{src}")
            self.convert_btn.configure(state="normal")
            return

        self.log_message(f"Found {total_files} files to convert...")
        success_count = 0
        error_count = 0

        for i, filename in enumerate(files_to_convert):
            try:
                img_path = os.path.normpath(os.path.join(src, filename))
                img = Image.open(img_path)

                # Handle RGBA to JPG/BMP conversion
                if ext in ['jpeg', 'jpg', 'bmp'] and img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[3])
                    img = background

                name_without_ext = os.path.splitext(filename)[0]
                new_filename = f"{name_without_ext}.{ext}"
                dest_path = os.path.normpath(os.path.join(dest, new_filename))

                # Save logic
                if ext in ['jpeg', 'jpg', 'webp', 'heic']:
                    # Pillow explicitly looks for 'JPEG' rather than 'JPG' as the format string
                    if ext == 'heic':
                        save_format = "HEIF"
                    elif ext == 'jpg':
                        save_format = "JPEG"
                    else:
                        save_format = ext.upper()
                        
                    img.save(dest_path, format=save_format, quality=quality_val)
                else:
                    img.save(dest_path, format=ext.upper())
                    
                success_count += 1
                self.log_message(f"[SUCCESS] Converted: {filename} -> {new_filename}")
                
            except Exception as e:
                error_count += 1
                self.log_message(f"[ERROR] Failed to convert {filename}: {e}")

            # Update progress bar
            progress = (i + 1) / total_files
            self.progress_bar.set(progress)
            self.root.update_idletasks()

        # Final Status
        self.log_message("-" * 40)
        self.log_message(f"Conversion Complete! Success: {success_count} | Errors: {error_count}")
        
        self.convert_btn.configure(state="normal")
        
        msg = f"Conversion complete!\n\nSuccessfully converted: {success_count} files."
        if error_count > 0:
            msg += f"\nFailed to convert: {error_count} files (check log for details)."
        messagebox.showinfo("Done", msg)

if __name__ == "__main__":
    root = ctk.CTk()
    app = BatchImageConverter(root)
    root.mainloop()
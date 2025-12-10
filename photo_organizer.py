import os
import shutil
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from PIL import Image

class PhotoOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("UIUPC Photo Organizer")
        self.root.geometry("600x500")
        
        # Variables
        self.source_folder = tk.StringVar()
        self.dest_folder = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar()
        
        # Supported image extensions
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="UIUPC Photo Collection System", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Source Folder Selection
        source_frame = tk.Frame(self.root)
        source_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(source_frame, text="Source Folder (with subfolders):", 
                font=("Arial", 10)).pack(anchor="w")
        
        source_entry_frame = tk.Frame(source_frame)
        source_entry_frame.pack(fill="x", pady=5)
        
        tk.Entry(source_entry_frame, textvariable=self.source_folder, 
                width=50).pack(side="left", fill="x", expand=True)
        tk.Button(source_entry_frame, text="Browse", 
                 command=self.browse_source).pack(side="right", padx=5)
        
        # Destination Folder Selection
        dest_frame = tk.Frame(self.root)
        dest_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(dest_frame, text="Destination Location:", 
                font=("Arial", 10)).pack(anchor="w")
        
        dest_entry_frame = tk.Frame(dest_frame)
        dest_entry_frame.pack(fill="x", pady=5)
        
        tk.Entry(dest_entry_frame, textvariable=self.dest_folder, 
                width=50).pack(side="left", fill="x", expand=True)
        tk.Button(dest_entry_frame, text="Browse", 
                 command=self.browse_dest).pack(side="right", padx=5)
        
        # Process Button
        process_btn = tk.Button(self.root, text="Start Processing Photos", 
                               command=self.process_photos,
                               bg="#4CAF50", fg="white",
                               font=("Arial", 12, "bold"),
                               height=2)
        process_btn.pack(pady=20)
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.root, 
                                          variable=self.progress_var,
                                          maximum=100, length=400)
        self.progress_bar.pack(pady=10)
        
        # Status Label
        status_label = tk.Label(self.root, textvariable=self.status_text,
                               font=("Arial", 10), fg="blue")
        status_label.pack(pady=5)
        
        # Log Text Area
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(log_frame, text="Process Log:", 
                font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.log_text = tk.Text(log_frame, height=8, width=70)
        self.log_text.pack(fill="both", expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder (contains subfolders with photos)")
        if folder:
            self.source_folder.set(folder)
            self.log_message(f"Source folder set: {folder}")
    
    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select Destination Location for 'SSIV ALL SUBMISSIONS' folder")
        if folder:
            self.dest_folder.set(folder)
            self.log_message(f"Destination set: {folder}")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def is_image_file(self, filename):
        return Path(filename).suffix.lower() in self.image_extensions
    
    def get_all_image_files(self, folder):
        """Recursively get all image files from folder and subfolders"""
        image_files = []
        for root_dir, dirs, files in os.walk(folder):
            for file in files:
                if self.is_image_file(file):
                    full_path = os.path.join(root_dir, file)
                    image_files.append(full_path)
        return image_files
    
    def process_photos(self):
        # Validate inputs
        if not self.source_folder.get():
            messagebox.showerror("Error", "Please select source folder!")
            return
        
        if not self.dest_folder.get():
            messagebox.showerror("Error", "Please select destination location!")
            return
        
        # Create destination folder
        dest_main_folder = os.path.join(self.dest_folder.get(), "SSIV ALL SUBMISSIONS")
        try:
            os.makedirs(dest_main_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create destination folder: {e}")
            return
        
        # Get all image files
        self.log_message("Scanning for image files...")
        all_images = self.get_all_image_files(self.source_folder.get())
        
        if not all_images:
            messagebox.showinfo("No Images", "No image files found in the source folder!")
            return
        
        # Initialize tracking
        csv_file = os.path.join(dest_main_folder, "photo_tracking.csv")
        processed_count = 0
        skipped_count = 0
        
        # Open CSV for logging
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header
            csv_writer.writerow(['Serial No', 'New File Name', 'Original File Name', 
                               'Original Folder Path', 'File Extension', 'Status'])
            
            # Process each image
            total_images = len(all_images)
            self.log_message(f"Found {total_images} image(s) to process")
            
            for idx, image_path in enumerate(all_images, 1):
                try:
                    # Update progress
                    progress = (idx / total_images) * 100
                    self.progress_var.set(progress)
                    self.status_text.set(f"Processing {idx}/{total_images}")
                    
                    # Get file info
                    original_filename = os.path.basename(image_path)
                    original_folder = os.path.dirname(image_path)
                    file_extension = Path(image_path).suffix.lower()
                    
                    # Create new filename with 3-digit serial
                    new_filename = f"UIUPC_SI_{idx:03d}{file_extension}"
                    new_filepath = os.path.join(dest_main_folder, new_filename)
                    
                    # Copy file (preserve original)
                    shutil.copy2(image_path, new_filepath)
                    
                    # Log to CSV
                    csv_writer.writerow([
                        idx,
                        new_filename,
                        original_filename,
                        original_folder,
                        file_extension,
                        'SUCCESS'
                    ])
                    
                    self.log_message(f"✓ {original_filename} → {new_filename}")
                    processed_count += 1
                    
                except Exception as e:
                    self.log_message(f"✗ Failed: {original_filename} - {str(e)}")
                    # Still log failure to CSV
                    try:
                        csv_writer.writerow([
                            idx,
                            'FAILED',
                            original_filename,
                            original_folder,
                            file_extension,
                            f'ERROR: {str(e)}'
                        ])
                    except:
                        pass
                    skipped_count += 1
                
                self.root.update()
        
        # Complete process
        self.progress_var.set(100)
        self.status_text.set("Process Complete!")
        
        # Show summary
        summary = f"""
        ╔═══════════════════════════════════╗
        ║         PROCESS COMPLETE!         ║
        ╠═══════════════════════════════════╣
        ║ Total Images Found: {total_images:>11} ║
        ║ Successfully Processed: {processed_count:>7} ║
        ║ Failed/Skipped: {skipped_count:>12} ║
        ║                                   ║
        ║ Output Folder:                    ║
        ║ {dest_main_folder[-40:]:>40} ║
        ║                                   ║
        ║ CSV Log File Created:             ║
        ║ photo_tracking.csv               ║
        ╚═══════════════════════════════════╝
        """
        
        self.log_message(summary)
        messagebox.showinfo("Success", 
                          f"Process completed!\n\n"
                          f"Processed: {processed_count} files\n"
                          f"Failed: {skipped_count} files\n\n"
                          f"Files saved to:\n{dest_main_folder}\n\n"
                          f"CSV log file created in the same folder.")

def main():
    root = tk.Tk()
    app = PhotoOrganizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
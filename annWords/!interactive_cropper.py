#!/usr/bin/env python3
"""
Interactive Outline Cropper
A GUI application that allows users to click on outlines in PNG images to crop them.
Each image can contain up to three outlines. Users can select one outline to crop or skip the image.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import glob
from pathlib import Path

class InteractiveOutlineCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Outline Cropper")
        self.root.geometry("1000x800")
        
        # Get script directory and setup paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.trimmed_dir = os.path.join(self.script_dir, "trimmed")
        self.skipped_dir = os.path.join(self.script_dir, "skipped")
        
        # Create output directories
        os.makedirs(self.trimmed_dir, exist_ok=True)
        os.makedirs(self.skipped_dir, exist_ok=True)
        
        # Initialize variables
        self.png_files = []
        self.current_index = 0
        self.current_image = None
        self.current_cv_image = None
        self.outlines = []
        self.display_scale = 1.0
        
        # Setup GUI
        self.setup_gui()
        
        # Load images
        self.load_images()
        
        # Display first image
        if self.png_files:
            self.display_current_image()
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Info label
        self.info_label = ttk.Label(main_frame, text="Loading images...", font=("Arial", 12))
        self.info_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Image canvas
        self.canvas = tk.Canvas(main_frame, bg="white", width=800, height=600)
        self.canvas.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # Buttons
        self.skip_button = ttk.Button(button_frame, text="Skip", command=self.skip_image, width=15)
        self.skip_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.prev_button = ttk.Button(button_frame, text="← Previous", command=self.previous_image, width=15)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_button = ttk.Button(button_frame, text="Next →", command=self.next_image, width=15)
        self.next_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="Click on an outline to crop it, or click 'Skip' to save the uncropped image.",
                               font=("Arial", 10))
        instructions.grid(row=4, column=0, columnspan=3, pady=(10, 0))
    
    def load_images(self):
        """Load all PNG files from the script directory"""
        self.png_files = glob.glob(os.path.join(self.script_dir, "*.png"))
        self.png_files.sort()  # Sort for consistent order
        
        if not self.png_files:
            messagebox.showwarning("No Images", "No PNG files found in the current directory.")
            return
        
        self.update_progress()
        self.info_label.config(text=f"Found {len(self.png_files)} PNG files")
    
    def find_outlines(self, image_path):
        """Find up to 3 outlines in the image"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to create binary image
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and sort by area (largest first)
        min_area = 100  # Minimum area to consider as an outline
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        valid_contours.sort(key=cv2.contourArea, reverse=True)
        
        # Take up to 3 largest contours
        selected_contours = valid_contours[:3]
        
        # Convert contours to bounding rectangles
        outlines = []
        for i, contour in enumerate(selected_contours):
            x, y, w, h = cv2.boundingRect(contour)
            # No padding - crop tight to the symbol
            x = max(0, x)
            y = max(0, y)
            w = min(img.shape[1] - x, w)
            h = min(img.shape[0] - y, h)
            
            outlines.append({
                'id': i,
                'rect': (x, y, w, h),
                'contour': contour,
                'area': cv2.contourArea(contour)
            })
        
        return outlines
    
    def display_current_image(self):
        """Display the current image with outlined regions"""
        if not self.png_files or self.current_index >= len(self.png_files):
            return
        
        current_file = self.png_files[self.current_index]
        filename = os.path.basename(current_file)
        
        # Update info
        self.info_label.config(text=f"Image {self.current_index + 1} of {len(self.png_files)}: {filename}")
        
        # Find outlines
        self.outlines = self.find_outlines(current_file)
        
        # Load image
        self.current_cv_image = cv2.imread(current_file)
        if self.current_cv_image is None:
            messagebox.showerror("Error", f"Could not load image: {filename}")
            return
        
        # Convert to RGB for display
        rgb_image = cv2.cvtColor(self.current_cv_image, cv2.COLOR_BGR2RGB)
        
        # Draw outline rectangles
        display_image = rgb_image.copy()
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Red, Green, Blue
        
        for i, outline in enumerate(self.outlines):
            x, y, w, h = outline['rect']
            color = colors[i % len(colors)]
            cv2.rectangle(display_image, (x, y), (x + w, y + h), color, 3)
            
            # Add label
            label = f"Outline {i + 1}"
            cv2.putText(display_image, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Scale image to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:  # Canvas is initialized
            img_height, img_width = display_image.shape[:2]
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            self.display_scale = min(scale_x, scale_y, 1.0)  # Don't scale up
            
            if self.display_scale < 1.0:
                new_width = int(img_width * self.display_scale)
                new_height = int(img_height * self.display_scale)
                display_image = cv2.resize(display_image, (new_width, new_height))
        
        # Convert to PIL and display
        pil_image = Image.fromarray(display_image)
        self.current_image = ImageTk.PhotoImage(pil_image)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2 if canvas_width > 1 else 400,
            canvas_height // 2 if canvas_height > 1 else 300,
            image=self.current_image
        )
        
        # Update progress
        self.update_progress()
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if not self.outlines:
            return
        
        # Convert click coordinates to image coordinates
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Calculate image position on canvas
        img_width = int(self.current_cv_image.shape[1] * self.display_scale)
        img_height = int(self.current_cv_image.shape[0] * self.display_scale)
        
        img_x = (canvas_width - img_width) // 2
        img_y = (canvas_height - img_height) // 2
        
        # Convert click to image coordinates
        click_x = int((event.x - img_x) / self.display_scale)
        click_y = int((event.y - img_y) / self.display_scale)
        
        # Check which outline was clicked
        for outline in self.outlines:
            x, y, w, h = outline['rect']
            if x <= click_x <= x + w and y <= click_y <= y + h:
                self.crop_outline(outline)
                return
    
    def crop_outline(self, outline):
        """Crop the selected outline and save it with transparent background"""
        if not self.current_cv_image.any():
            return
        
        current_file = self.png_files[self.current_index]
        filename = Path(current_file).name
        
        # Get outline bounds
        x, y, w, h = outline['rect']
        
        # Crop the image
        cropped = self.current_cv_image[y:y+h, x:x+w]
        
        # Convert to PIL for background removal
        cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cropped_rgb)
        
        # Convert to RGBA for transparency
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        
        # Convert to numpy array for processing
        img_array = np.array(pil_image)
        
        # Create mask for background removal
        gray = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2GRAY)
        
        # Background threshold - pixels above this are considered background
        background_threshold = 240
        background_mask = gray > background_threshold
        
        # Make background pixels transparent
        img_array[background_mask] = [255, 255, 255, 0]  # White with 0 alpha
        
        # Convert back to PIL Image
        transparent_img = Image.fromarray(img_array, 'RGBA')
        
        # Save cropped image with transparent background
        output_path = os.path.join(self.trimmed_dir, filename)
        transparent_img.save(output_path, "PNG")
        
        # Move to next image
        self.next_image()
    
    def skip_image(self):
        """Skip current image and save uncropped version"""
        if not self.png_files:
            return
        
        current_file = self.png_files[self.current_index]
        filename = Path(current_file).name
        
        # Copy uncropped image to skipped folder
        import shutil
        output_path = os.path.join(self.skipped_dir, filename)
        shutil.copy2(current_file, output_path)
        
        # Move to next image
        self.next_image()
    
    def next_image(self):
        """Move to next image"""
        if self.current_index < len(self.png_files) - 1:
            self.current_index += 1
            self.display_current_image()
        else:
            messagebox.showinfo("Complete", "All images have been processed!")
    
    def previous_image(self):
        """Move to previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()
    
    def update_progress(self):
        """Update the progress bar"""
        if self.png_files:
            progress = ((self.current_index + 1) / len(self.png_files)) * 100
            self.progress_var.set(progress)

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = InteractiveOutlineCropper(root)
    root.mainloop()

if __name__ == "__main__":
    main()

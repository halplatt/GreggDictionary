import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImageDistanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Distance Tool")
        self.image_folder = os.getcwd()
        self.image_files = [f for f in os.listdir(self.image_folder) if f.lower().endswith('.png')]
        self.filtered_files = self.image_files.copy()
        self.current_image = None
        self.current_image_name = None
        self.tk_image = None

        # Search bar
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.update_filter)
        search_entry = ttk.Entry(root, textvariable=self.search_var, width=40)
        search_entry.pack(padx=8, pady=8, anchor='nw')

        # Listbox for images
        self.listbox = tk.Listbox(root, width=40, height=25)
        self.listbox.pack(side='left', fill='y', padx=(8,0), pady=8)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        # Image display area
        self.image_panel = tk.Label(root)
        self.image_panel.pack(side='left', padx=8, pady=8)
        self.image_panel.bind('<Button-1>', self.on_image_click)

        self.update_listbox()

    def update_filter(self, *args):
        search = self.search_var.get().lower()
        if search:
            self.filtered_files = [f for f in self.image_files if search in f.lower()]
        else:
            self.filtered_files = self.image_files.copy()
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for fname in self.filtered_files:
            self.listbox.insert(tk.END, fname)

    def on_select(self, event):
        if not self.listbox.curselection():
            return
        idx = self.listbox.curselection()[0]
        fname = self.filtered_files[idx]
        self.show_image(fname)

    def show_image(self, fname):
        img_path = os.path.join(self.image_folder, fname)
        try:
            img = Image.open(img_path)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Cannot open image: {e}")
            return
        self.current_image = img
        self.current_image_name = fname
        # Resize for display if too large
        max_size = (600, 600)
        display_img = img.copy()
        display_img.thumbnail(max_size, Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(display_img)
        self.image_panel.config(image=self.tk_image)
        self.image_panel.image = self.tk_image
        self.display_scale = img.height / display_img.height
        self.display_offset = (display_img.width, display_img.height)

    def on_image_click(self, event):
        if not self.current_image:
            return
        # Map click to original image coordinates
        display_w, display_h = self.tk_image.width(), self.tk_image.height()
        orig_w, orig_h = self.current_image.width, self.current_image.height
        scale = orig_h / display_h
        click_y = int(event.y * scale)
        distance = orig_h - click_y
        if distance < 0:
            distance = 0  # If clicked below the image, use 0
        # Save result
        base, _ = os.path.splitext(self.current_image_name)
        txt_path = os.path.join(self.image_folder, f"{base}.txt")
        with open(txt_path, 'w') as f:
            f.write(str(distance))
        # Optional: show feedback
        self.root.title(f"Saved distance: {distance} px for {self.current_image_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDistanceApp(root)
    root.mainloop()
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class ImageDistanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Distance Tool")
        self.image_folder = os.getcwd()
        self.image_files = [
            f for f in os.listdir(self.image_folder)
            if f.lower().endswith('.png')
            and not f.lower().endswith('.tag.png')
            and not os.path.exists(os.path.join(self.image_folder, os.path.splitext(f)[0] + '.txt'))
        ]     
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
            self.filtered_files = [
                f for f in self.image_files
                if f.lower().startswith(search)
                and not os.path.exists(os.path.join(self.image_folder, os.path.splitext(f)[0] + '.txt'))
            ]
        else:
            self.filtered_files = [
                f for f in self.image_files
                if not os.path.exists(os.path.join(self.image_folder, os.path.splitext(f)[0] + '.txt'))
            ]
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

    def show_image(self, fname, line_y=None):
        img_path = os.path.join(self.image_folder, fname)
        try:
            img = Image.open(img_path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open image: {e}")
            return
        self.current_image = img
        self.current_image_name = fname
        max_size = (600, 600)
        display_img = img.copy()
        display_img.thumbnail(max_size, Image.LANCZOS)
    
        # If no line_y provided, check for .txt file and use its value
        if line_y is None:
            txt_path = os.path.join(self.image_folder, os.path.splitext(fname)[0] + '.txt')
            if os.path.exists(txt_path):
                try:
                    with open(txt_path, 'r') as f:
                        value = int(f.read().strip())
                    # Map original y to display y
                    scale = display_img.height / img.height
                    line_y = int(img.height - value) * scale
                except Exception:
                    line_y = None
    
        # Draw line if requested
        if line_y is not None:
            draw = ImageDraw.Draw(display_img)
            draw.line([(0, int(line_y)), (display_img.width, int(line_y))], fill="red", width=2)
    
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
        # Draw horizontal line at click position on display image
        self.show_image(self.current_image_name, line_y=event.y)

        # Advance to next item in the list
        current_idx = self.filtered_files.index(self.current_image_name)
        if current_idx + 1 < len(self.filtered_files):
            next_idx = current_idx + 1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(next_idx)
            self.listbox.activate(next_idx)
            self.show_image(self.filtered_files[next_idx])

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDistanceApp(root)
    root.mainloop()
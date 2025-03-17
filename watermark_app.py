import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import os


class WatermarkApp:
    """A GUI application for adding watermarks to images."""

    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Image Watermarking App")

        self.canvas = tk.Canvas(root, width=600, height=400)
        self.canvas.pack()

        self.upload_btn = tk.Button(root, text="Upload Image",
                                    command=self.upload_image)
        self.upload_btn.pack(pady=10)

        self.font_btn = tk.Button(self.root, text="Watermark Properties",
                                  command=self.open_properties)
        self.font_btn.pack(pady=5)

        self.watermark_btn = tk.Button(self.root, text="Add Watermark",
                                       command=self.add_watermark)
        self.watermark_btn.pack(pady=5)

        self.save_btn = tk.Button(self.root, text="Save Image",
                                  command=self.save_image)
        self.save_btn.pack(pady=5)

        # Default font settings
        self.selected_font = "Arial"
        self.selected_size = 24
        self.selected_color = "#feffff"
        self.selected_color_text = "#FEFFFF"
        self.selected_opacity = 64
        self.selected_rotation = 0
        self.selected_position = "center"
        self.tile_watermark = False
        self.watermark_type = "text"
        self.logo_path = None
        self.watermark_text = "Enter Watermark Text"

    def upload_image(self):
        """Upload an image file."""
        f_path = filedialog.askopenfilename(initialdir='./assets/',
                                            title='Select File',
                                            filetypes=[("Image Files",
                                                        "*.png"),
                                                       ("Image Files",
                                                        "*.jpg"),
                                                       ("Image Files",
                                                        "*.jpeg")])
        if f_path:
            self.image = Image.open(f_path)
            self.display_image(self.image)

    def display_image(self, img):
        """Display the image on the canvas."""
        img.thumbnail((400, 400))
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(300, 200, image=self.tk_img)

    def add_watermark(self):
        """Add a watermark to the image."""
        if hasattr(self, "image"):
            watermark = Image.new("RGBA", self.image.size)
            draw = ImageDraw.Draw(watermark)
            rgba_color = self.hex_to_rgba(self.selected_color,
                                          self.selected_opacity)
            if self.watermark_type == "text":
                self.add_text_watermark(draw, rgba_color)
            elif self.watermark_type == "logo" and self.logo_path:
                self.add_logo_watermark(watermark)

            watermark = watermark.rotate(self.selected_rotation, expand=1)
            self.image.paste(watermark, (0, 0), watermark)
            self.display_image(self.image)

    def add_text_watermark(self, draw, rgba_color):
        """Add a text watermark to the image."""
        text = self.watermark_text
        font = ImageFont.truetype(f"{self.selected_font}.ttf",
                                  self.selected_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        if self.tile_watermark:
            for y in range(0, self.image.size[1], text_height + 10):
                for x in range(0, self.image.size[0], text_width + 10):
                    draw.text((x, y), text, fill=rgba_color, font=font)
        else:
            position = self.calculate_position(text_width, text_height)
            draw.text(position, text, fill=rgba_color, font=font)

    def add_logo_watermark(self, watermark):
        """Add a logo watermark to the image."""
        logo = Image.open(self.logo_path).convert("RGBA")
        logo = logo.resize((self.selected_size,
                            self.selected_size), Image.LANCZOS)
        logo = self.apply_opacity(logo, self.selected_opacity)

        if self.tile_watermark:
            for y in range(0, self.image.size[1], logo.size[1] + 10):
                for x in range(0, self.image.size[0], logo.size[0] + 10):
                    watermark.paste(logo, (x, y), logo)
        else:
            position = self.calculate_position(logo.size[0], logo.size[1])
            watermark.paste(logo, position, logo)

    def calculate_position(self, width, height):
        """Calculate the position for the watermark."""
        positions = {
            "top-left": (10, 10),
            "top-center": ((self.image.size[0] - width) // 2, 10),
            "top-right": (self.image.size[0] - width - 10, 10),
            "center-left": (10, (self.image.size[1] - height) // 2),
            "center": ((self.image.size[0] - width) // 2,
                       (self.image.size[1] - height) // 2),
            "center-right": (self.image.size[0] - width - 10,
                             (self.image.size[1] - height) // 2),
            "bottom-left": (10, self.image.size[1] - height - 10),
            "bottom-center": ((self.image.size[0] - width) // 2,
                              self.image.size[1] - height - 10),
            "bottom-right": (self.image.size[0] - width - 10,
                             self.image.size[1] - height - 10),
        }
        return positions.get(self.selected_position, (10, 10))

    def apply_opacity(self, image, opacity):
        """Apply opacity to an image."""
        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity / 255.0)
        image.putalpha(alpha)
        return image

    def hex_to_rgba(self, hex_color, opacity):
        """Convert hex color to RGBA."""
        hex_color = hex_color.lstrip('#')
        lv = len(hex_color)
        rgb = tuple(int(hex_color[i:i + lv // 3], 16)
                    for i in range(0, lv, lv // 3))
        return rgb + (opacity,)

    def save_image(self):
        """Save the watermarked image."""
        if hasattr(self, "image"):
            save_path = filedialog.asksaveasfilename(initialdir='./output/',
                                                     defaultextension=".png",
                                                     filetypes=[("PNG Files",
                                                                 "*.png"),
                                                                ("JPEG Files",
                                                                 "*.jpg")])
            if save_path:
                self.image.save(save_path)
                messagebox.showinfo("Success", "Image saved successfully!")

    def open_properties(self):
        """Open the watermark properties dialog."""
        properties = tk.Toplevel(self.root)
        properties.title("Watermark Properties")
        properties.geometry("600x900")

        font_list = sorted(font.families())
        slf_path = "/System/Library/Fonts/"
        valid_fonts = [f for f in font_list
                       if os.path.exists(f"/Library/Fonts/{f}.ttf")
                       or os.path.exists(f"{slf_path}Supplemental/{f}.ttf")
                       or os.path.exists(f"{slf_path}{f}.ttf")]
        font_var = tk.StringVar(value=self.selected_font)
        size_var = tk.IntVar(value=self.selected_size)
        opacity_var = tk.IntVar(value=self.selected_opacity)
        rotation_var = tk.IntVar(value=self.selected_rotation)
        position_var = tk.StringVar(value=self.selected_position)
        tile_var = tk.BooleanVar(value=self.tile_watermark)
        watermark_type_var = tk.StringVar(value=self.watermark_type)
        text_var = tk.StringVar(value=self.watermark_text)

        def update_font(event=None):
            self.selected_font = font_var.get()
            self.selected_size = size_var.get()
            self.selected_opacity = opacity_var.get()
            self.selected_rotation = rotation_var.get()
            self.selected_position = position_var.get()
            self.tile_watermark = tile_var.get()
            self.watermark_type = watermark_type_var.get()
            self.watermark_text = text_var.get()
            # Update the sample text label
            label.config(font=(self.selected_font, self.selected_size))

        def choose_color():
            color_code = colorchooser.askcolor(title="Choose Text Color")[1]
            if color_code:
                self.selected_color = color_code
                self.selected_color_text = color_code.upper()
                # Update the button background color
                color_label.config(text=self.selected_color_text,
                                   bg=self.selected_color)

        def upload_logo():
            logo_path = filedialog.askopenfilename(initialdir='./assets/',
                                                   title='Select Logo',
                                                   filetypes=[("Image Files",
                                                               "*.png"),
                                                              ("Image Files",
                                                               "*.jpg"),
                                                              ("Image Files",
                                                               "*.jpeg")])
            if logo_path:
                self.logo_path = logo_path
                path_text = self.logo_path[-40:]
                ttk.Label(properties,
                          text=path_text).grid(row=16, column=1,
                                               padx=5, pady=5, sticky="w")

        ttk.Label(properties,
                  text="Size:").grid(row=0, column=0,
                                     padx=5, pady=5, sticky="e")
        size_scale = tk.Scale(properties,
                              from_=1, to=100,
                              orient="horizontal",
                              variable=size_var,
                              command=update_font,
                              length=300, resolution=1)
        size_scale.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(properties,
                  text="Opacity:").grid(row=1, column=0,
                                        padx=5, pady=5, sticky="e")
        opacity_scale = tk.Scale(properties,
                                 from_=0, to=255,
                                 orient="horizontal",
                                 variable=opacity_var,
                                 command=update_font,
                                 length=300, resolution=1)
        opacity_scale.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(properties,
                  text="Rotation:").grid(row=2, column=0,
                                         padx=5, pady=5, sticky="e")
        rotation_scale = tk.Scale(properties,
                                  from_=0, to=360,
                                  orient="horizontal",
                                  variable=rotation_var,
                                  command=update_font,
                                  length=300, resolution=45)
        rotation_scale.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(properties,
                  text="Position:").grid(row=3, column=0,
                                         padx=5, pady=5, sticky="e")
        position_combo = ttk.Combobox(properties,
                                      textvariable=position_var,
                                      values=["top-left", "top-center",
                                              "top-right", "center-left",
                                              "center", "center-right",
                                              "bottom-left", "bottom-center",
                                              "bottom-right"],
                                      state="readonly")
        position_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        position_combo.bind("<<ComboboxSelected>>", update_font)

        tile_check = ttk.Checkbutton(properties,
                                     text="Tile Watermark",
                                     variable=tile_var, command=update_font)
        tile_check.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Label(properties,
                  text="Watermark Type:").grid(row=5, column=0,
                                               padx=5, pady=5, sticky="e")
        text_radio = ttk.Radiobutton(properties, text="Text",
                                     variable=watermark_type_var,
                                     value="text", command=update_font)
        text_radio.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        logo_radio = ttk.Radiobutton(properties, text="Logo",
                                     variable=watermark_type_var,
                                     value="logo", command=update_font)
        logo_radio.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Separator
        line = ("-" * 70)
        ttk.Label(properties, text=line).grid(row=7, column=0, columnspan=3)

        ttk.Label(properties,
                  text="TEXT - ATTRIBUTES").grid(row=8, column=0,
                                                 padx=5, pady=5, sticky="e")

        ttk.Label(properties,
                  text="Enter Watermark Text:").grid(row=9, column=0,
                                                     padx=5, pady=5,
                                                     sticky="e")
        text_entry = tk.Entry(properties, textvariable=text_var, width=30)
        text_entry.grid(row=9, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(properties,
                  text="Select Font:").grid(row=10, column=0,
                                            padx=5, pady=5, sticky="e")
        combo = ttk.Combobox(properties,
                             textvariable=font_var,
                             values=valid_fonts, state="readonly")
        combo.grid(row=10, column=1, padx=5, pady=5, sticky="w")
        combo.bind("<<ComboboxSelected>>", update_font)

        color_button = ttk.Button(properties,
                                  text="Choose Font Color",
                                  command=choose_color)
        color_button.grid(row=11, column=0, columnspan=2, pady=10)
        # Create a button with custom colors
        color_label = tk.Label(properties,
                               text=self.selected_color.upper(),
                               bg=self.selected_color, fg="#000000")
        color_label.grid(row=11, column=0, padx=5, pady=5, sticky="e")

        # Create a label to display the selected font
        label = ttk.Label(properties,
                          text="Sample Text",
                          font=(self.selected_font, self.selected_size))
        label.grid(row=12, column=0, columnspan=2, padx=5, pady=20)

        # Separator
        ttk.Label(properties, text=line).grid(row=13, column=0, columnspan=3)

        ttk.Label(properties,
                  text="LOGO - ATTRIBUTES").grid(row=15, column=0,
                                                 padx=5, pady=5, sticky="e")

        ttk.Label(properties,
                  text="Logo File:").grid(row=16, column=0,
                                          padx=5, pady=5, sticky="e")
        if self.logo_path:
            path_text = self.logo_path[-40:]
            ttk.Label(properties,
                      text=path_text).grid(row=16, column=1,
                                           padx=5, pady=5, sticky="w")

        logo_button = ttk.Button(properties, text="Upload Logo",
                                 command=upload_logo)
        logo_button.grid(row=17, column=0, columnspan=2, pady=10)

        properties.grid_columnconfigure(0, weight=1)
        properties.grid_columnconfigure(1, weight=1)

        def on_close():
            update_font()
            properties.destroy()

        properties.protocol("WM_DELETE_WINDOW", on_close)


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()

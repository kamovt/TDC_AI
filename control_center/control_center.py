import os
import psutil
import customtkinter as ctk
import pygetwindow as gw
import time

from .settings import settings

import threading

def cclaunch():

    threading.Thread(
        target=lambda: ControlCenter().mainloop(),
        daemon=True
    ).start()

class ControlCenter(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Lumina")
        self.geometry("260x260")

        self.create_subtitle_window()
        
        self.resizable(False, False)
        self.attributes("-topmost", True)

        # Process used for CPU/RAM
        self.process = psutil.Process(os.getpid())

        # --------------------
        # Title
        # --------------------

        ctk.CTkLabel(
            self,
            text="ChatBot",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(10, 15))

        # --------------------
        # Switches
        # --------------------

        self.vision_var = ctk.BooleanVar(value=settings.vision)
        self.tts_var = ctk.BooleanVar(value=settings.tts)
        self.avatar_var = ctk.BooleanVar(value=settings.avatar)
        self.memory_var = ctk.BooleanVar(value=settings.memory)
        self.voice_var = ctk.BooleanVar(value=settings.VOICE_MODE)

        ctk.CTkSwitch(
            self,
            text="Vision",
            variable=self.vision_var,
            command=self.update_settings
        ).pack(anchor="w", padx=20)

        ctk.CTkSwitch(
            self,
            text="Voice",
            variable=self.tts_var,
            command=self.update_settings
        ).pack(anchor="w", padx=20)

        ctk.CTkSwitch(
            self,
            text="Avatar",
            variable=self.avatar_var,
            command=self.update_settings
        ).pack(anchor="w", padx=20)

        ctk.CTkSwitch(
            self,
            text="Memory",
            variable=self.memory_var,
            command=self.update_settings
        ).pack(anchor="w", padx=20)

        ctk.CTkSwitch(
            self,
            text="User Voice",
            variable=self.voice_var,
            command=self.update_settings
        ).pack(anchor="w", padx=20)

        # --------------------
        # Separator
        # --------------------

        ctk.CTkFrame(
            self,
            height=2
        ).pack(fill="x", padx=15, pady=15)

        # --------------------
        # Stats
        # --------------------

        self.cpu_label = ctk.CTkLabel(
            self,
            text="CPU: --%"
        )
        self.cpu_label.pack()

        self.ram_label = ctk.CTkLabel(
            self,
            text="RAM: --%"
        )
        self.ram_label.pack()

        self.update_stats()

    def update_settings(self):

        settings.vision = self.vision_var.get()
        settings.tts = self.tts_var.get()
        settings.avatar = self.avatar_var.get()
        settings.memory = self.memory_var.get()
        settings.VOICE_MODE = self.voice_var.get()
       
    def update_stats(self):

        cpu = psutil.cpu_percent()

        psutil.virtual_memory()
        dict(psutil.virtual_memory()._asdict())

        ram = psutil.virtual_memory().percent

        self.cpu_label.configure(
            text=f"CPU: {cpu:.1f}%"
        )

        self.ram_label.configure(
            text=f"RAM: {ram:.0f}%"
        )

        if hasattr(self, 'subtitle_window'):
            self.subtitle_window.lift()
            
        self.after(
            1000,
            self.update_stats
        )

    def create_subtitle_window(self):

        self.subtitle_window = ctk.CTkToplevel(self)

        self.subtitle_window.title("Lumina Subtitle")
        self.subtitle_window.attributes('-topmost', True)
        self.subtitle_window.attributes('-toolwindow', True)  


        # Subtitle size
        width = 600
        height = 160

        # Get primary monitor size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Padding from edges
        margin_x = -30
        margin_y = 40

        # Bottom-right position
        x = screen_width - width - margin_x
        y = screen_height - height - margin_y

        self.subtitle_window.geometry(
            f"{width}x{height}+{x}+{y}"
        )

        self.subtitle_window.overrideredirect(True)

        # Make the window background transparent
        self.subtitle_window.configure(
            fg_color="black"
        )

        self.subtitle_window.attributes(
            "-transparentcolor",
            "black"
        )

        self.subtitle_window.attributes(
            "-topmost",
            True
        )

        self.subtitle_label = ctk.CTkLabel(
            self.subtitle_window,
            text="",
            font=("Nacional Park", 28, "bold"),
            fg_color="black",
            text_color="white",
            wraplength=560,
            justify="center"
        )

        self.subtitle_label.pack(
            expand=True,
            fill="both"
        )

        from subtitle import subtitle

        subtitle.connect(
            self.subtitle_label
        )

    
if __name__ == "__main__":

    app = ControlCenter()
    app.mainloop()
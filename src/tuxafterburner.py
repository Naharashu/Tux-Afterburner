#!/usr/bin/env python3
import customtkinter as ctk 
import platform
import pyautogui
import api
from PIL import Image
import sys
import os

os_ = platform.system()


if os_ != "Linux":
    pyautogui.alert("Tux afterburner is supported only on desktop linux systems", "System error")
    exit(1)

PLATFORM = api.get_gpu_name()

def get_asset_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

PATH = ""
if(PLATFORM=="Nvidia"):
    PATH = get_asset_path("imgs/NVIDIA_.png")
#elif PLATFORM == "AMD":
else:
    PATH = get_asset_path("imgs/AMD.png")




ctk.set_appearance_mode("dark")
app = ctk.CTk()


app.title("Tux Afterburner - " + api.get_gpu_name())
app.geometry("600x480")
textbox = ctk.CTkTextbox(app, 300, 105)
textbox.pack(pady=20)
textbox.place(x=0)
textbox.place(y=10)


my_image = ctk.CTkImage(
    light_image=Image.open(PATH), 
    dark_image=Image.open(PATH), 
    size=(250, 100)
)


def stat():
    textbox.configure(state="normal")
    textbox.delete("0.0", "end")
    textbox.insert("0.0", "Core temperature: " + str(api.get_temp()) + " °C"
        + "\nVRAM temperature: " + api.get_temp_vram()
        + "\nVRAM total: " + str(api.get_vram()) 
        + "\nVRAM free: " + str(api.get_vram_free())
        + "\nFans speed: " + str(api.get_gpu_fan_speed()) + " rpm"
    )
    textbox.configure(state="disabled")
    app.after(1000, stat)

image_label = ctk.CTkLabel(app, image=my_image, text="")
image_label.place(x=320, y=10) 

image_label.image = my_image 


stat()

app.mainloop()

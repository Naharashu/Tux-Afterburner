#!/usr/bin/env python3
#import customtkinter as ctk 
import platform
import pyautogui
import api
import sys
import os
import flet as ft
import threading
import time

os_ = platform.system()


if os_ != "Linux":
    pyautogui.alert("Tux afterburner is supported only on desktop linux systems", "System error")
    exit(1)

PLATFORM = api.detect_platform(0)

def get_asset_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

PATH = ""
if PLATFORM == "Nvidia":
    PATH = get_asset_path("assets/NVIDIA.png")
elif PLATFORM == "AMD":
    PATH = get_asset_path("assets/AMD.png")
else:
    pyautogui.alert("Intel Graphics are not currently supported", "Support warning")
    PATH = get_asset_path("assets/INTEL.jpg")

"""

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


ctk.set_appearance_mode("dark")
app = ctk.CTk()


app.title("Tux Afterburner - " + api.get_gpu_name())
app.geometry("600x480")
textbox = ctk.CTkTextbox(app, 280, 105)
textbox.pack(pady=20)
textbox.place(x=0)
textbox.place(y=10)

raw_img = Image.open(PATH)
if raw_img.mode != "RGBA":
    raw_img = raw_img.convert("RGBA")


image = ctk.CTkImage(
    light_image=raw_img.copy(), 
    dark_image=raw_img.copy(), 
    size=(100, 100)
)

app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure(0, weight=1)



textbox.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
#image.gri (row=0, column=1, sticky="nsew", padx=20, pady=20)







image_label = ctk.CTkLabel(app, image=image, text="")
image_label.place(x=320, y=10) 

image_label.image = image 

image_label.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

stat()

app.mainloop()

"""



def main(page: ft.Page):
    page.title = "TuxAfterburner - " + api.get_gpu_name()
    page.window.width = 600
    page.window.height = 480
    page.theme_mode = page.theme_mode.DARK
    img = ft.Image(
        src=PATH,
        fit=ft.BoxFit.SCALE_DOWN,
        expand=True              
    )

    

    def stat():
        return "Core temperature: " + str(api.get_temp()) + " °C" + "\nVRAM temperature: " + api.get_temp_vram() + "\nVRAM total: " + str(api.get_vram())  + "\nVRAM free: " + str(api.get_vram_free()) + "\nFans speed: " + str(api.get_gpu_fan_speed()) + " rpm"

    statistic = ft.Text(value=stat())

    async def update_stat():
        import asyncio
        while page.session.id is not None:
            statistic.value = stat()
            page.update()
            await asyncio.sleep(0.5)

    page.run_task(update_stat)
    

    page.add(ft.Row(
        controls=[
        statistic,
        img
        ],
        #expand=True
    ))

    
    fanSpeedChange = ft.Slider(label="Fan speed %", value=api.__get_fan_speed(), min=0, max=100, round=0)
    labelFan = ft.Text("Fan Speed " + str(fanSpeedChange.value) + " %")


    async def update_fan_text():
        import asyncio
        __fanSpeedCache = api.get_gpu_fan_speed()
        while page.session.id is not None:
            if __fanSpeedCache != fanSpeedChange.value:
                api.set_fan_speed(fanSpeedChange.value)
                labelFan.value = f"Fan Speed {fanSpeedChange.value:.0f} %"
                page.update()
            await asyncio.sleep(0.05)

    page.run_task(update_fan_text)
    
    page.add(ft.Row(
        controls=[
        labelFan,
        fanSpeedChange
        ]
    ))

    def handle_events(e: ft.WindowEvent):
        if e == ft.WindowEventType.CLOSE:
            cleanup()
        
    ft.Window.prevent_close = True
    page.window.on_event = handle_events

    def cleanup():
        if(PLATFORM=="Nvidia"):
            api.pynvml.nvmlShutdown()
        elif(PLATFORM=="AMD"):
            api.amdsmi.amdsmi_shut_down()
        print("Exiting...")
        ft.Window.destroy()


ft.run(main) 

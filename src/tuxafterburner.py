#!/usr/bin/env python3
import customtkinter as ctk 
import platform
import pyautogui
import api

os = platform.system()


if os != "Linux":
    pyautogui.alert("Tux afterburner is supported only on desktop linux systems", "System error")
    exit(1)



ctk.set_appearance_mode("dark")
app = ctk.CTk()


app.title("Tux Afterburner - " + api.get_gpu_name())
app.geometry("600x480")
textbox = ctk.CTkTextbox(app, 600, 100)
textbox.pack(pady=20)

def stat():
    textbox.configure(state="normal")
    textbox.delete("0.0", "end")
    textbox.insert("0.0", "Temperature: " + str(api.get_temp()) + " C"
        + "\nVRAM total: " + str(api.get_vram()) 
        + "\nVRAM free: " + str(api.get_vram_free())
    )
    textbox.configure(state="disabled")
    app.after(1000, stat)
    
stat()

app.mainloop()

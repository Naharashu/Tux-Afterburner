#!/usr/bin/env python3
import customtkinter as ctk 
import platform
import pyautogui
import api

os = platform.system()


if os != "Linux":
    pyautogui.alert("Tux afterburner is supported only on desktop linux systems", "System error")
    exit(1)

textbox = ctk.CTkTextbox(app)
textbox.insert("0.0", "Temp: " + api.get_temp)

ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Tux Afterburner")
app.geometry("600x480")
app.mainloop()

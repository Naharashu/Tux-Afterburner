import pynvml
import pyamdgpuinfo
import pyautogui


def is_int(n):
    try:
        float(n)
        return True
    except ValueError:
        return False

def detect_platform(n):
    try:
        pynvml.nvmlInit()
        return "Nvidia"
    except Exception:
        try:
            import amdsmi
            pyamdgpuinfo.get_gpu(n)
            return "AMD"
        except Exception:
            return "Unknown"


def get_gpu_series(n):
    manufact = detect_platform(n)
    if manufact == "Unknown":
        raise RuntimeError("Unknown GPU found")
    
    if manufact == "Nvidia":
        # Nvidia
        pynvml.nvmlInit()
        name = pynvml.nvmlDeviceGetName(pynvml.nvmlDeviceGetHandleByIndex(n)) # For example NVIDIA GeForce GTX 1650 SUPER
        modele = name[14:]
        if "GT " in modele:
            pyautogui.alert("GT series GPU`s are not currently supported", "Support Error")
            exit(1)
        
        series_number = "" # for example GTX 1650 -> 1650
        for c in modele[3:]: # Skips GTX/RTX
            if not is_int(c):
                break
            series_number += c
        
        series_number = int(series_number)
        if series_number<=640:
            pyautogui.alert("GTX 640 and below are not supported", "Support Error")
            exit(1)

        return series_number

    else:
        # AMD
        amdsmi.amdsmi_init()
        temp = amdsmi.amdsmi_get_gpu_asic_info()
        name = temp.get("market_name") # for example AMD Radeon RX 9060
        if "FirePro" in name:
            pyautogui.alert("FirePro gpu`s are not supported", "Support Error")
            exit(1)
        modele = name[13:] if "Pro" not in name else name[15:] 
        for c in modele:
            if not is_int(c):
                break
            series_number += c
        return int(series_number)


def get_temp():
    PLATRFORM = detect_platform(0)
    if PLATRFORM == "Unknown":
        return 0;
    elif PLATRFORM == "Nvidia":
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        return pynvml.nvmlDeviceGetTemperature(
            handle,
            pynvml.NVML_TEMPERATURE_GPU
        )
    else:
        return 0

def get_vram():
    PLATRFORM = detect_platform(0)
    if PLATRFORM == "Unknown":
        return 0;
    elif PLATRFORM == "Nvidia":
        info = pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(0))
        return info.total/1000000
    else:
        return 0

def get_vram_free():
    PLATRFORM = detect_platform(0)
    if PLATRFORM == "Unknown":
        return 0;
    elif PLATRFORM == "Nvidia":
        info = pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(0))
        return info.free/1000000
    else:
        return 0


def get_gpu_name():
    PLATRFORM = detect_platform(0)
    if PLATRFORM == "Unknown":
        return "Unknown GPU";
    elif PLATRFORM == "Nvidia":
        return pynvml.nvmlDeviceGetName(pynvml.nvmlDeviceGetHandleByIndex(0))
    else:
        amdsmi.amdsmi_init()
        return amdsmi.amdsmi_get_gpu_asic_info().get("market_name")
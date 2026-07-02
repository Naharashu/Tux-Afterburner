import pynvml
import pyautogui
import subprocess
import random
try:
    import amdsmi
except ImportError:
    raw = subprocess.run(["lspci"], capture_output=True, text=True)
    res = subprocess.run(["grep", "-E", "VGA|3D"], input=raw.stdout, capture_output=True, text=True)
    if "AMD" not in res.stdout or "Advanced Micro Devices" not in res.stdout:
        pyautogui.alert(
            "For AMD gpus, amdsmi have to be installed\n"
            + "\nDebian/Ubuntu: sudo apt install amd-smi-lib"
            + "\nFedora: sudo dnf install amdsmi rocm-smi rocminfo"
            + "\nArch: sudo pacman -S amdsmi",
            "Dependency error",
            "exit"
        )
        exit(1)

def is_int(n):
    try:
        float(n)
        return True
    except ValueError:
        return False

GPU_MANUF = ""


def detect_platform(n):
    global GPU_MANUF
    if GPU_MANUF != "": 
        return GPU_MANUF
    try:
        pynvml.nvmlInit()
        pynvml.nvmlDeviceGetHandleByIndex(0)
        GPU_MANUF = "Nvidia"
        return "Nvidia"
    except Exception:
        try:
            amdsmi.amdsmi_init()
            devices = amdsmi.amdsmi_get_processor_handles()
            if len(devices) == 0:
                GPU_MANUF = "Unknown"
                return "Unknown"
            GPU_MANUF = "Unknown"
            return "AMD"
        except Exception:
            GPU_MANUF = "Unknown"
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
        devices = amdsmi.amdsmi_get_processor_handles()
        temp = amdsmi.amdsmi_get_gpu_asic_info(devices[0])
        name = temp.get("market_name") # for example AMD Radeon RX 9060
        if "FirePro" in name:
            pyautogui.alert("FirePro gpu`s are not supported", "Support Error")
            exit(1)
        series_number = ""
        modele = name[13:] if "Pro" not in name else name[15:] 
        for c in modele:
            if not is_int(c):
                break
            series_number += c
        return int(series_number)


def get_temp():
    PLATFORM = detect_platform(0)
    if PLATFORM == "Unknown":
        return random.randint(1,60);
    elif PLATFORM == "Nvidia":
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)

        return pynvml.nvmlDeviceGetTemperature(
            handle,
            pynvml.NVML_TEMPERATURE_GPU
        )
    else:
        # AMD
        devices = amdsmi.amdsmi_get_processor_handles()
        temp = amdsmi.amdsmi_get_temp_metric(devices[0], amdsmi.AmdSmiTemperatureType.EDGE, amdsmi.AmdSmiTemperatureMetric.CURRENT)/1000
        return round(temp, 1)

def get_vram():
    PLATFORM = detect_platform(0)
    if PLATFORM == "Unknown":
        return 0;
    elif PLATFORM == "Nvidia":
        info = pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(0))
        return round(info.total/1000000, 2)
    else:
        # AMD
        devices = amdsmi.amdsmi_get_processor_handles()
        info = amdsmi.amdsmi_get_gpu_vram_usage(devices[0])
        return round(info.get("vram_total"), 2)

def get_vram_free():
    PLATFORM = detect_platform(0)
    if PLATFORM == "Unknown":
        return 0;
    elif PLATFORM == "Nvidia":
        info = pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(0))
        return round(info.free/1000000, 2)
    else:
        # AMD
        devices = amdsmi.amdsmi_get_processor_handles()
        info = amdsmi.amdsmi_get_gpu_vram_usage(devices[0])
        return round(info.get("vram_total")-info.get("vram_used"), 2)


def get_gpu_name():
    PLATFORM = detect_platform(0)
    if PLATFORM == "Unknown":
        return "Unknown GPU";
    elif PLATFORM == "Nvidia":
        return pynvml.nvmlDeviceGetName(pynvml.nvmlDeviceGetHandleByIndex(0))
    else:
        devices = amdsmi.amdsmi_get_processor_handles()
        return amdsmi.amdsmi_get_gpu_asic_info(devices[0]).get("market_name")

def get_gpu_fan_speed():
    PLATFORM = detect_platform(0)
    if PLATFORM == "Unknown":
        return 0;
    elif PLATFORM == "Nvidia":
        info = pynvml.nvmlDeviceGetFanSpeedRPM(pynvml.nvmlDeviceGetHandleByIndex(0))
        return info
    else:
        # AMD
        devices = amdsmi.amdsmi_get_processor_handles()
        info = amdsmi.amdsmi_get_gpu_fan_rpms(devices[0], 0)
        return info

def get_temp_vram():
    PLATFORM = detect_platform(0)
    if PLATFORM == "Unknown":
        return "0 °C"
    elif PLATFORM == "Nvidia":
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        
        values = pynvml.nvmlDeviceGetFieldValues(handle, [pynvml.NVML_FI_DEV_MEMORY_TEMP])
        field = values[0]
        if field.nvmlReturn == pynvml.NVML_SUCCESS:
            return str(field.value.uiVal) + " °C"
        else:
            return "Unsupported"
    else:
        # AMD
        devices = amdsmi.amdsmi_get_processor_handles()
        temp = amdsmi.amdsmi_get_temp_metric(devices[0], amdsmi.AmdSmiTemperatureType.VRAM , amdsmi.AmdSmiTemperatureMetric.CURRENT)/1000
        return str(round(temp, 1)) + " °C"


def set_fan_speed(speed):
    PLATFORM = detect_platform(0)
    if PLATFORM == "Unknown":
        return
    elif PLATFORM == "Nvidia":
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        i = pynvml.nvmlDeviceGetNumFans(handle)
        for j in range(i):
            try:
                pynvml.nvmlDeviceSetFanSpeed_v2(handle, j, speed)
            except Exception as e:
                pyautogui.alert(e, "NVML Internal Error")
                print(e)
    else:
        # AMD
        try:
            devices = amdsmi.amdsmi_get_processor_handles()
            amdsmi.amdsmi_set_gpu_fan_speed(devices[0], 0, amdsmi.amdsmi_get_gpu_fan_speed_max(devices[0])*speed/100)
        except amdsmi.AmdSmiException as e:
            pyautogui.alert(e, "AMD Internal Error")


def __get_fan_speed():
    PLATFORM = detect_platform(0)
    if PLATFORM == "Unknown":
        return 0
    elif PLATFORM == "Nvidia":
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        return pynvml.nvmlDeviceGetFanSpeed(handle) 
    else:
        # AMD
        try:
            devices = amdsmi.amdsmi_get_processor_handles()
            curr = amdsmi.amdsmi_get_gpu_fan_speed(devices[0], 0)
            max = amdsmi.amdsmi_get_gpu_fan_speed_max(devices[0], 0)
            return curr / max * 100
        except amdsmi.AmdSmiException as e:
            pyautogui.alert(e, "AMD Internal Error")


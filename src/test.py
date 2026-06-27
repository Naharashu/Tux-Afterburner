import pynvml

pynvml.nvmlInit()

device_count = pynvml.nvmlDeviceGetCount()

for i in range(device_count):
    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
    print(i)
    print(pynvml.nvmlDeviceGetName(handle))
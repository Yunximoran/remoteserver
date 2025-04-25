import psutil
import platform

# 本机信息
NODE = platform.node()
OS = platform.system()
VERSION = platform.version()
MACHINE = platform.machine()
RAM = psutil.virtual_memory().total / (1024 ** 3)

# CPU信息
PROCESSOR = platform.processor()
PHYSICALCORES = psutil.cpu_count(logical=False)
LOGICALCORES = psutil.cpu_count(logical=True)
ARCHITECTURE = platform.architecture()[0]

if OS == "Windows":
    from .windows import Windows as System
elif OS == "Linux":
    from .linux import Linux as System
elif OS == "MacOS":
    from .macos import MacOS as System
else:
    raise "系统标识错误"

SYSTEM = System()
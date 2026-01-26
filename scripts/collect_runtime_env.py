import platform
import psutil
import sys

def collect_runtime_env():
    print("Collecting Runtime Environment Information...")
    print("-" * 40)
    
    # OS
    print(f"OS: {platform.system()} {platform.release()}")
    
    # CPU
    # cpu_count = psutil.cpu_count(logical=False)
    # logical_count = psutil.cpu_count(logical=True)
    # print(f"CPU Cores: {cpu_count} physical, {logical_count} logical")
    try:
        # Mac specific
        if platform.system() == "Darwin":
            import subprocess
            brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).strip().decode()
            print(f"CPU Model: {brand}")
        elif platform.system() == "Linux":
             with open('/proc/cpuinfo') as f:
                for line in f:
                    if "model name" in line:
                        print(f"CPU Model: {line.split(':')[1].strip()}")
                        break
        else:
            print(f"CPU Architecture: {platform.machine()}")
    except Exception as e:
        print(f"Could not determine CPU model: {e}")

    # Memory
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3)
    print(f"RAM: {total_gb:.2f} GB")

    # Python
    print(f"Python Version: {sys.version.split()[0]}")
    print("-" * 40)

if __name__ == "__main__":
    collect_runtime_env()

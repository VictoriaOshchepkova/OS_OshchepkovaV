import os
import socket


def PrintOSInfo():
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith("PRETTY_NAME"):
                    print(f"OS: {line.split('=', 1)[1].strip().strip('"')}")
    except:
        print("OS: Unknown")

def PrintKernel():
    print(f"Kernel: {os.uname().release}")

def GetArchitecture():
    print(f"Architecture: {os.uname().machine}")

def PrintHostname():
    print(f"Hostname: {socket.gethostname()}")

def PrintUsername():
    print(f"Username: {os.getlogin()}")

def PrintMemoryInfo():
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                key, value = line.split(':', 1)
                value = int(value.strip().split()[0]) // 1024
                if key == 'MemFree':
                    freeMem = value
                elif key =='MemTotal':
                    totalMem = value
                elif key =='SwapFree':
                    swapFree = value
                elif key =='SwapTotal':
                    swapTotal = value
                elif key =='VmallocTotal':
                    virtualMem = value

        print(f"RAM: {freeMem} MB free / {totalMem} MB total")
        print(f"Swap: {swapFree} MB free / {swapTotal} MB total")
        print(f"Virtual memory: {virtualMem//1024} MB")
    except:
        print("RAM: Unknown")
        print("Swap: Unknown")
        print("Virtual memory: Unknown")

def PrintProcessorCount():
    print("Logical processors: ", os.cpu_count())

def PrintLoadAVG():
    try:
        with open('/proc/loadavg', 'r') as f:
            data = f.read().split()
            print(f"Load average: {data[0]}, {data[1]}, {data[2]}")
    except:
        print(f"Load average: Unknown")

def PrintDriveInfo():
    print("Drives:")
    try:
        with open('/proc/mounts', 'r') as f:
            for line in f:
                parts = line.split()
                device, mountPoint, type = parts[0], parts[1], parts[2]
                
                if type in ['ext2', 'ext3', 'ext4', 'jfs', 'reiserfs', 'xfs', 'btrfs', 'zfs', 'fuse']:
                    try:
                        stat = os.statvfs(mountPoint)
                        freeMem = (stat.f_bavail * stat.f_frsize) / (1024**3)
                        totalMem = (stat.f_blocks * stat.f_frsize) / (1024**3)
                        
                        print(f"  {mountPoint} {type} {int(freeMem)}GB free / {int(totalMem)}GB total")
                    except:
                        continue
    except:
        print("Unknown")

PrintOSInfo()
PrintKernel()
GetArchitecture()
PrintHostname()
PrintUsername()
PrintMemoryInfo()
PrintProcessorCount()
PrintLoadAVG()
PrintDriveInfo()

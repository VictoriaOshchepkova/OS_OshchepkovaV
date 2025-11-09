using System;
using System.Runtime.InteropServices;
using System.Text;

class SysInfoWin
{
    static void Main(string[] args)
    {
        try
        {
            PrintOSInfo();
            PrintComputerAndUserInfo();
            PrintProcessorArchitecture();
            PrintMemoryInfo();
            Console.WriteLine();
            PrintProcessorCount();
            PrintDriveInfo();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }

        Console.ReadKey();
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct OSVERSIONINFOEX
    {
        public uint dwOSVersionInfoSize;
        public uint dwMajorVersion;
        public uint dwMinorVersion;
        public uint dwBuildNumber;
        public uint dwPlatformId;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
        public string szCSDVersion;

        public ushort wServicePackMajor;
        public ushort wServicePackMinor;
        public ushort wSuiteMask;
        public byte wProductType;
        public byte wReserved;
    }

    [DllImport("ntdll.dll")]
    public static extern int RtlGetVersion(ref OSVERSIONINFOEX versionInfo);

    static void PrintOSInfo()
    {
        var versionInfo = new OSVERSIONINFOEX();
        versionInfo.dwOSVersionInfoSize = (uint)Marshal.SizeOf(typeof(OSVERSIONINFOEX));

        int result = RtlGetVersion(ref versionInfo);

        if (result == 0)
        {
            if (versionInfo.dwMajorVersion == 10)
                Console.WriteLine("OS: Windows 10 or Greater");
            else if (versionInfo.dwMajorVersion == 6 && versionInfo.dwMinorVersion == 3)
                Console.WriteLine("OS: Windows 8.1");
            else if (versionInfo.dwMajorVersion == 6 && versionInfo.dwMinorVersion == 2)
                Console.WriteLine("OS: Windows 8");
            else if (versionInfo.dwMajorVersion == 6 && versionInfo.dwMinorVersion == 1)
                Console.WriteLine("OS: Windows 7");
            else if (versionInfo.dwMajorVersion == 6 && versionInfo.dwMinorVersion == 0)
                Console.WriteLine("OS: Windows Vista");
            else if (versionInfo.dwMajorVersion == 5 && versionInfo.dwMinorVersion == 1)
                Console.WriteLine("OS: Windows XP");
            else
                Console.WriteLine("OS: Unknown");
        }
        else
        {
            throw new Exception($"Failed to get OS version");
        }
    }

    [DllImport("kernel32.dll")]
    static extern uint GetComputerName(StringBuilder lpBuffer, ref uint lpnSize);

    [DllImport("advapi32.dll")]
    static extern bool GetUserName(StringBuilder lpBuffer, ref uint lpnSize);

    static void PrintComputerAndUserInfo()
    {
        uint bufferSize = 256;
        StringBuilder computerName = new StringBuilder((int)bufferSize);
        if (GetComputerName(computerName, ref bufferSize) != 0)
        {
            Console.WriteLine($"Computer Name: {computerName}");
        }
        else
        {
            throw new Exception("Failed to get computer name");
        }

        bufferSize = 256;
        StringBuilder userName = new StringBuilder((int)bufferSize);
        if (GetUserName(userName, ref bufferSize))
        {
            Console.WriteLine($"User: {userName}");
        }
        else
        {
            throw new Exception("Failed to get user name");
        }
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct SYSTEM_INFO
    {
        public ushort wProcessorArchitecture;
        public ushort wReserved;
        public uint dwPageSize;
        public IntPtr lpMinimumApplicationAddress;
        public IntPtr lpMaximumApplicationAddress;
        public IntPtr dwActiveProcessorMask;
        public uint dwNumberOfProcessors;
        public uint dwProcessorType;
        public uint dwAllocationGranularity;
        public ushort wProcessorLevel;
        public ushort wProcessorRevision;
    }

    [DllImport("kernel32.dll")]
    static extern void GetNativeSystemInfo(ref SYSTEM_INFO lpSystemInfo);

    static void PrintProcessorArchitecture()
    {
        var systemInfo = new SYSTEM_INFO();
        GetNativeSystemInfo(ref systemInfo);

        switch (systemInfo.wProcessorArchitecture)
        {
            case 9:
                Console.WriteLine($"Architecture: x64 (AMD64)");
                break;
            case 5:
                Console.WriteLine($"Architecture: ARM"); 
                break;
            case 12:
                Console.WriteLine($"Architecture: ARM64");
                break;
            case 6:
                Console.WriteLine($"Architecture: Intel Itanium-based");
                break;
            case 0:
                Console.WriteLine($"Architecture: x86");
                break;
            default:
                Console.WriteLine($"Architecture: Unknown");
                break;
        }
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
    public struct MEMORYSTATUSEX
    {
        public uint dwLength;
        public uint dwMemoryLoad;
        public ulong ullTotalPhys;
        public ulong ullAvailPhys;
        public ulong ullTotalPageFile;
        public ulong ullAvailPageFile;
        public ulong ullTotalVirtual;
        public ulong ullAvailVirtual;
        public ulong ullAvailExtendedVirtual;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool GlobalMemoryStatusEx(ref MEMORYSTATUSEX lpBuffer);

    static void PrintMemoryInfo()
    {
        var memoryStatus = new MEMORYSTATUSEX();
        memoryStatus.dwLength = (uint)Marshal.SizeOf(typeof(MEMORYSTATUSEX));

        if (GlobalMemoryStatusEx(ref memoryStatus))
        {
            ulong usedPhys = memoryStatus.ullTotalPhys - memoryStatus.ullAvailPhys;

            Console.WriteLine($"RAM: {usedPhys / (1024 * 1024)}MB / {memoryStatus.ullTotalPhys / (1024 * 1024)}MB");
            Console.WriteLine($"Virtual Memory: {memoryStatus.ullTotalPageFile / (1024 * 1024)}MB");
            Console.WriteLine($"Memory Load: {memoryStatus.dwMemoryLoad}%");
            Console.WriteLine($"Pagefile: {(memoryStatus.ullTotalPageFile - memoryStatus.ullTotalPhys) / (1024 * 1024)}MB");
        }
        else
        {
            throw new Exception("Failed to get memory information");
        }
    }

    [DllImport("kernel32.dll")]
    internal static extern void GetSystemInfo(ref SYSTEM_INFO lpSystemInfo);

    static void PrintProcessorCount()
    {
        var systemInfo = new SYSTEM_INFO();
        GetSystemInfo(ref systemInfo);

        Console.WriteLine($"Processors: {systemInfo.dwNumberOfProcessors}");
    }

    [DllImport("kernel32.dll")]
    static extern uint GetLogicalDriveStrings(uint nBufferLength, [Out] StringBuilder lpBuffer);

    [DllImport("kernel32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool GetDiskFreeSpaceEx(string lpDirectoryName, out ulong lpFreeBytesAvailable, out ulong lpTotalNumberOfBytes, out ulong lpTotalNumberOfFreeBytes);

    [DllImport("Kernel32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public extern static bool GetVolumeInformation(string rootPathName, StringBuilder volumeNameBuffer, int volumeNameSize, out uint volumeSerialNumber, out uint maximumComponentLength, out uint fileSystemFlags, StringBuilder fileSystemNameBuffer, int nFileSystemNameSize);

    static void PrintDriveInfo()
    {
        uint bufferLength = 256;
        StringBuilder driveStrings = new StringBuilder((int)bufferLength);
        uint result = GetLogicalDriveStrings(bufferLength, driveStrings);

        if (result == 0)
        {
            throw new Exception("Failed to get drive information");
        }

        Console.WriteLine("Drives:");
        string[] drives = driveStrings.ToString().Split('\0');

        foreach (string drive in drives)
        {
            if (string.IsNullOrEmpty(drive)) 
                continue;

            string fileSystem = GetFileSystemType(drive);

            if (GetDiskFreeSpaceEx(drive, out ulong freeBytes, out ulong totalBytes, out ulong _))
            {
                Console.WriteLine($"  - {drive}  ({fileSystem}): {Math.Round(freeBytes / (1024.0 * 1024.0 * 1024.0))} GB free / {Math.Round(totalBytes / (1024.0 * 1024.0 * 1024.0))} GB total");
            }
            else
            {
                Console.WriteLine($"  - {drive}  ({fileSystem}): Unknown");
            }
        }
    }

    static string GetFileSystemType(string drivePath)
    {
        StringBuilder volumeName = new StringBuilder(256);
        StringBuilder fileSystemName = new StringBuilder(256);

        bool success = GetVolumeInformation(drivePath, volumeName, volumeName.Capacity, out uint _, out uint _, out uint _, fileSystemName, fileSystemName.Capacity);

        if (success)
        {
            return fileSystemName.ToString();
        }
        else
        {
            return "Unknown";
        }
    }
}



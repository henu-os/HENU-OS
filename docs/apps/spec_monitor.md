# HENU OS Application Specification: henu-monitor

> **System Component: System Monitor & Resource Viewer**  
> **Package Identifier: henu-monitor**  
> **Status: Specification Draft**

---

## 1. Purpose
Provides real-time graphs and detail lists for system resources usage, processor temperatures, network load, active process threads, and GPU rendering levels.

## 2. Features
- **Process List Grid**: Sortable lists showing memory, CPU usage, and PID stats.
- **Resource Performance Charts**: Live scrolling charts for hardware outputs.
- **Process Controller**: Terminate (SIGKILL), pause (SIGSTOP), or resume (SIGCONT) operations.

## 3. Dependencies
- `python3-psutil`
- `libadwaita`
- `lm_sensors`

## 4. Permissions
- **System Information**: Read access to `/proc` and `/sys` virtual file systems.
- **Process Signals**: Access right to terminate processes (wheel group authentication needed for system processes).

## 5. User Interface (UI)
Multi-tab GTK window with graphs (CPU, Memory, Network, Disk) and filterable task lists.

## 6. Future Roadmap
- Display active temperature maps for core CPUs.
- Dynamic RAM flush trigger configurations.

import subprocess
import os
import json
import psutil
from typing import Dict, Any, List
from .base_agent import BaseAgent
from crewai import Agent


class SystemAgent(BaseAgent):
    """Specialized agent for system administration and performance optimization tasks."""
    
    def __init__(self, name: str = "SystemAdmin", complexity: float = 0.5):
        super().__init__(
            name=name,
            role="System Administrator",
            goal="Diagnose and optimize system performance, manage services, and maintain server health",
            backstory="An experienced system administrator skilled in Linux server management, performance optimization, and troubleshooting system issues."
        )
        self.complexity = complexity
    
    def create_crew_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=True,
            allow_delegation=False
        )
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """Execute actual system administration tasks."""
        self.logger.info(f"Executing system task: {task_description}")
        
        try:
            # Determine task type and execute appropriate commands
            if "performance" in task_description.lower() or "optimize" in task_description.lower():
                result = self._optimize_performance()
            elif "service" in task_description.lower():
                result = self._analyze_services()
            elif "memory" in task_description.lower():
                result = self._analyze_memory()
            elif "disk" in task_description.lower():
                result = self._analyze_disk()
            elif "network" in task_description.lower():
                result = self._analyze_network()
            else:
                # General system analysis
                result = self._general_system_analysis()
            
            return {
                "agent_id": self.id,
                "agent_name": self.name,
                "task": task_description,
                "status": "completed",
                "output": result,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"System task failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "agent_id": self.id,
                "agent_name": self.name,
                "task": task_description,
                "status": "failed",
                "output": None,
                "error": error_msg
            }
    
    def _run_command_safe(self, command: str, timeout: int = 30) -> str:
        """Safely execute a system command with timeout and error handling."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,      
                text=True,
                timeout=timeout,
                check=False  # Don't raise exception on non-zero exit
            )
            return result.stdout.strip() if result.stdout else result.stderr.strip()
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Command execution error: {str(e)}"
    
    def _optimize_performance(self) -> Dict[str, Any]:
        """Analyze and optimize system performance."""
        analysis = {}
        
        # CPU Analysis
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        analysis["cpu"] = {
            "usage_percent": cpu_percent,
            "core_count": cpu_count,
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
        # Memory Analysis
        memory = psutil.virtual_memory()
        analysis["memory"] = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_percent": memory.percent,
            "free_gb": round(memory.free / (1024**3), 2)
        }
        
        # Disk Analysis
        disk_usage = psutil.disk_usage('/')
        analysis["disk"] = {
            "total_gb": round(disk_usage.total / (1024**3), 2),
            "used_gb": round(disk_usage.used / (1024**3), 2),
            "free_gb": round(disk_usage.free / (1024**3), 2),
            "used_percent": round((disk_usage.used / disk_usage.total) * 100, 2)
        }
        
        # Process Analysis
        processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                          key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:10]
        analysis["top_processes"] = [
            {
                "pid": p.info['pid'],
                "name": p.info['name'],
                "cpu_percent": p.info['cpu_percent'] or 0,
                "memory_percent": round(p.info['memory_percent'] or 0, 2)
            }
            for p in processes
        ]
        
        # System uptime
        boot_time = psutil.boot_time()
        uptime_seconds = psutil.time.time() - boot_time
        analysis["uptime_hours"] = round(uptime_seconds / 3600, 2)
        
        # Performance recommendations
        recommendations = []
        
        if cpu_percent > 80:
            recommendations.append("High CPU usage detected. Consider identifying resource-heavy processes.")
        
        if memory.percent > 85:
            recommendations.append("High memory usage detected. Consider restarting memory-intensive services or adding more RAM.")
        
        if disk_usage.used / disk_usage.total > 0.9:
            recommendations.append("Disk space is running low. Consider cleaning up old files or adding storage.")
        
        analysis["recommendations"] = recommendations
        
        # Try to get additional system info
        try:
            analysis["system_info"] = {
                "kernel": self._run_command_safe("uname -r"),
                "distribution": self._run_command_safe("lsb_release -d 2>/dev/null | cut -f2") or 
                               self._run_command_safe("cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2").strip('"'),
                "architecture": self._run_command_safe("uname -m")
            }
        except:
            pass
        
        return analysis
    
    def _analyze_services(self) -> Dict[str, Any]:
        """Analyze running services and their status."""
        services_info = {}
        
        # Get systemd services status
        services_output = self._run_command_safe("systemctl list-units --type=service --state=running --no-pager --plain")
        running_services = []
        
        for line in services_output.split('\n')[1:]:  # Skip header
            if line.strip() and not line.startswith('●'):
                parts = line.split()
                if len(parts) >= 4:
                    running_services.append({
                        "name": parts[0],
                        "state": parts[2],
                        "status": parts[3]
                    })
        
        services_info["running_services_count"] = len(running_services)
        services_info["sample_services"] = running_services[:10]  # Show first 10
        
        # Check for failed services
        failed_output = self._run_command_safe("systemctl list-units --type=service --state=failed --no-pager --plain")
        failed_services = []
        
        for line in failed_output.split('\n')[1:]:
            if line.strip() and '●' in line:
                parts = line.split()
                if len(parts) >= 4:
                    failed_services.append({
                        "name": parts[1],
                        "state": parts[3],
                        "status": parts[4] if len(parts) > 4 else "failed"
                    })
        
        services_info["failed_services"] = failed_services
        
        return services_info
    
    def _analyze_memory(self) -> Dict[str, Any]:
        """Detailed memory analysis."""
        memory_info = {}
        
        # System memory
        vm = psutil.virtual_memory()
        memory_info["virtual_memory"] = {
            "total": vm.total,
            "available": vm.available,
            "percent": vm.percent,
            "used": vm.used,
            "free": vm.free
        }
        
        # Swap memory
        swap = psutil.swap_memory()
        memory_info["swap"] = {
            "total": swap.total,
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent
        }
        
        # Memory usage by process
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "memory_mb": round(proc.info['memory_info'].rss / (1024**2), 2),
                    "memory_percent": round(proc.info['memory_percent'], 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by memory usage and get top 10
        processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        memory_info["top_memory_processes"] = processes[:10]
        
        return memory_info
    
    def _analyze_disk(self) -> Dict[str, Any]:
        """Detailed disk analysis."""
        disk_info = {}
        
        # Disk usage for all mounted filesystems
        partitions = psutil.disk_partitions()
        disk_usage = []
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": round((usage.used / usage.total) * 100, 2)
                })
            except PermissionError:
                continue
        
        disk_info["disk_usage"] = disk_usage
        
        # Disk I/O statistics
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_info["io_stats"] = {
                    "read_bytes": disk_io.read_bytes,
                    "write_bytes": disk_io.write_bytes,
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count
                }
        except:
            pass
        
        return disk_info
    
    def _analyze_network(self) -> Dict[str, Any]:
        """Network analysis."""
        network_info = {}
        
        # Network interfaces
        interfaces = psutil.net_if_addrs()
        interface_stats = {}
        
        for interface_name, addresses in interfaces.items():
            interface_stats[interface_name] = []
            for addr in addresses:
                interface_stats[interface_name].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
        
        network_info["interfaces"] = interface_stats
        
        # Network I/O statistics
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                network_info["io_stats"] = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
        except:
            pass
        
        return network_info
    
    def _general_system_analysis(self) -> Dict[str, Any]:
        """General system analysis combining multiple aspects."""
        return {
            "performance": self._optimize_performance(),
            "services": self._analyze_services(),
            "summary": "Complete system analysis performed including CPU, memory, disk, and service status."
        }
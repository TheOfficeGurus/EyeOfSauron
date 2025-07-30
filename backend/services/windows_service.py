# import wmi
from backend.exceptions.APIException import InvalidRequestError
import backend.utils.helpers as message

# def  connect_to_sql_server(server_name):
#     try:
#         c = wmi.WMI(computer=server_name)
#         return c
#     except Exception as e:
#         message.error_response(f"Server Not Found:{server_name}: {e}",404)
#         return None
        

# def get_server_stats(wmi_connection):
#     if not wmi_connection:
#         return message.error_response("WMI connection is not established.")
        
#     try:
#         # CPU
#         cpu_info = wmi_connection.Win32_Processor()[0]
        
#         # Memory
#         os_info = wmi_connection.Win32_OperatingSystem()[0]
#         total_mem = int(os_info.TotalVisibleMemorySize) * 1024
#         free_mem = int(os_info.FreePhysicalMemory) * 1024
#         used_mem_percent = ((total_mem - free_mem) / total_mem) * 100
        
#         # Disk C:
#         disk_c = wmi_connection.Win32_LogicalDisk(DeviceID="C:")[0]
#         disk_total = int(disk_c.Size)
#         disk_free = int(disk_c.FreeSpace)
#         disk_used_percent = ((disk_total - disk_free) / disk_total) * 100
        
#         # SQL Services
#         sql_services = []
#         for service in wmi_connection.Win32_Service():
#             if 'SQL' in service.Name.upper():
#                 sql_services.append({
#                     'name': service.Name,
#                     'status': service.State,
#                     'start_mode': service.StartMode
#                 })
        
#         return {
#             'cpu_percent': cpu_info.LoadPercentage or 0,
#             'memory_percent': round(used_mem_percent, 2),
#             'memory_total_gb': round(total_mem / (1024**3), 2),
#             'disk_percent': round(disk_used_percent, 2),
#             'disk_total_gb': round(disk_total / (1024**3), 2),
#             'sql_services': sql_services
#         }
        
#     except InvalidRequestError as e:
#         return message.error_response(str(e.message))
#### testing linux #### 
import paramiko
import json
import re

def get_linux_stats_ssh(hostname, username, password=None, key_path=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Conectar con password o key
        if key_path:
            ssh.connect(hostname, username=username, key_filename=key_path)
        else:
            ssh.connect(hostname, username=username, password=password)
        
        stats = {}
        
        # CPU
        stdin, stdout, stderr = ssh.exec_command("grep 'cpu ' /proc/stat")
        cpu_line = stdout.read().decode().strip()
        # Parsear CPU usage...
        
        # Memoria
        stdin, stdout, stderr = ssh.exec_command("free -m")
        mem_output = stdout.read().decode()
        
        # Disco
        stdin, stdout, stderr = ssh.exec_command("df -h /")
        disk_output = stdout.read().decode()
        
        # Load average
        stdin, stdout, stderr = ssh.exec_command("uptime")
        uptime_output = stdout.read().decode()
        
        # Parsear outputs y construir stats dict...
        return cpu_line
        
    except Exception as e:
        print(f"Error SSH: {e}")
        return message.error_response("error conectando")
    finally:
        ssh.close()
from concurrent.futures import ThreadPoolExecutor
import json
from pypsrp.wsman import WSMan
from pypsrp.powershell import PowerShell, RunspacePool
import subprocess
from backend.services.cache_service import CacheService
cache_service = CacheService()

def get_disk_info_cached(server_fqdn):
    """Versión con cache del get_disk_info"""
    cache_key = cache_service.generate_key(server_fqdn, "disk")
    
    # Intentar obtener del cache
    cached_data = cache_service.get(cache_key)
    if cached_data:
        return cached_data
    
    # Si no está en cache, obtener datos
    data = get_disk_info(server_fqdn)
    
    # Guardar en cache por 30 minutos
    if data:
        cache_service.set(cache_key, data, 1800)
    
    return data
def get_updates_info(server_fqdn):
    commands = {
        "updates": r""" # Función para verificar si hay un reboot pendiente
            function Test-PendingReboot {
                $rebootPending = $false
                $rebootReasons = @()
                
                # Verificar Windows Update
                try {
                    $wu = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired" -ErrorAction SilentlyContinue
                    if ($wu) {
                        $rebootPending = $true
                        $rebootReasons += "Windows Update"
                    }
                } catch {}
                
                # Verificar Component Based Servicing
                try {
                    $cbs = Get-ChildItem "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending" -ErrorAction SilentlyContinue
                    if ($cbs) {
                        $rebootPending = $true
                        $rebootReasons += "Component Based Servicing"
                    }
                } catch {}
                
                # Verificar PendingFileRenameOperations
                try {
                    $pfro = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager" -Name "PendingFileRenameOperations" -ErrorAction SilentlyContinue
                    if ($pfro -and $pfro.PendingFileRenameOperations) {
                        $rebootPending = $true
                        $rebootReasons += "Pending File Rename Operations"
                    }
                } catch {}
                
                # Verificar usando WMI para CCM_ClientSDK (si SCCM está instalado)
                try {
                    $sccm = Invoke-WmiMethod -Namespace "ROOT\ccm\ClientSDK" -Class "CCM_ClientUtilities" -Name "DetermineIfRebootPending" -ErrorAction SilentlyContinue
                    if ($sccm -and ($sccm.RebootPending -or $sccm.IsHardRebootPending)) {
                        $rebootPending = $true
                        $rebootReasons += "SCCM Client"
                    }
                } catch {}
                
                return @{
                    IsPending = $rebootPending
                    Reasons = $rebootReasons
                }
            }

            # Script principal para obtener actualizaciones y estado de reboot
            $updateSession = New-Object -ComObject Microsoft.Update.Session                
            $updateSearcher = $updateSession.CreateUpdateSearcher()                
            $searchResult = $updateSearcher.Search("IsInstalled=0")

            # Obtener lista de actualizaciones pendientes
            $updatesList = @()
            foreach ($update in $searchResult.Updates) {
                # Extraer KB de diferentes fuentes
                $kbNumber = ""
                if ($update.KBArticleIDs -and $update.KBArticleIDs.Count -gt 0) {
                    $kbNumber = ($update.KBArticleIDs -join ", ")
                } elseif ($update.Title -match "KB(\d+)") {
                    $kbNumber = $matches[1]
                }
                
                $updatesList += [PSCustomObject]@{
                    Title = $update.Title
                    KB    = $kbNumber
                    Size  = [math]::Round($update.MaxDownloadSize / 1MB, 2)
                    IsDownloaded = $update.IsDownloaded
                    RebootRequired = $update.RebootRequired
                    Description = $update.Description
                    Categories = ($update.Categories | ForEach-Object { $_.Name }) -join ", "
                    SeverityText = if ($update.MsrcSeverity) { $update.MsrcSeverity } else { "Not Specified" }
                    ReleaseDate = if ($update.LastDeploymentChangeTime) { 
                        $update.LastDeploymentChangeTime.ToString("yyyy-MM-dd") 
                    } else { 
                        "Unknown" 
                    }
                }
            }

            # Verificar estado de reboot pendiente
            $rebootStatus = Test-PendingReboot

            # Crear objeto resultado completo
            $result = [PSCustomObject]@{
                PendingUpdates = $updatesList
                UpdatesCount = $updatesList.Count
                RebootStatus = [PSCustomObject]@{
                    IsPending = $rebootStatus.IsPending
                    Reasons = $rebootStatus.Reasons -join ", "
                    ReasonsList = $rebootStatus.Reasons
                }
                Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }

            # Convertir a JSON y retornar
        return $result | ConvertTo-Json -Depth 4 -AsArray
        """
    }

    results = {}

    for name, ps_script in commands.items():
        ps_script = (
            f"Invoke-Command -ComputerName {server_fqdn} -ScriptBlock {{{ps_script}}}"
        )
        results[name] = subprocess.run(
            ["powershell", "-Command", ps_script], capture_output=True, text=True
        )
        if results[name].returncode != 0:
            results[name] = f"Error: {results[name].stderr.strip()}"
        else:
            results[name] = results[name].stdout.strip()
    return results

def get_disk_info(server_fqdn):
    commands = {
        "disk": """
            Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
            $sizeGB = [math]::Round($_.Size / 1GB, 2)
            $freeGB = [math]::Round($_.FreeSpace / 1GB, 2)
            $usedGB = [math]::Round($sizeGB - $freeGB, 2)
            $VolumeName = $_.VolumeName

            $percentUsed = if ($_.Size -gt 0) {
                [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 1)
            } else { 0 }

            $percentFree = 100 - $percentUsed

            [PSCustomObject]@{
                DeviceID       = $_.DeviceID
                SizeGB         = $sizeGB
                FreeSpaceGB    = $freeGB
                UsedSpaceGB    = $usedGB
                PercentUsed    = "$percentUsed`%"
                PercentFree    = "$percentFree`%"
                VolumeName = "$VolumeName"
            } } | ConvertTo-Json -Depth 3 -AsArray
        """
    }

    results = {}

    for name, ps_script in commands.items():
        ps_script = (
            f"Invoke-Command -ComputerName {server_fqdn} -ScriptBlock {{{ps_script}}}"
        )
        results[name] = subprocess.run(
            ["powershell", "-Command", ps_script], capture_output=True, text=True
        )
        if results[name].returncode != 0:
            results[name] = f"Error: {results[name].stderr.strip()}"
        else:
            results[name] = results[name].stdout.strip()
    return results

def get_sql_services_info(server_fqdn):
    commands = {
        "services": """
            Get-Service | Where-Object { $_.Name -like '*SQL*' } | ForEach-Object {
            $statusMap = @{
                1 = "Stopped"; 2 = "StartPending"; 3 = "StopPending"
                4 = "Running"; 5 = "ContinuePending"; 6 = "PausePending"; 7 = "Paused"
            }
            $startTypeMap = @{
                0 = "Boot"; 1 = "System"; 2 = "Automatic"; 3 = "Manual"; 4 = "Disabled"
            }

            [PSCustomObject]@{
                Name      = $_.Name
                Status    = $statusMap[$_.Status.value__]
                StartType = $startTypeMap[$_.StartType.value__]
            } } | ConvertTo-Json -Depth 3 -AsArray
        """
    }

    results = {}

    for name, ps_script in commands.items():
        ps_script = (
            f"Invoke-Command -ComputerName {server_fqdn} -ScriptBlock {{{ps_script}}}"
        )
        results[name] = subprocess.run(
            ["powershell", "-Command", ps_script], capture_output=True, text=True
        )
        if results[name].returncode != 0:
            results[name] = f"Error: {results[name].stderr.strip()}"
        else:
            results[name] = results[name].stdout.strip()
    return results

def get_memory_info(server_fqdn):
    commands = {
        "memory": """
            function Get-MemoryInfo {
                param(
                    [string]$Computer = $env:COMPUTERNAME
                )
                
                try {
                    if ($Computer -eq $env:COMPUTERNAME) {
                        $computerSystem = Get-CimInstance -ClassName Win32_ComputerSystem
                        $operatingSystem = Get-CimInstance -ClassName Win32_OperatingSystem
                    } else {
                        $computerSystem = Get-CimInstance -ComputerName $Computer -ClassName Win32_ComputerSystem
                        $operatingSystem = Get-CimInstance -ComputerName $Computer -ClassName Win32_OperatingSystem
                    }
                    
                        $totalMemoryGB = [math]::Round($computerSystem.TotalPhysicalMemory / 1GB, 2)        
                        $freeMemoryGB = [math]::Round($operatingSystem.FreePhysicalMemory / 1MB , 2)        
                        $usedMemoryGB = [math]::Round($totalMemoryGB - $freeMemoryGB, 2)        
                        $usedPercentage = [math]::Round(($usedMemoryGB / $totalMemoryGB) * 100, 2)
                        $freePercentage = [math]::Round(($freeMemoryGB / $totalMemoryGB) * 100, 2)
                    
                        $memoryInfo = [PSCustomObject]@{
                        ComputerName = $Computer
                        TotalMemoryGB = $totalMemoryGB
                        UsedMemoryGB = $usedMemoryGB
                        FreeMemoryGB = $freeMemoryGB
                        UsedPercentage = $usedPercentage
                        FreePercentage = $freePercentage
                        Status = if ($usedPercentage -gt 90) { "Critical" } 
                                elseif ($usedPercentage -gt 80) { "Warning" } 
                                else { "OK" }
                        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }        
                    return $memoryInfo        
                } catch {
                    Write-Error "Error Getting info from $Computer : $($_.Exception.Message)"
                    return $null
                }
            }
            
            Get-MemoryInfo -Computer $ComputerName | ConvertTo-Json -Depth 2 -AsArray
        """
    }

    results = {}

    for name, ps_script in commands.items():
        # ps_script = (
            # f"Invoke-Command -ComputerName {server_fqdn} -ScriptBlock {{{ps_script}}}"            
        # )
        ps_script = ps_script.replace("$ComputerName",server_fqdn)
        results[name] = subprocess.run(
            ["powershell", "-Command", ps_script], capture_output=True, text=True
        )
        if results[name].returncode != 0:
            results[name] = f"Error: {results[name].stderr.strip()}"
        else:
            results[name] = results[name].stdout.strip()
    return results

# Pool de conexiones PowerShell reutilizable
class PowerShellPool:
    def __init__(self, max_workers=5):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute_command(self, server_fqdn, script, timeout=60):
        """Ejecuta comando PowerShell con timeout y manejo de errores mejorado"""
        
        # Optimizar el script de PowerShell para reducir overhead
        optimized_script = f"""
        try {{
            $ErrorActionPreference = 'Stop'
            $ProgressPreference = 'SilentlyContinue'
            
            Invoke-Command -ComputerName {server_fqdn} -ScriptBlock {{
                {script}
            }} -ErrorAction Stop
        }}
        catch {{
            Write-Error "Connection failed: $($_.Exception.Message)"
            exit 1
        }}
        """
        
        def run_ps_command():
            try:
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", optimized_script],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    creationflags=subprocess.CREATE_NO_WINDOW  # No mostrar ventana en Windows
                )
                
                if result.returncode != 0:
                    return {"error": result.stderr.strip()}
                
                return {"data": result.stdout.strip()}
            except subprocess.TimeoutExpired:
                return {"error": f"Command timeout after {timeout} seconds"}
            except Exception as e:
                return {"error": str(e)}
        
        future = self.executor.submit(run_ps_command)
        try:
            return future.result(timeout=timeout + 10)
        except Exception as e:
            return {"error": f"Execution error: {str(e)}"}

# Instancia global del pool
ps_pool = PowerShellPool()

def get_all_server_info_optimized(server_fqdn):
    """Obtiene toda la información del servidor en una sola conexión PowerShell"""
    
    # Script combinado que obtiene toda la información de una vez
    combined_script = '''
    $result = @{}
    
    # Disk Information
    try {
        $diskInfo = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
            $sizeGB = [math]::Round($_.Size / 1GB, 2)
            $freeGB = [math]::Round($_.FreeSpace / 1GB, 2)
            $usedGB = [math]::Round($sizeGB - $freeGB, 2)
            $percentUsed = if ($_.Size -gt 0) { [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 1) } else { 0 }
            $percentFree = 100 - $percentUsed
            $volumeName = $_.VolumeName
            
            [PSCustomObject]@{
                DeviceID = $_.DeviceID
                SizeGB = $sizeGB
                FreeSpaceGB = $freeGB
                UsedSpaceGB = $usedGB
                PercentUsed = "$percentUsed%"
                PercentFree = "$percentFree%"
                VolumeName = "$VolumeName"
            }
        }
        $result.disk = $diskInfo
    }
    catch {
        $result.disk_error = $_.Exception.Message
    }
    
    # SQL Services
    try {
        $sqlServices = Get-Service | Where-Object { $_.Name -like '*SQL*' } | ForEach-Object {
            $statusMap = @{ 1 = "Stopped"; 2 = "StartPending"; 3 = "StopPending"; 4 = "Running"; 5 = "ContinuePending"; 6 = "PausePending"; 7 = "Paused" }
            $startTypeMap = @{ 0 = "Boot"; 1 = "System"; 2 = "Automatic"; 3 = "Manual"; 4 = "Disabled" }
            
            [PSCustomObject]@{
                Name = $_.Name
                Status = $statusMap[$_.Status.value__]
                StartType = $startTypeMap[$_.StartType.value__]
            }
        }
        $result.services = $sqlServices
    }
    catch {
        $result.services_error = $_.Exception.Message
    }
    
    # Windows Updates 
    try {
        $updateSession = New-Object -ComObject Microsoft.Update.Session
        $updateSearcher = $updateSession.CreateUpdateSearcher()
        $searchResult = $updateSearcher.Search("IsInstalled=0")
        
        $updateCount = $searchResult.Updates.Count
        $totalSize = 0
        $criticalCount = 0
        $rebootRequired = $false
        
        foreach ($update in $searchResult.Updates) {
            $totalSize += $update.MaxDownloadSize / 1MB
            if ($update.MsrcSeverity -eq "Critical") { $criticalCount++ }
            if ($update.RebootRequired) { $rebootRequired = $true }
        }
        
        # Verificar reboot pendiente del sistema
        $rebootPending = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired" -ErrorAction SilentlyContinue) -ne $null
        
        $result.updates = @{
            UpdatesCount = $updateCount
            TotalSizeMB = [math]::Round($totalSize, 1)
            CriticalCount = $criticalCount
            RebootRequired = $rebootRequired -or $rebootPending
            LastChecked = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }
    }
    catch {
        $result.updates_error = $_.Exception.Message
    }
    
    # Memory Information
    try {
        $os = Get-CimInstance Win32_OperatingSystem
        $totalMemGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
        $freeMemGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
        $usedMemGB = $totalMemGB - $freeMemGB
        $memoryPercent = [math]::Round(($usedMemGB / $totalMemGB) * 100, 1)
        
        $result.memory = @{
            TotalMemoryGB = $totalMemGB
            UsedMemoryGB = $usedMemGB
            FreeMemoryGB = $freeMemGB
            UsedPercentage = $memoryPercent
            Status = if ($memoryPercent -gt 90) { "Critical" } elseif ($memoryPercent -gt 80) { "Warning" } else { "OK" }
        }
    }
    catch {
        $result.memory_error = $_.Exception.Message
    }
    
    # Server Info
    $result.server_info = @{
        ComputerName = $env:COMPUTERNAME
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
    }
    
    # Convertir todo a JSON
    $result | ConvertTo-Json -Depth 5 -AsArray
    '''
    
    # Ejecutar el script combinado
    result = ps_pool.execute_command(server_fqdn, combined_script, timeout=120)
    
    if "error" in result:
        return None
    
    try:
        return json.loads(result["data"])
    except json.JSONDecodeError:
        return None
from pypsrp.wsman import WSMan
from pypsrp.powershell import PowerShell, RunspacePool
import subprocess

def get_updates_info(server_fqdn):
    commands = {
        "updates": """ $updateSession = New-Object -ComObject Microsoft.Update.Session                
                $updateSearcher = $updateSession.CreateUpdateSearcher()                
                $searchResult = $updateSearcher.Search("IsInstalled=0")
                $updatesList = @()
                foreach ($update in $searchResult.Updates) {
                    $updatesList += [PSCustomObject]@{
                        Title = $update.Title
                        KB    = ($update.KBArticleIDs -join ", ")
                    }
                }
                return $updatesList | ConvertTo-Json -Depth 3 
        """
    }    

    results = {}

    for name, ps_script in commands.items():
            ps_script = f"Invoke-Command -ComputerName {server_fqdn} -ScriptBlock {{{ps_script}}}"            
            results[name]=subprocess.run(["powershell","-Command",ps_script],capture_output=True,text=True)
            if results[name].returncode !=0:
                results[name] =f"Error: {results[name].stderr.strip()}"
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
            } } | ConvertTo-Json -Depth 3
        """
    }    

    results = {}

    for name, ps_script in commands.items():
            ps_script = f"Invoke-Command -ComputerName {server_fqdn} -ScriptBlock {{{ps_script}}}"            
            results[name]=subprocess.run(["powershell","-Command",ps_script],capture_output=True,text=True)
            if results[name].returncode !=0:
                results[name] =f"Error: {results[name].stderr.strip()}"
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
            } } | ConvertTo-Json -Depth 3
        """
    }    

    results = {}

    for name, ps_script in commands.items():
            ps_script = f"Invoke-Command -ComputerName {server_fqdn} -ScriptBlock {{{ps_script}}}"            
            results[name]=subprocess.run(["powershell","-Command",ps_script],capture_output=True,text=True)
            if results[name].returncode !=0:
                results[name] =f"Error: {results[name].stderr.strip()}"
            else:
                results[name] = results[name].stdout.strip()
    return results

# Deploy Regulatory Radar onto this Windows Server.
# Safe to run again: each run stops the old app, replaces C:\app, and starts it.
#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Source
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$TaskName = 'RegulatoryRadar'
$AppRoot = 'C:\app'
$FirewallRuleName = 'Regulatory Radar HTTP'
$PythonVersion = '3.12.7'

function Test-Python310OrNewer {
    param([string]$Python)
    & $Python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
    return $LASTEXITCODE -eq 0
}

function Find-Python {
    $candidates = @(
        "$env:ProgramFiles\Python312\python.exe",
        "$env:LocalAppData\Programs\Python\Python312\python.exe"
    )
    $pyLauncher = Join-Path $env:WINDIR 'py.exe'
    if (Test-Path -LiteralPath $pyLauncher) {
        $printed = @(& $pyLauncher -3 -c "import sys; print(sys.executable)")
        if ($LASTEXITCODE -eq 0 -and $printed.Count -gt 0) {
            $candidates += $printed[-1].ToString().Trim()
        }
    }
    $installed = Get-ChildItem -Path "$env:ProgramFiles\Python*\python.exe" -ErrorAction SilentlyContinue |
        Sort-Object -Property FullName -Descending
    foreach ($item in $installed) {
        $candidates += $item.FullName
    }
    $onPath = Get-Command python.exe -ErrorAction SilentlyContinue |
        Where-Object { $_.Source -notlike '*\WindowsApps\*' }
    foreach ($item in $onPath) {
        $candidates += $item.Source
    }

    $seen = @{}
    foreach ($path in $candidates) {
        if ([string]::IsNullOrWhiteSpace($path) -or $seen.ContainsKey($path)) {
            continue
        }
        $seen[$path] = $true
        if ((Test-Path -LiteralPath $path) -and (Test-Python310OrNewer -Python $path)) {
            return $path
        }
    }
    return $null
}

function Install-PythonIfMissing {
    $existing = Find-Python
    if ($existing) {
        Write-Host "Python is already installed: $existing"
        return $existing
    }

    Write-Host "Python is missing. Installing Python $PythonVersion..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $installer = Join-Path $env:TEMP "python-$PythonVersion-amd64.exe"
    $url = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
    Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
    if ((Get-Item -LiteralPath $installer).Length -lt 1MB) {
        throw "The Python installer download looks empty."
    }

    $installerArgs = @(
        '/quiet',
        'InstallAllUsers=1',
        'PrependPath=1',
        'Include_pip=1',
        'Include_test=0',
        'AssociateFiles=0',
        'Shortcuts=0'
    )
    $proc = Start-Process -FilePath $installer -ArgumentList $installerArgs -Wait -PassThru
    if ($proc.ExitCode -ne 0) {
        throw "The Python installer failed with exit code $($proc.ExitCode)."
    }

    $python = Join-Path $env:ProgramFiles 'Python312\python.exe'
    if (-not (Test-Path -LiteralPath $python)) {
        throw "Python installed, but python.exe was not found at $python."
    }
    Write-Host "Installed Python: $python"
    return $python
}

function Stop-App {
    Write-Host 'Stopping the running app, if there is one...'
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $task -and $task.State -eq 'Running') {
        Stop-ScheduledTask -TaskName $TaskName
    }

    $processes = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue)
    foreach ($proc in $processes) {
        $command = [string]$proc.CommandLine
        $executable = [string]$proc.ExecutablePath
        $ours = ($command -like '*uvicorn*') -or ($executable -like "$AppRoot\*")
        if ($ours) {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
}

function Install-AppCode {
    param([string]$From)
    $fromFull = [IO.Path]::GetFullPath($From)
    if (-not (Test-Path -LiteralPath $fromFull)) {
        throw "Source folder not found: $fromFull"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $fromFull 'requirements.txt'))) {
        throw "requirements.txt is missing from $fromFull"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $fromFull 'app\main.py'))) {
        throw "app\main.py is missing from $fromFull"
    }

    Write-Host "Putting the new code in $AppRoot..."
    if ($fromFull -eq $AppRoot) {
        return
    }
    if (Test-Path -LiteralPath $AppRoot) {
        Remove-Item -LiteralPath $AppRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $AppRoot | Out-Null

    $skip = @('.git', '.venv', 'venv', '.env', '.cursor')
    Get-ChildItem -LiteralPath $fromFull -Force | Where-Object { $skip -notcontains $_.Name } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $AppRoot $_.Name) -Recurse -Force
    }
}

function Install-Requirements {
    param([string]$Python)
    Write-Host 'Installing requirements into a virtual environment...'
    $venvPython = Join-Path $AppRoot '.venv\Scripts\python.exe'
    & $Python -m venv (Join-Path $AppRoot '.venv')
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the virtual environment (exit code $LASTEXITCODE)."
    }
    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Could not upgrade pip (exit code $LASTEXITCODE)."
    }
    & $venvPython -m pip install -r (Join-Path $AppRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) {
        throw "Could not install requirements.txt (exit code $LASTEXITCODE)."
    }
}

function Open-Port80 {
    Write-Host 'Opening port 80 in the firewall...'
    $existing = @(Get-NetFirewallRule -DisplayName $FirewallRuleName -ErrorAction SilentlyContinue)
    if ($existing.Count -gt 0) {
        $existing | Remove-NetFirewallRule
    }
    New-NetFirewallRule -DisplayName $FirewallRuleName -Direction Inbound -Action Allow -Protocol TCP -LocalPort 80 -Profile Any -Enabled True | Out-Null
}

function Start-AppTask {
    param([string]$VenvPython)
    Write-Host "Starting scheduled task $TaskName..."
    $action = New-ScheduledTaskAction -Execute $VenvPython -Argument '-m uvicorn app.main:app --host 0.0.0.0 --port 80' -WorkingDirectory $AppRoot
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
    Start-ScheduledTask -TaskName $TaskName

    $task = $null
    $deadline = (Get-Date).AddSeconds(30)
    do {
        Start-Sleep -Seconds 2
        $task = Get-ScheduledTask -TaskName $TaskName
        if ($task.State -eq 'Running') {
            Write-Host "$TaskName is running."
            return
        }
    } while ((Get-Date) -lt $deadline)

    $info = Get-ScheduledTaskInfo -TaskName $TaskName
    throw "$TaskName did not stay running (state: $($task.State), last result: $($info.LastTaskResult))."
}

if ([string]::IsNullOrWhiteSpace($Source)) {
    if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        throw 'Pass -Source, the folder that contains the new app files.'
    }
    $Source = Split-Path -Parent $PSScriptRoot
}

$python = Install-PythonIfMissing
Stop-App
Install-AppCode -From $Source
Install-Requirements -Python $python
Open-Port80
Start-AppTask -VenvPython (Join-Path $AppRoot '.venv\Scripts\python.exe')
Write-Host 'Deploy finished.'

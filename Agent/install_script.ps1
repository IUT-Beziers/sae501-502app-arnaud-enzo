param (
    [string]$apiUrl,
    [string]$apiKey,
    [string]$interface
)

# Validate parameters
if (-not $apiUrl -or -not $apiKey -or -not $interface) {
    Write-Host "Usage: .\script.ps1 --api-url <API_URL> --api-key <API_KEY> --interface <INTERFACE>"
    exit 1
}

# Function to install Chocolatey
function Install-Chocolatey {
    Write-Host "Chocolatey is not installed. Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "Chocolatey installed successfully."
}

# Check if Chocolatey is installed, and install it if not
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Install-Chocolatey
}

# Install dependencies
Write-Host "Installing dependencies..."
choco install python3 -y

# Start new PowerShell session to reload the PATH
Write-Host "Reloading PATH..."
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") 

# Install Python packages
python.exe -m pip install --upgrade pip
pip install scapy requests pywin32

# Download the agent script
Write-Host "Downloading agent script..."
$agentScriptUrl = "https://raw.githubusercontent.com/IUT-Beziers/sae501-502app-arnaud-enzo/refs/heads/main/Agent/arp_agent.py"
$agentScriptPath = "$env:USERPROFILE\arp_agent.py"
Invoke-WebRequest -Uri $agentScriptUrl -OutFile $agentScriptPath

# Start the agent script

Write-Host "Starting agent script..."
$agentScriptCommand = "python $agentScriptPath install --api-url $apiUrl --api-key $apiKey --interface $interface"

Write-Host "ARP agent setup complete. The script will run at startup."
# This script automates the setup and execution of the DocuMental application.
# It ensures a virtual environment is created, the project is installed,
# and then launches the main application, keeping the console window open.

# Get the directory where the script is located to ensure all paths are correct.
$scriptDir = $PSScriptRoot

# Define the name of the virtual environment directory.
$venvName = ".venv"
$venvDir = Join-Path $scriptDir $venvName

# Define the full paths to the executables within the virtual environment.
$pipPath = Join-Path -Path $venvDir -ChildPath "Scripts\pip.exe"
$appExecutable = Join-Path -Path $venvDir -ChildPath "Scripts\documental.exe"

# --- Step 1: Set up the Virtual Environment ---
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment at: $venvDir"
    try {
        # Use the system's python to create the venv.
        python -m venv $venvDir
        Write-Host "Virtual environment created successfully." -ForegroundColor Green
    } catch {
        Write-Host "Error: Python is not installed or not found in your system's PATH." -ForegroundColor Red
        Write-Host "Please install Python 3 from python.org and ensure it's added to your PATH." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists."
}

# --- Step 2: Install the Project and its Dependencies ---
Write-Host "Installing the DocuMental package and its dependencies..."
# Execute pip from the virtual environment to install the project.
# This reads pyproject.toml and installs the package and its dependencies.
& $pipPath install .
$installResult = $LASTEXITCODE
if ($installResult -ne 0) {
    Write-Host "Error installing the project. Please check the console for errors." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Project installed successfully." -ForegroundColor Green

# --- Step 3: Run the Application ---
Write-Host "Launching DocuMental..." -ForegroundColor Cyan
Write-Host "The agent is now monitoring your printers. Close this window to stop it." -ForegroundColor Yellow

# Execute the installed application entry point.
& $appExecutable

# --- Step 4: Keep Window Open ---
# This line will only be reached if the application terminates for any reason.
# This prevents the window from closing immediately on error or completion.
Write-Host "DocuMental has terminated." -ForegroundColor Yellow
Read-Host "Press Enter to close this window."
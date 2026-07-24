1# MarketPulse SAAS Practice Demo

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

Create and activate the virtual environment:

```bash
uv venv
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

cmd.exe:

```cmd
.venv\Scripts\activate.bat
```

## Running

```bash
uv run uvicorn main:app --reload
```

## Health Check

Once running, check that the app is live and see its version:

```bash
curl http://127.0.0.1:8000/health
```

Returns:

```json
{"status": "live", "version": "0.1.0"}
```

## Dependencies

Add a new dependency:

```bash
uv add <package>
```

Sync dependencies from the lockfile:

```bash
uv sync
```

## Author

Manoj Kumar Yendluri

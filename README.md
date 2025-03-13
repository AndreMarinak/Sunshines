#NEW TEST LINE


# SunshinesWorking
PSU Sunshines App

## Setup Instructions

1. Move your Firebase service account JSON file to a secure location outside your project directory.
2. Set the environment variable `FIREBASE_CRED_PATH` to the path of your Firebase service account JSON file for local testing.

### Example (Linux/Mac)
```bash
export FIREBASE_CRED_PATH=/path/to/your-firebase-service-account.json
```

### Example (Windows)
```powershell
$env:FIREBASE_CRED_PATH="C:\path\to\your-firebase-service-account.json"
```

3. For deployment, set the `FIREBASE_CONFIG` environment variable with the content of your Firebase service account JSON file.

### Example (Linux/Mac)
```bash
export FIREBASE_CONFIG='{"type": "service_account", "project_id": "sunshines-c396f", ...}'
```

### Example (Windows)
```powershell
$env:FIREBASE_CONFIG='{"type": "service_account", "project_id": "sunshines-c396f", ...}'
```

4. Run your Flask app.
```bash
python Sunshines.py
```

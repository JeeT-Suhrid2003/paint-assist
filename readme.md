# Painting Web

A small Flask web app that uploads a painting image, saves it to Google Cloud Storage, and uses Gemini/Vertex AI to analyze the painting and generate paint-mixing recipes.

## Requirements

- Python 3.11+ or 3.12
- Docker (for container deployment)
- A Google Cloud project with:
  - A Storage bucket
  - Vertex AI enabled
  - A service account with at least:
    - `Storage Object Creator` or equivalent for the upload bucket
    - `Vertex AI User` or equivalent for Gemini/Vertex AI access

## Setup

1. Create a service account JSON key in Google Cloud.
2. Download the JSON key file locally.
3. Place the key file somewhere on your host machine, for example:
   - `C:\Users\suhri\Documents\coding\painting_web\key.json`

## Environment Variables

When running locally, set:

- `GOOGLE_APPLICATION_CREDENTIALS` to the path of the JSON key file
- `PROJECT_ID` to your Google Cloud project ID
- `BUCKET_NAME` to your Cloud Storage bucket name

Example PowerShell for local Flask:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = 'C:\Users\suhri\Documents\coding\painting_web\key.json'
$env:PROJECT_ID = 'your-gcp-project-id'
$env:BUCKET_NAME = 'your-bucket-name'
python main.py
```

## Docker Usage

Build the image:

```powershell
docker build -t painting-web .
```

Run the container with credentials mounted:

```powershell
docker run -p 8080:8080 `
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/key.json `
  --mount type=bind,source="C:\Users\suhri\Documents\coding\painting_web\key.json",target=/secrets/key.json `
  -e PROJECT_ID=your-gcp-project-id `
  -e BUCKET_NAME=your-bucket-name `
  painting-web
```

> Important: make sure the host path points to a real file, not a directory. If Docker creates `/secrets/key.json` as a directory, the app will fail.

## Local Container Execution & Authentication

Because Docker containers run inside an isolated network sandbox, you must explicitly bind your host machine's authorized `gcloud` identity tokens directly into the runtime context:

### On Windows (PowerShell):

```powershell
# 1. Compile the local container image tag
docker build -t painting-app-local .

# 2. Spin up the container while passing the Windows AppData credentials directory
docker run -p 8080:8080 `
  -v "$env:APPDATA\gcloud:/tmp/.config/gcloud" `
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/.config/gcloud/application_default_credentials.json `
  painting-app-local
```

### On Linux / macOS (Terminal):

```bash
docker run -p 8080:8080 \
  -v "$HOME/.config/gcloud:/tmp/.config/gcloud" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/.config/gcloud/application_default_credentials.json \
  painting-app-local
```

Once initialized, visit your environment endpoint at `http://localhost:8080`.

## ☁️ Continuous Cloud Run Deployment Workflow

When pushing onto managed infrastructure, avoid direct programmatic credential key generation. Leverage identity inheritance by explicitly utilizing the default project execution identities:

```powershell
# Deploy the codebase directly from local storage source
gcloud run deploy painting-web `
    --source . `
    --region us-west1 `
    --service-account="YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com"
```

## Notes

- The app now initializes GCP clients only when a request is handled, so the container can start even before credentials are loaded.
- If the service account key is missing or invalid, the app will return an error telling you to set `GOOGLE_APPLICATION_CREDENTIALS` correctly.

## Template file

- `templates/index.html` contains the upload form and improved recipe rendering.

## File list

- `main.py` - Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - container build instructions
- `templates/index.html` - UI template
- `readme.md` - this file

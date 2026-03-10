# Project UNDERLINK Backend

## How to Start

### 1. Start Database

Run this in project root:

```bash
docker compose up -d
```

### 2. Install Backend Dependencies

Run this in the `backend` folder:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Flask App

Run this in the `backend` folder:

```bash
python -m flask --app app.main run
```

### 4. Backend URL

```
http://127.0.0.1:5000
```
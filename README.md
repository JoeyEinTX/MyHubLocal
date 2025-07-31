# MyHubLocal

A **lightweight, local-first smart home hub** built for Raspberry Pi 5.  
No cloud dependencies. Just your LAN, your devices, your control.

---

## 🚀 Features (Current / Planned)

- ✅ FastAPI backend with device control endpoints
- ✅ Single test Z-Wave device for development  
- ✅ REST API endpoints: GET /devices/list, POST /devices/control
- ✅ React frontend with TailwindCSS
- ✅ Device dashboard with toggle controls
- ✅ **NEW: Dual theme system (Light & Dark modes)**
- ✅ **NEW: Theme toggle in navigation bar**
- 🔮 Future: Real Z-Wave integration, Shelly devices, ESP32 support
- 🔮 Future: Secure remote access, touchscreen UI, automation rules

---

## 🏗 Architecture (v0.1)

```text
[ Raspberry Pi 5 ]
 ├── Backend: FastAPI (Python)
 │    ├── /devices → REST endpoints
 │    ├── ZwaveManager → handles USB Z-Wave stick
 │    └── Config → stores device info (YAML/JSON)
 │
 ├── Frontend: React SPA
 │    ├── Talks to backend REST API
 │    ├── Desktop + mobile friendly
 │    └── Future: Touchscreen UI
 │
 └── Local Network: Smart devices (Z-Wave, Shelly, Kasa, ESP32)
```

## 📂 Project Structure

```text
MyHubLocal/
├── backend/
│   ├── main.py         # FastAPI entrypoint
│   ├── devices.py      # Device control endpoints
│   ├── models.py       # Pydantic data models
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/Home.jsx      # Main dashboard
│   │   ├── components/DeviceCard.jsx  # Device control component
│   │   ├── api.js              # Backend API client
│   │   └── App.jsx             # React app entry
│   ├── package.json
│   └── tailwind.config.js
│
├── start.sh            # Combined startup script
└── README.md
```

## 🛠 Setup (Dev Mode)

**Quick Start (Recommended):**
```bash
./start.sh
```

**Manual Setup:**
1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run backend:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. Start frontend (in another terminal):
```bash
cd frontend
npm install
npm run dev
```

## 📜 License

MIT (open-source, free to use and modify)
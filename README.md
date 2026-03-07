# SyahdanKijang – FastAPI + ETD 8A12 Control

Fitur:
- ✅ FastAPI + JWT Auth
- ✅ SQLModel + SQLite
- ✅ Modbus TCP (pymodbus, async) untuk ETD 8A12 @ 10.21.240.5:5000
- ✅ Endpoint khusus ETD: baca 12 kanal, set ON/OFF (0x0100/0x0200)
- ✅ Halaman kontrol Jinja2 `/etd8a12`
- ✅ Background polling

## Jalankan (Dev)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Auth
```bash
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  http://127.0.0.1:8000/auth/token
```
Pakailah `access_token` untuk memanggil endpoint protected.

## ETD Endpoints
- GET `/etd8a12/outputs` → 12 boolean
- GET `/etd8a12/outputs/{channel}` → 1 boolean (1..12)
- POST `/etd8a12/outputs/set` body: `{ "channel": 7, "on": true }`
- UI: `http://127.0.0.1:8000/etd8a12`

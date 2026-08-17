# 🐾 ResQPaws AI: Intelligent Animal Emergency Response and Rescue Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)

> **ResQPaws AI** is an AI-powered web application that allows citizens to report injured animals by uploading a photo. The system automatically detects animal species and injury severity (Critical, Severe, Moderate, Minor), captures GPS location, routes the case to the nearest animal hospital using the Haversine geo-algorithm, triggers ambulance dispatch, and delivers real-time veterinary first-aid guidance.

---

## 🌟 Key Features

1. **AI Vision & Diagnostic Engine**:
   - Analyzes animal imagery via OpenCV & Deep Learning heuristics.
   - Detects species (*Dog, Cat, Bird, Cow/Cattle, Horse, Wildlife*).
   - Classifies trauma levels (*Critical, Severe, Moderate, Minor*).
   - Renders annotated bounding boxes over wound sites.

2. **Automated GPS & Hospital Allocation**:
   - Captures client geolocation with HTML5 GPS & OpenStreetMap/Leaflet integration.
   - Computes shortest Euclidean distances via **Haversine formula**.
   - Notifies the nearest animal clinic or NGO shelter.

3. **Veterinary First-Aid Guidance Engine**:
   - Immediate step-by-step life support instructions tailored to species and injury type.
   - Critical DOs and DON'Ts (e.g. preventing lethal human medications, shock care, bleeding pressure pads).

4. **Hospital & Rescue Fleet Command**:
   - Real-time emergency triage stream prioritized by Code Red urgency.
   - 1-click ambulance and paramedic dispatch.
   - Patient admission, medical notes recording, and post-recovery photo updates.

5. **Citizen Rescue Tracker**:
   - Live interactive tracking map with ambulance telemetry.
   - Direct call link to dispatched ambulance driver.
   - Step-by-step audit log history.

6. **Macro Analytics & Admin Dashboard**:
   - Visual charts (Species distribution, injury severity breakdown).
   - Hospital occupancy and response time performance.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Django 4.2+ (Django ORM, Authentication, Signals)
- **Frontend**: HTML5, Modern CSS3 (Custom Design System), Bootstrap 5, JavaScript (ES6+), AJAX
- **Mapping & Geolocation**: Leaflet.js, OpenStreetMap Nominatim API, HTML5 Geolocation API
- **AI & Computer Vision**: OpenCV (`cv2`), Pillow (PIL), NumPy, PyTorch / YOLO hooks
- **Database**: SQLite (Zero-configuration out-of-the-box) / PostgreSQL & MySQL ready
- **Notifications**: SMTP Email alerts, browser status notifications

---

## 🚀 Quick Start Guide (Windows / Mac / Linux)

### Step 1: Navigate to the Project Directory
```powershell
cd C:\Users\acer\.gemini\antigravity\scratch\resqpaws_ai
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Seed Demo Hospitals, Ambulances & Test Users
```powershell
python seed_data.py
```

### Step 6: Start the Development Server
```powershell
python manage.py runserver
```
Visit the application in your browser at: **`http://127.0.0.1:8000/`**

---

## 🔑 Pre-Configured Demo Credentials

The `seed_data.py` script automatically creates ready-to-test accounts:

| Role | Username | Password | Access / Dashboard |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin` | `admin123` | [Admin Analytics Dashboard](http://127.0.0.1:8000/analytics/dashboard/) & Django Admin |
| **Hospital Staff / Vet** | `vet_staff` | `staff123` | [Hospital Triage & Ambulance Dispatch](http://127.0.0.1:8000/hospitals/dashboard/) |
| **Citizen Rescuer** | `citizen1` | `user123` | [Citizen Reports & Live Tracker](http://127.0.0.1:8000/rescue/my-rescues/) |

---

## 📂 Project Architecture

```
resqpaws_ai/
├── manage.py                       # Django CLI controller
├── requirements.txt                # Python library dependencies
├── seed_data.py                    # Preloaded demo datasets
├── README.md                       # Comprehensive documentation
├── resqpaws_project/               # Core configuration & settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                           # Home, About, Contact, Global Context
├── accounts/                       # Custom profile roles (Citizen, Staff, Admin)
├── rescue/                         # Emergency reporting, GPS calculation, Dispatch
│   ├── models.py                   # RescueReport & RescueStatusLog
│   ├── views.py                    # Report wizard, AI Result, Tracker
│   └── utils.py                    # Haversine distance & alert engine
├── ai_engine/                      # Computer vision & diagnostic pipeline
│   ├── vision_analyzer.py          # AI image analyzer & bounding box renderer
│   └── first_aid_data.py           # Veterinary emergency first-aid protocols
├── hospitals/                      # Hospital triage & Ambulance fleet manager
├── analytics/                      # Macro KPIs, Chart.js trends, audit logs
├── static/
│   ├── css/style.css               # Modern healthcare/rescue UI design tokens
│   └── js/
│       ├── main.js                 # Camera capture WebRTC & preview
│       ├── geolocation.js          # Leaflet GPS pinning & reverse geocoding
│       └── tracker.js              # Live telemetry simulator & status poller
└── templates/                      # Responsive HTML5 + Bootstrap 5 layouts
    ├── base.html
    ├── core/
    ├── accounts/
    ├── rescue/
    ├── hospitals/
    └── analytics/
```

---

## 💡 Workflow Walkthrough

1. **Citizen Discovers Injured Animal**:
   - Opens the web application and clicks **"Report Injured Animal"**.
   - Snaps or uploads a photo; device GPS coordinates are automatically pinned on the Leaflet map.
2. **AI Vision Diagnosis**:
   - The AI identifies species (e.g., *Dog*), scans for trauma markers (hemorrhage, fractures), classifies the severity (*Critical / Code Red*), and draws diagnostic bounding boxes.
3. **Haversine Geo-Routing**:
   - Calculates the closest active animal hospital (e.g., *City Central Trauma Center - 0.8 km away*) and assigns the case.
4. **Emergency Hospital Triage & Ambulance Dispatch**:
   - Hospital staff reviews the case on their live Triage Dashboard and clicks **Dispatch Ambulance**.
5. **Real-Time Guidance**:
   - While the ambulance is in transit, the citizen receives dynamic **First-Aid instructions** to prevent shock and bleeding.
   - The citizen can monitor the ambulance's live progress and call the driver directly.

---

## 📄 License
This project is open-source and built for social impact and animal welfare under the **MIT License**.

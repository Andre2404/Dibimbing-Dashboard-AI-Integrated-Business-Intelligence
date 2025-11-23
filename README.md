# Business Intelligence Dashboard - Full Stack Web Application

<img width="784" height="399" alt="Preview" src="https://github.com/user-attachments/assets/2fc46da0-93f1-49e1-b6f0-0e9f4fb5f78b" />

## Project Overview
This project implements an interactive, real-time Business Intelligence dashboard that moves beyond traditional GUI-based tools like Looker Studio. Built with a code-first approach using Python and the Reflex framework, it enables advanced features not typically available in standard BI tools.

## Key Differentiators
- **AI Chatbot Integration**: Natural language data queries and prediction simulations
- **Custom Python ETL**: Programmatic data cleaning and processing using Pandas
- **Real-time Data Fetching**: Live connection to Google Sheets data source
- **Custom Visualization**: Beyond standard drag-and-drop limitations

## Technology Stack
- **Framework**: Reflex (Python-native Web Framework)
- **Data Processing**: Pandas
- **Visualization**: Recharts (via Reflex integration)
- **Backend**: Python State Management
- **Data Source**: Google Sheets (CSV Export)

## Dataset
The application uses dummy transaction data hosted on Google Sheets, fetched live when the application runs or when the refresh button is triggered.

**Public Sheet Access**: [Dataset Link]([https://docs.google.com/spreadsheets/d/your-sheet-id/edit?usp=sharing](https://docs.google.com/spreadsheets/d/1M4ZG7-CsPGvhyU7_YHOSUo-dssu-jSs0E4ralASFg60/edit?gid=678977029#gid=678977029))

**Format**: CSV via Google Sheets export endpoint

## Installation & Setup Guide

### Prerequisites
- Python 3.9 or higher
- Node.js 20 LTS or higher

### Step 1: Clone and Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd Business-Intelligence-dashboard

# Create virtual environment (optional)
python -m venv venv

# Windows activation
.\venv\Scripts\activate

# Mac/Linux activation
source venv/bin/activate
```

Step 2: Install Python Dependencies
```bash
pip install reflex pandas
```
Step 3: Initialize and Resolve Frontend Dependencies
```bash
# Initial setup (may generate errors initially)
reflex init
```

Frontend Conflict Resolution: If the process fails during frontend setup:
Step 3: Initialize and Resolve Frontend Dependencies
```bash
# Initial setup (may generate errors initially)
reflex init
```

Frontend Conflict Resolution: If the process fails during frontend setup:
```bash
# Navigate to frontend directory
cd .web

# Install dependencies with legacy peer deps flag
npm install --legacy-peer-deps

# Return to root directory
cd ..
Step 4: Run the Application
bash
reflex run
bash
# Navigate to frontend directory
cd .web

# Install dependencies with legacy peer deps flag
npm install --legacy-peer-deps

# Return to root directory
cd ..
```
Step 4: Run the Application
```bash
reflex run
```

# Pelajaran yg gw dapet 

1. Masalah Dependency Node.js
Yang gw alamin:
Pas pertama kali jalanin reflex init, sering error gegara bentrok antara module CommonJS lama sama ES Modules modern di library p-map. Apalagi di Windows, makin ribet.

Yang gw pelajari:
- Ternyata harus pake Node.js versi LTS (Long Term Support) yang lebih stabil biasa nya yg paling baru 
- Bisa paksa install pake flag --legacy-peer-deps buat ignore konflik versi
- Ngoprek file package.json langsung buat debug dependency

2. State Management vs Filter Biasa
Yang gw rasain beda:
- Kalau di Looker Studio, filter itu statis - cuma nge-filter data doang. Tapi di Reflex, setiap interaksi (ngetik di chatbot, refresh data) itu ngubah state di backend Python.



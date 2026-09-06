# CareerPath Ghana

CareerPath Ghana is an intelligent career guidance and tertiary eligibility evaluation platform designed specifically for the Ghanaian educational system. It empowers Junior High School (JHS) and Senior High School (SHS) students to make informed decisions by mapping career aspirations to academic tracks, validating WASSCE grades against university cut-off benchmarks, and recommending verified degree pathways across top Ghanaian universities.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Database Setup & Seeding](#database-setup--seeding)
  - [Running the Application](#running-the-application)
- [Environment Variables](#environment-variables)
- [REST API Reference](#rest-api-reference)
- [Copyright & Licensing](#copyright--licensing)

---

## Overview

Navigating secondary school track selections and tertiary admissions in Ghana can be challenging due to disparate cutoff points, complex prerequisite combinations, and evolving curriculum tracks under NaCCA (National Council for Curriculum and Assessment).

CareerPath Ghana solves this by providing:
1. An automated WASSCE aggregate calculator and entry requirement validator for undergraduate programs.
2. An AI-powered career recommendation engine that translates student passions and strengths into viable academic pathways.
3. A NaCCA-aligned JHS-to-SHS curriculum guide that prioritizes direct subject combinations.
4. A searchable repository of programs and cut-off points for major public universities in Ghana.

---

## Key Features

### 1. WASSCE Eligibility Assessment Engine
- **Accurate Aggregate Calculation**: Automatically computes the standard aggregate score (Best 3 Core Subjects + Best 3 Electives) using official WAEC grading scales (A1 = 1, B2 = 2, B3 = 3, C4 = 4, C5 = 5, C6 = 6, D7 = 7, E8 = 8, F9 = 9).
- **Prerequisite Validation**: Verifies subject-specific prerequisites (e.g., Core Mathematics minimum C6, Elective Physics minimum B3) before checking aggregate cutoffs.
- **Admission Classification**: Categorizes student eligibility into:
  - **Direct Qualified**: Meets or beats the cut-off point and satisfies all subject rules.
  - **Borderline / Fee-Paying**: Meets academic prerequisites but lies within the extended cut-off margin for fee-paying or alternate admission streams.
  - **Not Qualified**: Clearly explains the specific deficit (aggregate threshold or missing prerequisite).
- **Automated Results Slip OCR**: Supports uploading WASSCE result slips with automated grade extraction powered by Google Gemini Multimodal AI.

### 2. AI-Powered Career Advisor
- **Natural Language Matching**: Students can express interests, hobbies, or dream professions in plain English (e.g., *"I love robotics, coding, and problem-solving"*).
- **Curriculum Mapping**: Connects each career to recommended SHS academic tracks (General Science, Business, General Arts, Visual Arts, Home Economics, Technical / STEM) and specific elective combinations.
- **University Degree Linkage**: Directs students to university programs that lead directly into their chosen field.

### 3. NaCCA JHS-to-SHS Track Advisor
- **Elective Pathway Priority**: Automatically highlights direct pathways first, falling back to secondary pathways only when direct routes are unavailable.
- **Integrated Search**: Quick search and category filter for fast exploration of senior high academic programmes.

### 4. University & Degree Programme Directory
- Up-to-date benchmark cut-off points, tuition category options, campus locations, and degree durations for top universities:
  - Kwame Nkrumah University of Science and Technology (KNUST)
  - University of Ghana (UG, Legon)
  - University of Cape Coast (UCC)
  - University for Development Studies (UDS)
  - University of Energy and Natural Resources (UENR)
- Clean, responsive card grid optimized for mobile and desktop screens.

---

## Technology Stack

- **Backend**: Django 6.x, Django REST Framework (DRF)
- **AI & NLP**: Google Gemini API (`google-genai` / REST API), spaCy, scikit-learn
- **Database**: SQLite (local development) / PostgreSQL with `dj-database-url` (production)
- **Frontend**: Responsive HTML5, Vanilla CSS, SVG Icons (zero external frontend build steps or node dependencies required)
- **Production Server**: Gunicorn, WhiteNoise for static file serving

---

## Project Structure

```
careerpath/
├── api/                        # Django REST Framework API views and serializers
│   ├── urls.py                 # API routing endpoints
│   └── views.py                # Eligibility evaluation, AI matching, & catalog APIs
├── careers/                    # Career pathways, NaCCA tracks, and JHS models
│   ├── admin.py                # Django admin configuration
│   └── models.py               # Career, SHSTrack, ElectiveSubject models
├── config/                     # Django root settings and WSGI/ASGI configurations
│   ├── settings.py             # Main settings configuration
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI entrypoint
├── eligibility/                # University, Faculty, Program, & Benchmark models
│   ├── admin.py                # Admin configuration for universities and programs
│   ├── models.py               # University, Program, CutoffPoint models
│   └── services.py             # Core eligibility logic & aggregate calculator
├── frontend/                   # Frontend views and templates
│   ├── templates/frontend/     # Modular HTML templates
│   │   ├── base.html           # Base layout template
│   │   ├── career_detail.html  # Career profile & track requirements
│   │   ├── careers.html        # Career discovery directory
│   │   ├── jhs_guide.html      # NaCCA JHS-to-SHS track guide
│   │   ├── landing.html        # Main landing page
│   │   ├── shs_eligibility.html# WASSCE eligibility assessment wizard
│   │   ├── universities.html   # University catalog & search
│   │   └── university_detail.html # University degree details & cutoffs
│   ├── static/                 # Static CSS, JavaScript, and assets
│   └── views.py                # Frontend view controllers
├── seed_data.py                # Comprehensive database seeder with real 2026 data
├── manage.py                   # Django CLI management script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── CONTRIBUTING.md             # Contribution guidelines
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- (Optional) A Google Gemini API Key from Google AI Studio

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/careerpath.git
   cd careerpath
   ```

2. **Create and activate a virtual environment:**
   - **On Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **On macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Copy the sample environment file and configure your local settings:

```bash
cp .env.example .env
```

Open `.env` and fill in your values:
```ini
SECRET_KEY=your-custom-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your_gemini_api_key_here
```

### Database Setup & Seeding

1. **Apply initial migrations:**
   ```bash
   python manage.py migrate
   ```

2. **Create an administrative user:**
   ```bash
   python manage.py createsuperuser
   ```

3. **Seed benchmark data:**
   Populate all universities (KNUST, UG, UCC, UDS, UENR), faculties, programs, cut-off points, NaCCA tracks, and careers:
   ```bash
   python seed_data.py
   ```

### Running the Application

Start the local Django development server:

```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Web Application**: `http://127.0.0.1:8000/`
- **Django Admin Portal**: `http://127.0.0.1:8000/admin/`
- **REST API Explorer**: `http://127.0.0.1:8000/api/`

---

## Environment Variables

| Variable Name | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | Yes | - | Secret key used for cryptographic signing in Django |
| `DEBUG` | No | `False` | Enable or disable debug mode (`True` for local development) |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated list of host/domain names Django can serve |
| `GEMINI_API_KEY` | No | - | Google Gemini API key used for natural language career matching and OCR |
| `DATABASE_URL` | No | SQLite default | PostgreSQL database connection URL for production environments |

---

## REST API Reference

CareerPath Ghana exposes REST API endpoints for seamless integration:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/universities/` | List all available universities with meta counts |
| `GET` | `/api/universities/<id>/` | Retrieve detailed university profile and faculties |
| `GET` | `/api/programs/` | List and search degree programmes with cutoff filters |
| `GET` | `/api/programs/<id>/` | Retrieve specific program prerequisites and cutoffs |
| `POST` | `/api/eligibility/evaluate/` | Evaluate student WASSCE grades against a program |
| `POST` | `/api/eligibility/qualifying-programs/` | Discover all programs a student qualifies for |
| `POST` | `/api/careers/ai-match/` | Match user interest descriptions to careers using Gemini AI |
| `GET` | `/api/jhs-guide/tracks/` | List NaCCA academic tracks and elective combinations |

---

## Copyright & Licensing

Copyright (c) 2026 CareerPath Ghana. All Rights Reserved.

This codebase and associated assets are proprietary and confidential. Unauthorized copying, distribution, modification, or commercial use without prior written consent from the copyright holder is strictly prohibited.

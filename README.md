# CareerPath Ghana

CareerPath Ghana is an intelligent career guidance and tertiary academic eligibility evaluation platform built specifically for the Ghanaian educational system. It empowers Junior High School (JHS) and Senior High School (SHS) students to make informed educational decisions by mapping career aspirations to academic tracks, validating WASSCE grades against university cut-off benchmarks, generating real-time AI career prospects for degree programmes, and recommending verified pathways across premier Ghanaian universities.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
  - [1. WASSCE Eligibility Assessment & Auto-Qualification Engine](#1-wassce-eligibility-assessment--auto-qualification-engine)
  - [2. AI-Powered Career Advisor & Interest Matching](#2-ai-powered-career-advisor--interest-matching)
  - [3. AI-Generated Career Outlook & Prospects for Every Programme](#3-ai-generated-career-outlook--prospects-for-every-programme)
  - [4. NaCCA JHS-to-SHS Track Advisor](#4-nacca-jhs-to-shs-track-advisor)
  - [5. University & Degree Programme Directory](#5-university--degree-programme-directory)
  - [6. Administrative Management & Seeding](#6-administrative-management--seeding)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Local Development Setup](#local-development-setup)
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
2. A reverse qualification engine that discovers every university degree a student qualifies for based on their grades.
3. An AI-powered career recommendation engine that translates student passions and strengths into viable academic pathways.
4. An AI-driven career lookup engine that generates real-time, Ghana-specific career outlooks, professional job roles, and key employers for every degree programme.
5. A NaCCA-aligned JHS-to-SHS curriculum guide that prioritizes direct subject combinations.
6. A searchable repository of programs and cut-off points for major public universities in Ghana.

---

## Key Features

### 1. WASSCE Eligibility Assessment & Auto-Qualification Engine
- **Accurate Aggregate Calculation**: Automatically computes the official WAEC aggregate score (Best 3 Core Subjects + Best 3 Electives) using official Ghanaian grading standards (A1 = 1, B2 = 2, B3 = 3, C4 = 4, C5 = 5, C6 = 6, D7 = 7, E8 = 8, F9 = 9).
- **Prerequisite Validation**: Verifies subject-specific prerequisites (e.g., Core Mathematics minimum C6, Elective Physics minimum B3) before checking aggregate cutoffs.
- **Three-Tier Admission Classification**:
  - **Direct Qualified**: Meets or beats the cut-off point and satisfies all subject prerequisite rules.
  - **Borderline / Fee-Paying**: Meets academic prerequisites but lies within the extended cut-off margin for fee-paying or alternate admission streams.
  - **Not Qualified**: Clearly explains the specific deficit (aggregate threshold or missing prerequisite).
- **Reverse Qualification ("Find What I Qualify For")**: Allows students to enter their 8 WASSCE grades once and instantly receive a ranked list of all qualifying degree programs across all universities.
- **Automated Results Slip OCR**: Upload WASSCE result slips (images or scans) with automated grade extraction powered by Google Gemini Multimodal AI.

### 2. AI-Powered Career Advisor & Interest Matching
- **Natural Language Query Matching**: Students can express interests, hobbies, or dream professions in natural language (e.g., *"I love robotics, coding, and problem-solving"* or *"I want to work in maternal healthcare and help babies"*).
- **Intelligent Semantic Matching**: Powered by Google Gemini AI to analyze nuanced user prompts and match them to verified careers and degree programs.
- **Domain Knowledge Fallback**: Built-in Ghanaian curriculum domain ontology ensures reliable matching even during network or rate-limited scenarios.
- **Curriculum Mapping**: Automatically connects identified careers to recommended Senior High School tracks and university degrees.

### 3. AI-Generated Career Outlook & Prospects for Every Programme
- **Dynamic Real-Time Career Lookup**: When exploring any degree programme (e.g., BSc Computer Engineering, BSc Optometry, BA Communication Studies), the platform dynamically generates a tailored, Ghana-specific professional outlook powered by Google Gemini AI.
- **Actionable Career Intelligence**:
  - **Specific Professional Roles**: Pinpoints exact job titles and career specializations graduates can step into (e.g., Embedded Systems Engineer, Clinical Optometrist, Corporate Communications Strategist).
  - **Real Ghanaian Employers & Institutions**: Identifies real hiring institutions in Ghana across public and private sectors (e.g., Ghana Health Service, Food & Drugs Authority, Bank of Ghana, Volta River Authority, Ghana Standards Authority, leading financial institutions, and tech firms).
  - **Industry Sector Mapping**: Highlights primary and emerging industries served by the academic degree.
- **High-Speed Delivery & Fallbacks**: Utilizes Google Gemini with structured responses, cached fallbacks, and instantaneous delivery for a seamless browsing experience.

### 4. NaCCA JHS-to-SHS Track Advisor
- **Curriculum Framework Alignment**: Structured according to the National Council for Curriculum and Assessment (NaCCA) standards.
- **Elective Pathway Priority**: Automatically highlights **Direct Pathways** (optimal subject combinations) first, falling back to secondary pathways only when direct routes are unavailable.
- **Interactive Search & Category Filters**: Search and filter across General Science, Business, General Arts, Visual Arts, Home Economics, and Technical / STEM tracks.

### 5. University & Degree Programme Directory
- **Premier Ghanaian Universities**: Comprehensive data for top public institutions:
  - Kwame Nkrumah University of Science and Technology (KNUST)
  - University of Ghana (UG, Legon)
  - University of Cape Coast (UCC)
  - University for Development Studies (UDS)
  - University of Energy and Natural Resources (UENR)
- **Rich Programme Information**: Benchmark cut-off points, campus locations, tuition categories (Regular vs. Fee-Paying notes), and specific subject requirements.
- **Responsive Layout**: Clean, responsive card grid optimized for mobile and desktop screens (2-3 cards per row on mobile for rapid browsing).

### 6. Administrative Management & Seeding
- **Django Admin Portal**: Full administrative interface for managing universities, colleges, faculties, programs, cut-off points, and curriculum tracks.
- **Automated Data Seeding**: Includes a comprehensive seeder (`seed_data.py`) pre-populated with verified 2026/2027 academic year cut-off points and curriculum tracks.

---

## Technology Stack

- **Backend**: Django 6.x, Django REST Framework (DRF)
- **AI & Multimodal**: Google Gemini API (`gemini-2.0-flash`, `gemini-1.5-flash` for Natural Language Career Matching, Programme Outlooks, and WASSCE OCR)
- **Database**: PostgreSQL with `psycopg2-binary` and `dj-database-url`
- **Frontend**: Responsive HTML5, Vanilla CSS, SVG Icons (zero external node/npm build dependencies)
- **Production Server**: Gunicorn, WhiteNoise for static file serving

---

## Project Structure

```
careerpath/
├── api/                        # Django REST Framework API views and serializers
│   ├── urls.py                 # API routing endpoints
│   └── views.py                # Eligibility evaluation, AI matching, career outlook, & catalog APIs
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
├── seed_data.py                # Comprehensive database seeder with real benchmark data
├── manage.py                   # Django CLI management script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # Proprietary / All Rights Reserved notice
└── README.md                   # Project documentation
```

---

## Local Development Setup

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
| `DATABASE_URL` | Yes | - | PostgreSQL database connection URL (e.g. `postgres://user:password@host:5432/dbname`) |

---

## REST API Reference

CareerPath Ghana exposes REST API endpoints for seamless integration:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/universities/` | List all available universities with meta counts |
| `POST` | `/api/program-details/` | Retrieve specific program offerings, campus locations, and prerequisites |
| `POST` | `/api/career-outlook/` | Generate dynamic Ghana-specific AI career outlook for any degree programme |
| `POST` | `/api/evaluate-eligibility/` | Evaluate student WASSCE grades against a degree program |
| `POST` | `/api/wassce-check/` | Discover all programs a student qualifies for across all universities |
| `POST` | `/api/ai-career-match/` | Match user natural language interest descriptions to careers using Gemini AI |
| `POST` | `/api/career-search/` | Search career catalog and fetch track mappings |
| `POST` | `/api/subject-recommendation/` | Get NaCCA elective combinations and subject recommendations |
| `POST` | `/api/ocr-wassce-results/` | Extract WASSCE grades automatically from uploaded result slips via Gemini Vision |

---

## Copyright & Licensing

Copyright (c) 2026 CareerPath Ghana. All Rights Reserved.

This codebase and associated assets are proprietary and confidential. Unauthorized copying, distribution, modification, or commercial use without prior written consent from the copyright holder is strictly prohibited.

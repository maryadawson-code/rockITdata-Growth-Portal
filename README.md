# AMANDA™ Portal

**Putting Answers at Your Fingertips™**

A secure, role-based AI assistant portal for federal proposal development built by rockITdata.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.32+-red)

---

## 🚀 Features

### Portal Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Executive overview with pipeline stats, active deals, issues, and reviews |
| **Deals Pipeline** | Track opportunities through the Shipley lifecycle with pWin tracking |
| **Workflows** | Phase Navigator (P0→P4) with gate approvals and checklists |
| **Artifacts** | Document library with version control and compliance tracking |
| **Compliance** | Requirements matrix with SHALL/SHOULD/EVAL tracking |
| **Reviews** | Color team reviews (Blue/Pink/Red/Gold) and issue management |
| **Partners** | Teaming partner management with workshare and TA status |
| **Playbook** | Learning engine with golden examples and best practices |
| **AI Chat** | Chat with 7 specialized AI assistants |
| **Admin** | User management, demo scenarios, and integrations |

### AI Assistants

| Assistant | Purpose | Access |
|-----------|---------|--------|
| 🎯 Capture Assistant | Win strategy & competitive intelligence | Private (Capture Lead+) |
| 📝 Proposal Writer | Compelling federal proposal content | All Internal |
| 🛡️ Compliance Checker | Section L/M validation, FAR/DFARS | All Internal |
| 🎭 Red Team Reviewer | Harsh but constructive proposal critique | Private (PM+) |
| 💵 Pricing Analyst | BOE development, rate analysis | Private (Finance+) |
| 📜 Contracts Advisor | T&C review, clause analysis | Private (Contracts) |
| 💬 General Assistant | General-purpose help | All Users |

### Role-Based Access Control (11 Roles)

**Internal Roles:**
- Admin, COO/President, Capture Lead, Proposal Manager, Finance, Contracts, HR, Analyst/Writer

**External Roles:**
- Partner (Service), Vendor (Product), Consultant

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- pip

### Quick Start

```bash
# Clone or extract the project
cd amanda-portal

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required for live AI (optional if using Demo Mode)
ANTHROPIC_API_KEY=your-api-key-here
```

---

## 🎬 Demo Mode

The portal includes a **Demo Mode** that simulates Claude responses without making API calls. This is perfect for:

- Demonstrations to stakeholders
- Training new users
- Testing without using API credits

### Enabling Demo Mode

1. Toggle "Enable Demo Mode" in the sidebar
2. Or run pre-configured scenarios from Admin → Demo Scenarios

### Available Demo Scenarios

| Scenario | Description |
|----------|-------------|
| Win Theme Discovery | Develop win themes for CCN Next Gen |
| RFP Shredding | Extract requirements from sample PWS |
| Compliance Review | Check draft against Section L requirements |

---

## 🗂️ Project Structure

```
amanda-portal/
├── app.py              # Main application with all pages
├── config.py           # Brand constants, roles, bots, gates
├── database.py         # Mock database with seed data
├── demo_mode.py        # Demo engine with simulated responses
├── components.py       # Reusable UI components
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🎨 Brand System

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#990000` | Headers, buttons, accents |
| Primary Light | `#B31B1B` | Hover states |
| Primary Dark | `#7A0000` | Active states |
| Success | `#10B981` | On track, approved |
| Warning | `#F59E0B` | At risk, in review |
| Error | `#EF4444` | Critical issues |

### Phase Colors (Shipley)

| Phase | Color | Name |
|-------|-------|------|
| P0 | Gray | Qualification |
| P1 | Blue | Capture Planning |
| P2 | Purple | Kickoff & Shredding |
| P3 | Amber | Proposal Development |
| P4 | Green | Final QA |

---

## 📊 Seed Data

The portal comes pre-loaded with realistic demo data:

- **5 Deals** - CCN Next Gen, EHRM Restart, IHT 2.0, DHA Data Gov, PPI MEDIC
- **7 Artifacts** - Technical volumes, compliance matrices, strategy briefs
- **7 Requirements** - Sample Section L/M requirements
- **4 Reviews** - Blue, Pink, Red, Gold team reviews
- **4 Issues** - Critical, Major, Minor findings
- **4 Partners** - TriWest, Peraton, TISTA, Leidos
- **5 Playbook Lessons** - Win themes, discriminators, templates
- **6 Users** - Various roles for testing

---

## 🔐 Security Notes

1. **No hardcoded keys** - API keys via environment variables only
2. **RBAC enforced** - Private bots/pages restricted by role
3. **System prompts isolated** - Never exposed to client-side
4. **Demo Mode safe** - No API calls, no data leakage

---

## 🚀 Deployment

### Local Development

```bash
streamlit run app.py --server.port 8501
```

### Production (Docker)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.headless", "true"]
```

### Streamlit Cloud

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set `ANTHROPIC_API_KEY` in secrets

---

## 📝 License

© 2026 rockITdata LLC. All rights reserved.

---

## 🤝 Support

For questions or issues, contact:
- **Mary Womack** - Federal Civilian Account Lead
- Email: mary.womack@rockitdata.com

<div align="center">

# 🎵 Spotify MVC Platform

### A music platform built on a strict three-layer architecture, with both a web UI and a REST API

Users, songs, playlists and subscriptions, served through Jinja2 pages and an OpenAPI-documented
API over the same service layer, with a CLI for data import and statistics.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.12-blue)

</div>

---

## 🛠 Tech Stack

<div align="center">

**Backend**<br>
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2-E92063?logo=pydantic&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

**Frontend and tooling**<br>
![Jinja2](https://img.shields.io/badge/Jinja2-B41717?logo=jinja&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-499848?logo=gunicorn&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-OpenAPI-85EA2D?logo=swagger&logoColor=black)

</div>

---

## 🎬 Demo

<div align="center">

![Demo](docs/demo.gif)

*Home, songs, the create form, playlists, a playlist detail page, statistics and the generated API docs.*

**[▶ Watch the full video](docs/demo.mp4)**

</div>

<details>
<summary><b>Screenshots of every page</b></summary>

<br>

**Home** — summary counters pulled from the service layer

![Home](docs/01-home.png)

**Songs** — the full list with edit and delete actions

![Songs](docs/02-songs.png)

**Song form** — used for both creating and editing

![Song form](docs/03-song-form.png)

**Playlists** — cards showing the owner and the track count

![Playlists](docs/04-playlists.png)

**Playlist detail** — its tracks, plus a picker to attach another song

![Playlist detail](docs/05-playlist-detail.png)

**Statistics** — totals, the subscription breakdown and the average playlist size

![Statistics](docs/06-statistics.png)

**API documentation** — OpenAPI generated from the same routes

![API docs](docs/07-api-docs.png)

</details>

---

## 🚀 Quick Start

### Requirements

- Python 3.12+

### Run

```bash
git clone https://github.com/sergiyclas/spotify-mvc-platform.git
cd spotify-mvc-platform
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env
python cli.py import-csv        # loads the bundled dataset
python main.py
```

Open **http://localhost:8000** for the web interface, or **http://localhost:8000/docs** for the API.

---

## ✨ Features

### 🔀 One service layer, two interfaces

- HTML pages and the JSON API both call the same `SpotifyService`
- A change to a business rule takes effect in both without being written twice
- The CLI uses that same layer, so there are three entry points and one implementation

### 🧱 Layers that are actually separated

- Presentation never touches the database: routes call services, services call repositories
- Only repositories know about SQLAlchemy
- The boundaries are visible in the directory structure, not just in a diagram

### 💳 Subscription types as polymorphism

- Free, Student and Premium are separate classes with their own limits
- No enum plus branching — adding a tier means adding a class
- Limits are enforced in the business layer, not in the templates

### ✏️ CRUD from the browser

- Songs and playlists can be created, edited and deleted from the web interface
- Songs are attached to a playlist from its detail page
- The same operations are available over the REST API

### 🖥 CLI for the data lifecycle

- `init-db` creates the schema
- `import-csv` loads the bundled dataset of 139 tracks, deduplicating users
- `stats` prints totals and the subscription breakdown
- `clean` drops all data
- Setup lives here instead of leaking into the application code

---

## 🏗 Architecture

```mermaid
flowchart TB
    W([Browser]) --> PL
    A([API client]) --> PL
    C([CLI]) --> BLL
    PL[Presentation layer<br/>routes, Jinja2 templates, schemas] --> BLL
    BLL[Business logic layer<br/>SpotifyService, StatisticsService] --> DAL
    DAL[Data access layer<br/>repositories, models] --> DB[(SQLite)]
```

**Project layout**

```
src/
├── pl/         FastAPI routes and Pydantic schemas
├── bll/        business services
├── dal/        SQLAlchemy models, repositories, session handling
├── common/     logging and constants
└── generators/ sample data generation
templates/      Jinja2 pages
static/         stylesheet
cli.py          init-db, import-csv, stats, clean
main.py         application entry point
spotify_data.csv  bundled dataset
```

---

## 📡 API

The full schema is generated at `/docs`. Web routes render pages; `/api/*` routes return JSON.

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/` | Home page with the summary counters |
| `GET` | `/songs` | Song list with CRUD actions |
| `GET` | `/playlists` | Playlist cards |
| `GET` | `/playlists/{id}` | Playlist detail with its songs |
| `GET` | `/statistics` | Platform statistics |
| `GET` | `/docs` | OpenAPI documentation |

---

## 🖥 CLI

```bash
python cli.py init-db              # create the schema
python cli.py import-csv           # import spotify_data.csv
python cli.py import-csv --csv other.csv
python cli.py stats                # counts and subscription breakdown
python cli.py clean                # drop all data
```

---

## 📬 Contact

**Serhiy Dzen** – AI Software Engineer

[![Email](https://img.shields.io/badge/Email-sergiyclas@gmail.com-EA4335?logo=gmail&logoColor=white)](mailto:sergiyclas@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-in/sergiyclas-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sergiyclas/)
[![GitHub](https://img.shields.io/badge/GitHub-sergiyclas-181717?logo=github&logoColor=white)](https://github.com/sergiyclas)

---

<div align="center">

Licensed under the [MIT License](LICENSE)

</div>

# Apna Mumbai Local

Your pocket guide to Mumbai's local train network — 7,500+ trains across Western, Central & Harbour lines.

## Live App

https://apnalocal.streamlit.app

## Features

- **Train Search** — Find trains between any two stations with time-based filtering
- **7,500+ Trains** — Western, Central & Harbour line coverage including AC trains
- **Mid-Route Support** — Search between any intermediate stations, not just endpoints
- **Fare Calculator** — Get ticket prices for any route
- **Platform Info** — Platform numbers, peak hours & metro connectivity
- **Bus Connectivity** — First/last mile BEST bus routes
- **User Reviews** — Submit and read station reviews (synced via Google Sheets)
- **Smart Suggestions** — Dynamic query suggestions based on your searches
- **Language Support** — Hindi & Marathi understanding

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What Can You Ask?

**Train Timings**
- "Andheri to Churchgate"
- "Dadar to Thane at 5 pm"
- "AC trains from Virar"

**Station Info**
- "Platform info Dadar"
- "Reviews for Andheri"

**Fares & Rules**
- "Fare Andheri to Borivali"
- "Monthly pass price"
- "Student concession"
- "Luggage rules"

**Connectivity**
- "Powai to BKC" (bus + train combo)

## Tech Stack

- **Python 3.8+**
- **Streamlit** — Web interface
- **Google Sheets API** — Review storage
- **Pandas** — Train data processing

## Project Structure

```
app.py                    — Main Streamlit app & UI
train_chatbot_enhanced.py — Chatbot logic & train search
fare_calculator.py        — Fare calculation
bus_connections.py        — BEST bus connectivity
station_info.py           — Platform & station details
language_support.py       — Hindi/Marathi support
google_sheets_reviews.py  — Google Sheets review sync
reviews.py                — Review utilities
mumbai_local_trains.csv   — Train schedule data
mumbai_ac_trains.csv      — AC train schedule data
```

## Stations Covered

**Western Line** — Churchgate, Marine Lines, Dadar, Bandra, Andheri, Borivali, Virar & more

**Central Line** — CSMT, Dadar, Kurla, Ghatkopar, Thane, Kalyan, Dombivli & more

**Harbour Line** — CSMT, Kurla, Vashi, Belapur, Panvel & more

---

**Made with love for Mumbai's local train travelers**

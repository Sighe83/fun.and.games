# Aula Ugenoter App

En simpel web-applikation til at logge ind på Aula og se ugenoter for denne og næste uge.

## Installation

1. Installer dependencies:
```bash
pip install -r requirements.txt
```

## Brug

1. Start applikationen:
```bash
python app.py
```

2. Åbn din browser og gå til:
```
http://127.0.0.1:5000
```

3. Log ind med dit UNI-Login brugernavn og adgangskode

4. Se ugenoter for denne uge og næste uge

## Features

- Login med UNI-Login
- Vis information om børn og institutioner
- Vis ugenoter (kalender events) for indeværende uge
- Vis ugenoter (kalender events) for næste uge
- Responsivt design med pæn styling
- Sikker session håndtering

## Filer

- `aula_client.py` - API klient til Aula
- `app.py` - Flask web applikation
- `templates/` - HTML templates
  - `base.html` - Base template
  - `login.html` - Login side
  - `weekly_notes.html` - Ugenoter visning
- `requirements.txt` - Python dependencies

## Sikkerhed

VIGTIGT: Denne app er til privat brug. Del aldrig dine login oplysninger, og lad være med at køre denne app på et offentligt tilgængeligt netværk uden yderligere sikkerhedsforanstaltninger.

## API Information

Applikationen bruger Aula's officielle API (v18) til at hente data.

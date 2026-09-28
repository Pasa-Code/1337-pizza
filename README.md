# 1337 Pizza – REST-Backend für einen Pizza-Lieferdienst

Teamprojekt im Modul **Software Engineering** an der Hochschule Darmstadt (Sommersemester 2026), umgesetzt von vier Studierenden.
Der Service stellt eine REST-API für einen fiktiven Pizza-Lieferdienst bereit: Bestellungen, Pizzatypen, Teige, Saucen, Toppings, Getränke, Lagerbestände und Lieferadressen.

## Tech-Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Datenbank:** PostgreSQL
- **Infrastruktur:** Docker, Docker Compose, Kubernetes (Deployment-Manifeste)
- **CI/CD & Qualität:** GitLab CI, SonarQube, Ruff, mypy
- **Tests:** pytest (Unit- und Integrationstests), Tavern (Service-Tests)
- **Logging:** Graylog

## Ausgangslage

Das Grundgerüst des Projekts (Projektstruktur, CI-Vorlage, Teile der Dokumentation) wurde von der Hochschule bereitgestellt.
Darauf aufbauend hat das Team die Funktionalität über mehrere Labs hinweg erweitert.

## Mein Beitrag

- **Sauce-Endpunkt:** vollständig umgesetzt – Datenmodell, Alembic-Migration, Schemas, CRUD-Logik und Router, inklusive Integrationstest und Anpassung der bestehenden Tests
- **Bestellungen:** Filtern nach Status und Sortieren nach Erstellungszeit
- **Logging:** Logging für Bestellungen, Adressen und Lagerbestände ergänzt (Anbindung an Graylog)
- **Tests:** Integrationstests für Teige, Zutaten, Getränkebestand und Pizzatypen; Service-Tests mit Tavern
- **Code-Qualität:** Ruff- und SonarQube-Findings behoben

## Lokal starten

Voraussetzung: Docker

```bash
docker compose up --build
```

Die interaktive API-Dokumentation ist anschließend unter http://localhost:8000/docs erreichbar.

## Hinweis

Das Projekt wurde ursprünglich im GitLab der Hochschule entwickelt.
Links in `doc/` und in der CI-Konfiguration verweisen teilweise auf interne Hochschul-Systeme, die öffentlich nicht erreichbar sind.

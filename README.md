# Bagel Alley website

Website van Bagel Alley, bagel- en koffiezaak in Wassenaar. Pagina's: home, menu, taarten bestellen (afhalen), shop, vacatures en reserveren (telefonisch). Gebouwd met Flask en Jinja, gehost op Vercel.

## Lokaal draaien

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run
```

De site draait dan op http://127.0.0.1:5000. Zonder env vars werkt alles, behalve het versturen van mail (zie hieronder).

Tests:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Environment variables

Zet deze op Vercel onder Settings, Environment Variables (Production). Lokaal mogen ze in je shell of in een `.env` die niet in git komt.

| Variabele | Verplicht | Wat |
|---|---|---|
| `SITE_URL` | ja | Volledige basis-URL zonder slash aan het eind, bijv. `https://www.bagelalley.nl`. Wordt gebruikt voor canonical, og-tags, sitemap, robots en afbeeldingen in e-mails. |
| `SENDGRID_API_KEY` | ja, voor bestellingen | API-key van SendGrid. |
| `MAIL_VAN` | ja, voor bestellingen | Afzenderadres van de mails. Moet in SendGrid als afzender geverifieerd zijn. Er is bewust geen standaardwaarde. |
| `ORDER_MAIL_TO` | ja | Adres waar taartbestellingen binnenkomen. |
| `SECRET_KEY` | aanbevolen | Lange willekeurige string voor Flask-sessies. Zonder deze waarde wordt bij elke start een tijdelijke sleutel gemaakt. |
| `ONLINE_RESERVEREN` | nee, laat leeg | Zie hieronder. |
| `ADMIN_ENABLED` | nee, laat leeg | Zie hieronder. |
| `ADMIN_PASS` | alleen met `ADMIN_ENABLED` | Wachtwoord voor de admin. Zonder deze waarde kan niemand inloggen. |

Ontbreekt `SENDGRID_API_KEY` of `MAIL_VAN`, dan crasht er niets: het bestelformulier meldt netjes "Nog niet verstuurd" en geeft de klant de gegevens om zelf contact op te nemen.

### De twee schakelaars

- `ONLINE_RESERVEREN`: staat standaard uit. Reserveren gaat telefonisch; alle reserveerknoppen bellen de zaak en de chat verwijst naar de telefoon. Met `ONLINE_RESERVEREN=1` komt het online reserveringsformulier op /reserveren terug. De code daarvoor blijft bewust in de repo staan.
- `ADMIN_ENABLED`: staat standaard uit. Dan geeft elke /admin-URL een 404. Met `ADMIN_ENABLED=1` en een `ADMIN_PASS` werkt het gearchiveerde beheerscherm voor reserveringen weer (templates in `templates/archief/`).

Op Vercel bewaart de reserveringsdatabase alleen tijdelijk (`/tmp`). Zet online reserveren dus pas aan met een echte database.

## Bestanden

- `app.py`: routes, chatbot, bestelvalidatie en mails.
- `menukaart.py`: tekstversie van de menukaart.
- `beeldmanifest.py`: lijst van geoptimaliseerde afbeeldingsvarianten (AVIF/WebP) voor `pic()`.
- `templates/`: Jinja-templates. Gedeelde stukken beginnen met `_`.
- `public/static/`: alle statische bestanden (afbeeldingen, lettertypes, favicons, e-mailafbeeldingen). Vercel serveert deze map via zijn CDN onder `/static/...`; lokaal doet Flask dat. Data die de Python-code tijdens het draaien nodig heeft, hoort daarom niet in `public/` maar in een Python-module naast `app.py`.

De sitemap haalt `lastmod` uit `SITEMAP` in `app.py`: zet daar de datum als de inhoud van een pagina verandert.

`vercel.json` zet de browsercache voor `/static/`: lettertypes een jaar (een nieuw lettertype krijgt dus een nieuwe bestandsnaam), de rest een dag.

De originele bronfoto's staan niet in de repo. Alleen de verkleinde varianten in `public/static/opt/` worden gebruikt.

## Chatbot

De chat gebruikt geen externe AI. Hij herkent de vraag met vaste patronen en antwoordt met ingebouwde teksten uit `app.py` (openingstijden, menu, bestellen, reserveren en dergelijke). Waar een antwoord nog niet bevestigd is, verwijst hij naar de telefoon. Vragen die hij niet herkent worden alleen als tekst gelogd, zonder IP of andere gegevens.

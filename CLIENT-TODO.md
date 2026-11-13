# CLIENT-TODO

Open vragen voor de klant. Alles hieronder staat nu bewust ongewijzigd (of zonder feit) op de site.
Regelnummers gelden voor branch `polish-2027`. Na antwoord: tekst aanpassen op de genoemde plek en het punt hier weghalen.

## 1. Naam van de chatbot (Sonja)
De chat heet "Sonja" en zegt nu "de automatische hulp van Bagel Alley" (niet meer "de eigenares").
Vraag: mag de naam Sonja blijven, of liever geen naam?
- `app.py:510` `"avatar_naam": "Sonja"` (ook de initialen `"avatar_initialen": "SO"` op de regel eronder). De chat noemt zich nu "de automatische hulp".
- `templates/index.html:1423` welkomstbericht

## 2. "Donderdag open!"
Vraag: is dit nog nieuws, of mag het weg (of vervangen door bijv. "Keuken open tot 15:30")?
- `templates/index.html:636` infostrook op de homepage

## 3. Chatbot: veilige antwoorden
Voor deze onderwerpen herkent de chat de vraag, maar zegt hij nog: "Goede vraag over ..., dat vertellen we je graag even persoonlijk: bel 070-514 61 16."
Invullen op één plek: `app.py:679` (`CHAT_FEITEN`). Zet daar het bevestigde antwoord (kort, 1 tot 3 zinnen) in plaats van `None`; de chat gebruikt het dan meteen.

| intent | vraag aan de klant |
|---|---|
| `feestdagen` | Zijn jullie open met kerst, oud en nieuw, pasen, pinksteren, koningsdag, hemelvaart? Welke tijden? (nu: "Op feestdagen kunnen onze tijden afwijken" plus bellen) |
| `parking` | Waar kun je parkeren, betaald of blauwe zone? (nu: bellen plus routelink) |
| `huisdieren` | Mogen honden en andere huisdieren mee, binnen en op het terras? (eerder in de chat genoemd: "toegestaan binnen en op het terras"; volgens de laatste opdracht nog onbevestigd) |
| `kinderstoel` | Is er een kinderstoel? |
| `betalen` | Pin, contant, creditcard, Tikkie, Apple Pay? |
| `wifi_laptop` | Wifi voor gasten? Stopcontacten? Is werken met een laptop welkom? |
| `terras` | Is er een terras of kun je buiten zitten? |
| `toegankelijkheid` | Rolstoeltoegankelijk, drempel, aangepast toilet? |
| `toilet` | Toilet voor gasten, verschoontafel? |
| `instagram_social` | Instagram/Facebook-account (zie ook punt 4)? |
| `drukte` | Wanneer is het druk, hoe lang is de wachttijd? |

Ook nog: **vegan** krijgt nu alleen wat op de kaart staat (vegetarische bagels, twee vegan soepen). Zijn er meer vegan opties?

## 4. Instagram
Vraag: klopt `@bagelalleywassenaar`? Dan zetten we hem ook op de site en in de structured data.
- `app.py:231` e-mailfooter
- `app.py:544` `SOCIAL = [...]` (leeg; voor schema.org `sameAs`)

## 5. Privacyverklaring
Er is geen privacyverklaring. Het bestelformulier vraagt naam, e-mail en telefoon. De technische kant is gedaan (lettertypes zelf gehost, Google Maps pas na een tik).
Vraag: wie levert de tekst? Daarna een link in de footer en in de cookiemelding.
- `templates/index.html:904` footer-onderkant (link toevoegen)
- `templates/_cookie.html:4` tekst cookiemelding

## 6. Vacatures en het 06-nummer
Vraag: wordt er nog gezocht, en kloppen deze punten? Van wie is 06-513 43 359 en mag het openbaar?
- `templates/jobs.html:128` "Meteen starten"
- `templates/jobs.html:156` "Eerlijk salaris" (liever de echte basis, bijv. cao Horeca)
- `templates/jobs.html:162-167` "Wat wij bieden" (gezellige werkvloer, flexibele tijden, zelfstandig werken, gratis koffie & lunch, ruimte om te groeien)
- `templates/jobs.html:178` belknop 06-513 43 359
- `templates/shop.html:108` WhatsApp-link in de bestelnotitie
- `templates/bestellen.html:593` WhatsApp-nummer als terugvaloptie als de bestelling niet automatisch verstuurd kan worden

## 7. Overige [bevestigen]-punten uit AUDIT.md
- **Menu-intro "Elke dag wisselend aanbod"** (copy 27): klopt dat naast een vaste kaart? `templates/menu.html:258`
- **"Online reserveren komt binnenkort."** (copy 35): weghalen? `templates/booking.html:261`
- **Favorieten in de reserveringsmail** (copy 38, E1): "New York Classic" en "Smoked Salmon Deluxe" staan niet op de kaart (wel "Roomkaas" en "Bagel zalm"). Echte namen? `app.py:317-318` en `app.py:393` (nieuwsbrief). Wordt pas verstuurd als online reserveren aan gaat.

## 8. Menukaart (afbeeldingen en tekstversie)
De tekstversie op /menu (`menukaart.py`) is letterlijk van de gedrukte kaart overgenomen. Bewust weggelaten of onzeker:
- Het blok "Order for take away" (bellen of WhatsApp 06-51343359): weggelaten tot punt 6 beantwoord is.
- Het koffie-tekstje van de brander: op de kaart staat "Lagaranta", de klant schrijft "La Garanta". Welke spelling klopt? Op de site staat nu "La Garanta".
- IJskoffie, haver-/sojamelk en extra shot staan op de kaart in de L-kolom; in de tekstversie zonder maat vermeld.

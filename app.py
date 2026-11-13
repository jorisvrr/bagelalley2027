# region ── IMPORTS ─────────────────────────────────────────────
from flask import Flask, render_template, request, jsonify, session, Response, abort
import os
import json
import re
import requests
import sqlite3
from datetime import datetime, date, timedelta
import html as _html
# endregion

# Statische bestanden staan in public/static: Vercel serveert public/ via zijn CDN
# (Flask's eigen static-map wordt daar genegeerd). Lokaal serveert Flask ze zelf.
app = Flask(__name__, static_folder="public/static", static_url_path="/static")
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)  # geen vaste fallback

# Iconen-partial: valt terug op een lege macro als templates/_icons.html ontbreekt,
# zodat `{% from "_icons.html" import icon %}` een pagina nooit kan breken.
from jinja2 import ChoiceLoader, DictLoader
app.jinja_loader = ChoiceLoader([
    app.jinja_loader,
    DictLoader({"_icons.html": "{% macro icon(name, size=20, label=None) %}{% endmacro %}"}),
])
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=bool(os.environ.get("VERCEL")),  # Vercel = altijd HTTPS
    MAX_CONTENT_LENGTH=64 * 1024,  # alleen kleine JSON-berichten, geen uploads
)

@app.after_request
def _security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if os.environ.get("VERCEL"):
        resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
    return resp

# region ── SECURITY: proxy, rate limiting, validatie-helpers ────
import hmac
from werkzeug.middleware.proxy_fix import ProxyFix

# Railway zit achter een reverse proxy: vertrouw 1 proxy-hop zodat we het
# echte client-IP zien (nodig voor correcte rate limiting) en de juiste scheme.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Rate limiter op ALLE endpoints (default), met strengere limieten per route.
# In-memory volstaat voor 1 instance; voor meerdere workers/instances:
# zet RATELIMIT_STORAGE_URI naar bijv. een Redis-URL.
# Defensief geladen: ontbreekt Flask-Limiter, dan blijft de site draaien
# (zonder rate limiting) i.p.v. te crashen. Voeg het toe aan requirements.txt
# om de limieten echt te activeren.
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["300 per hour", "60 per minute"],
        storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
        strategy="fixed-window",
    )

    @limiter.request_filter
    def _rate_limit_exempt():
        # Statische bestanden en infra-endpoints niet limiteren (anders breken
        # asset-loads en health checks). Echte endpoints blijven wél begrensd.
        return request.endpoint in {"static", "ping", "robots_txt", "sitemap_xml"}

except ImportError:
    print("[WAARSCHUWING] Flask-Limiter niet geinstalleerd - rate limiting staat UIT. "
          "Voeg 'Flask-Limiter' toe aan requirements.txt en deploy opnieuw.")

    class _NoLimiter:
        """Vervanger die niets limiteert, zodat de decorators blijven werken."""
        def limit(self, *a, **k):
            def deco(f):
                return f
            return deco

        def request_filter(self, f):
            return f

        def exempt(self, f):
            return f

    limiter = _NoLimiter()

def _safe_eq(a, b) -> bool:
    """Constant-time string-vergelijking (tegen timing-attacks)."""
    return hmac.compare_digest(str(a), str(b))

def _clean_str(value, maxlen: int) -> str:
    """Strip + harde lengtelimiet voor vrije-tekst input."""
    return str(value or "").strip()[:maxlen]

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _valid_iso_date(s: str):
    """Geeft een geldige ISO-datum terug, of None bij ongeldige invoer."""
    try:
        return date.fromisoformat(str(s))
    except (ValueError, TypeError):
        return None

@app.errorhandler(429)
def _ratelimit_handler(e):
    return jsonify({
        "succes": False,
        "antwoord": "Te veel verzoeken. Wacht even en probeer het zo opnieuw.",
        "fout": "Te veel verzoeken. Wacht even en probeer het zo opnieuw.",
    }), 429

def _error_pagina(titel: str, tekst: str, code: int):
    # Inline HTML zonder template, zodat de foutpagina zelf nooit kan falen.
    html = f"""<!DOCTYPE html><html lang="nl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>{titel} | Bagel Alley</title>
<meta name="theme-color" content="#1A1018"><meta name="robots" content="noindex">
<style>
@font-face{{font-family:'Playfair Display';font-weight:400 900;font-display:swap;src:url('/static/fonts/playfair-display-latin.woff2') format('woff2')}}
@font-face{{font-family:'DM Sans';font-weight:100 1000;font-display:swap;src:url('/static/fonts/dm-sans-latin.woff2') format('woff2')}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;min-height:100svh;display:flex;align-items:center;justify-content:center;
background:radial-gradient(circle at 50% 40%,#271b30,#1A1018);color:#F5F0E8;font-family:'DM Sans',Arial,sans-serif;
text-align:center;padding:max(24px,env(safe-area-inset-top)) 24px max(24px,env(safe-area-inset-bottom))}}
.c{{max-width:460px}}.b{{font-family:'Playfair Display',Georgia,serif;font-size:64px;font-weight:700;color:#9B6EE0;line-height:1}}
h1{{font-family:'Playfair Display',Georgia,serif;font-size:26px;margin:14px 0 8px}}
p{{color:rgba(245,240,232,.75);font-size:16px;line-height:1.6;margin:0}}
nav{{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:24px}}
a{{display:inline-flex;align-items:center;min-height:44px;padding:0 20px;border-radius:3px;text-decoration:none;font-size:14px;font-weight:600;
color:#F5F0E8;border:1.5px solid rgba(245,240,232,.35)}}a.p{{background:#8758CE;border-color:#8758CE;color:#fff}}
a:focus-visible{{outline:2px solid #B394EC;outline-offset:2px}}</style>
</head><body><main class="c"><div class="b">{code}</div><h1>{titel}</h1><p>{tekst}</p>
<nav aria-label="Verder naar"><a class="p" href="/">Naar de homepage</a><a href="/menu">Bekijk de kaart</a>
<a href="tel:+31705146116">Bel 070-514 61 16</a>
<a href="https://www.google.com/maps/search/?api=1&amp;query=Bagel%20Alley%20Langstraat%2042%20Wassenaar" rel="noopener">Route</a></nav></main></body></html>"""
    return html, code

@app.errorhandler(404)
def _not_found(e):
    return _error_pagina("Pagina niet gevonden",
                         "Deze pagina bestaat niet. Bekijk de kaart, bel ons of ga terug naar de homepage.", 404)

@app.errorhandler(500)
def _server_error(e):
    return _error_pagina("Er ging iets mis",
                         "Er is een onverwachte fout opgetreden. Probeer het zo nog eens.", 500)
# endregion

# Tekstversie van de menukaart (menukaart.py). Ontbreekt het bestand, dan alleen de afbeeldingen.
try:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("menukaart", os.path.join(os.path.dirname(os.path.abspath(__file__)), "menukaart.py"))
    _mod = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_mod)
    MENUKAART = _mod.MENUKAART
except Exception as e:
    print(f"[MENU] tekstversie niet geladen: {e}")
    MENUKAART = []

# region ── SENDGRID MAIL ───────────────────────────────────────
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
MAIL_VAN         = os.environ.get("MAIL_VAN", "jorisvrr@gmail.com")
MAIL_VAN_NAAM    = "Bagel Alley"

def datum_nl(datum_str: str) -> str:
    """Zet 2026-06-08 om naar 'maandag 8 juni 2026'."""
    from datetime import date as dt
    dagen   = ["maandag","dinsdag","woensdag","donderdag","vrijdag","zaterdag","zondag"]
    maanden = ["januari","februari","maart","april","mei","juni",
               "juli","augustus","september","oktober","november","december"]
    d = dt.fromisoformat(datum_str)
    return f"{dagen[d.weekday()]} {d.day} {maanden[d.month - 1]} {d.year}"

def _fav_row(img, titel, tekst):
    return f"""<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:14px;background:#ffffff;border-radius:10px;overflow:hidden;"><tr>
      <td style="width:90px;font-size:0;line-height:0;"><img src="{img}" width="90" height="90" alt="{titel}" style="display:block;width:90px;height:90px;object-fit:cover;"></td>
      <td style="padding:12px 16px;vertical-align:middle;">
        <div style="font-family:Georgia,serif;font-size:15px;font-weight:bold;color:#2a2230;margin-bottom:4px;">{titel}</div>
        <div style="font-family:Arial,sans-serif;font-size:12px;color:#8a8294;line-height:1.6;">{tekst}</div>
      </td>
    </tr></table>"""

def _mail_footer():
    return f"""<tr><td style="background:#efe9e0;padding:30px 34px;border-top:1px solid #e4dcd0;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td class="col" width="33%" valign="top" style="font-family:Arial,sans-serif;padding-right:10px;">
        <div style="font-size:10px;letter-spacing:1.5px;color:#8758ce;text-transform:uppercase;margin-bottom:8px;">Openingstijden</div>
        <div style="font-size:12px;color:#7c7484;line-height:1.7;">Maandag, woensdag t/m zondag<br>08:00 &ndash; 16:00<br>Dinsdag gesloten</div>
      </td>
      <td class="col" width="34%" valign="top" style="font-family:Arial,sans-serif;padding-right:10px;">
        <div style="font-size:10px;letter-spacing:1.5px;color:#8758ce;text-transform:uppercase;margin-bottom:8px;">Bagel Alley Wassenaar</div>
        <div style="font-size:12px;color:#7c7484;line-height:1.7;">Langstraat 42<br>2242 KM Wassenaar<br>070 514 61 16<br>info@bagelalley.nl</div>
      </td>
      <td class="col" width="33%" valign="top" style="font-family:Arial,sans-serif;padding-right:10px;">
        <div style="font-size:10px;letter-spacing:1.5px;color:#8758ce;text-transform:uppercase;margin-bottom:8px;">Volg ons</div>
        <div style="font-size:12px;color:#7c7484;line-height:1.7;">Voor de lekkerste bagels, nieuwtjes en dagelijkse inspiratie.<br><a href="https://instagram.com/bagelalleywassenaar" style="color:#8758ce;text-decoration:none;">@bagelalleywassenaar</a></div>
      </td>
    </tr></table>
  </td></tr>
  <tr><td style="background:#8758ce;padding:14px;text-align:center;border-radius:0 0 14px 14px;"><a href="{SITE_URL}" style="font-family:Arial,sans-serif;font-size:12px;letter-spacing:2px;color:#ffffff;text-decoration:none;text-transform:uppercase;font-weight:bold;">bagelalley.nl</a></td></tr>"""

def _mail_topbar():
    return """<tr><td style="background:#faf7f2;padding:20px 32px;border-bottom:1px solid #ece7df;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td style="font-family:Georgia,serif;font-size:20px;font-weight:bold;color:#2a2230;">Bagel <span style="color:#8758ce;">Alley</span></td>
      <td style="text-align:right;font-family:Arial,sans-serif;font-size:10px;letter-spacing:1.5px;color:#9a8fa6;text-transform:uppercase;">&bull; Wassenaar &middot; Langstraat 42</td>
    </tr></table>
  </td></tr>"""

# ── Bagel van de maand (centraal beheerd; pas dit maandelijks aan) ──
BAGEL_VD_MAAND = {
    "maand": "Juni 2026",
    "naam": "The Spanish Classic",
    "tagline": "Mediterraan. Hartig. Vol van smaak.",
    "beschrijving": "Een mediterrane klassieker: onze krokante alles-bagel met verse rucola, "
                    "luchtige omelet, pittige chorizo en zoete zongedroogde tomaten. "
                    "Zuid-Europese smaken in &eacute;&eacute;n perfecte hap.",
    "inspiratie": "Ge&iuml;nspireerd op Zuid-Europa: lichte, zonnige smaken en de juiste "
                  "balans tussen hartig en fris. Een bagel die net zo goed werkt bij het "
                  "ontbijt, de lunch of een ontspannen weekendbrunch.",
    "ingredienten": ["Rucola", "Omelet", "Chorizo", "Zongedroogde tomaten"],
    "afbeelding": "/static/specials/bagelvdmaand.png",
}

def mail_html(naam: str, datum_str: str, tijd: str, gasten: int) -> str:
    """Reserverings-bevestigingsmail (warme, redactionele stijl)."""
    datum_display = datum_nl(datum_str)
    delen = naam.split()
    voornaam = delen[0] if delen else naam
    gasten_label = "persoon" if gasten == 1 else "personen"
    img_hero    = f"{SITE_URL}/static/fotos/pexels-amar-28056733.jpg"
    img_classic = f"{SITE_URL}/static/fotos/pexels-barbara-g-135944487-11599632.jpg"
    img_salmon  = f"{SITE_URL}/static/fotos/pexels-amar-28056766.jpg"
    img_coffee  = f"{SITE_URL}/static/specials/koffie.png"
    return f"""<!DOCTYPE html><html lang="nl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Je tafel staat klaar | Bagel Alley</title><style>@media (max-width:480px){{.col{{display:block!important;width:100%!important;padding-bottom:18px!important}}}}</style></head>
<body style="margin:0;padding:0;background:#ece7df;font-family:Georgia,'Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ece7df;"><tr><td align="center" style="padding:26px 12px;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background:#faf7f2;border-radius:14px;overflow:hidden;">
  {_mail_topbar()}

  <tr><td style="font-size:0;line-height:0;"><img src="{img_hero}" width="600" alt="Vers ontbijt bij Bagel Alley" style="display:block;width:100%;max-width:600px;height:auto;"></td></tr>

  <tr><td style="background:#faf7f2;padding:36px 40px 28px;text-align:center;">
    <div style="font-family:Arial,sans-serif;font-size:11px;letter-spacing:2px;color:#8758ce;text-transform:uppercase;margin-bottom:14px;">Reservering bevestigd</div>
    <div style="font-family:Georgia,serif;font-size:40px;font-weight:bold;color:#2a2230;line-height:1.05;">Je tafel<br>staat klaar.</div>
    <div style="font-family:Arial,sans-serif;font-size:14px;color:#7c7484;line-height:1.7;margin-top:16px;">Hoi {voornaam}, we kijken ernaar uit je te verwelkomen bij Bagel Alley Wassenaar.</div>
  </td></tr>

  <tr><td style="background:#ffffff;padding:0 40px 30px;">
    <div style="font-family:Arial,sans-serif;font-size:11px;letter-spacing:2px;color:#8758ce;text-transform:uppercase;text-align:center;padding:26px 0 18px;">Jouw reservering</div>
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr><td style="padding:11px 0;border-bottom:1px solid #f1ece4;font-family:Arial,sans-serif;font-size:12px;color:#a99fb3;">Datum</td><td style="padding:11px 0;border-bottom:1px solid #f1ece4;text-align:right;font-family:Georgia,serif;font-size:16px;font-weight:bold;color:#2a2230;">{datum_display}</td></tr>
      <tr><td style="padding:11px 0;border-bottom:1px solid #f1ece4;font-family:Arial,sans-serif;font-size:12px;color:#a99fb3;">Tijdstip</td><td style="padding:11px 0;border-bottom:1px solid #f1ece4;text-align:right;font-family:Georgia,serif;font-size:16px;font-weight:bold;color:#2a2230;">{tijd}</td></tr>
      <tr><td style="padding:11px 0;border-bottom:1px solid #f1ece4;font-family:Arial,sans-serif;font-size:12px;color:#a99fb3;">Gasten</td><td style="padding:11px 0;border-bottom:1px solid #f1ece4;text-align:right;font-family:Georgia,serif;font-size:16px;font-weight:bold;color:#2a2230;">{gasten} {gasten_label}</td></tr>
      <tr><td style="padding:11px 0;font-family:Arial,sans-serif;font-size:12px;color:#a99fb3;">Locatie</td><td style="padding:11px 0;text-align:right;font-family:Georgia,serif;font-size:15px;font-weight:bold;color:#2a2230;">Langstraat 42, Wassenaar</td></tr>
    </table>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:22px;"><tr><td align="center">
      <a href="https://maps.google.com/?q=Langstraat+42+2242+KM+Wassenaar" style="display:inline-block;background:#8758ce;color:#ffffff;font-family:Arial,sans-serif;font-size:13px;font-weight:bold;text-decoration:none;padding:13px 30px;border-radius:8px;">Route plannen &rarr;</a>
    </td></tr></table>
    <div style="font-family:Arial,sans-serif;font-size:11px;color:#b3a9bd;text-align:center;margin-top:14px;">Parkeren mogelijk in de omgeving</div>
  </td></tr>

  <tr><td style="background:#f5f0e8;padding:34px 40px 8px;">
    <div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:#2a2230;margin-bottom:12px;">Even weg uit de drukte.</div>
    <div style="font-family:Arial,sans-serif;font-size:13px;color:#7c7484;line-height:1.8;">Bij Bagel Alley draait alles om verse ingredi&euml;nten, huisgemaakte smaken en een plek waar je rustig kunt genieten. Van een uitgebreid ontbijt tot een ontspannen lunch, wij zorgen dat alles voor je klaarstaat.</div>
  </td></tr>

  <tr><td style="background:#f5f0e8;padding:24px 40px 30px;">
    <div style="font-family:Georgia,serif;font-size:18px;font-weight:bold;font-style:italic;color:#8758ce;margin-bottom:16px;">Favorieten van onze gasten</div>
    {_fav_row(img_classic, "New York Classic", "Onze klassieke bagel met roomkaas. Simpel, vers en precies zoals het hoort.")}
    {_fav_row(img_salmon, "Smoked Salmon Deluxe", "Gerookte zalm, roomkaas, rode ui, kappertjes en rucola. Een favoriet voor iedere dag.")}
    {_fav_row(img_coffee, "Specialty Coffee", "Vers gezet met zorgvuldig geselecteerde bonen. Perfect bij je bagel.")}
  </td></tr>

  <tr><td style="background:#f5f0e8;padding:4px 40px 38px;text-align:center;">
    <div style="font-family:Georgia,serif;font-size:18px;font-style:italic;color:#8758ce;margin-bottom:6px;">Tot snel bij Bagel Alley!</div>
    <div style="font-family:Arial,sans-serif;font-size:12px;font-weight:bold;letter-spacing:1px;color:#2a2230;text-transform:uppercase;">Team Bagel Alley</div>
  </td></tr>

  {_mail_footer()}
</table></td></tr></table>
</body></html>"""

def newsletter_html(naam: str = "") -> str:
    """Maandelijkse nieuwsbrief rond de Bagel van de Maand."""
    b = BAGEL_VD_MAAND
    delen = naam.split() if naam else []
    voornaam = delen[0] if delen else ""
    intro = (f"Hoi {voornaam}, ontdek " if voornaam else "Ontdek ")
    img_botm   = f"{SITE_URL}{b['afbeelding']}"
    img_coffee = f"{SITE_URL}/static/specials/koffie.png"
    img_cake   = f"{SITE_URL}/static/taarten/redvelvet.png"
    img_bagel  = f"{SITE_URL}/static/fotos/pexels-anchornhaven-43716305-29445728.jpg"

    ing = "".join(
        f"""<td align="center" valign="top" style="padding:4px;">
          <div style="display:inline-block;font-family:Arial,sans-serif;font-size:12px;color:#5a4f68;background:#ffffff;border:1px solid #e4dcd0;border-radius:999px;padding:6px 12px;line-height:1.3;">{label}</div>
        </td>"""
        for label in b["ingredienten"]
    )

    def _more(img, titel, tekst):
        return f"""<td class="col" width="33%" valign="top" style="padding:0 6px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border-radius:10px;overflow:hidden;">
            <tr><td style="font-size:0;line-height:0;"><img src="{img}" width="170" alt="{titel}" style="display:block;width:100%;height:110px;object-fit:cover;"></td></tr>
            <tr><td style="padding:12px 12px 14px;">
              <div style="font-family:Arial,sans-serif;font-size:11px;font-weight:bold;letter-spacing:.5px;color:#2a2230;text-transform:uppercase;margin-bottom:5px;">{titel}</div>
              <div style="font-family:Arial,sans-serif;font-size:11px;color:#8a8294;line-height:1.5;">{tekst}</div>
            </td></tr>
          </table>
        </td>"""

    return f"""<!DOCTYPE html><html lang="nl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Bagel van de maand | Bagel Alley</title><style>@media (max-width:480px){{.col{{display:block!important;width:100%!important;padding-bottom:18px!important}}}}</style></head>
<body style="margin:0;padding:0;background:#ece7df;font-family:Georgia,'Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ece7df;"><tr><td align="center" style="padding:26px 12px;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background:#faf7f2;border-radius:14px;overflow:hidden;">
  {_mail_topbar()}

  <tr><td style="background:#faf7f2;padding:38px 40px 6px;text-align:center;">
    <span style="display:inline-block;border:1px solid #c9a8f0;color:#8758ce;font-family:Arial,sans-serif;font-size:10px;letter-spacing:2px;text-transform:uppercase;padding:5px 14px;border-radius:20px;">Nieuw</span>
    <div style="font-family:Georgia,serif;font-size:38px;font-weight:bold;color:#2a2230;line-height:1.1;margin-top:18px;">Bagel van<br>de <span style="font-style:italic;color:#8758ce;">maand.</span></div>
    <div style="font-family:Arial,sans-serif;font-size:12px;font-weight:bold;letter-spacing:2px;color:#2a2230;text-transform:uppercase;margin-top:14px;">{b['naam']}</div>
    <div style="font-family:Georgia,serif;font-size:17px;font-style:italic;color:#8758ce;margin-top:10px;">{b['tagline']}</div>
    <div style="font-family:Arial,sans-serif;font-size:13px;color:#7c7484;line-height:1.8;margin-top:14px;">{intro}onze nieuwste creatie van {b['maand'].lower()}. {b['beschrijving']}</div>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:22px;"><tr><td align="center">
      <a href="{SITE_URL}/menu" style="display:inline-block;background:#8758ce;color:#ffffff;font-family:Arial,sans-serif;font-size:13px;font-weight:bold;text-decoration:none;padding:13px 30px;border-radius:8px;">Proef hem deze maand &rarr;</a>
    </td></tr></table>
  </td></tr>

  <tr><td style="font-size:0;line-height:0;padding-top:24px;"><img src="{img_botm}" width="600" alt="{b['naam']}" style="display:block;width:100%;max-width:600px;height:auto;"></td></tr>

  <tr><td style="background:#f5f0e8;padding:26px 30px;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>{ing}</tr></table>
  </td></tr>

  <tr><td style="background:#faf7f2;padding:32px 40px;">
    <div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:#2a2230;margin-bottom:12px;">Ge&iuml;nspireerd op Zuid-Europa.</div>
    <div style="font-family:Arial,sans-serif;font-size:13px;color:#7c7484;line-height:1.8;">{b['inspiratie']}</div>
  </td></tr>

  <tr><td style="background:#f5f0e8;padding:30px 34px;">
    <div style="font-family:Georgia,serif;font-size:18px;font-weight:bold;font-style:italic;color:#8758ce;margin-bottom:16px;">Meer om van te genieten</div>
    <table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      {_more(img_coffee, "Specialty Coffee", "Vers gezet, perfect bij je bagel of als moment voor jezelf.")}
      {_more(img_cake, "Verse taarten", "Huisgemaakt en elke dag vers, ook op bestelling via onze webshop.")}
      {_more(img_bagel, "Klassieke bagels", "Van New York Classic tot Smoked Salmon Deluxe. Onze alltime favorieten.")}
    </tr></table>
  </td></tr>

  <tr><td style="background:#8758ce;padding:36px 40px;text-align:center;">
    <div style="font-family:Georgia,serif;font-size:24px;font-weight:bold;color:#ffffff;margin-bottom:10px;">Zin in gezelligheid?</div>
    <div style="font-family:Arial,sans-serif;font-size:13px;color:rgba(255,255,255,0.85);line-height:1.7;margin-bottom:22px;">Kom langs en ontdek waarom onze gasten telkens terugkomen voor iets nieuws. Reserveer eenvoudig je tafel en geniet.</div>
    <a href="{SITE_URL}/reserveren" style="display:inline-block;background:#ffffff;color:#8758ce;font-family:Arial,sans-serif;font-size:13px;font-weight:bold;text-decoration:none;padding:13px 30px;border-radius:8px;">Reserveer een tafel &rarr;</a>
  </td></tr>

  {_mail_footer()}
</table></td></tr></table>
</body></html>"""


def sendgrid_verstuur(naar: str, onderwerp: str, html_inhoud: str, antwoord_naar: str = "info@bagelalley.nl") -> bool:
    """Verstuurt een HTML-mail via SendGrid. Geeft alleen True terug als SendGrid
    de mail heeft geaccepteerd (status 200/202). Zonder API-key: False."""
    if not SENDGRID_API_KEY:
        print("[MAIL] SENDGRID_API_KEY ontbreekt, mail niet verstuurd")
        return False
    try:
        payload = {
            "personalizations": [{"to": [{"email": naar}]}],
            "from": {"email": MAIL_VAN, "name": MAIL_VAN_NAAM},
            "reply_to": {"email": antwoord_naar},
            "subject": onderwerp,
            "content": [{"type": "text/html", "value": html_inhoud}],
        }
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            json=payload,
            headers={"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"},
            timeout=10,
        )
        ok = resp.status_code in (200, 202)
        print(f"[MAIL] {onderwerp[:40]} -> status {resp.status_code}")
        if not ok:
            print(f"[MAIL FOUT] {resp.text[:300]}")
        return ok
    except Exception as e:
        print(f"[MAIL FOUT] {e}")
        return False


def stuur_bevestigingsmail(naam: str, email: str, datum: str, tijd: str, gasten: int):
    """Stuurt de reserverings-bevestiging (alleen relevant als ONLINE_RESERVEREN aan staat)."""
    sendgrid_verstuur(email, f"Reservering bevestigd: {datum_nl(datum)} om {tijd} · Bagel Alley",
                      mail_html(naam, datum, tijd, gasten))

def stuur_newsletter(email: str, naam: str = ""):
    """Stuurt de maandelijkse nieuwsbrief (Bagel van de Maand) via SendGrid."""
    sendgrid_verstuur(email, f"Bagel van de maand: {BAGEL_VD_MAAND['naam']} · Bagel Alley", newsletter_html(naam))

# endregion

# region ── DATABASE SETUP ─────────────────────────────────────
# Op Vercel is alleen /tmp schrijfbaar (en tijdelijk). Online reserveren staat uit,
# dus dit is alleen nodig zodat de app niet crasht bij het opstarten.
DB_PATH = "/tmp/boekingen.db" if os.environ.get("VERCEL") else "boekingen.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS boekingen (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                naam      TEXT    NOT NULL,
                email     TEXT    NOT NULL,
                gasten    INTEGER NOT NULL,
                datum     TEXT    NOT NULL,
                tijd      TEXT    NOT NULL,
                telefoon  TEXT    DEFAULT '',
                aangemaakt TEXT   DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()

try:
    init_db()
except Exception as e:  # database mag de site nooit platleggen
    print(f"[DB] init mislukt: {e}")

ALLE_SLOTS = [
    "08:00","08:30","09:00","09:30",
    "10:00","10:30","11:00","11:30",
    "12:00","12:30","13:00","13:30",
    "14:00","14:30","15:00","15:30"
]

def get_boekingen_voor_datum(datum: str) -> list:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM boekingen WHERE datum = ? ORDER BY tijd",
            (datum,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_volle_slots(datum: str) -> list:
    # Alleen actieve (niet-geannuleerde) boekingen blokkeren een slot
    return [b["tijd"] for b in get_boekingen_voor_datum(datum)
            if not b.get("geannuleerd")]

def bereken_stats(datum: str) -> dict:
    boekingen = get_boekingen_voor_datum(datum)
    volle_slots = get_volle_slots(datum)
    return {
        "totaal": len(boekingen),
        "gasten": sum(b["gasten"] for b in boekingen),
        "vrij":   len(ALLE_SLOTS) - len(volle_slots)
    }
# endregion

# region ── BEDRIJFSINSTELLINGEN ────────────────────────────────
# Pas dit blok aan voor elk nieuw bedrijf
BEDRIJF = {
    "naam": "Bagel Alley",
    "avatar_naam": "Sonja",
    "avatar_initialen": "SO",
    "telefoon": "070-514 61 16",
    "email": "info@bagelalley.nl",
    "adres": "Langstraat 42, 2242 KM Wassenaar",
    "openingstijden": {
        0: ("08:00", "16:00"),   # maandag
        1: None,                  # dinsdag gesloten
        2: ("08:00", "16:00"),   # woensdag
        3: ("08:00", "16:00"),   # donderdag
        4: ("08:00", "16:00"),   # vrijdag
        5: ("08:00", "16:00"),   # zaterdag
        6: ("08:00", "16:00"),   # zondag
    }
}
# endregion

# region ── SEO / STRUCTURED DATA ───────────────────────────────
# Canonieke domein. Zet desnoods de env var SITE_URL als je een ander
# (sub)domein gebruikt, bijv. https://bagelalley.up.railway.app
SITE_URL = (os.environ.get("SITE_URL")
            or (("https://" + os.environ["VERCEL_PROJECT_PRODUCTION_URL"]) if os.environ.get("VERCEL_PROJECT_PRODUCTION_URL") else "")
            or "https://bagelalley.nl").rstrip("/")

# Online reserveren aan/uit. Standaard UIT: reserveren gaat telefonisch.
# Weer aanzetten: env var ONLINE_RESERVEREN=1 op Railway (geen codewijziging nodig).
ONLINE_RESERVEREN = os.environ.get("ONLINE_RESERVEREN", "0").strip().lower() in ("1", "true", "ja", "yes")
RESERVEER_TEL_LINK = "tel:+31705146116"

# Geo-coordinaten van de zaak. Controleer deze in Google Maps en pas
# ze hier aan als ze niet exact kloppen (rechtsklik op de pin → coordinaten).
GEO = {"lat": 52.1463, "lng": 4.4012}

# (Optioneel) social profielen van de zaak, vul aan voor 'sameAs'.
SOCIAL = [
    # "https://www.instagram.com/bagelalley/",
    # "https://www.facebook.com/bagelalley/",
]

_DAGEN = {0: "Monday", 1: "Tuesday", 2: "Wednesday",
          3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

def _tel_e164(nummer: str) -> str:
    digits = re.sub(r"\D", "", nummer)
    if digits.startswith("0"):
        digits = "31" + digits[1:]
    return "+" + digits

def build_restaurant_schema() -> str:
    spec = []
    for idx, val in BEDRIJF["openingstijden"].items():
        if val:
            spec.append({
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": "https://schema.org/" + _DAGEN[idx],
                "opens": val[0],
                "closes": val[1],
            })
    schema = {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "name": BEDRIJF["naam"],
        "image": SITE_URL + "/static/og-image.jpg",
        "logo": SITE_URL + "/static/favicon/android-chrome-512x512.png",
        "url": SITE_URL,
        "telephone": _tel_e164(BEDRIJF["telefoon"]),
        "email": BEDRIJF["email"],
        "priceRange": "\u20ac\u20ac",
        "servesCuisine": ["Bagels", "Breakfast", "Lunch", "High Tea", "Tapas", "Koffie"],
        "acceptsReservations": True,
        "hasMenu": SITE_URL + "/menu",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Langstraat 42",
            "postalCode": "2242 KM",
            "addressLocality": "Wassenaar",
            "addressRegion": "Zuid-Holland",
            "addressCountry": "NL",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": GEO["lat"],
            "longitude": GEO["lng"],
        },
        "openingHoursSpecification": spec,
    }
    if SOCIAL:
        schema["sameAs"] = SOCIAL
    return json.dumps(schema, ensure_ascii=False)

@app.context_processor
def inject_seo_globals():
    try:
        schema = build_restaurant_schema()
    except Exception as e:
        print(f"[SEO] schema-fout: {e}")
        schema = "{}"
    return {
        "site_url": SITE_URL,
        "jaar": date.today().year,
        "restaurant_schema_json": schema,
        "online_reserveren": ONLINE_RESERVEREN,
        "reserveer_url": "/reserveren" if ONLINE_RESERVEREN else RESERVEER_TEL_LINK,
        "reserveer_label": "Tafel reserveren" if ONLINE_RESERVEREN else "Bel om te reserveren",
    }

@app.route("/robots.txt")
def robots_txt():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        + ("Disallow: /admin\n" if ADMIN_ENABLED else "") + "\n"
        "Sitemap: " + SITE_URL + "/sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap_xml():
    vandaag = date.today().isoformat()
    paginas = [
        ("/", "1.0"),
        ("/menu", "0.9"),
        ("/shop", "0.9"),
        ("/reserveren", "0.8"),
        ("/bestellen", "0.7"),
        ("/jobs", "0.5"),
    ]
    items = "".join(
        "<url><loc>{0}{1}</loc><lastmod>{2}</lastmod><changefreq>weekly</changefreq>"
        "<priority>{3}</priority></url>".format(SITE_URL, pad, vandaag, prio)
        for pad, prio in paginas
    )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + items + "</urlset>")
    return Response(xml, mimetype="application/xml")

import base64 as _b64
_FAVICON_BYTES = _b64.b64decode(
    "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"
)

@app.route("/favicon.ico")
def favicon_ico():
    # Favicon vanuit de code geserveerd, los van static-bestanden/templates.
    return Response(_FAVICON_BYTES, mimetype="image/png",
                    headers={"Cache-Control": "public, max-age=86400"})
# endregion

# region ── LINK HULPFUNCTIE ────────────────────────────────────
def link(tekst, url):
    """Maakt een klikbare HTML link met huisstijl."""
    return f'<a href="{url}" target="_blank" rel="noopener" style="color:#8758ce;font-weight:600;text-decoration:none;border-bottom:1px solid #c9a8f0;">{tekst}</a>'
# endregion

# region ── KENNISBANK ──────────────────────────────────────────
# Alle antwoorden van de chatbot, vul per bedrijf in
KENNISBANK = {
    "openingstijden": f'We zijn open van maandag en woensdag t/m zondag van 08:00 tot 16:00. Op dinsdag zijn wij gesloten. Meer info vind je {link("hier", "https://www.bagelalley.nl")}.',
    "adres":          f'Je vindt ons op Langstraat 42, 2242 KM Wassenaar. Plan je route {link("hier", "https://maps.google.com/?q=Langstraat+42+Wassenaar")}.',
    "contact":        f'Bel ons op 070-514 61 16 of neem contact op via {link("ons contactformulier", "https://www.bagelalley.nl/contact")}.',
    "menu":           f'We serveren vers ontbijt en lunch met zelfgemaakte bagels, sandwiches en salades. Bekijk het volledige menu {link("hier", "https://www.bagelalley.nl/menu-takeaway")}.',
    "bagels":         f'Onze bagels zijn zelfgemaakt met verse ingrediënten, elke dag vers gebakken. Bekijk alle opties {link("hier", "https://www.bagelalley.nl/menu-takeaway")}.',
    "high_tea":       f'Onze High Tea is perfect voor een bijzondere gelegenheid. De Take Away box is €39,50 voor 2 personen. Bekijk ons aanbod {link("hier", "https://www.bagelalley.nl/high-tea")}.',
    "tapas":          f'We hebben een heerlijk tapas aanbod! Bekijk de tapaskaart {link("hier", "https://www.bagelalley.nl/tapas")}.',
    "takeaway":       f'Takeaway is zeker mogelijk! Bestel online via onze webshop, ga {link("hier", "https://www.bagelalley.nl/online-shop")} naartoe.',
    "shop":           f'Online bestellen kan via onze webshop. Klik {link("hier", "https://www.bagelalley.nl/online-shop")} voor pie & box orders.',
    "cadeaubon":      f'Cadeaubonnen zijn verkrijgbaar vanaf €5,00, af te halen in de zaak. Meer info vind je {link("hier", "https://www.bagelalley.nl/cadeaubon")}.',
    "parking":        f'In Wassenaar zijn er parkeerplekken in de omgeving van de Langstraat. Bekijk de route {link("hier", "https://maps.google.com/?q=Langstraat+42+Wassenaar")}.',
    "allergieen":     f'Voor vragen over allergenen of dieetwensen neem je contact op via {link("dit formulier", "https://www.bagelalley.nl/contact")} of bel 070-514 61 16.',
    "reserveren":     'Reserveren gaat op dit moment telefonisch. Bel ons op '
                      '<a href="tel:+31705146116" style="color:#8758ce;font-weight:600;text-decoration:none;border-bottom:1px solid #c9a8f0;">070-514 61 16</a>, '
                      'dan zetten we een tafel voor je klaar. We zijn bereikbaar op ma en wo t/m zo van 08:00 tot 16:00.',
    "groepen":        f'Voor groepen of speciale gelegenheden bel je ons op 070-514 61 16 of stuur een bericht via {link("onze contactpagina", "https://www.bagelalley.nl/contact")}.',
}
# endregion

# region ── CLAUDE AI INSTELLINGEN ─────────────────────────────
# Zet API key als omgevingsvariabele: export ANTHROPIC_API_KEY=sk-ant-...
# Zonder key: fallback naar keyword-matching
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

_RESERVEER_REGEL = (
    '- Als iemand wil reserveren of een tafel boeken: antwoord NOOIT met een link of telefoonnummer. '
    'Zeg kortweg: "Reserveer via het formulier hieronder!" - het formulier opent automatisch in de chat.'
    if ONLINE_RESERVEREN else
    '- Reserveren kan op dit moment alleen telefonisch, via 070-514 61 16 (tijdens openingstijden). '
    'Online reserveren is nog niet mogelijk. Als iemand wil reserveren, verwijs vriendelijk naar dat nummer.'
)

SYSTEM_PROMPT = f"""Je bent Sonja, de eigenares van Bagel Alley in Wassenaar. Je beantwoordt vragen van gasten op een warme, persoonlijke manier.

Bagel Alley is een gezellig ontbijt- en lunchcafé met verse, zelfgemaakte bagels, Amerikaans-geïnspireerd eten en een warme sfeer.

Kennisbank:
{json.dumps(KENNISBANK, ensure_ascii=False, indent=2)}

Bedrijfsinfo:
- Naam: Bagel Alley
- Telefoon: 070-514 61 16
- Adres: Langstraat 42, 2242 KM Wassenaar
- Website: https://www.bagelalley.nl
- Open: ma, wo, do, vr, za, zo van 08:00-16:00 | dinsdag gesloten

Regels:
- Antwoord ALTIJD in dezelfde taal als de gebruiker
- Wees warm, informeel en enthousiast, praat als een echte eigenares die haar zaak kent
- Kort en to-the-point (max 2-3 zinnen)
- Voeg altijd een klikbare HTML link toe als er een relevante pagina is, gebruik dit format exact:
  <a href="https://..." target="_blank" style="color:#8758ce;font-weight:600;text-decoration:none;border-bottom:1px solid #c9a8f0;">ankertekst</a>
  Gebruik ankerteksten zoals "hier", "ons menu", "het formulier". Schrijf NOOIT de URL uit
- Als je iets niet weet, verwijs naar 070-514 61 16
- Geen markdown, geen opsommingstekens, gewone tekst
- Gebruik nooit een lang gedachtestreepje; gebruik een komma of punt
{_RESERVEER_REGEL}
"""
# endregion

# region ── AI ANTWOORDFUNCTIES ─────────────────────────────────
def reageer_met_ai(bericht: str) -> str:
    """Stuurt bericht naar Claude API, fallback naar keyword-matching."""
    if not ANTHROPIC_API_KEY:
        return reageer_zonder_ai(bericht)
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 300,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": bericht}],
            },
            timeout=10,
        )
        data = resp.json()
        return data["content"][0]["text"].strip()
    except Exception:
        return reageer_zonder_ai(bericht)


def reageer_zonder_ai(bericht: str) -> str:
    """Fallback keyword-matching zonder API key."""
    b = bericht.lower()
    # Reserveren eerst: anders matcht "online reserveren" op de webshop.
    if not ONLINE_RESERVEREN and re.search(r"reserv|tafel|boek|plekje", b):
        return KENNISBANK["reserveren"]
    # Allergie/dieet voor menu/bagel: "glutenvrije bagels?" hoort hier.
    if any(w in b for w in ["allergie", "allergeen", "allergenen", "glutenvrij", "vegan", "vegetarisch", "lactose", "dieet"]):
        return KENNISBANK["allergieen"]
    # Let op: gebruik \b woordgrens voor "open" zodat "verkopen" niet matcht
    if re.search(r'\b(open|uur)\b', b) or any(w in b for w in ["tijden", "wanneer", "openingstijden"]):
        return KENNISBANK["openingstijden"]
    elif any(w in b for w in ["adres", "locatie", "waar", "vinden", "wassenaar"]):
        return KENNISBANK["adres"]
    elif any(w in b for w in ["telefoon", "bellen", "mail", "contact", "bereiken"]):
        return KENNISBANK["contact"]
    elif any(w in b for w in ["high tea", "high-tea", "hightea", "tea"]):
        return KENNISBANK["high_tea"]
    elif any(w in b for w in ["tapas"]):
        return KENNISBANK["tapas"]
    elif any(w in b for w in ["takeaway", "afhalen", "meenemen", "take away"]):
        return KENNISBANK["takeaway"]
    elif any(w in b for w in ["shop", "webshop", "online", "bestell"]):
        return KENNISBANK["shop"]
    elif any(w in b for w in ["cadeau", "bon", "kado", "gift"]):
        return KENNISBANK["cadeaubon"]
    elif any(w in b for w in ["menu", "eten", "kaart", "lunch", "ontbijt"]):
        return KENNISBANK["menu"]
    elif any(w in b for w in ["bagel"]):
        return KENNISBANK["bagels"]
    elif any(w in b for w in ["groep", "verjaardag", "feest", "jubileum"]):
        return KENNISBANK["groepen"]
    elif any(w in b for w in ["parke", "auto"]):
        return KENNISBANK["parking"]
    elif re.search(r"\b(hallo|hoi|hey|hi|hello|goedemorgen|goedemiddag)\b", b):
        return "Hallo! Welkom bij Bagel Alley Wassenaar. Leuk dat je er bent!"
    elif any(w in b for w in ["doei", "bye", "tot ziens", "bedankt", "dankjewel", "thanks"]):
        return "STOP"
    else:
        return f'Dat weet ik niet zeker. Bel ons op 070-514 61 16 of kijk {link("op onze website", "https://www.bagelalley.nl")}!'
# endregion

# region ── FLASK ROUTES ────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html", bedrijf=BEDRIJF)


@app.route("/menu")
def menu():
    return render_template("menu.html", bedrijf=BEDRIJF, menukaart=MENUKAART)


@app.route("/shop")
def shop():
    return render_template("shop.html", bedrijf=BEDRIJF)


@app.route("/bestellen")
def bestellen():
    return render_template("bestellen.html", bedrijf=BEDRIJF)


@app.route("/jobs")
def jobs():
    return render_template("jobs.html", bedrijf=BEDRIJF)


# ── TAARTBESTELLING ──────────────────────────────────────────
ORDER_MAIL_TO = os.environ.get("ORDER_MAIL_TO", "info@bagelalley.nl")
TAARTEN = {  # id: (naam, prijs klein, prijs groot); None = formaat niet leverbaar
    "apple":  ("Apple Pie", 32.50, 45.00),
    "choco":  ("Chocoladetaart", 32.50, 45.00),
    "oreo":   ("Oreo taart", 32.50, 45.00),
    "redvel": ("Red Velvet Cake", 32.50, 45.00),
    "carrot": ("Carrot Cake", None, 45.00),
}
TEKST_OP_TAART_PRIJS = 6.00
AFHAAL_SLOTS = ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
                "13:00", "13:30", "14:00", "14:30", "15:00", "15:30"]
_TEL_RE = re.compile(r"^\+?[0-9][0-9 ()\-]{7,19}$")


def nu_amsterdam() -> datetime:
    """Huidige tijd in Nederland (val terug op servertijd als tzdata ontbreekt)."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Europe/Amsterdam"))
    except Exception:
        return datetime.now()


def _euro(bedrag: float) -> str:
    return "€" + f"{bedrag:.2f}".replace(".", ",")


def valideer_bestelling(data: dict):
    """Controleert een taartbestelling. Geeft (bestelling, None) of (None, foutmelding)."""
    taarten_in = data.get("taarten")
    if not isinstance(taarten_in, list) or not 1 <= len(taarten_in) <= len(TAARTEN):
        return None, "Kies minimaal één taart."
    regels, totaal, gezien = [], 0.0, set()
    for t in taarten_in:
        if not isinstance(t, dict):
            return None, "Ongeldige taart."
        tid = _clean_str(t.get("id"), 20)
        formaat = _clean_str(t.get("formaat"), 10)
        if tid not in TAARTEN or tid in gezien or formaat not in ("klein", "groot"):
            return None, "Ongeldige taart of formaat."
        naam, klein, groot = TAARTEN[tid]
        prijs = klein if formaat == "klein" else groot
        if prijs is None:
            return None, f"{naam} is alleen in groot formaat leverbaar."
        gezien.add(tid)
        regels.append((naam, "Klein" if formaat == "klein" else "Groot", prijs))
        totaal += prijs
    tekst = _clean_str(data.get("tekst"), 40)
    if tekst:
        totaal += TEKST_OP_TAART_PRIJS
    datum = _valid_iso_date(data.get("afhaaldatum"))
    vandaag = nu_amsterdam().date()
    if datum is None or datum <= vandaag or datum > vandaag + timedelta(days=365):
        return None, "Kies een afhaaldatum vanaf morgen."
    if datum.weekday() == 1:
        return None, "Op dinsdag zijn we gesloten. Kies een andere afhaaldatum."
    tijd = _clean_str(data.get("afhaaltijd"), 5)
    if tijd not in AFHAAL_SLOTS:
        return None, "Kies een afhaaltijd."
    naam = _clean_str(data.get("naam"), 100)
    email = _clean_str(data.get("email"), 150)
    telefoon = _clean_str(data.get("telefoon"), 30)
    opmerkingen = _clean_str(data.get("opmerkingen"), 1000)
    if not naam:
        return None, "Vul je naam in."
    if not _EMAIL_RE.match(email):
        return None, "Vul een geldig e-mailadres in."
    if not _TEL_RE.match(telefoon):
        return None, "Vul een geldig telefoonnummer in."
    return {"regels": regels, "tekst": tekst, "totaal": totaal, "datum": datum, "tijd": tijd,
            "naam": naam, "email": email, "telefoon": telefoon, "opmerkingen": opmerkingen}, None


def bestelling_mail_html(b: dict) -> str:
    e = _html.escape
    rijen = "".join(
        f"<tr><td style='padding:6px 0;'>{e(n)} ({f})</td><td style='padding:6px 0;text-align:right;'>{_euro(p)}</td></tr>"
        for n, f, p in b["regels"])
    if b["tekst"]:
        rijen += (f"<tr><td style='padding:6px 0;'>Tekst op taart: &ldquo;{e(b['tekst'])}&rdquo;</td>"
                  f"<td style='padding:6px 0;text-align:right;'>{_euro(TEKST_OP_TAART_PRIJS)}</td></tr>")
    return f"""<!DOCTYPE html><html lang="nl"><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:24px;background:#F5F0E8;font-family:Arial,sans-serif;color:#1E1828;">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background:#ffffff;border-radius:12px;">
<tr><td style="padding:24px 28px;">
<h1 style="font-family:Georgia,serif;font-size:22px;margin:0 0 4px;">Nieuwe taartbestelling</h1>
<p style="margin:0 0 18px;color:#6B5F7A;font-size:14px;">Via het bestelformulier op de website.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;border-top:1px solid #EDE6D6;border-bottom:1px solid #EDE6D6;">{rijen}
<tr><td style="padding:10px 0;font-weight:bold;">Totaal</td><td style="padding:10px 0;text-align:right;font-weight:bold;">{_euro(b['totaal'])}</td></tr></table>
<p style="font-size:14px;line-height:1.7;margin:18px 0 0;">
<strong>Afhalen:</strong> {e(datum_nl(b['datum'].isoformat()))} om {e(b['tijd'])}<br>
<strong>Naam:</strong> {e(b['naam'])}<br>
<strong>E-mail:</strong> {e(b['email'])}<br>
<strong>Telefoon:</strong> {e(b['telefoon'])}<br>
<strong>Opmerkingen:</strong> {e(b['opmerkingen']) or '-'}</p>
<p style="font-size:13px;color:#6B5F7A;margin:18px 0 0;">Beantwoord deze mail om de klant te bevestigen.</p>
</td></tr></table></body></html>"""


@app.route("/bestellen/verstuur", methods=["POST"])
@limiter.limit("5 per minute")
def bestelling_verstuur():
    data = request.get_json(silent=True) or {}
    bestelling, fout = valideer_bestelling(data)
    if fout:
        return jsonify({"succes": False, "reden": "ongeldig", "fout": fout}), 400
    if not SENDGRID_API_KEY:
        return jsonify({"succes": False, "reden": "niet_verstuurd",
                        "fout": "De bestelling kon niet automatisch worden verstuurd."}), 503
    onderwerp = f"Taartbestelling {bestelling['naam']} (afhalen {bestelling['datum'].strftime('%d-%m-%Y')} {bestelling['tijd']})"
    if not sendgrid_verstuur(ORDER_MAIL_TO, onderwerp, bestelling_mail_html(bestelling), antwoord_naar=bestelling["email"]):
        return jsonify({"succes": False, "reden": "niet_verstuurd",
                        "fout": "De bestelling kon niet automatisch worden verstuurd."}), 502
    print(f"[BESTELLING] {bestelling['naam']} | {bestelling['datum']} {bestelling['tijd']} | {_euro(bestelling['totaal'])}")
    return jsonify({"succes": True})


@app.route("/chat", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
    data = request.get_json(silent=True) or {}
    bericht = _clean_str(data.get("bericht"), 1000)   # harde lengtelimiet
    if not bericht:
        return jsonify({"antwoord": "Ik begreep je niet, kun je het opnieuw proberen?"})
    antwoord = reageer_met_ai(bericht)
    return jsonify({"antwoord": antwoord})


@app.route("/callback", methods=["POST"])
@limiter.limit("10 per minute")
def callback():
    data = request.get_json(silent=True) or {}
    naam = _clean_str(data.get("naam"), 100)
    telefoon = _clean_str(data.get("telefoon"), 30)
    if not naam or not telefoon:
        return jsonify({"succes": False, "fout": "Naam en telefoon zijn verplicht."}), 400
    print(f"[TERUGBELVERZOEK] {naam} - {telefoon}")
    return jsonify({"succes": True})


@app.route("/volle-slots", methods=["GET"])
@limiter.limit("60 per minute")
def volle_slots():
    parsed = _valid_iso_date(request.args.get("datum")) or date.today()
    return jsonify({"volle_slots": get_volle_slots(parsed.isoformat())})


@app.route("/reserveren", methods=["GET"])
def reserveren_get():
    # Geen boekingsdata naar de publieke pagina: de template gebruikt die niet,
    # en zo kan een DB-probleem deze pagina nooit laten crashen.
    return render_template("booking.html")


@app.route("/reserveren", methods=["POST"])
@limiter.limit("10 per minute")
def reserveren_post():
    if not ONLINE_RESERVEREN:
        return jsonify({
            "succes": False,
            "fout": "Online reserveren is op dit moment niet mogelijk. Bel ons op 070-514 61 16.",
        }), 403
    data = request.get_json(silent=True) or {}
    naam     = _clean_str(data.get("naam"), 100)
    email    = _clean_str(data.get("email"), 150)
    telefoon = _clean_str(data.get("telefoon"), 30)
    tijd     = _clean_str(data.get("tijd"), 10)

    # aantal gasten veilig parsen en begrenzen
    try:
        gasten = int(str(data.get("gasten", 2)).split()[0])
    except (ValueError, IndexError):
        return jsonify({"succes": False, "fout": "Ongeldig aantal gasten."}), 400
    if gasten < 1 or gasten > 50:
        return jsonify({"succes": False, "fout": "Aantal gasten moet tussen 1 en 50 liggen."}), 400

    if not naam:
        return jsonify({"succes": False, "fout": "Naam is verplicht."}), 400
    if not _EMAIL_RE.match(email):
        return jsonify({"succes": False, "fout": "Ongeldig e-mailadres."}), 400
    if tijd not in ALLE_SLOTS:
        return jsonify({"succes": False, "fout": "Ongeldig tijdslot."}), 400

    parsed = _valid_iso_date(data.get("datum"))
    if parsed is None:
        return jsonify({"succes": False, "fout": "Ongeldige datum."}), 400
    datum = parsed.isoformat()
    if parsed.weekday() == 1:  # 1 = dinsdag (gesloten)
        return jsonify({"succes": False, "fout": "Bagel Alley is op dinsdag gesloten."}), 400

    volle_slots = get_volle_slots(datum)
    if tijd in volle_slots:
        return jsonify({"succes": False, "fout": f"Tijdslot {tijd} is helaas al bezet."})

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO boekingen (naam, email, gasten, datum, tijd, telefoon) VALUES (?,?,?,?,?,?)",
            (naam, email, gasten, datum, tijd, telefoon)
        )
        conn.commit()

    print(f"[RESERVERING] {naam} | {email} | {datum} om {tijd} | {gasten} gasten")
    stuur_bevestigingsmail(naam, email, datum, tijd, gasten)
    # Nieuwsbrief alleen bij expliciete opt-in (AVG-conform)
    if bool(data.get("nieuwsbrief")):
        stuur_newsletter(email, naam)
    stuur_notificatie({"naam": naam, "datum": datum, "tijd": tijd, "gasten": gasten})
    stats = bereken_stats(datum)
    return jsonify({"succes": True, "tijd": tijd, "stats": stats})
# endregion

# region ── SERVER-SENT EVENTS (live notificaties) ──────────────
import queue, threading
_notif_queues = []
_notif_lock   = threading.Lock()

def _broadcast(data: str):
    with _notif_lock:
        dode = []
        for q in _notif_queues:
            try:
                q.put_nowait(data)
            except Exception:
                dode.append(q)
        for q in dode:
            _notif_queues.remove(q)

_geziene_notif_ids = set()

def stuur_notificatie(boeking: dict):
    import json as _json
    global _geziene_notif_ids
    notif_id = f"{boeking.get('naam')}-{boeking.get('datum')}-{boeking.get('tijd')}"
    if notif_id in _geziene_notif_ids:
        return
    _geziene_notif_ids.add(notif_id)
    _broadcast(_json.dumps(boeking))

@app.route("/admin/events")
def admin_events():
    if not session.get("admin_ingelogd"):
        return "Niet ingelogd", 401
    q = queue.Queue(maxsize=20)
    with _notif_lock:
        _notif_queues.append(q)
    def stream():
        yield "data: connected\n\n"
        while True:
            try:
                msg = q.get(timeout=25)
                yield f"data: {msg}\n\n"
            except queue.Empty:
                yield ": ping\n\n"
    from flask import Response, stream_with_context
    return Response(stream_with_context(stream()),
                    mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
# endregion

# region ── ADMIN INSTELLINGEN ───────────────────────────────────
# GEARCHIVEERD: de admin wordt op dit moment niet gebruikt. Standaard UIT, dan
# geeft elke /admin-URL een 404 (alsof hij niet bestaat). De code blijft bewaard.
# Weer aanzetten: env vars ADMIN_ENABLED=1 en ADMIN_PASS=<sterk wachtwoord>.
ADMIN_ENABLED = os.environ.get("ADMIN_ENABLED", "0").strip().lower() in ("1", "true", "ja", "yes")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
# Geen standaardwachtwoord: zonder ADMIN_PASS kan niemand inloggen.
ADMIN_PASS = os.environ.get("ADMIN_PASS", "")

@app.before_request
def _admin_gearchiveerd():
    if not ADMIN_ENABLED and (request.path == "/admin" or request.path.startswith("/admin/")):
        abort(404)
# endregion

# region ── ADMIN ROUTES ──────────────────────────────────────────
from functools import wraps

def login_vereist(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_ingelogd"):
            return jsonify({"fout": "Niet ingelogd"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/admin")
def admin():
    return render_template("archief/admin.html")

@app.route("/admin/login", methods=["POST"])
@limiter.limit("5 per minute")
def admin_login():
    data = request.get_json(silent=True) or {}
    gebruiker = _clean_str(data.get("gebruiker"), 100)
    wachtwoord = str(data.get("wachtwoord") or "")[:200]
    if ADMIN_PASS and _safe_eq(gebruiker, ADMIN_USER) and _safe_eq(wachtwoord, ADMIN_PASS):
        session["admin_ingelogd"] = True
        return jsonify({"succes": True})
    return jsonify({"succes": False, "fout": "Onjuiste inloggegevens"}), 401

@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("admin_ingelogd", None)
    return jsonify({"succes": True})

@app.route("/admin/boekingen", methods=["GET"])
@login_vereist
def admin_boekingen():
    datum = request.args.get("datum", date.today().isoformat())
    boekingen = get_boekingen_voor_datum(datum)
    stats = bereken_stats(datum)
    return jsonify({"boekingen": boekingen, "stats": stats})

@app.route("/admin/week", methods=["GET"])
@login_vereist
def admin_week():
    from datetime import timedelta
    start = request.args.get("start", date.today().isoformat())
    week = {}
    start_datum = date.fromisoformat(start)
    for i in range(7):
        dag = start_datum + timedelta(days=i)
        iso = dag.isoformat()
        week[iso] = get_boekingen_voor_datum(iso)
    return jsonify({"week": week})

@app.route("/admin/annuleer/<int:boeking_id>", methods=["POST"])
@login_vereist
def admin_annuleer(boeking_id):
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute("ALTER TABLE boekingen ADD COLUMN geannuleerd INTEGER DEFAULT 0")
            conn.commit()
        except Exception:
            pass
        conn.execute("UPDATE boekingen SET geannuleerd = 1 WHERE id = ?", (boeking_id,))
        conn.commit()
    return jsonify({"succes": True})


@app.route("/admin/verwijder/<int:boeking_id>", methods=["POST"])
@login_vereist
def admin_verwijder(boeking_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM boekingen WHERE id = ?", (boeking_id,))
        conn.commit()
    return jsonify({"succes": True})
# endregion

@app.route("/ping")
def ping():
    return "ok", 200


# region ── OPSTARTEN ───────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
# endregion

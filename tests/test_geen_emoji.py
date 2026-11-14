"""Huisregel: geen emoji op de site, in de chat of in de e-mails.

Controleert bronbestanden (templates, app.py, menukaart.py), alle gerenderde pagina's,
alle chatantwoorden en beide e-mails op emoji- en symboolbereiken.

Uitzondering: templates/archief/ (het gearchiveerde beheerscherm). Dat staat uit
(ADMIN_ENABLED) en blijft bewust ongewijzigd bewaard.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402

EMOJI = re.compile(
    "["
    "⌀-⏿"          # technische symbolen (o.a. ⏱ ⌚ ⏰)
    "①-⓿"          # omcirkelde tekens
    "■-◿"          # geometrische vormen (▶ ◀ ⬛-achtig)
    "☀-➿"          # diverse symbolen en dingbats (☀ ✓ ✔ ❤)
    "⤀-⥿"          # pijlen-aanvulling (⤴ ⤵)
    "⬀-⯿"          # diverse symbolen en pijlen (⬆ ⭐)
    "〰〽㊗㊙"
    "︎️"           # variation selectors
    "‍"                 # zero width joiner (samengestelde emoji)
    "⃣"                 # keycap
    "\U0001F000-\U0001FAFF"  # emoji, pictogrammen, symbolen
    "\U0001FB00-\U0001FBFF"
    "\U000E0020-\U000E007F"  # tag-tekens (vlaggen)
    "]"
)


def vondsten(tekst):
    return sorted({f"U+{ord(m.group()):04X}" for m in EMOJI.finditer(tekst)})


def bronbestanden():
    for p in sorted((ROOT / "templates").glob("*.html")):
        yield p
    yield ROOT / "app.py"
    yield ROOT / "menukaart.py"


def test_geen_emoji_in_bronbestanden():
    fouten = {}
    for p in bronbestanden():
        for nr, regel in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if "base64," in regel:
                continue
            v = vondsten(regel)
            if v:
                fouten[f"{p.relative_to(ROOT)}:{nr}"] = v
    assert not fouten, fouten


def test_geen_emoji_in_gerenderde_paginas():
    c = app.app.test_client()
    fouten = {}
    for pad in ["/", "/menu", "/high-tea", "/shop", "/bestellen", "/jobs", "/reserveren", "/privacy", "/bestaat-niet"]:
        v = vondsten(c.get(pad).get_data(as_text=True))
        if v:
            fouten[pad] = v
    assert not fouten, fouten


def test_geen_emoji_in_chatantwoorden():
    fouten = {}
    intents = list(app.KENNISBANK) + list(getattr(app, "_DYNAMISCH", {}))
    for intent in intents:
        v = vondsten(app.chat_antwoord(intent, ""))
        if v:
            fouten[intent] = v
    for vraag in ["hoi", "doei", "asdfgh", "zijn jullie morgen open", "wat kost een taart"]:
        v = vondsten(app.reageer_zonder_ai(vraag) if hasattr(app, "reageer_zonder_ai") else "")
        if v:
            fouten[vraag] = v
    assert not fouten, fouten


def _voorbeeldbestelling():
    from datetime import timedelta
    d = app.nu_amsterdam().date() + timedelta(days=3)
    if d.weekday() == 1:
        d += timedelta(days=1)
    b, fout = app.valideer_bestelling({
        "taarten": [{"id": "apple", "formaat": "klein"}], "tekst": "Gefeliciteerd",
        "afhaaldatum": d.isoformat(), "afhaaltijd": app.AFHAAL_SLOTS[0],
        "naam": "Anne de Vries", "email": "anne@voorbeeld.nl", "telefoon": "0612345678",
        "opmerkingen": "Graag met kaarsjes"})
    assert fout is None, fout
    return b


def test_geen_emoji_in_emails():
    mails = {
        "reservering": app.mail_html("Anne de Vries", "2026-11-14", "10:00", 2),
        "nieuwsbrief": app.newsletter_html("Anne"),
        "bestelling": app.bestelling_mail_html(_voorbeeldbestelling()),
    }
    fouten = {naam: vondsten(html) for naam, html in mails.items() if vondsten(html)}
    assert not fouten, fouten


def test_patroon_vangt_bekende_emoji():
    for teken in ["⏱", "⏰", "☕", "✅", "❤️", "⭐", "😀", "🥯", "👍🏽", "🇳🇱"]:
        assert vondsten(teken), teken
    for teken in ["©", "€", "→", "–", "·", "é", "ë", "’", "−"]:
        assert not vondsten(teken), teken

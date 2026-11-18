"""Tests voor de ingebouwde chatbot (reageer_zonder_ai / bepaal_intent in app.py).

Draaien:  pip install -r requirements-dev.txt  &&  pytest -q
"""
import os
import re
import sys
from datetime import datetime

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app  # noqa: E402
from chat_cases import CASES  # noqa: E402

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⭐]")
TAG = re.compile(r"<[^>]+>")


@pytest.mark.parametrize("vraag,verwacht", CASES, ids=[c[0][:40] for c in CASES])
def test_intent(vraag, verwacht):
    assert app.bepaal_intent(vraag)[0] == verwacht


def test_tabel_is_groot_genoeg():
    assert len(CASES) >= 120


def _alle_antwoorden():
    intents = set(app.CHAT_INTENTS) | {"greeting", "goodbye", "fallback"}
    momenten = [datetime(2026, 11, d, h, 0) for d, h in [(16, 7), (16, 12), (16, 17), (17, 12), (22, 12)]]
    vragen = ["zijn jullie nu open", "zijn jullie morgen open", "zijn jullie dinsdag open", "zondag open?"]
    out = []
    for intent in intents:
        for nu in momenten:
            for v in vragen:
                out.append((intent, app.chat_antwoord(intent, v, nu)))
    return out


@pytest.mark.parametrize("intent,antwoord", _alle_antwoorden()[::7])
def test_antwoord_regels(intent, antwoord):
    zichtbaar = TAG.sub("", antwoord)
    assert "—" not in antwoord and "&mdash;" not in antwoord, "geen em-dash"
    assert not EMOJI.search(antwoord), "geen emoji"
    assert "bagelalley.nl" not in antwoord, "geen links naar de oude site"
    assert len(zichtbaar) < 300, f"te lang ({len(zichtbaar)} tekens)"


def test_links_alleen_eigen_paginas_tel_mail_maps():
    for intent, antwoord in _alle_antwoorden():
        for href in re.findall(r'href="([^"]+)"', antwoord):
            assert href.startswith(("/", "tel:", "mailto:", "https://www.google.com/maps", "https://www.instagram.com/bagelalleywassenaar/")), (intent, href)


def test_allergie_antwoorden_eindigen_met_vaste_zin():
    for intent in ["allergie", "glutenvrij", "vegan_vegetarisch", "lactose_plantaardige_melk", "noten_sesam"]:
        zichtbaar = TAG.sub("", app.chat_antwoord(intent))
        assert zichtbaar.endswith("Heb je een allergie? Bel ons even, dan vertellen we precies wat erin zit.")


def test_veilig_antwoord_voor_onbevestigde_feiten():
    for intent in app.CHAT_FEITEN:
        if app.CHAT_FEITEN[intent] is None:
            assert "Goede vraag over" in app.chat_antwoord(intent)


def test_vandaag_open_rekent_met_echte_tijden():
    di = datetime(2026, 11, 17, 12, 0)      # dinsdag
    assert "gesloten" in app.antwoord_vandaag_open("zijn jullie vandaag open", di)
    assert "morgen weer open vanaf 08:00" in app.antwoord_vandaag_open("zijn jullie vandaag open", di)
    ma_middag = datetime(2026, 11, 16, 12, 0)
    assert "nu open, tot 16:00" in app.antwoord_vandaag_open("zijn jullie nu open", ma_middag)
    ma_avond = datetime(2026, 11, 16, 17, 0)  # morgen is dinsdag: volgende open dag is woensdag
    assert "op woensdag" in app.antwoord_vandaag_open("zijn jullie nog open", ma_avond).lower()
    assert "Op dinsdag zijn we gesloten" in app.antwoord_vandaag_open("zijn jullie dinsdag open", ma_middag)
    assert "Op zondag zijn we open van 08:00 tot 16:00" in app.antwoord_vandaag_open("zondag open", ma_middag)


def test_afscheid_geeft_stop_en_onbekend_wordt_gelogd(capsys):
    assert app.reageer_zonder_ai("bedankt!") == "STOP"
    app.reageer_zonder_ai("wat vind je van het weer")
    assert "[CHAT-ONBEKEND] wat vind je van het weer" in capsys.readouterr().out


def test_bevestigde_feiten_klant():
    assert "naast de Langstraat" in app.chat_antwoord("parking")
    assert "52.143773331281174%2C4.392209959142655" in app.chat_antwoord("parking")
    assert app.chat_antwoord("wifi_laptop") == "Ja, we hebben wifi voor gasten."
    assert "Langstraat 43" in app.chat_antwoord("terras")
    assert "@bagelalleywassenaar" in app.chat_antwoord("instagram_social")
    for intent in ["parking", "wifi_laptop", "terras", "instagram_social"]:
        assert "Goede vraag over" not in app.chat_antwoord(intent)
    for vraag, intent in [("waar kan ik parkeren", "parking"), ("is er wifi", "wifi_laptop"),
                          ("hebben jullie een terras", "terras"), ("hebben jullie instagram", "instagram_social")]:
        assert app.bepaal_intent(vraag)[0] == intent


def test_high_tea_prijzen_zijn_per_persoon():
    assert "Per persoon" in app.chat_antwoord("high_tea")
    assert "€17,95 per persoon" in app.chat_antwoord("prijzen")
    c = app.app.test_client()
    pagina = c.get("/high-tea").get_data(as_text=True)
    assert pagina.count('title="per persoon">p.p.</abbr>') == 3
    assert "€32,50 per persoon" in pagina                    # meta-omschrijving
    assert "Vanaf €17,95 p.p." in c.get("/").get_data(as_text=True)
    assert "prijzen per persoon" in c.get("/menu").get_data(as_text=True)

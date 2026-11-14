"""Wet van Postel: rommelige invoer accepteren, nette uitvoer teruggeven."""
import pathlib
import sys
from datetime import timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import app  # noqa: E402


def _bestelling(**over):
    d = app.nu_amsterdam().date() + timedelta(days=3)
    if d.weekday() == 1:
        d += timedelta(days=1)
    data = {"taarten": [{"id": "apple", "formaat": "klein"}], "afhaaldatum": d.isoformat(),
            "afhaaltijd": app.AFHAAL_SLOTS[0], "naam": "Anne", "email": "anne@voorbeeld.nl",
            "telefoon": "0612345678"}
    data.update(over)
    return app.valideer_bestelling(data)


def test_telefoon_normaliseren():
    goed = {
        "0612345678": "06-12345678", "06-12345678": "06-12345678", "06 12 34 56 78": "06-12345678",
        "06.12.34.56.78": "06-12345678", "(06) 12345678": "06-12345678", "+31612345678": "06-12345678",
        "+31 6 12345678": "06-12345678", "+31 (0)6 12 34 56 78": "06-12345678", "0031 6 1234 5678": "06-12345678",
        "070-514 61 16": "0705146116", "+31 70 514 6116": "0705146116", "(070) 514 61 16": "0705146116",
        "+32 470 12 34 56": "+32470123456", "0032470123456": "+32470123456",
    }
    for invoer, verwacht in goed.items():
        assert app.normaliseer_telefoon(invoer) == verwacht, invoer
    for fout in ["", "bel me", "123", "06-1234", "06123456789012345678", "+", "06 12a45678"]:
        assert app.normaliseer_telefoon(fout) is None, fout


def test_bestelling_maakt_invoer_netjes():
    b, fout = _bestelling(email="  Anne@Voorbeeld.NL ", telefoon="+31 (0)6 12 34 56 78", naam="Anne-Marie d'Hondt-Éléonore")
    assert fout is None, fout
    assert b["email"] == "anne@voorbeeld.nl"
    assert b["telefoon"] == "06-12345678"
    assert b["naam"] == "Anne-Marie d'Hondt-Éléonore"


def test_meldingen_zeggen_wat_te_doen():
    _, fout = _bestelling(telefoon="bel me")
    assert "bijvoorbeeld 06-12345678" in fout
    _, fout = _bestelling(email="anne@voorbeeld")
    assert "bijvoorbeeld naam@voorbeeld.nl" in fout
    dinsdag = app.nu_amsterdam().date() + timedelta(days=1)
    while dinsdag.weekday() != 1:
        dinsdag += timedelta(days=1)
    _, fout = _bestelling(afhaaldatum=dinsdag.isoformat())
    assert "Kies maandag of woensdag tot en met zondag" in fout
    _, fout = _bestelling(afhaaldatum=app.nu_amsterdam().date().isoformat())
    assert "vanaf morgen" in fout


def test_chat_losse_dagwoorden():
    for vraag in ["vandaag", "morgen", "Morgen?", "zaterdag", "zondag!"]:
        assert app.bepaal_intent(vraag)[0] == "vandaag_open", vraag
    assert app.bepaal_intent("goedemorgen")[0] == "greeting"
    assert app.bepaal_intent("hoi")[0] == "greeting"

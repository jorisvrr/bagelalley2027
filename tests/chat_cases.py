"""Testtabel voor de chatbot: realistische vragen -> verwachte intent.

Gedeeld door tests/test_chatbot.py en de voor/na-meting. Bij multi-intent zinnen
staat in het commentaar waarom deze intent wint.
"""

CASES = [
    # ── reserveren ──────────────────────────────────────────
    ("Ik wil graag een tafel reserveren", "reserveren"),
    ("Kan ik online reserveren?", "reserveren"),            # botsing: "online" mag niet naar de webshop
    ("kan ik reserveren voor zaterdag", "reserveren"),
    ("tafel voor 4 personen boeken", "reserveren"),          # multi: reserveren wint van groepen
    ("Can I book a table?", "reserveren"),
    ("reservering maken", "reserveren"),
    ("is er nog een plekje vrij morgen", "reserveren"),
    ("kan ik resserveren", "reserveren"),                    # typfout
    # ── openingstijden ──────────────────────────────────────
    ("Wat zijn jullie openingstijden?", "openingstijden"),
    ("openingstijde", "openingstijden"),                     # typfout
    ("opening hours", "openingstijden"),
    ("Hoe laat gaan jullie open?", "openingstijden"),
    ("hoi, hoe laat gaan jullie open", "openingstijden"),    # botsing: groet + vraag -> vraag wint
    ("ik wil weten of jullie open zijn", "openingstijden"),
    ("tot hoe laat zijn jullie open", "openingstijden"),
    ("Wanneer zijn jullie open?", "openingstijden"),
    ("wanneer gaan jullie dicht", "openingstijden"),
    ("hoe laat sluiten jullie", "openingstijden"),
    # ── vandaag_open ────────────────────────────────────────
    ("Zijn jullie nu open?", "vandaag_open"),
    ("zijn jullie vandaag open", "vandaag_open"),
    ("zijn jullie morgen open?", "vandaag_open"),
    ("Zijn jullie op dinsdag open?", "vandaag_open"),
    ("zijn jullie zondag open", "vandaag_open"),
    ("are you open today", "vandaag_open"),
    ("Open op maandag?", "vandaag_open"),
    ("zijn jullie vanavond nog open", "vandaag_open"),
    # ── feestdagen ──────────────────────────────────────────
    ("Zijn jullie open met kerst?", "feestdagen"),
    ("open op tweede kerstdag?", "feestdagen"),
    ("openingstijden rond oud en nieuw", "feestdagen"),
    ("zijn jullie open op koningsdag", "feestdagen"),
    ("Pasen open?", "feestdagen"),
    ("hemelvaartsdag open?", "feestdagen"),
    ("zijn jullie op feestdagen open", "feestdagen"),
    ("open op nieuwjaarsdag", "feestdagen"),
    # ── keuken ──────────────────────────────────────────────
    ("Hoe laat sluit de keuken?", "keuken"),
    ("wat is de laatste bestelling", "keuken"),
    ("tot hoe laat kan ik eten bestellen", "keuken"),
    ("is de keuken nog open", "keuken"),
    # ── adres / parkeren / contact ──────────────────────────
    ("Wat is het adres?", "adres"),
    ("Waar zitten jullie?", "adres"),
    ("waar vind ik jullie", "adres"),
    ("hoe kom ik bij jullie", "adres"),
    ("route naar bagel alley", "adres"),                     # multi: adres wint van "bagel"
    ("what is your address", "adres"),
    ("waar kan ik parkeren", "parking"),                     # botsing: "waar" mag niet naar adres
    ("Kan ik in de buurt parkeren?", "parking"),
    ("is er parkeergelegenheid", "parking"),
    ("kan ik met de auto komen", "parking"),
    ("parking nearby?", "parking"),
    ("wat is jullie telefoonnummer", "contact"),
    ("hoe kan ik jullie bereiken", "contact"),
    ("Mag ik jullie mailen?", "contact"),
    ("wat is jullie e-mailadres", "contact"),
    ("contact", "contact"),
    # ── menu / prijzen / bagels ─────────────────────────────
    ("Wat staat er op het menu?", "menu"),
    ("mag ik de menukaart zien", "menu"),
    ("wat hebben jullie te eten", "menu"),
    ("heb je steak", "menu"),                                # botsing: "steak" bevat "tea"; onbekend gerecht -> kaart
    ("do you have a menu", "menu"),
    ("wat zijn de prijzen", "prijzen"),
    ("hoe duur is het bij jullie", "prijzen"),               # botsing: "duur" bevat "uur"
    ("prijslijst", "prijzen"),
    ("how much does it cost", "prijzen"),
    ("hoe duur is een bagel", "bagels"),                     # prijs + product: productantwoord met prijzen wint
    ("Wat kost een bagel?", "bagels"),
    ("hoeveel soorten bagels hebben jullie", "bagels"),
    ("welke bagels hebben jullie", "bagels"),
    ("begel met zalm", "bagels"),                            # typfout
    ("bagel met roomkaas", "bagels"),
    ("wat is de bagel van de maand", "bagel_van_de_maand"),
    ("bagel of the month", "bagel_van_de_maand"),
    ("spanish classic", "bagel_van_de_maand"),
    # ── ontbijt / lunch ─────────────────────────────────────
    ("kan ik bij jullie ontbijten", "ontbijt_brunch_lunch"),
    ("hebben jullie soep?", "ontbijt_brunch_lunch"),
    ("wat voor lunch hebben jullie", "ontbijt_brunch_lunch"),
    ("brunch in het weekend?", "ontbijt_brunch_lunch"),
    ("breakfast options", "ontbijt_brunch_lunch"),
    # ── high tea / tapas ────────────────────────────────────
    ("wanneer kan ik high tea doen", "high_tea"),            # botsing: "wanneer" mag niet naar openingstijden
    ("Hoe duur is de high tea?", "high_tea"),
    ("high-tea voor 2", "high_tea"),
    ("afternoon tea", "high_tea"),
    ("hebben jullie tapas", "tapas"),
    ("iets voor bij de borrel", "tapas"),
    # ── koffie / thee / sappen ──────────────────────────────
    ("welke koffiebonen gebruiken jullie", "koffie"),        # botsing: "bonen" bevat "bon"
    ("Welke koffie schenken jullie?", "koffie"),
    ("wat kost een cappuccino", "koffie"),
    ("hebben jullie flat white", "koffie"),
    ("capuccino", "koffie"),                                 # typfout
    ("do you serve coffee", "koffie"),
    ("waar komen de koffiebonen vandaan", "koffie"),
    ("hebben jullie thee", "thee"),
    ("verse muntthee?", "thee"),
    ("chai latte", "thee"),
    ("hebben jullie verse jus", "sappen_smoothies"),
    ("smoothies?", "sappen_smoothies"),
    ("vers sinaasappelsap", "sappen_smoothies"),
    ("fresh juice", "sappen_smoothies"),
    # ── allergie en dieet ───────────────────────────────────
    ("ik heb een allergie", "allergie"),
    ("welke allergenen zitten erin", "allergie"),
    ("ik heb een voedselintolerantie", "allergie"),
    ("glutenvrij?", "glutenvrij"),
    ("Hebben jullie glutenvrije bagels?", "glutenvrij"),
    ("ik heb coeliakie", "glutenvrij"),
    ("gluten free options", "glutenvrij"),
    ("hebben jullie vegan opties", "vegan_vegetarisch"),
    ("Is er iets vegetarisch?", "vegan_vegetarisch"),
    ("ik eet geen vlees", "vegan_vegetarisch"),
    ("veggie?", "vegan_vegetarisch"),
    ("Hebben jullie lactosevrije melk?", "lactose_plantaardige_melk"),
    ("havermelk in mijn koffie?", "lactose_plantaardige_melk"),   # multi: dieet wint van koffie
    ("ik ben lactose intolerant", "lactose_plantaardige_melk"),   # specifiek wint van algemene allergie
    ("sojamelk", "lactose_plantaardige_melk"),
    ("zitten er noten in", "noten_sesam"),
    ("ik ben allergisch voor pinda's", "noten_sesam"),
    ("sesam allergie", "noten_sesam"),
    # ── afhalen / taart / shop / bezorgen ───────────────────
    ("kan ik afhalen", "takeaway"),
    ("Kan ik eten meenemen?", "takeaway"),
    ("take away", "takeaway"),
    ("to go?", "takeaway"),
    ("Kan ik een taart bestellen?", "taart_bestellen"),
    ("apple pie bestellen", "taart_bestellen"),
    ("hoeveel kost een oreo taart", "taart_bestellen"),
    ("red velvet cake", "taart_bestellen"),
    ("carrot cake voor zaterdag", "taart_bestellen"),
    ("taart ophalen", "taart_bestellen"),
    ("hoe ver van tevoren moet ik een taart bestellen", "taart_bestellen"),
    ("hebben jullie een webshop", "shop"),
    ("kan ik online bestellen", "shop"),
    ("Maken jullie ook een bruidstaart?", "bruidstaart"),
    ("trouwtaart", "bruidstaart"),
    ("wij gaan trouwen", "bruidstaart"),
    ("wedding cake", "bruidstaart"),
    ("bezorgen jullie ook", "bezorgen"),
    ("thuisbezorgd", "bezorgen"),
    ("uber eats?", "bezorgen"),
    ("do you deliver", "bezorgen"),
    ("kunnen jullie het thuis bezorgen", "bezorgen"),
    ("doen jullie catering", "zakelijk_catering"),
    ("lunch voor op kantoor", "zakelijk_catering"),
    ("grote bestelling voor een bedrijf", "zakelijk_catering"),
    ("zakelijke lunch", "zakelijk_catering"),
    # ── cadeaubon / groepen / kinderen / huisdieren ─────────
    ("Verkopen jullie cadeaubonnen?", "cadeaubon"),
    ("kado bon", "cadeaubon"),
    ("gift card", "cadeaubon"),
    ("kan ik een bon kopen", "cadeaubon"),
    ("We komen met 10 personen, kan dat?", "groepen"),
    ("verjaardag vieren bij jullie", "groepen"),
    ("groepsuitje", "groepen"),
    ("feestje met 12 man", "groepen"),
    ("zijn kinderen welkom", "kinderen"),
    ("kan ik met mijn baby komen", "kinderen"),
    ("kindvriendelijk?", "kinderen"),
    ("kids welcome?", "kinderen"),
    ("hebben jullie een kinderstoel", "kinderstoel"),
    ("high chair available?", "kinderstoel"),
    ("zijn honden toegestaan", "huisdieren"),
    ("Mag mijn hond mee?", "huisdieren"),
    ("mag de kat mee", "huisdieren"),
    ("are dogs allowed", "huisdieren"),
    # ── werken bij ──────────────────────────────────────────
    ("hebben jullie vacatures", "jobs"),
    ("kan ik bij jullie komen werken", "jobs"),
    ("ik zoek een bijbaan", "jobs"),
    ("solliciteren", "jobs"),
    # ── praktisch (veilige antwoorden) ──────────────────────
    ("kan ik pinnen", "betalen"),
    ("accepteren jullie contant", "betalen"),
    ("kan ik met creditcard betalen", "betalen"),
    ("tikkie?", "betalen"),
    ("apple pay", "betalen"),
    ("kan ik hier met mijn laptop werken", "wifi_laptop"),   # botsing: "werken" mag niet naar vacatures
    ("do you have wifi", "wifi_laptop"),
    ("is er wifi", "wifi_laptop"),
    ("zijn er stopcontacten", "wifi_laptop"),
    ("goede werkplek?", "wifi_laptop"),
    ("hebben jullie een terras", "terras"),
    ("kan ik buiten zitten", "terras"),
    ("is het rolstoeltoegankelijk", "toegankelijkheid"),
    ("is er een drempel", "toegankelijkheid"),
    ("toegankelijk voor mindervaliden", "toegankelijkheid"),
    ("hebben jullie een wc", "toilet"),
    ("is er een toilet", "toilet"),
    ("hebben jullie instagram", "instagram_social"),
    ("zitten jullie op facebook", "instagram_social"),
    ("is het nu druk", "drukte"),
    ("hoe lang is de wachttijd", "drukte"),
    # ── over de chat / groet / afscheid ─────────────────────
    ("is dat automatisch", "over_chat"),                     # botsing: "automatisch" bevat "auto"
    ("ben je een robot", "over_chat"),
    ("praat ik met een echt persoon", "over_chat"),
    ("hoi", "greeting"),
    ("Goedemorgen!", "greeting"),
    ("hallo sonja", "greeting"),
    ("hey", "greeting"),
    ("bedankt!", "goodbye"),
    ("doei", "goodbye"),
    ("dankjewel", "goodbye"),
    ("thanks", "goodbye"),
    # ── multi-intent (beste intent wint) ────────────────────
    ("bedankt, en kan ik ook pinnen?", "betalen"),           # afscheid telt niet naast een echte vraag
    ("kan ik reserveren en is er een kinderstoel", "reserveren"),  # gelijk gewicht -> reserveren heeft voorrang
    ("is het glutenvrij en wat kost het", "glutenvrij"),     # dieet gaat voor prijs
    ("wat kost de high tea en moet ik reserveren", "reserveren"),
    ("zijn jullie zondag open en kan ik parkeren", "vandaag_open"),
    ("waar zitten jullie en hoe laat open", "openingstijden"),     # twee open-woorden tegen één adreswoord
    # ── onbekend -> fallback ────────────────────────────────
    ("wat vind je van het weer", "fallback"),
    ("hoeveel is 2+2", "fallback"),
    ("ik wil een fiets kopen", "fallback"),
    ("kun je mijn huiswerk maken", "fallback"),
    ("blabla", "fallback"),
    ("asdfgh", "fallback"),
]

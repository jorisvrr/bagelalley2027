"""Tekstversie van de menukaart, letterlijk overgenomen van
public/static/menu/menu_1.webp en menu_2.webp (de gedrukte kaart).

Pas dit bestand aan als de kaart verandert. Prijzen zonder euroteken, zoals op de kaart.
Niet opgenomen (bewust): het koffie-tekstje van de brander en het blok
"Order for take away" met het 06-nummer (zie CLIENT-TODO.md in de projectdocumenten, buiten de repo).
"""

# Elke sectie: titel, optionele subtitel/kolommen, en regels (naam, omschrijving, prijzen).
# prijzen is een string zoals op de kaart; bij S/M/L-kolommen staat de maat erbij.

MENUKAART = [
    {
        "titel": "Breakfast",
        "regels": [
            ("Ontbijt 1", "Koffie of thee, verse sap, bagel met jam en roomkaas", "11,50"),
            ("Ontbijt 2", "Koffie of thee, verse sap, muesli met yoghurt en vers fruit", "13,95"),
            ("Ontbijt 3", "Koffie of thee, verse sap, bagel met roerei en spek", "14,95"),
            ("Ontbijt 4", "Amerikaanse pannenkoekjes (3) met boter en stroop of Nutella", "9,50"),
            ("Ontbijt 5", "Gebakken ei, worstje, witte bonen, tomaat, champignon en spek", "16,50"),
            ("Ontbijt 6", "Bagel met zalm, roomkaas, gepocheerd ei, rucola en bieslook", "10,50"),
        ],
    },
    {
        "titel": "Fresh Juices",
        "regels": [
            ("Sinaasappelsap", "", "M 3,75 / L 4,75"),
            ("- banaan", "", "M 4,95 / L 5,95"),
            ("- appel", "", "M 4,95 / L 5,95"),
            ("- kiwi", "", "M 4,95 / L 5,95"),
            ("- gemixed fruit", "", "L 6,95"),
        ],
    },
    {
        "titel": "Smoothies",
        "regels": [
            ("Rood", "Rood fruit, juice, yoghurt, banaan en honing", "7,95"),
            ("Groen", "Juice, spinazie, kiwi en avocado", "7,95"),
            ("Oranje", "Mango, juice, banaan en honing", "7,95"),
            ("Wit", "Havermout, juice, banaan en honing", "7,95"),
            ("Sunny XL", "Groot glas juice met yoghurt", "7,95"),
        ],
    },
    {
        "titel": "Yogurt",
        "regels": [
            ("Yoghurt met muesli en fruit", "", "8,50"),
            ("Yoghurt met vers fruit", "", "7,95"),
            ("Fruit los", "", "1,50"),
        ],
    },
    {
        "titel": "Bowls",
        "regels": [
            ("Acai of Pitaya bowl", "Met havermelk, vers fruit en kokos", "11,95"),
        ],
    },
    {
        "titel": "Bagels",
        "intro": "Kies een bagel: Naturel, Bruin, Sesam, Spelt, Multi-graan, Ui, Tomaat, "
                 "Kaneel/Rozijn, Spinazie/Olijf, Maanzaad, Alle Zaadjes, Pompoen, Glutenvrije bagel.",
        "regels": [
            ("Bagel naar keuze", "", "2,95"),
            ("met:", "", ""),
            ("Roomboter", "", "4,95"),
            ("Roomboter en jam", "", "5,95"),
            ("Roomboter en hagelslag", "", "5,95"),
            ("Chocopasta of pindakaas", "", "5,95"),
            ("Roomkaas", "", "5,95"),
            ("Roomkaas en jam", "", "6,50"),
            ("Rode of groene pesto", "", "6,50"),
            ("Roomkaas, bieslook en ui", "", "6,95"),
            ("Roomkaas en spek", "", "7,50"),
        ],
    },
    {
        "titel": "Bagels: vegetarische keuze",
        "regels": [
            ("Bagel jonge kaas", "", "5,95"),
            ("Bagel tosti, kaas", "", "6,45"),
            ("Bagel “Old Dutchie”", "Oude kaas, mosterd, pijnboompitjes mix", "6,95"),
            ("Bagel Gouda", "Gesmolten kaas met tomaat", "6,95"),
            ("Bagel eiersalade", "Huisgemaakt", "7,50"),
            ("Bagel roerei", "", "7,50"),
            ("Bagel Cheddar", "Gesmolten cheddar met tomaat", "7,50"),
            ("Bagel Tasty Tom", "Mosterdmayo, tomaat, ui en gesmolten kaas", "7,50"),
            ("Bagel hummus", "Hummus, avocado, tomaat", "7,95"),
            ("Bagel mozzarella", "Tomaat, groene pesto, mozzarella", "7,95"),
            ("Bagel ATM", "Avocado, tomaat, mozzarella", "7,95"),
            ("Bagel geitenkaas", "Mosterdmayo, geitenkaas, honing, pijnboompitjes mix", "7,95"),
            ("Bagel Mindfulness", "Hummus, rucola, zongedroogde tomaat, avocado, pijnboompitjes mix", "9,95"),
        ],
    },
    {
        "titel": "More Bagels: vlees",
        "regels": [
            ("Spek", "", "5,95"),
            ("Roerei en spek", "", "8,95"),
            ("Ham en gesmolten kaas", "", "6,75"),
            ("BLT", "Spek, sla, tomaat, mayo", "7,95"),
            ("Bagel kip", "Kipfilet, sla, tomaat, komkommer, mosterdmayo", "7,95"),
            ("Pizza bagel", "Salami, tomatensaus, mozzarella", "7,95"),
            ("Italiaanse bagel", "Kipfilet, mozzarella, pesto, komkommer, tomaat, pijnboompitjes mix", "8,95"),
            ("Club bagel", "Kipfilet, spek, sla, tomaat, komkommer, mayo, kaas", "9,95"),
            ("Bagel carpaccio", "Rundercarpaccio, sla, komkommer, pesto, parma kaas, pijnboompitjes mix", "9,95"),
            ("Bagel Alley", "Gegrilde kipfilet, rode pesto, avocado, roomkaas", "9,95"),
            ("Mexicaanse bagel", "Avocado, tomaat, roomkaas, gegrilde kip, nacho’s, gesmolten cheddar", "10,50"),
            ("Legendary bagel", "Rosbief, truffelmayo, rucola, pijnboompitjes mix, parma kaas", "10,50"),
            ("Bagel Popeye (the sailorman)", "Geitenkaas, spinazie, bacon, walnoten en honing", "9,95"),
        ],
    },
    {
        "titel": "More Bagels: vis",
        "regels": [
            ("Bagel tonijn", "Huisgemaakte tonijnsalade, sla, tomaat", "9,95"),
            ("Bagel zalm", "Gerookte zalm, roomkaas, kappertjes, ui", "10,50"),
            ("Bagel tuna melt", "Tonijnsalade met gesmolten cheddar", "9,95"),
        ],
    },
    {
        "titel": "Om mee te nemen",
        "regels": [
            ("Bevroren bagel, 1 stuk", "", "2,15"),
            ("Bevroren bagels, 12 stuks", "", "22,50"),
            ("Afgebakken bagel, 1 stuk", "", "2,65"),
            ("Afgebakken bagels, 12 stuks", "", "26,50"),
        ],
    },
    {
        "titel": "Soups & Salads",
        "regels": [
            ("Tomatensoep (vegan)", "", "7,95"),
            ("Courgettesoep (vegan)", "", "7,95"),
            ("Extra met bagel en roomkaas", "", "+4,50"),
            ("Tonijn salade", "Tonijn, sla, tomaat, rode ui, komkommer, vinaigrette en kappertjes", "13,50"),
            ("Caesar salade kip of zalm", "Gegrilde kip of zalm, sla, tomaat, komkommer, parma kaas en caesar-dressing", "13,50"),
            ("Kip salade", "Sla, tomaat, komkommer, croutons, vinaigrette en gegrilde kipstukjes", "13,50"),
        ],
    },
    {
        "titel": "Sweets & Goodies",
        "intro": "Zelf gebakken taarten. Taarten ook geheel te bestellen!",
        "regels": [
            ("Appeltaart", "", "4,50"),
            ("Worteltaart met rozijnen en walnoot", "", "4,50"),
            ("Oreo choco taart", "", "4,50"),
            ("Kwarktaart NY style", "", "4,50"),
            ("Chocoladetaart", "", "4,50"),
            ("Lemon square", "", "4,50"),
            ("Rood fruit cake", "", "4,50"),
            ("Pompoen taart (seizoen)", "", "4,50"),
        ],
    },
    {
        "titel": "Meer zoetigheden",
        "regels": [
            ("Donuts", "", "1,95"),
            ("Muffin groot", "", "3,95"),
            ("Koeken, diverse", "", "2,75"),
            ("Bananen noten cake", "", "3,25"),
            ("Brownie", "", "3,25"),
            ("Kaneelbroodje", "", "3,95"),
            ("Kaneelbroodje met glazuur", "", "4,95"),
            ("2 scones met room & jam", "", "9,50"),
        ],
    },
    {
        "titel": "High Tea",
        "intro": "Vanaf 2 personen. Zie onze wandborden voor meer informatie.",
        "regels": [
            ("Afternoon tea", "", "17,95"),
            ("Dream tea", "", "27,50"),
            ("Alley’s tea", "", "32,50"),
        ],
    },
    {
        "titel": "Tapas",
        "intro": "Als heerlijke snack of voor bij de borrel.",
        "regels": [
            ("Tapas bagels voor 2 personen",
             "3 gesneden bagels met 6 heerlijke dips: chives, rode en groene pesto, tonijnsalade, eiersalade en hummus",
             "24,95"),
        ],
    },
    {
        "titel": "Coffee",
        "regels": [
            ("Koffie", "", "S 2,75 / L 3,95"),
            ("Espresso", "", "S 3,10 / L 4,75"),
            ("Espresso macchiato", "", "S 3,25 / L 4,85"),
            ("Amerikano", "", "S 3,30 / L 4,75"),
            ("Cappuccino", "", "S 3,50 / M 4,00 / L 5,50"),
            ("Flat white", "", "S 4,50 / L 5,50"),
            ("Caffe latte", "", "S 3,85 / L 4,85"),
            ("Latte macchiato", "", "L 4,95"),
            ("Babyccino", "", "S 2,50"),
            ("IJskoffie", "", "4,50"),
            ("- slagroom", "", "4,95"),
            ("- caramel en slagroom", "", "5,95"),
            ("Haver- of sojamelk", "", "0,75"),
            ("Extra espresso shot", "", "1,25"),
        ],
    },
    {
        "titel": "Tea",
        "regels": [
            ("Thee, smaak naar keuze", "", "3,25"),
            ("Thee met melk", "", "3,50"),
            ("Verse munt thee", "", "3,95"),
            ("Verse gember thee", "", "3,95"),
            ("Thee per pot", "", "7,25"),
            ("Chai thee / Latte", "", "4,95"),
        ],
    },
    {
        "titel": "Hot Chocolate",
        "regels": [
            ("Warme choco", "", "3,95"),
            ("- slagroom", "", "4,50"),
            ("- marshmallows", "", "4,50"),
            ("- beide", "", "4,95"),
        ],
    },
    {
        "titel": "Cold Drinks",
        "regels": [
            ("Melk, karnemelk", "", "2,50"),
            ("Chocomel, Fristi", "", "3,75"),
            ("Chaudfontaine blauw of rood", "", "3,25"),
            ("Olmenhorst organic appelsap", "", "3,95"),
            ("Olmenhorst organic perensap", "", "3,95"),
            ("MM appel of sinaasappel", "", "3,50"),
            ("Tomatensap, glas", "", "3,50"),
        ],
    },
    {
        "titel": "Frisdrank (per blik)",
        "regels": [
            ("Coca Cola (light / zero / cherry)", "", "3,50"),
            ("Fanta (orange / lemon / cassis), Sprite", "", "3,50"),
            ("Bitter lemon, Tonic", "", "3,50"),
            ("Fuze iced tea (regular / green / lemon / chai)", "", "3,50"),
            ("Arizona ice tea, diverse smaken", "", "4,20"),
        ],
    },
    {
        "titel": "18+ jaar",
        "regels": [
            ("Heineken bier (fles)", "", "4,50"),
            ("Corona (fles)", "", "5,25"),
            ("Heineken 0.0%", "", "3,95"),
            ("Witte wijn (per glas)", "", "5,25"),
            ("Rose (per glas)", "", "5,25"),
            ("Rode wijn (per glas)", "", "5,25"),
        ],
    },
]

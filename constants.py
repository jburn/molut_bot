MOKOUS_TEXT = """
***MOKOUSOHJESÄÄNTÖ***
Jokainen Molut-ryhmän jäsen ja kannatusjäsen on oikeutettu pitämään yhdistyksen kokouksia (tuttavallisemmin mokouksia). Moluen jokseenkin kiistanalaisen luonteen takia mokoukset eivät ole tarkkaan säänneltyjä.
Mokouksen järjestämiseen riittää yksi molut, joka sisältää olutta ja maitoa noin 50/50 suhteessa. Oluttyypillä ja maidolla ei ole väliä, hyväksi todettuja ovat kuitenkin tummat oluet (esim. Guinness) sekä rasvaton/kauramaito.
Mokouksen aikana molutta ei tarvitse juoda kokonaan loppuun.
Molut-ryhmän jäseneksi voi päästä yksinkertaisesti maistamalla molutta joko mokouksen aikana tai sen ulkopuolella.
Mokouksista voi halutessaan ottaa kuvan, sekä ilmoittaa kuvan yhteydessä moluen hinnan (mindeksi)."""

DB_PATH = "./mokous_database.db"

MAITO = ["maito"]

MIEDOT = [
    " olut", 
    "lonkero", 
    "siideri", 
    "seltzer", 
    "punaviini", 
    "valkoviini", 
]

KOVAT = [
    "viina",
    "jallu",
    "viski",
    "gini",
    "gambina",
    "marjakossu",
    "salmari",
    "minttu"
]

COMMANDS = {
    "/help": "Listaa kaikki komennot",
    "/kirottu": "Arpoo valitunlaisen siunatun juomayhdistelmän (TOIMII VAIN YKSITYISVIESTILLÄ)",
    "/ohjesaanto": "Lähettää mokousohjesäännön yksityisviestinä",
    "/mokous": "Tallentaa mokouksen tietoineen mietokantaan KÄYTTÖ: /mokous paikka,mindeksi",
    "/mokoukset": "Hakee tiedot kaikista tiedossa olevista mokouksista"
}

from fax import FAXController

msg = {'id': 820,'vorname': 'ABCDEFGHIJKLMN',  'nachname': 'ABCDEFGHIJK',  'geburtsdatum': '01.34.2900',  'strasse': 'ABCDEFGH',  'hausnummer': '7t',  'plz': '10189',  'ort': "ABCDEFGHIJKLMNOPQRSTUVWX",  "ortsteil": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  "stockwerk": "ABCD",  "fahrstuhl": False,  "personenzustand": False,  "allergien": [],  "vorerkrangungen": [],  "medikation": [],  "krankenkasse": "ABCDEFGHIJKLMNO",  "versichertennummer": "ABCDEFGH",  "gewicht": 13.0,  "groesse": 175.25,  "position": "ABCDEFGHIJKLMNOPQRSTUVWXYZABC",  "bild": "ABCDE"}
link = "https://127.0.0.1/testlink=code1234235"

faxc = FAXController()

faxc.buildPDF(msg, link)

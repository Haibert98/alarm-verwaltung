from fpdf import FPDF
# and pip install pdfkit


class FAXController:
  def __init__(self):
    None

  def buildPDF(self, msg, link):
    #create pdf
    pdf = FPDF()
    #add page
    pdf.add_page()
    #set schrift
    pdf.set_font("Arial", size=15)
    pdf.cell(200, 10, txt = "Notfall Fax", ln=1, align="C")
    
    pdf.cell(200, 10, txt = "WER:", ln=1, align="L")
    pdf.cell(200, 10, txt = "Vorname: " + msg['vorname'], ln=1, align="L")
    pdf.cell(200, 10, txt = "Nachname: " + msg['nachname'], ln=1, align="L")
    pdf.cell(200, 10, txt = "Geburtsdatum: " + msg['geburtsdatum'], ln=1, align="L")

    pdf.cell(200, 10, txt = "WO:", ln=1, align="L")
    pdf.cell(200, 10, txt = "Straße: " + msg['strasse'], ln=1, align="L")
    pdf.cell(200, 10, txt = "PLZ:"+ msg['plz'] + " " + msg['ort'], ln=1, align="L")
    pdf.cell(200, 10, txt = "Stockwerk: " + msg['stockwerk'], ln=1, align="L")
    if msg['fahrstuhl']:
      pdf.cell(200, 10, txt = "Fahrstuhl vorhanden", ln=1, align="L")
    else:
      pdf.cell(200, 10, txt = "Fahrstuhl nicht vorhanden.", ln=1, align="L")

    pdf.cell(200, 10, txt = "WAS: " , ln=1, align="L")
    pdf.cell(200, 10, txt = "Das Smart-Home Notfallerkennungssystem hat einen Notfall erkannt.", ln=1, align="L")
    try:
      if msg['personenzustand']:
        pdf.cell(200, 10, txt = "Die verunfallte Person ist bei Bewusstsein und hat Hilfe angefordert", ln=2, align="L")
      else:
          pdf.cell(200, 10, txt = "Die verunfallte Person ist nicht bei Bewusstsein.", ln=1, align="L")
          pdf.cell(200, 10, txt = "Der Notruf wurde automatisert abgesetzt.", ln=1, align="L")
    except KeyError:
      pdf.cell(200, 10, txt = "Keine Informationen darüber, ob Person bei Bewusstsein ist.", ln=2, align="L")
    pdf.cell(200, 10, txt = "Weitere Informationen unter folgendem Link abrufbar:", ln=2, align="L")
    pdf.cell(200, 10, txt = link, ln=2, align="L")
    # save pdf with name
    pdf.output("notfall_" + str(msg['id']) + ".pdf")
    
    return True





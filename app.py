import streamlit as st
from fpdf import FPDF
from datetime import datetime
import base64
import tempfile

# Dummy data til rapport
data = {
  'nummerplade': 'XX12345',
  'model': 'VW ID.3 Life',
  'årgang': '2021',
  'km': '42.000',
  'lakfelter': 2,
  'variant_tillæg': 25000,
  'udstyrstillæg': 11000,
  'km_afskrivning': -8400,
  'udsalg': 228300,
  'køb': 194000,
  'avance_dkk': 34300,
  'avance_pct': 15,
  'score': 87,
  'annoncer': 26,
  'dynamisk_km': True,
  'dynamisk_udstyr': True
}

class PDFRapport(FPDF):
  def header(self):
    self.set_fill_color(10, 45, 90)
    self.set_text_color(255)
    self.set_font('Arial', 'B', 14)
    self.cell(0, 12, 'TA Biler - Vurderingsrapport', ln=True, align='C', fill=True)
    self.ln(3)
    self.set_font('Arial', '', 10)
    self.set_text_color(80)
    self.cell(0, 8, f'Rapport genereret: {datetime.now().strftime("%d-%m-%Y %H:%M")}', ln=True, align='C')
    self.ln(4)
    self.set_draw_color(180)
    self.line(10, self.get_y(), 200, self.get_y())
    self.ln(6)

  def section_title(self, title):
    self.set_font('Arial', 'B', 12)
    self.set_text_color(0, 45, 100)
    self.cell(0, 8, title, ln=True)
    self.set_draw_color(210)
    self.line(10, self.get_y(), 200, self.get_y())
    self.ln(3)

  def kv(self, key, value):
    self.set_font('Arial', '', 11)
    self.set_text_color(60)
    self.cell(60, 7, f'{key}:', border=0)
    self.set_text_color(0)
    self.cell(0, 7, value, ln=True)

  def badge(self, score):
    self.ln(6)
    self.set_font('Arial', 'B', 11)
    if score >= 80:
      self.set_fill_color(0, 180, 0)
      label = f'Datakvalitet: {score}% - HØJ'
    elif score >= 60:
      self.set_fill_color(255, 200, 0)
      label = f'Datakvalitet: {score}% - MIDDEL'
    else:
      self.set_fill_color(220, 50, 50)
      label = f'Datakvalitet: {score}% - LAV'
    self.set_text_color(255)
    self.cell(0, 12, label, ln=True, align='C', fill=True)
    self.set_text_color(0)

st.title('TA Biler - Vurderingsrapport')
if st.button('Download rapport som PDF'):
  pdf = PDFRapport()
  pdf.add_page()
  pdf.section_title('BILOPLYSNINGER')
  pdf.kv('Nummerplade', data['nummerplade'])
  pdf.kv('Model', data['model'])
  pdf.kv('Årgang', data['årgang'])
  pdf.kv('Kilometerstand', data['km'] + ' km')
  pdf.kv('Lakfelter', str(data['lakfelter']))
  pdf.section_title('PRISVURDERING')
  pdf.kv('Anbefalet udsalgspris', f"{data['udsalg']:,} DKK")
  pdf.kv('Anbefalet købspris', f"{data['køb']:,} DKK")
  pdf.kv('Avance', f"{data['avance_dkk']:,} DKK ({data['avance_pct']}%)")
  pdf.section_title('JUSTERINGER')
  pdf.kv('Variant-tillæg', f"{data['variant_tillæg']:,} DKK")
  pdf.kv('Udstyrstillæg', f"{data['udstyrstillæg']:,} DKK")
  pdf.kv('Km-afskrivning', f"{data['km_afskrivning']:,} DKK")
  pdf.section_title('DATAGRUNDLAG')
  pdf.badge(data['score'])
  pdf.kv('Bilbasen-annoncer fundet', str(data['annoncer']))
  pdf.kv('Dynamisk km-afskrivning', 'Ja' if data['dynamisk_km'] else 'Nej')
  pdf.kv('Dynamisk udstyrsanalyse', 'Ja' if data['dynamisk_udstyr'] else 'Nej')
  pdf.ln(8)
  pdf.set_font('Arial', 'I', 9)
  pdf.set_text_color(100)
  pdf.multi_cell(0, 5, 'TA Biler ApS - Ole Romers Vej 9, 6760 Ribe\nTlf: 71 74 71 41 - Web: www.tabiler.dk - Mail: salg@tabiler.dk', align='C')
  with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
    pdf.output(tmp_file.name)
    with open(tmp_file.name, 'rb') as f:
      base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="vurderingsrapport.pdf">Klik her for at hente vurderingsrapporten</a>'
    st.markdown(href, unsafe_allow_html=True)

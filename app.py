
import streamlit as st
from fpdf import FPDF
from datetime import datetime
import base64
import tempfile

# Input fra bruger
st.title("TA Biler – Automatisk vurdering")

nummerplade = st.text_input("Nummerplade")
km = st.number_input("Kilometerstand", 0, 500000, step=1000)
lakfelter = st.number_input("Lakfelter", 0, 10, step=1)

if st.button("Beregn vurdering"):
    # Simuleret opslag (Skat.dk placeholder)
    mærke, model, variant, årgang = "VW", "ID.3", "Life", 2021
    brændstof = "El"

    # Dummy data for vurdering (prisen er dynamisk baseret på input)
    base_price = 235000
    afskriv_km = km * 0.20
    afskriv_lak = 1500 + max(0, lakfelter - 1) * 500
    variant_tillæg = 25000
    udsalg = base_price - afskriv_km - afskriv_lak + variant_tillæg
    avance = max(20000, udsalg * 0.15)
    køb = udsalg - avance
    score = 87

    st.success("Vurdering gennemført")
    st.write(f"**Anbefalet udsalgspris:** {round(udsalg):,} kr")
    st.write(f"**Anbefalet købspris:** {round(køb):,} kr")
    st.write(f"**Avance:** {round(avance):,} kr")
    st.write(f"**Datakvalitetsscore:** {score}%")

    class PDFRapport(FPDF):
        def header(self):
            self.set_fill_color(10, 45, 90)
            self.set_text_color(255)
            self.set_font("Arial", "B", 14)
            self.cell(0, 12, "TA Biler - Vurderingsrapport", ln=True, align="C", fill=True)
            self.ln(3)
            self.set_font("Arial", "", 10)
            self.set_text_color(80)
            self.cell(0, 8, f"Rapport genereret: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True, align="C")
            self.ln(4)
            self.set_draw_color(180)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)

        def section_title(self, title):
            self.set_font("Arial", "B", 12)
            self.set_text_color(0, 45, 100)
            self.cell(0, 8, title, ln=True)
            self.set_draw_color(210)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)

        def kv(self, key, value):
            self.set_font("Arial", "", 11)
            self.set_text_color(60)
            self.cell(60, 7, f"{key}:", border=0)
            self.set_text_color(0)
            self.cell(0, 7, value, ln=True)

        def badge(self, score):
            self.ln(6)
            self.set_font("Arial", "B", 11)
            if score >= 80:
                self.set_fill_color(0, 180, 0)
                label = f"Datakvalitet: {score}% - HØJ"
            elif score >= 60:
                self.set_fill_color(255, 200, 0)
                label = f"Datakvalitet: {score}% - MIDDEL"
            else:
                self.set_fill_color(220, 50, 50)
                label = f"Datakvalitet: {score}% - LAV"
            self.set_text_color(255)
            self.cell(0, 12, label, ln=True, align="C", fill=True)
            self.set_text_color(0)

    if st.button("Download PDF-rapport"):
        pdf = PDFRapport()
        pdf.add_page()
        pdf.section_title("BILOPLYSNINGER")
        pdf.kv("Nummerplade", nummerplade)
        pdf.kv("Model", f"{mærke} {model} {variant}")
        pdf.kv("Årgang", str(årgang))
        pdf.kv("Kilometerstand", f"{km:,} km")
        pdf.kv("Lakfelter", str(lakfelter))

        pdf.section_title("VURDERING")
        pdf.kv("Anbefalet udsalgspris", f"{round(udsalg):,} DKK")
        pdf.kv("Anbefalet købspris", f"{round(køb):,} DKK")
        pdf.kv("Avance", f"{round(avance):,} DKK")

        pdf.section_title("JUSTERINGER")
        pdf.kv("Variant-tillæg", f"{variant_tillæg:,} DKK")
        pdf.kv("Afskrivning km", f"{round(afskriv_km):,} DKK")
        pdf.kv("Afskrivning lak", f"{round(afskriv_lak):,} DKK")

        pdf.section_title("DATAGRUNDLAG")
        pdf.badge(score)

        pdf.ln(8)
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(100)
        pdf.multi_cell(0, 5, "TA Biler ApS - Ole Romers Vej 9, 6760 Ribe\nTlf: 71 74 71 41 - Web: www.tabiler.dk - Mail: salg@tabiler.dk", align="C")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            with open(tmp_file.name, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="vurderingsrapport.pdf">Klik her for at hente vurderingsrapporten</a>'
            st.markdown(href, unsafe_allow_html=True)

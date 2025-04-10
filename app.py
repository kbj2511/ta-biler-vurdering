
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def hent_bildata_skat(nummerplade):
    url = f"https://motorregister.skat.dk/Selvbetjening/Koeretoej/Soegning?soeg={nummerplade}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    data = {}
    tekstfelter = soup.find_all("div", class_="vehicle-field")
    for felt in tekstfelter:
        label = felt.find("div", class_="vehicle-label")
        value = felt.find("div", class_="vehicle-value")
        if label and value:
            data[label.text.strip()] = value.text.strip()

    return data


def beregn_anbefalet_kobspris(salgspris, årgang, kilometer, brændstof):
    alder = datetime.now().year - årgang
    afskriv_km = kilometer * 0.05
    afskriv_år = alder * 5000

    brændstof_faktor = {"benzin": 0, "diesel": -3000, "el": 10000}
    fuel_just = brændstof_faktor.get(brændstof.lower(), 0)

    vurderet = salgspris - afskriv_km - afskriv_år + fuel_just
    min_avance = max(vurderet * 0.15, 20000)
    kobspris = vurderet - min_avance

    return round(kobspris, 2), round(min_avance, 2)


def hent_markedspriser_bilbasen(mærke, model, årgang):
    query_model = model.replace(" ", "%20")
    url = f"https://www.bilbasen.dk/brugt/bil/resultat?Make={mærke}&Model={query_model}&YearFrom={årgang}&YearTo={årgang}"

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    priser = []
    biler = soup.find_all("div", class_="bb-listing__price")
    for bil in biler:
        pris_txt = bil.text.strip().replace(" kr.", "").replace(".", "").replace(" ", "")
        try:
            pris = int(pris_txt)
            priser.append(pris)
        except:
            continue

    if priser:
        return {
            "antal": len(priser),
            "gennemsnit": sum(priser) / len(priser),
            "min": min(priser),
            "max": max(priser)
        }
    return None


# Streamlit Webapp
st.set_page_config(page_title="TA Biler - Prisvurdering", layout="centered")
st.title("🚗 TA Biler - Automatisk prisvurdering")
st.markdown("Indtast en nummerplade og en forventet salgspris, så vurderer vi maksimal købspris baseret på alder, km og brændstof.")

nummerplade = st.text_input("Nummerplade", max_chars=10)
salgspris_input = st.number_input("Forventet salgspris (DKK)", min_value=0.0, step=1000.0)

if st.button("Vurder bil") and nummerplade and salgspris_input:
    with st.spinner("🔍 Henter data fra Skat.dk..."):
        try:
            data = hent_bildata_skat(nummerplade)
            årgang = int(data.get("Førstegangsregistrering", "2020")[-4:])
            kilometer = int(data.get("Kilometerstand", "100000").replace('.', '').replace(' km', ''))
            brændstof = data.get("Drivmiddel", "benzin")
            model_full = data.get("Model", "")
            mærke = data.get("Mærke", "")

            anbefalet_kobspris, min_avance = beregn_anbefalet_kobspris(salgspris_input, årgang, kilometer, brændstof)

            st.success("✅ Vurdering fuldført")
            st.write(f"**Førstegangsregistrering:** {årgang}")
            st.write(f"**Kilometerstand:** {kilometer:,} km")
            st.write(f"**Brændstof:** {brændstof}")
            st.write(f"**Minimum avancekrav:** {min_avance:,.2f} DKK")
            st.write(f"### 💰 Anbefalet maksimal købspris: `{anbefalet_kobspris:,.2f} DKK`")

            st.subheader("📈 Markedsdata fra Bilbasen")
            markedsdata = hent_markedspriser_bilbasen(mærke, model_full, årgang)
            if markedsdata:
                st.write(f"Antal fundne biler: {markedsdata['antal']}")
                st.write(f"Gennemsnitspris: {markedsdata['gennemsnit']:,.0f} DKK")
                st.write(f"Prisinterval: {markedsdata['min']:,.0f} – {markedsdata['max']:,.0f} DKK")
            else:
                st.info("Ingen markedsdata kunne hentes fra Bilbasen.")

        except Exception as e:
            st.error(f"Der opstod en fejl under hentning eller behandling af data: {str(e)}")

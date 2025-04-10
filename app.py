
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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


def hent_markedspriser_bilbasen(mærke, model, årgang):
    query_model = model.replace(" ", "%20")
    url = f"https://www.bilbasen.dk/brugt/bil/resultat?Make={mærke}&Model={query_model}&YearFrom={årgang}&YearTo={årgang}"

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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


def justeret_markedspris(base_price, årgang, kilometer, udstyrsniveau=0):
    alder = datetime.now().year - årgang
    afskriv_km = kilometer * 0.20  # 20 øre pr. km
    afskriv_år = alder * 7000      # 7.000 kr. pr år
    værdi_justering = -afskriv_km - afskriv_år + udstyrsniveau
    return max(base_price + værdi_justering, 0)


def beregn_kobspris(markedspris):
    min_avance = max(markedspris * 0.15, 20000)
    return round(markedspris - min_avance, 2), round(min_avance, 2)


# Streamlit Webapp
st.set_page_config(page_title="TA Biler - Prisvurdering", layout="centered")
st.title("🚗 TA Biler - Automatisk prisvurdering")
st.markdown("Indtast en nummerplade, så vurderer vi udsalgspris og beregner den maksimale købspris ud fra markedsdata og afskrivninger.")

nummerplade = st.text_input("Nummerplade", max_chars=10)
udstyrsniveau = st.slider("Tilføj udstyrsjustering (DKK)", min_value=-10000, max_value=20000, step=1000, value=0)

if st.button("Vurder bil") and nummerplade:
    with st.spinner("🔍 Henter data fra Skat.dk..."):
        try:
            data = hent_bildata_skat(nummerplade)
            årgang = int(data.get("Førstegangsregistrering", "2020")[-4:])
            kilometer = int(data.get("Kilometerstand", "100000").replace('.', '').replace(' km', ''))
            brændstof = data.get("Drivmiddel", "benzin")
            model_full = data.get("Model", "")
            mærke = data.get("Mærke", "")

            st.success("✅ Data fundet")
            st.write(f"**Årgang:** {årgang}")
            st.write(f"**Kilometer:** {kilometer:,} km")
            st.write(f"**Brændstof:** {brændstof}")

            markedsdata = hent_markedspriser_bilbasen(mærke, model_full, årgang)
            if markedsdata:
                base_price = markedsdata['gennemsnit']
                justeret_udsalg = justeret_markedspris(base_price, årgang, kilometer, udstyrsniveau)
                kobspris, avance = beregn_kobspris(justeret_udsalg)

                st.subheader("📈 Markedsdata")
                st.write(f"Gennemsnit: {base_price:,.0f} DKK")
                st.write(f"Justering for alder/km/udstyr: {justeret_udsalg:,.0f} DKK")
                st.write(f"Minimum avancekrav: {avance:,.0f} DKK")
                st.write(f"### 💰 Anbefalet maksimal købspris: `{kobspris:,.0f} DKK`")
            else:
                st.warning("Kunne ikke finde markedsdata fra Bilbasen.")

        except Exception as e:
            st.error(f"Der opstod en fejl: {str(e)}")

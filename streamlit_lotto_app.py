import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tecnica del Lotto", layout="centered")
st.title("Tecnica del Lotto – Prima estrazione del mese")

# 1) Carica dati da CSV
@st.cache_data
def load_data(path):
    # Il CSV deve avere: giorno,mese,anno,terzo_bari,terzo_cagliari
    return pd.read_csv(path)

try:
    df = load_data("numeri.csv")
    row = df.iloc[0]
    giorno = int(row["giorno"])
    mese = int(row["mese"])
    anno = int(row["anno"])
    terzo_bari = int(row["terzo_bari"])
    terzo_cagliari = int(row["terzo_cagliari"])
except FileNotFoundError:
    st.error("⚠️ File 'numeri.csv' non trovato! Caricalo nella root del repo.")
    st.stop()
except Exception as e:

    st.error(f"⚠️ Errore CSV: {e}")
    st.stop()

# 2) Calcola la tecnica
@st.cache_data
def calcola_tecnica_lotto(bari, cagliari):
    dec_b = bari // 10
    dec_c = cagliari // 10
    amb = dec_b + dec_c
    if amb > 90: amb -= 90
    return dec_b, dec_c, amb

dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)

# 3) Mostra i risultati
st.markdown("---")
st.subheader(f"Risultati per {giorno:02d}/{mese:02d}/{anno}")
st.write(f"**Bari:** {terzo_bari} (decina {dec_b})")
st.write(f"**Cagliari:** {terzo_cagliari} (decina {dec_c})")
st.write(f"**Ambata:** {ambata}")
st.write(f"**Ambi:** {terzo_bari} – {terzo_cagliari}")
st.write(f"**Terna:** {ambata} – {terzo_bari} – {terzo_cagliari}")
st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale")


import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(
    page_title="Tecnica del Lotto",
    layout="centered",
)

# Titolo
st.title("Tecnica del Lotto – Estrazione del mese")

# Funzione per caricare i dati dal CSV
@st.cache_data
def load_data(path):
    """
    Carica un DataFrame dal file CSV specificato.
    Il CSV deve contenere le colonne: giorno, mese, anno, terzo_bari, terzo_cagliari
    """
    return pd.read_csv(path)

# Percorso del file CSV
DATA_FILE = "numeri.csv"

# Caricamento dati e gestione errori
try:
    df = load_data(DATA_FILE)
except FileNotFoundError:
    st.error(f"⚠️ File '{DATA_FILE}' non trovato! Caricalo nella root del repo.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Errore caricando '{DATA_FILE}': {e}")
    st.stop()

# Sidebar: selezione data estrazione
st.sidebar.header("Seleziona data estrazione")
giorno = st.sidebar.number_input("Giorno", min_value=1, max_value=31, value=1)
mese   = st.sidebar.number_input("Mese",   min_value=1, max_value=12, value=1)
anno   = st.sidebar.number_input("Anno",   min_value=1900, max_value=2100, value=2025)

# Filtra i dati per la data scelta
df_sel = df[(df["giorno"] == giorno) & (df["mese"] == mese) & (df["anno"] == anno)]
if df_sel.empty:
    st.error(f"⚠️ Nessuna estrazione trovata per {giorno:02d}/{mese:02d}/{anno} in '{DATA_FILE}'.")
    st.stop()
row = df_sel.iloc[0]
terzo_bari     = int(row["terzo_bari"])
terzo_cagliari = int(row["terzo_cagliari"])

# Funzione per calcolare la tecnica del lotto
@st.cache_data
def calcola_tecnica_lotto(bari: int, cagliari: int):
    dec_b = bari // 10
    dec_c = cagliari // 10
    ambata = dec_b + dec_c
    if ambata > 90:
        ambata -= 90
    return dec_b, dec_c, ambata

# Calcolo dei risultati
dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)

# Visualizzazione dei risultati
st.markdown("---")
st.subheader(f"Risultati per estrazione del {giorno:02d}/{mese:02d}/{anno}")
st.write(f"**Terzo estratto Bari:** {terzo_bari} (decina: {dec_b})")
st.write(f"**Terzo estratto Cagliari:** {terzo_cagliari} (decina: {dec_c})")
st.write(f"**Ambata:** {ambata} (derivante da {dec_b} + {dec_c})")
st.write(f"**Ambi da giocare:** {terzo_bari} – {terzo_cagliari}")
st.write(f"**Terna da giocare:** {ambata} – {terzo_bari} – {terzo_cagliari}")
st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale")

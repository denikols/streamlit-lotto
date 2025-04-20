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
    df = pd.read_csv(path)
    # Aggiunge colonna data formattata
    df['data'] = pd.to_datetime(df[['anno','mese','giorno']])
    return df

# Percorso CSV
data_file = "numeri.csv"

# Caricamento dati
try:
    df = load_data(data_file)
except FileNotFoundError:
    st.error(f"⚠️ File '{data_file}' non trovato! Caricalo nella root del repo.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Errore caricando '{data_file}': {e}")
    st.stop()

# Sidebar: selezione data estrazione
date_list = df['data'].dt.strftime("%d/%m/%Y").tolist()
selected_date = st.sidebar.selectbox("Seleziona estrazione", options=date_list)

# Filtra dati per la data scelta
df_sel = df[df['data'].dt.strftime("%d/%m/%Y") == selected_date]
row = df_sel.iloc[0]
terzo_bari = int(row['terzo_bari'])
terzo_cagliari = int(row['terzo_cagliari'])

# Funzione per calcolare la tecnica del lotto
@st.cache_data
def calcola_tecnica_lotto(bari: int, cagliari: int):
    dec_b = bari // 10
    dec_c = cagliari // 10
    amb = dec_b + dec_c
    if amb > 90:
        amb -= 90
    return dec_b, dec_c, amb

# Calcolo dei risultati
dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)

# Visualizzazione dei risultati
st.markdown("---")
st.subheader(f"Risultati per estrazione del {selected_date}")
st.write(f"**Terzo estratto Bari:** {terzo_bari} (decina: {dec_b})")
st.write(f"**Terzo estratto Cagliari:** {terzo_cagliari} (decina: {dec_c})")
st.write(f"**Ambata:** {ambata} (derivante da {dec_b} + {dec_c})")
st.write(f"**Ambi da giocare:** {terzo_bari} – {terzo_cagliari}")
st.write(f"**Terna da giocare:** {ambata} – {terzo_bari} – {terzo_cagliari}")
st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale")

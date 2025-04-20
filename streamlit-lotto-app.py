import streamlit as st
import pandas as pd
from datetime import datetime

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
    try:
        df = pd.read_csv(path)
        # Converti le colonne numeriche se necessario
        for col in ['giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Crea la colonna 'data' usando i nomi delle colonne personalizzate
        df['data'] = pd.to_datetime({
            'year': df['anno'],
            'month': df['mese'],
            'day': df['giorno']
        }, errors='coerce')
        
        # Rimuovi righe con date non valide
        df = df.dropna(subset=['data'])
        
        # Ordina per data crescente
        df = df.sort_values('data')
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {e}")
        return pd.DataFrame()

# Percorso CSV
data_file = "numeri.csv"

# Caricamento dati
try:
    df = load_data(data_file)
    if df.empty:
        st.error(f"⚠️ File '{data_file}' vuoto o formato non valido!")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Errore nel caricamento del file '{data_file}': {e}")
    st.stop()

# Visualizza il numero totale di date caricate
st.sidebar.write(f"**Totale estrazioni caricate:** {len(df['data'].unique())}")

# Prepara la lista delle date disponibili in formato leggibile
date_list = df['data'].dt.strftime("%d/%m/%Y").tolist()

# Sidebar: selezione data estrazione
# Utilizzare un container con altezza massima per migliorare lo scrolling
with st.sidebar:
    selected_date = st.selectbox(
        "Seleziona estrazione", 
        options=date_list,
        index=0
    )

# Filtra dati per la data scelta
df_sel = df[df['data'].dt.strftime("%d/%m/%Y") == selected_date]

if df_sel.empty:
    st.error("⚠️ Nessun dato trovato per la data selezionata.")
    st.stop()

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

# Debug: mostra tutte le date disponibili in una espandibile
with st.expander("Debug: Verifica tutte le date caricate"):
    st.write("Qui puoi verificare tutte le date caricate dal CSV:")
    st.dataframe(df[['giorno', 'mese', 'anno', 'data']].drop_duplicates().sort_values('data'))

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="Tecnica del Lotto",
    layout="wide",
)

# Titolo
st.title("Tecnica del Lotto – Estrazione del mese")

# Percorso file CSV
data_file = "numeri.csv"

# Verifica esistenza file
if not os.path.exists(data_file):
    st.error(f"⚠️ File '{data_file}' non trovato! Caricalo nella root del repo.")
    st.stop()

# Caricamento dati con caching leggero
@st.cache_data(ttl=1)
def load_data(path):
    try:
        df = pd.read_csv(path)
        # Converti le colonne numeriche
        for col in ['giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        # Crea la colonna data
        df['data'] = pd.to_datetime(
            dict(year=df['anno'], month=df['mese'], day=df['giorno']),
            errors='coerce'
        )
        # Rimuovi righe senza data valida e ordina
        df = df.dropna(subset=['data']).sort_values('data')
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {str(e)}")
        return pd.DataFrame()

# Carica il DataFrame
df = load_data(data_file)
if df.empty:
    st.error("⚠️ Nessun dato valido trovato nel file CSV.")
    st.stop()

# Prepara i dati
df['data_str'] = df['data'].dt.strftime("%d/%m/%Y")
max_date = df['data'].max().date()  # Data predefinita più recente

# Layout a due colonne: calendario + tabella a sinistra, risultati a destra
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Seleziona estrazione")
    # Calendar senza limiti, default ultima data disponibile
    selected_date = st.date_input(
        "Data estrazione",
        value=max_date
    )
    st.subheader("Tutte le estrazioni nel CSV")
    st.dataframe(
        df[['data_str', 'giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']]
            .rename(columns={'data_str': 'Data'})
            .reset_index(drop=True),
        height=500,
        use_container_width=True
    )

with col2:
    df_sel = df[df['data'].dt.date == selected_date]
    if df_sel.empty:
        st.error(f"⚠️ Nessun dato trovato per la data {selected_date.strftime('%d/%m/%Y')}.")
    else:
        row = df_sel.iloc[0]
        terzo_bari = int(row['terzo_bari'])
        terzo_cagliari = int(row['terzo_cagliari'])

        # Calcola tecnica del lotto
        def calcola_tecnica_lotto(bari: int, cagliari: int):
            dec_b = bari // 10
            dec_c = cagliari // 10
            amb = dec_b + dec_c
            if amb > 90:
                amb -= 90
            return dec_b, dec_c, amb

        dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)

        st.markdown("---")
        st.subheader(f"Risultati per estrazione del {selected_date.strftime('%d/%m/%Y')}")
        st.write(f"**Terzo estratto Bari:** {terzo_bari} (decina: {dec_b})")
        st.write(f"**Terzo estratto Cagliari:** {terzo_cagliari} (decina: {dec_c})")
        st.write(f"**Ambata:** {ambata} (derivante da {dec_b} + {dec_c})")
        st.write(f"**Ambi da giocare:** {terzo_bari} – {terzo_cagliari}")
        st.write(f"**Terna da giocare:** {ambata} – {terzo_bari} – {terzo_cagliari}")
        st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale")

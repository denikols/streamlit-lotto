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
        # Crea la colonna data e stringa
        df['data'] = pd.to_datetime(
            dict(year=df['anno'], month=df['mese'], day=df['giorno']),
            errors='coerce'
        )
        df = df.dropna(subset=['data']).sort_values('data')
        df['data_str'] = df['data'].dt.strftime("%d/%m/%Y")
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {str(e)}")
        return pd.DataFrame()

# Carica il DataFrame
df = load_data(data_file)
if df.empty:
    st.error("⚠️ Nessun dato valido trovato nel file CSV.")
    st.stop()

# Prepara la lista di date
date_list = sorted(
    df['data_str'].unique().tolist(),
    key=lambda x: datetime.strptime(x, "%d/%m/%Y"),
    reverse=True
)

# Layout a due colonne
col1, col2 = st.columns([1, 3])

with col1:
    # Calendario per selezione data
    selected_date = st.date_input(
        "Data estrazione",
        value=datetime.strptime(date_list[0], "%d/%m/%Y").date()
    )
    sel_str = selected_date.strftime("%d/%m/%Y")

    # Mostra tabella completa con scroll
    st.write("Tutte le estrazioni nel CSV")
    st.dataframe(
        df[['data_str', 'giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']]
            .rename(columns={'data_str': 'Data'})
            .reset_index(drop=True),
        height=500,
        use_container_width=True
    )

with col2:
    # Filtra e mostra risultati
    df_sel = df[df['data_str'] == sel_str]
    if df_sel.empty:
        st.error(f"⚠️ Nessun dato trovato per la data {sel_str}.")
    else:
        row = df_sel.iloc[0]
        b = int(row['terzo_bari'])
        c = int(row['terzo_cagliari'])
        # Calcolo tecnica del lotto
        dec_b, dec_c = b // 10, c // 10
        amb = dec_b + dec_c
        if amb > 90: amb -= 90

        st.subheader(f"Risultati per estrazione del {sel_str}")
        st.write(f"**Terzo estratto Bari:** {b} (decina: {dec_b})")
        st.write(f"**Terzo estratto Cagliari:** {c} (decina: {dec_c})")
        st.write(f"**Ambata:** {amb} (derivante da {dec_b} + {dec_c})")
        st.write(f"**Ambi da giocare:** {b} – {c}")
        st.write(f"**Terna da giocare:** {amb} – {b} – {c}")
        st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale")

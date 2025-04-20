import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="Tecnica del Lotto",
    layout="centered",
)

# Titolo
st.title("Tecnica del Lotto – Estrazione del mese")

# File CSV path
data_file = "numeri.csv"

# Verifica dell'esistenza del file
if not os.path.exists(data_file):
    st.error(f"⚠️ File '{data_file}' non trovato! Caricalo nella root del repo.")
    st.stop()

# Carica il CSV senza caching per il debug
st.write("### Caricamento dati in corso...")

try:
    # Leggi il file CSV direttamente senza pre-elaborazione
    df_raw = pd.read_csv(data_file)
    
    # Mostra i dati grezzi per debug
    with st.expander("Dati grezzi dal CSV"):
        st.write(f"Numero di righe nel CSV originale: {len(df_raw)}")
        st.dataframe(df_raw)
    
    # Converti le colonne numeriche
    for col in ['giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']:
        if col in df_raw.columns:
            df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
    
    # Crea la colonna 'data'
    df_raw['data'] = pd.to_datetime({
        'year': df_raw['anno'],
        'month': df_raw['mese'],
        'day': df_raw['giorno']
    }, errors='coerce')
    
    # Rimuovi righe con date non valide
    df = df_raw.dropna(subset=['data'])
    
    # Mostra le righe dopo la conversione
    with st.expander("Dati dopo la conversione delle date"):
        st.write(f"Numero di righe dopo la conversione: {len(df)}")
        st.dataframe(df[['giorno', 'mese', 'anno', 'data', 'terzo_bari', 'terzo_cagliari']])
    
    # Ordina per data
    df = df.sort_values('data')
    
    # Visualizza il numero totale di date caricate
    unique_dates = df['data'].dt.strftime("%d/%m/%Y").unique()
    st.sidebar.write(f"**Totale estrazioni caricate:** {len(unique_dates)}")
    
    # Elenco completo delle date in formato leggibile
    with st.expander("Elenco completo delle date uniche"):
        st.write(unique_dates)
    
    # Prepara la lista delle date disponibili
    date_list = df['data'].dt.strftime("%d/%m/%Y").unique().tolist()
    
    if not date_list:
        st.error("⚠️ Nessuna data valida trovata nel file CSV.")
        st.stop()
    
    # Sidebar: selezione data estrazione
    selected_date = st.sidebar.selectbox(
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
    
except Exception as e:
    st.error(f"⚠️ Errore durante l'elaborazione del file: {e}")
    st.stop()

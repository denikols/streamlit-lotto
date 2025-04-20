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

# Disabilita il caching per il debug
@st.cache_data(ttl=1)  # cache con durata molto breve
def load_data(path):
    try:
        # Leggi il file CSV direttamente
        df = pd.read_csv(path)
        
        # Converti le colonne numeriche
        for col in ['giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Crea la colonna 'data'
        df['data'] = pd.to_datetime(df[['anno', 'mese', 'giorno']], errors='coerce')
        
        # Rimuovi righe con date non valide
        df = df.dropna(subset=['data'])
        
        # Ordina per data
        df = df.sort_values('data')
        
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {str(e)}")
        return pd.DataFrame()

try:
    # Carica i dati
    df = load_data(data_file)
    
    if df.empty:
        st.error("⚠️ Nessun dato valido trovato nel file CSV.")
        st.stop()
    
    # Debug info
    st.sidebar.write(f"**Totale righe nel CSV:** {len(df)}")
    
    # Crea la colonna di data in formato stringa per il confronto
    df['data_str'] = df['data'].dt.strftime("%d/%m/%Y")
    
    # Ottieni l'elenco delle date uniche
    date_list = df['data_str'].unique().tolist()
    
    st.sidebar.write(f"**Totale estrazioni uniche:** {len(date_list)}")
    
    # Sidebar: selezione data estrazione
    selected_date = st.sidebar.selectbox(
        "Seleziona estrazione", 
        options=date_list,
        index=0
    )
    
    # Filtra i dati per la data selezionata
    df_sel = df[df['data_str'] == selected_date]
    
    if df_sel.empty:
        st.error(f"⚠️ Nessun dato trovato per la data {selected_date}.")
        st.stop()
    
    # Debug: mostra la riga selezionata
    with st.expander("Dati selezionati"):
        st.dataframe(df_sel)
    
    # Usa la prima riga dei dati filtrati
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
    
    # Debug: mostra tutte le righe del CSV
    with st.expander("Tutte le estrazioni nel CSV"):
        st.dataframe(df[['data_str', 'giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']])
    
except Exception as e:
    st.error(f"⚠️ Errore durante l'esecuzione: {str(e)}")

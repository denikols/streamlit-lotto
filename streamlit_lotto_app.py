import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="Tecnica del Lotto",
    layout="wide",  # Usa layout wide per sfruttare tutta la larghezza e sidebar affiancata
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
        # Crea la colonna data usando un dict per unit mapping
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

# Crea la colonna stringa della data
df['data_str'] = df['data'].dt.strftime("%d/%m/%Y")
# Lista di date uniche e ordinamento
date_list = df['data_str'].unique().tolist()
date_list.sort(key=lambda x: datetime.strptime(x, "%d/%m/%Y"), reverse=True)

# Layout a due colonne: selettore a sinistra, risultati a destra
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Seleziona estrazione")
    selected_date = st.selectbox(
        "Data estrazione",
        options=date_list,
        index=0  # di default la più recente
    )
    # Mostra tutte le estrazioni nel CSV in un expander
    with st.expander("Tutte le estrazioni nel CSV"):
        st.dataframe(
            df[['data_str', 'giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']]
                .rename(columns={'data_str': 'Data'})
        )

with col2:
    # Filtra per la data selezionata
    df_sel = df[df['data_str'] == selected_date]
    if df_sel.empty:
        st.error(f"⚠️ Nessun dato trovato per la data {selected_date}.")
    else:
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

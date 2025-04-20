# --- START OF FILE streamlit_lotto_app.py ---

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

# --- MODIFICA: Nome del file CSV ---
data_file = "24e25.csv"

# Verifica esistenza file
if not os.path.exists(data_file):
    st.error(f"⚠️ File '{data_file}' non trovato! Assicurati che sia nella stessa directory dell'app.")
    st.stop() # Interrompe l'esecuzione se il file non esiste

# Caricamento dati con caching leggero
@st.cache_data(ttl=60)
def load_data(path):
    """
    Carica i dati dal file CSV specifico (24e25.csv), pulisce, converte i tipi e ordina.
    Gestisce la struttura particolare del file (header su riga 4, colonne multiple).
    """
    try:
        # --- MODIFICA: Legge il CSV specificando l'header e le colonne da usare ---
        # header=3 significa che la quarta riga (indice 3) contiene le intestazioni.
        # usecols=[0, 3, 8] seleziona:
        # Colonna 0: 'Data'
        # Colonna 3: Terzo estratto di Bari (la 3a colonna 'Bari')
        # Colonna 8: Terzo estratto di Cagliari (la 3a colonna 'Cagliari')
        df = pd.read_csv(path, header=3, usecols=[0, 3, 8])

        # --- MODIFICA: Rinomina le colonne subito dopo la lettura ---
        # Pandas potrebbe aver aggiunto suffissi se le colonne originali avevano lo stesso nome
        # ma con usecols dovremmo avere solo 3 colonne. Le rinominiamo per chiarezza.
        df.columns = ['data_raw', 'terzo_bari', 'terzo_cagliari']

        # Converti colonna 'Data' (formato YYYY-MM-DD) in datetime
        df['data'] = pd.to_datetime(df['data_raw'], format='%Y-%m-%d', errors='coerce')

        # Rimuovi righe dove la data non è stata convertita (NaT)
        df = df.dropna(subset=['data'])

        # Converti le colonne numeriche, gestendo eventuali errori
        for col in ['terzo_bari', 'terzo_cagliari']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Rimuovi righe dove mancano i numeri (NaN)
        df = df.dropna(subset=['terzo_bari', 'terzo_cagliari'])

        # Converti in interi dopo aver rimosso i NaN
        if not df.empty:
            df['terzo_bari'] = df['terzo_bari'].astype(int)
            df['terzo_cagliari'] = df['terzo_cagliari'].astype(int)
        else:
            st.warning("Nessun dato numerico valido trovato dopo la pulizia.")
            return pd.DataFrame()

        # Ordina per data decrescente (dalla più recente alla più vecchia)
        df = df.sort_values('data', ascending=False)

        # Crea la colonna data_str (DD/MM/YYYY) per visualizzazione
        df['data_str'] = df['data'].dt.strftime("%d/%m/%Y")

        # Seleziona e riordina le colonne finali
        df = df[['data', 'data_str', 'terzo_bari', 'terzo_cagliari']]

        # Rimuovi duplicati basati sulla data, mantenendo il primo (più recente)
        df = df.drop_duplicates(subset=['data'], keep='first')

        return df

    except FileNotFoundError:
        st.error(f"Errore: File '{path}' non trovato.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.error(f"Errore: Il file CSV '{path}' è vuoto o non formattato correttamente.")
        return pd.DataFrame()
    except ValueError as e:
        st.error(f"Errore nella selezione delle colonne o nell'indice dell'header. Verifica la struttura del CSV. Dettagli: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore generico nel caricamento o processamento dei dati: {str(e)}")
        return pd.DataFrame()

# Carica il DataFrame
df = load_data(data_file)

# Controlla se il DataFrame è vuoto dopo il caricamento e la pulizia
if df.empty:
    # Il messaggio di errore specifico è già stato mostrato dentro load_data
    st.warning("Impossibile caricare o processare i dati delle estrazioni.")
    st.stop() # Interrompe l'esecuzione dello script se non ci sono dati validi

# Ottieni date minime e massime per il date_input
min_date = df['data'].min().date()
max_date = df['data'].max().date()

# Layout a due colonne: selezione + tabella a sinistra, risultati a destra
col1, col2 = st.columns([1, 3]) # Colonna 1 più stretta (1/4 dello spazio)

with col1:
    st.subheader("Selezione Estrazione")

    # --- MODIFICA: Usa st.date_input con min/max e valore iniziale ---
    selected_date = st.date_input(
        "Scegli la data dell'estrazione:",
        value=max_date,      # Pre-seleziona la data più recente
        min_value=min_date,  # Data minima dal CSV
        max_value=max_date,  # Data massima dal CSV
        format="DD/MM/YYYY", # Formato di visualizzazione nel widget
        key="data_selezionata_calendario" # Chiave unica
    )

    st.divider() # Linea separatrice

    st.subheader("Estrazioni Disponibili")
    st.caption(f"Dati dal {min_date.strftime('%d/%m/%Y')} al {max_date.strftime('%d/%m/%Y')}")
    # Mostra i dati ordinati (dal più recente) come riferimento
    st.dataframe(
        df[['data_str', 'terzo_bari', 'terzo_cagliari']]
            .rename(columns={'data_str': 'Data', 'terzo_bari': '3° Bari', 'terzo_cagliari': '3° Cagliari'})
            .reset_index(drop=True), # Resetta l'indice per la visualizzazione
        height=400, # Altezza fissa per la tabella
        use_container_width=True,
        hide_index=True # Nasconde l'indice del dataframe nella tabella
    )

with col2:
    # Converti la data selezionata (datetime.date) in datetime64 per il confronto con la colonna del DataFrame
    selected_dt = pd.to_datetime(selected_date)
    selected_date_str_display = selected_date.strftime("%d/%m/%Y") # Per mostrare nei titoli

    st.subheader(f"Analisi Tecnica per il {selected_date_str_display}")

    # --- MODIFICA: Filtra usando l'oggetto datetime ---
    df_sel = df[df['data'] == selected_dt]

    # --- MODIFICA: Controlla se la data selezionata esiste EFFETTIVAMENTE nel DataFrame ---
    if df_sel.empty:
        st.warning(f"⚠️ Non sono presenti dati di estrazione per la data {selected_date_str_display}.")
        st.info("Seleziona una data diversa usando il calendario o consulta la tabella a sinistra per le date disponibili.")
    else:
        # Prendi la prima (e unica) riga corrispondente
        row = df_sel.iloc[0]
        # Le colonne sono già state convertite in int nel load_data
        terzo_bari = row['terzo_bari']
        terzo_cagliari = row['terzo_cagliari']

        # Funzione per calcolare la tecnica del lotto
        def calcola_tecnica_lotto(bari: int, cagliari: int) -> tuple[int, int, int]:
            """Calcola le decine e l'ambata sommando le decine."""
            dec_b = bari // 10
            dec_c = cagliari // 10
            amb = dec_b + dec_c
            if amb > 90:
                amb -= 90
            # if amb == 0 and (dec_b != 0 or dec_c != 0): amb = 90 # Regola opzionale 0 -> 90
            return dec_b, dec_c, amb

        # Calcola i risultati
        dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)

        st.markdown("---")
        st.markdown("#### Numeri Estratti di Riferimento")
        # Usa le colonne per affiancare i numeri
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.metric(label="3° Estratto BARI", value=terzo_bari)
            st.caption(f"Decina: {dec_b}")
        with sub_col2:
            st.metric(label="3° Estratto CAGLIARI", value=terzo_cagliari)
            st.caption(f"Decina: {dec_c}")

        st.markdown("---")
        st.markdown("#### Previsione Secondo la Tecnica")

        # Mostra l'ambata calcolata in modo prominente
        st.metric(label="🔥 AMBATA Calcolata", value=ambata)
        st.caption(f"Derivante dalla somma delle decine: {dec_b} + {dec_c} = {dec_b + dec_c}" + (f" (poi -90)" if (dec_b + dec_c) > 90 else ""))

        st.markdown("##### Giocate Suggerite:")
        # Usare `st.success` o `st.info` per evidenziare le giocate
        st.success(f"**Ambo Secco:** `{terzo_bari} – {terzo_cagliari}`")
        st.success(f"**Terno Secco:** `{ambata} – {terzo_bari} – {terzo_cagliari}`")

        st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale. \n*(Valutare anche Tutte per recupero spese)*")

# --- END OF FILE streamlit_lotto_app.py ---
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

# Percorso file CSV
data_file = "numeri.csv"

# Verifica esistenza file
if not os.path.exists(data_file):
    st.error(f"⚠️ File '{data_file}' non trovato! Assicurati che sia nella stessa directory dell'app.")
    st.stop() # Interrompe l'esecuzione se il file non esiste

# Caricamento dati con caching leggero
# Il decoratore @st.cache_data assicura che i dati siano caricati una sola volta
# finché il file non cambia o il TTL (60 secondi qui) non scade.
@st.cache_data(ttl=60)
def load_data(path):
    """
    Carica i dati dal file CSV, li pulisce, converte i tipi e li ordina.
    Gestisce vari errori potenziali durante il caricamento e la processazione.
    """
    try:
        df = pd.read_csv(path)

        # Colonne richieste
        required_cols = ['giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Errore: Colonne mancanti nel file CSV: {', '.join(missing_cols)}. Assicurati che il file contenga tutte le colonne necessarie.")
            return pd.DataFrame() # Ritorna DataFrame vuoto

        # Converti le colonne numeriche, gestendo eventuali errori
        for col in required_cols:
            # 'coerce' imposta NaN per valori non convertibili
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Gestisci valori NaN PRIMA di creare la data per evitare errori
        # Rimuovi righe dove manca uno qualsiasi dei valori fondamentali
        df = df.dropna(subset=required_cols)

        # Converti in interi dopo aver rimosso i NaN per evitare errori di tipo
        # Se dopo il dropna il df è vuoto, le conversioni falliranno o non avranno effetto
        if not df.empty:
            for col in ['giorno', 'mese', 'anno', 'terzo_bari', 'terzo_cagliari']:
                 df[col] = df[col].astype(int)
        else:
            st.warning("Nessun dato valido trovato dopo la rimozione di righe con valori mancanti.")
            return pd.DataFrame()

        # Crea la colonna data e gestisci errori di date non valide
        # Usa un dizionario per mappare le colonne ai nomi attesi da to_datetime
        df['data'] = pd.to_datetime(
            df[['anno', 'mese', 'giorno']].rename(columns={'anno': 'year', 'mese': 'month', 'giorno': 'day'}),
            errors='coerce' # Imposta NaT (Not a Time) per date non valide
        )

        # Rimuovi righe con date non valide (NaT)
        df = df.dropna(subset=['data'])

        # Controlla di nuovo se df è vuoto dopo la rimozione di date non valide
        if df.empty:
            st.warning("Nessun dato valido trovato dopo la rimozione di date non valide.")
            return pd.DataFrame()

        # Ordina per data e crea la stringa
        df = df.sort_values('data', ascending=False) # Ordina dalla più recente
        df['data_str'] = df['data'].dt.strftime("%d/%m/%Y")

        # Rimuovi duplicati basati sulla data stringa, mantenendo il primo (più recente grazie all'ordinamento)
        # Utile se il CSV contiene estrazioni duplicate per la stessa data
        df = df.drop_duplicates(subset=['data_str'], keep='first')

        return df

    except FileNotFoundError:
        st.error(f"Errore: File '{path}' non trovato.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.error(f"Errore: Il file CSV '{path}' è vuoto.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore generico nel caricamento o processamento dei dati: {str(e)}")
        return pd.DataFrame()

# Carica il DataFrame
df = load_data(data_file)

# Controlla se il DataFrame è vuoto dopo il caricamento e la pulizia
if df.empty:
    # Il messaggio di errore specifico è già stato mostrato dentro load_data
    st.stop() # Interrompe l'esecuzione dello script se non ci sono dati validi

# Lista di date uniche (formato stringa DD/MM/YYYY), già ordinate dal DataFrame
# (dal più recente al più vecchio grazie a sort_values precedente)
date_list = df['data_str'].unique().tolist()

# Layout a due colonne: selezione + tabella a sinistra, risultati a destra
col1, col2 = st.columns([1, 3]) # Colonna 1 più stretta (1/4 dello spazio)

with col1:
    st.subheader("Selezione Estrazione")

    # --- Usa st.selectbox invece di st.date_input ---
    # Fornisce all'utente solo le date presenti nel file CSV
    selected_date_str = st.selectbox(
        "Scegli la data dell'estrazione:",
        options=date_list,
        index=0, # Pre-seleziona la prima data (la più recente)
        # format_func=lambda x: x # Mostra le date come sono (DD/MM/YYYY), non necessario
        key="data_selezionata" # Chiave unica per il widget
    )

    st.divider() # Linea separatrice

    st.subheader("Estrazioni Caricate")
    # Mostra i dati ordinati come nel selectbox (dal più recente)
    st.dataframe(
        df[['data_str', 'terzo_bari', 'terzo_cagliari']]
            .rename(columns={'data_str': 'Data', 'terzo_bari': '3° Bari', 'terzo_cagliari': '3° Cagliari'})
            .reset_index(drop=True), # Resetta l'indice per la visualizzazione
        height=400, # Altezza fissa per la tabella
        use_container_width=True,
        hide_index=True # Nasconde l'indice del dataframe nella tabella
    )

with col2:
    st.subheader(f"Analisi Tecnica per l'Estrazione del {selected_date_str}")

    # Filtra usando la stringa selezionata direttamente dal selectbox
    # selected_date_str conterrà una delle date valide da date_list
    df_sel = df[df['data_str'] == selected_date_str]

    # Questo controllo ora dovrebbe essere quasi superfluo se date_list è corretto,
    # ma è una buona pratica mantenerlo per sicurezza.
    if df_sel.empty:
        st.error(f"⚠️ Errore imprevisto: Nessun dato trovato per la data {selected_date_str}, anche se dovrebbe esistere nel DataFrame caricato.")
    else:
        # Prendi la prima (e unica) riga corrispondente
        row = df_sel.iloc[0]
        # Le colonne sono già state convertite in int nel load_data
        terzo_bari = row['terzo_bari']
        terzo_cagliari = row['terzo_cagliari']

        # Funzione per calcolare la tecnica del lotto
        def calcola_tecnica_lotto(bari: int, cagliari: int) -> tuple[int, int, int]:
            """Calcola le decine e l'ambata sommando le decine."""
            # Calcola la decina (divisione intera)
            # Gestisce il caso in cui il numero sia < 10 (decina 0)
            dec_b = bari // 10
            dec_c = cagliari // 10

            # Somma delle decine
            amb = dec_b + dec_c

            # Applica la regola del "fuori 90" se la somma supera 90
            if amb > 90:
                amb -= 90
            # Gestisce il caso in cui la somma sia 0.
            # La regola standard solitamente non trasforma 0 in 90 in questo contesto,
            # a meno che non sia specificato. Se dec_b=0 e dec_c=0, amb=0.
            # Lasciamo amb=0 se la somma è 0.
            # if amb == 0 and (dec_b != 0 or dec_c != 0): # Condizione opzionale
            #     amb = 90

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
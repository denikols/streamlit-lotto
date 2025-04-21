import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io

# --- Funzioni Ausiliarie ---

def calcola_tecnica_lotto(bari: int, cagliari: int) -> tuple[int, int, int]:
    """Calcola le decine e l'ambata sommando le decine."""
    # La validazione dell'input viene fatta prima della chiamata
    dec_b = bari // 10
    dec_c = cagliari // 10
    amb = dec_b + dec_c
    if amb > 90:
        amb -= 90
    return dec_b, dec_c, amb

def calcola_antecedente_successivo(numero: int) -> tuple[int, int]:
    """Calcola l'antecedente e il successivo di un numero."""
    antecedente = numero - 1
    successivo = numero + 1
    
    # Gestione dei casi limite (1 e 90)
    if antecedente == 0:
        antecedente = 90
    if successivo == 91:
        successivo = 1
        
    return antecedente, successivo

@st.cache_data(ttl=3600) # Cache dati per 1 ora
def load_data(uploaded_file_content):
    """
    Carica e processa i dati dal contenuto del file CSV caricato.
    Ordina per data ASCENDENTE per la navigazione per indice.
    """
    try:
        file_content = io.BytesIO(uploaded_file_content)
        df = pd.read_csv(file_content, skiprows=3) # Salta le prime 3 righe

        # Converti colonna Data e rimuovi righe non valide
        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
        df = df.dropna(subset=["Data"])

        # Verifica se il DataFrame è vuoto dopo la conversione della data
        if df.empty:
            st.error("Nessuna data valida trovata nel file CSV.")
            return pd.DataFrame()

        # FIX: Cerca le colonne per nome invece che per indice
        # Trova le colonne per Bari e Cagliari cercando nei nomi
        bari_cols = [col for col in df.columns if col.startswith('Bari')]
        cagliari_cols = [col for col in df.columns if col.startswith('Cagliari')]
        
        if len(bari_cols) < 3 or len(cagliari_cols) < 3:
            raise ValueError("Non sono state trovate sufficienti colonne per Bari e Cagliari")
            
        # Usa la terza colonna per ciascuna ruota
        col_bari_3 = bari_cols[2]  # Terza colonna di Bari
        col_cagliari_3 = cagliari_cols[2]  # Terza colonna di Cagliari

        # Estrai e converti numeri per la tecnica (NaN se errore)
        df['terzo_bari'] = pd.to_numeric(df[col_bari_3], errors='coerce')
        df['terzo_cagliari'] = pd.to_numeric(df[col_cagliari_3], errors='coerce')

        # Ordina per data ASCENDENTE (dal più vecchio al più recente)
        df = df.sort_values("Data", ascending=True).reset_index(drop=True)
        return df

    except pd.errors.EmptyDataError:
        st.error("Errore: Il file CSV caricato è vuoto o non contiene dati leggibili dopo le righe iniziali.")
        return pd.DataFrame()
    except IndexError as e:
         st.error(f"Errore nell'accesso alle colonne: {e}. Assicurati che il CSV abbia la struttura attesa.")
         return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore durante la lettura o l'elaborazione iniziale del file CSV: {type(e).__name__}: {e}")
        return pd.DataFrame()

# --- Funzione di Styling aggiornata ---
def highlight_numbers(df, numeri_da_evidenziare, ruote_da_evidenziare):
    """
    Versione aggiornata per evidenziare le celle con i numeri specifici
    Funziona con DataFrame.style.apply invece di applymap
    """
    # Inizializza un DataFrame vuoto della stessa forma per lo stile
    style_df = pd.DataFrame('', index=df.index, columns=df.columns)
    
    style = 'background-color: #FF4B4B; color: white; font-weight: bold;'
    
    # Applica lo stile solo alle righe delle ruote da evidenziare
    for ruota in ruote_da_evidenziare:
        if ruota in df.index:
            for col in df.columns:
                val = df.loc[ruota, col]
                # Verifica se il valore è valido e da evidenziare
                if pd.notna(val) and isinstance(val, (int, float, np.number)):
                    try:
                        if int(val) in numeri_da_evidenziare:
                            style_df.loc[ruota, col] = style
                    except (ValueError, TypeError):
                        pass  # Ignora errori di conversione
    
    return style_df

# --- Configurazione Pagina e Titolo ---
st.set_page_config(layout="wide")
st.title("📊 Analisi Lotto: Tecnica & Estrazioni con Navigazione")

# --- Upload File ---
uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni (es: 24e25.csv)", type="csv")

if uploaded_file:
    # Usa il contenuto del file per permettere il caching
    uploaded_file_content = uploaded_file.getvalue()
    df_lotto = load_data(uploaded_file_content)

    # Procedi solo se il DataFrame è valido e non vuoto
    if df_lotto is not None and not df_lotto.empty:
        # Ottieni date uniche (oggetti date)
        date_uniche_dt_asc = sorted(df_lotto["Data"].dt.date.unique()) # Ordine ASC per logica indice
        date_uniche_dt_desc = sorted(date_uniche_dt_asc, reverse=True) # Ordine DESC per selectbox

        if not date_uniche_dt_desc:
            st.error("Non sono state trovate date uniche valide nel file.")
            st.stop()

        ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
                 "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

        # --- Gestione Stato Sessione per Indice Visualizzazione ---
        if 'visual_date_index_desc' not in st.session_state:
            st.session_state.visual_date_index_desc = 0 # Inizia dalla data più recente (indice 0 della lista DESC)
        else:
            # Assicura che l'indice sia valido dopo un possibile ricaricamento/cambio file
            max_idx_valido = len(date_uniche_dt_desc) - 1
            if st.session_state.visual_date_index_desc > max_idx_valido:
                st.session_state.visual_date_index_desc = max_idx_valido
            elif st.session_state.visual_date_index_desc < 0:
                 st.session_state.visual_date_index_desc = 0

        # Callback per sincronizzare l'indice se si usa il selectbox di destra
        def sync_index_from_selectbox():
            selected_date = st.session_state.select_visualizzazione # Oggetto date selezionato
            try:
                # Trova l'indice nella lista DESC usata dal selectbox
                st.session_state.visual_date_index_desc = date_uniche_dt_desc.index(selected_date)
            except ValueError:
                # Fallback se la data non viene trovata (non dovrebbe accadere)
                st.session_state.visual_date_index_desc = 0

        # Variabile per contenere i numeri della tecnica da evidenziare
        numeri_da_evidenziare = set()

        # --- Layout a Colonne ---
        col1, col2 = st.columns(2) # Uguale larghezza

        # --- Colonna 1: Calcolo Tecnica Lotto ---
        with col1:
            st.markdown("### 🔮 Tecnica Lotto (Bari/Cagliari)")
            st.markdown("Seleziona una data per calcolare la previsione:")

            # Selectbox per la tecnica (usa la lista DESC)
            data_scelta_tecnica = st.selectbox(
                "Data per calcolo Tecnica:",
                options=date_uniche_dt_desc, # Mostra date recenti prima
                format_func=lambda d: d.strftime('%d/%m/%Y'), # Formato GG/MM/AAAA
                key="select_tecnica"
            )

            # Calcola la tecnica basata sulla data scelta in col1
            if data_scelta_tecnica:
                try:
                    # Filtra il DataFrame per trovare la riga corrispondente
                    riga_tecnica_df = df_lotto[df_lotto["Data"].dt.date == data_scelta_tecnica]

                    if not riga_tecnica_df.empty:
                        riga_tecnica = riga_tecnica_df.iloc[0]
                        terzo_bari_val = riga_tecnica['terzo_bari']
                        terzo_cagliari_val = riga_tecnica['terzo_cagliari']

                        # Verifica che i numeri siano validi (non NaN)
                        if pd.notna(terzo_bari_val) and pd.notna(terzo_cagliari_val):
                             # Prova a convertire in int PRIMA di chiamare la funzione
                            try:
                                terzo_bari = int(terzo_bari_val)
                                terzo_cagliari = int(terzo_cagliari_val)
                                # Calcola la tecnica
                                dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)
                                
                                # Calcola antecedenti e successivi
                                ant_bari, suc_bari = calcola_antecedente_successivo(terzo_bari)
                                ant_cagliari, suc_cagliari = calcola_antecedente_successivo(terzo_cagliari)
                                ant_ambata, suc_ambata = calcola_antecedente_successivo(ambata)
                                
                                # Popola il set per l'evidenziazione con numeri originali e antecedenti/successivi
                                numeri_da_evidenziare = {
                                    ambata, terzo_bari, terzo_cagliari,  # Numeri originali
                                    ant_bari, suc_bari,                  # Antecedente e successivo del terzo di Bari
                                    ant_cagliari, suc_cagliari,          # Antecedente e successivo del terzo di Cagliari
                                    ant_ambata, suc_ambata               # Antecedente e successivo dell'ambata
                                }

                                # --- Visualizzazione risultati tecnica ---
                                st.markdown("---")
                                st.markdown("#### Numeri di Riferimento (Tecnica)")
                                sub_col_t1, sub_col_t2 = st.columns(2)
                                with sub_col_t1: 
                                    st.metric(label="3° Estratto BARI", value=terzo_bari)
                                    st.caption(f"Decina: {dec_b}")
                                    st.caption(f"Antecedente: {ant_bari} | Successivo: {suc_bari}")
                                
                                with sub_col_t2: 
                                    st.metric(label="3° Estratto CAGLIARI", value=terzo_cagliari)
                                    st.caption(f"Decina: {dec_c}")
                                    st.caption(f"Antecedente: {ant_cagliari} | Successivo: {suc_cagliari}")
                                
                                st.markdown("---")
                                st.markdown("#### Previsione Calcolata (Tecnica)")
                                st.metric(label="🔥 AMBATA Calcolata", value=ambata)
                                st.caption(f"Derivante da: {dec_b} + {dec_c} = {dec_b + dec_c}" + (f" (poi -90)" if (dec_b + dec_c) > 90 else ""))
                                st.caption(f"Antecedente: {ant_ambata} | Successivo: {suc_ambata}")
                                
                                st.markdown("##### Giocate Suggerite:")
                                st.success(f"**Ambo Secco:** `{terzo_bari} – {terzo_cagliari}`")
                                st.success(f"**Terno Secco:** `{ambata} – {terzo_bari} – {terzo_cagliari}`")
                                st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale. \n*(Valutare anche Tutte)*")
                                
                                # Visualizza anche gli antecedenti e successivi
                                st.markdown("##### Numeri Antecedenti e Successivi:")
                                st.markdown(f"**Bari:** {ant_bari}-{terzo_bari}-{suc_bari}")
                                st.markdown(f"**Cagliari:** {ant_cagliari}-{terzo_cagliari}-{suc_cagliari}")
                                st.markdown(f"**Ambata:** {ant_ambata}-{ambata}-{suc_ambata}")
                                # --- Fine visualizzazione ---

                            except (ValueError, TypeError):
                                st.warning(f"Impossibile usare numeri Bari/Cagliari per la tecnica del {data_scelta_tecnica.strftime('%d/%m/%Y')}. Valori: '{terzo_bari_val}', '{terzo_cagliari_val}'.")
                                numeri_da_evidenziare = set() # Svuota il set se errore
                        else:
                            st.warning(f"Dati Bari/Cagliari mancanti per la tecnica del {data_scelta_tecnica.strftime('%d/%m/%Y')}.")
                            numeri_da_evidenziare = set()
                    else:
                         st.warning(f"Nessun dato trovato nel DataFrame per la data tecnica {data_scelta_tecnica.strftime('%d/%m/%Y')}")
                         numeri_da_evidenziare = set()
                except Exception as e_tec:
                     st.error(f"Errore durante l'elaborazione della tecnica: {e_tec}")
                     numeri_da_evidenziare = set()

        # --- Colonna 2: Visualizzatore Estrazioni Complete ---
        with col2:
            st.markdown("### 📅 Visualizzatore Estrazioni Complete")
            st.markdown("Seleziona o naviga le date per vedere l'estrazione:")

            # Indice corrente e massimo (basato sulla lista DESC)
            idx_corrente_desc = st.session_state.visual_date_index_desc
            max_idx_desc = len(date_uniche_dt_desc) - 1

            # --- Selectbox Visualizzazione ---
            # Questo widget ora riflette l'indice nello stato della sessione
            data_selezionata_nel_box = st.selectbox(
                "Data visualizzata:",
                options=date_uniche_dt_desc, # Lista DESC
                index=st.session_state.visual_date_index_desc, # Usa l'indice dallo stato
                format_func=lambda d: d.strftime('%d/%m/%Y'),
           
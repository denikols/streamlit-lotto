# --- START OF FILE streamlit_lotto_app.py ---

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date # Import date specificamente

# --- Funzioni Ausiliarie ---

def calcola_tecnica_lotto(bari: int, cagliari: int) -> tuple[int, int, int]:
    """Calcola le decine e l'ambata sommando le decine."""
    if not isinstance(bari, (int, np.integer)) or not isinstance(cagliari, (int, np.integer)):
        raise ValueError("Input per calcola_tecnica_lotto devono essere interi.")
    dec_b = bari // 10
    dec_c = cagliari // 10
    amb = dec_b + dec_c
    if amb > 90:
        amb -= 90
    return dec_b, dec_c, amb

@st.cache_data(ttl=3600) # Aumentato TTL cache
def load_data(uploaded_file):
    """Carica e processa i dati dal file CSV."""
    try:
        # Usa BytesIO per leggere direttamente dall'oggetto UploadedFile
        # Questo è importante per il caching corretto con st.cache_data
        # import io
        # file_content = io.BytesIO(uploaded_file.getvalue())
        # df = pd.read_csv(file_content, skiprows=3)
        # Alternativa se sopra da problemi (meno ideale per caching):
        df = pd.read_csv(uploaded_file, skiprows=3)

        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
        df = df.dropna(subset=["Data"])

        col_bari_3_idx = 3
        col_cagliari_3_idx = 8

        if col_bari_3_idx >= len(df.columns) or col_cagliari_3_idx >= len(df.columns):
             raise IndexError("Indici di colonna per Bari/Cagliari (3 e 8) fuori dai limiti. Verifica struttura CSV.")

        col_bari_3 = df.columns[col_bari_3_idx]
        col_cagliari_3 = df.columns[col_cagliari_3_idx]

        df['terzo_bari'] = pd.to_numeric(df[col_bari_3], errors='coerce')
        df['terzo_cagliari'] = pd.to_numeric(df[col_cagliari_3], errors='coerce')

        # Ordina per data ASCENDENTE per facilitare navigazione prev/next con indici
        df = df.sort_values("Data", ascending=True).reset_index(drop=True)
        return df

    except pd.errors.EmptyDataError:
        st.error("Errore: Il file CSV caricato è vuoto o non contiene dati dopo le righe iniziali.")
        return pd.DataFrame()
    except IndexError as e:
         st.error(f"Errore: {e}. Verifica la struttura del file CSV e gli indici delle colonne.")
         return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore durante la lettura o l'elaborazione iniziale del file CSV: {str(e)}")
        return pd.DataFrame()

# --- Funzione di Styling ---
def highlight_numbers(val, numeri_da_evidenziare):
    """Restituisce lo stile CSS se il valore è nei numeri da evidenziare."""
    style = 'background-color: #FF4B4B; color: white; font-weight: bold;'
    try:
        # Tenta la conversione sicura a int prima del confronto
        if pd.notna(val) and int(val) in numeri_da_evidenziare:
            return style
    except (ValueError, TypeError):
        # Ignora se non è convertibile a int
        pass
    return ''

# --- Configurazione Pagina e Titolo ---
st.set_page_config(layout="wide")
st.title("📊 Analisi Lotto: Tecnica & Estrazioni con Navigazione")

# --- Upload File ---
uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni (es: 24e25.csv)", type="csv")

if uploaded_file:
    # Carica e processa i dati
    df_lotto = load_data(uploaded_file)

    if not df_lotto.empty:
        # Ottieni date uniche (come oggetti date) e ORDINA ASCENDENTE
        date_uniche_dt_asc = sorted(df_lotto["Data"].dt.date.unique())
        # Crea lista ordinata DISCENDENTE per i selectbox (più intuitivo per l'utente)
        date_uniche_dt_desc = sorted(date_uniche_dt_asc, reverse=True)


        # Lista delle ruote
        ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
                 "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

        # Inizializza lo stato della sessione per l'indice della data di visualizzazione
        # se non esiste già. Lo inizializziamo all'ultima data (indice 0 della lista discendente).
        if 'visual_date_index_desc' not in st.session_state:
            st.session_state.visual_date_index_desc = 0 # Indice nella lista DISCENDENTE

        # Funzione per aggiornare l'indice quando cambia il selectbox di visualizzazione
        def update_visual_index_from_selectbox():
            selected_date_str = st.session_state.select_visualizzazione # Data selezionata
            try:
                # Trova l'indice della data selezionata nella lista DISCENDENTE
                st.session_state.visual_date_index_desc = date_uniche_dt_desc.index(selected_date_str)
            except ValueError:
                 # Se la data non è trovata (non dovrebbe succedere), resetta a 0
                 st.session_state.visual_date_index_desc = 0

        # Inizializza il set dei numeri da evidenziare
        numeri_da_evidenziare = set()

        # --- Layout a Colonne ---
        col1, col2 = st.columns(2)

        # --- Colonna 1: Calcolo Tecnica Lotto ---
        with col1:
            st.markdown("### 🔮 Tecnica Lotto (Bari/Cagliari)")
            st.markdown("Seleziona una data per calcolare la previsione:")

            # Selectbox per la tecnica (usa la lista discendente)
            data_scelta_tecnica = st.selectbox(
                "Data per calcolo Tecnica:",
                options=date_uniche_dt_desc, # Lista discendente
                format_func=lambda d: d.strftime('%d/%m/%Y'),
                key="select_tecnica"
            )

            # --- Logica Calcolo Tecnica (invariata, ma popola numeri_da_evidenziare) ---
            if data_scelta_tecnica:
                try:
                    # Nota: df_lotto è ordinato ASC, quindi il filtro va bene comunque
                    riga_tecnica = df_lotto[df_lotto["Data"].dt.date == data_scelta_tecnica].iloc[0]
                    terzo_bari_val = riga_tecnica['terzo_bari']
                    terzo_cagliari_val = riga_tecnica['terzo_cagliari']

                    if pd.notna(terzo_bari_val) and pd.notna(terzo_cagliari_val):
                        terzo_bari = int(terzo_bari_val)
                        terzo_cagliari = int(terzo_cagliari_val)
                        dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)
                        numeri_da_evidenziare = {ambata, terzo_bari, terzo_cagliari}

                        # ... (resto del codice per mostrare i risultati della tecnica) ...
                        st.markdown("---")
                        st.markdown("#### Numeri di Riferimento (Tecnica)")
                        sub_col_t1, sub_col_t2 = st.columns(2)
                        with sub_col_t1: st.metric(label="3° Estratto BARI", value=terzo_bari); st.caption(f"Decina: {dec_b}")
                        with sub_col_t2: st.metric(label="3° Estratto CAGLIARI", value=terzo_cagliari); st.caption(f"Decina: {dec_c}")
                        st.markdown("---")
                        st.markdown("#### Previsione Calcolata (Tecnica)")
                        st.metric(label="🔥 AMBATA Calcolata", value=ambata)
                        st.caption(f"Derivante da: {dec_b} + {dec_c} = {dec_b + dec_c}" + (f" (poi -90)" if (dec_b + dec_c) > 90 else ""))
                        st.markdown("##### Giocate Suggerite:")
                        st.success(f"**Ambo Secco:** `{terzo_bari} – {terzo_cagliari}`")
                        st.success(f"**Terno Secco:** `{ambata} – {terzo_bari} – {terzo_cagliari}`")
                        st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale. \n*(Valutare anche Tutte)*")

                    else:
                        st.warning(f"Dati Bari/Cagliari mancanti/non validi per tecnica del {data_scelta_tecnica.strftime('%d/%m/%Y')}.")
                        numeri_da_evidenziare = set()
                except Exception as e_tec:
                     st.error(f"Errore elaborazione tecnica: {e_tec}")
                     numeri_da_evidenziare = set()


        # --- Colonna 2: Visualizzatore Estrazioni Complete ---
        with col2:
            st.markdown("### 📅 Visualizzatore Estrazioni Complete")
            st.markdown("Seleziona o naviga le date per vedere l'estrazione:")

            # --- Pulsanti di Navigazione ---
            # Usa l'indice della lista DISCENDENTE per i pulsanti
            # Precedente -> aumenta indice (va indietro nel tempo)
            # Successivo -> diminuisce indice (va avanti nel tempo)
            idx_corrente_desc = st.session_state.visual_date_index_desc
            max_idx_desc = len(date_uniche_dt_desc) - 1

            btn_cols = st.columns(2)
            with btn_cols[0]: # Pulsante Sinistra (Precedente)
                if st.button("⬅️ Estrazione Prec.", use_container_width=True, disabled=(idx_corrente_desc >= max_idx_desc)):
                    st.session_state.visual_date_index_desc += 1
                    st.rerun() # Ricarica per aggiornare selectbox e tabella

            with btn_cols[1]: # Pulsante Destra (Successiva)
                if st.button("Estrazione Succ. ➡️", use_container_width=True, disabled=(idx_corrente_desc <= 0)):
                    st.session_state.visual_date_index_desc -= 1
                    st.rerun() # Ricarica

            # --- Selectbox per Visualizzazione ---
            # L'indice selezionato è gestito da st.session_state.visual_date_index_desc
            data_selezionata_nel_box = st.selectbox(
                "Data visualizzata:",
                options=date_uniche_dt_desc, # Usa lista discendente per coerenza con indice
                index=st.session_state.visual_date_index_desc, # Imposta selezione corrente
                format_func=lambda d: d.strftime('%d/%m/%Y'),
                key="select_visualizzazione", # Chiave per accedere al valore selezionato
                on_change=update_visual_index_from_selectbox # Aggiorna l'indice se l'utente cambia qui
            )

            # La data effettiva da usare per filtrare è quella indicata dall'indice
            data_effettiva_visualizzazione = date_uniche_dt_desc[st.session_state.visual_date_index_desc]

            # --- Logica Visualizzazione Tabella ---
            if data_effettiva_visualizzazione:
                estrazione_visual = df_lotto[df_lotto["Data"].dt.date == data_effettiva_visualizzazione]

                if not estrazione_visual.empty:
                    riga_visual = estrazione_visual.iloc[0]
                    dati_tabella = {}
                    colonne_lette = list(df_lotto.columns)

                    for ruota in ruote:
                        numeri_ruota = [None] * 5 # Default a None
                        colonne_ruota = [col for col in colonne_lette if col.startswith(ruota)]
                        colonne_da_usare = colonne_ruota[:5]

                        if len(colonne_da_usare) == 5:
                            try:
                                numeri_ruota_raw = riga_visual[colonne_da_usare].tolist()
                                numeri_ruota = [int(n) if pd.notna(n) and isinstance(n, (int, float, np.number)) else None for n in numeri_ruota_raw]
                            except Exception:
                                numeri_ruota = [None] * 5
                        dati_tabella[ruota] = numeri_ruota

                    df_tabella_visualizzazione = pd.DataFrame(dati_tabella, index=["1º", "2º", "3º", "4º", "5º"])

                    st.markdown("---")
                    st.markdown(f"**Estrazione del {data_effettiva_visualizzazione.strftime('%d/%m/%Y')}**")

                    df_visual_transposed = df_tabella_visualizzazione.transpose()
                    ruote_da_evidenziare = ["Bari", "Cagliari", "Nazionale"]

                    if numeri_da_evidenziare:
                         # Crea lo Styler e applica la funzione di highlight
                         df_styler = df_visual_transposed.style.apply(
                              # Usa 'apply' sull'intero DataFrame per passare più info alla funzione
                              # ma qui usiamo applymap perché più semplice per cella singola
                              lambda df_slice: df_slice.applymap(lambda val: highlight_numbers(val, numeri_da_evidenziare)),
                              subset=pd.IndexSlice[ruote_da_evidenziare, :]
                         ).format(na_rep="-") # Formatta i NaN/None come '-' DOPO lo styling
                         st.dataframe(df_styler, use_container_width=True)
                    else:
                         # Mostra senza stile, formattando i NaN/None
                         st.dataframe(df_visual_transposed.fillna("-"), use_container_width=True)

                else:
                    st.warning("Nessuna estrazione trovata per la data selezionata per la visualizzazione.")
    else:
        st.warning("Impossibile caricare i dati. Verifica il file CSV.")

# --- END OF FILE streamlit_lotto_app.py ---
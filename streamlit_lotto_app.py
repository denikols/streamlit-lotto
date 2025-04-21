# --- START OF FILE streamlit_lotto_app.py ---

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

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

@st.cache_data(ttl=60)
def load_data(uploaded_file):
    """Carica e processa i dati dal file CSV."""
    try:
        df = pd.read_csv(uploaded_file, skiprows=3)
        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
        df = df.dropna(subset=["Data"])

        col_bari_3_idx = 3
        col_cagliari_3_idx = 8

        # Verifica se gli indici sono validi
        if col_bari_3_idx >= len(df.columns) or col_cagliari_3_idx >= len(df.columns):
             raise IndexError("Indici di colonna per Bari/Cagliari fuori dai limiti. Verifica struttura CSV.")

        col_bari_3 = df.columns[col_bari_3_idx]
        col_cagliari_3 = df.columns[col_cagliari_3_idx]

        df['terzo_bari'] = pd.to_numeric(df[col_bari_3], errors='coerce')
        df['terzo_cagliari'] = pd.to_numeric(df[col_cagliari_3], errors='coerce')

        df = df.sort_values("Data", ascending=False).reset_index(drop=True)
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
    style = 'background-color: #FF4B4B; color: white;' # Rosso Streamlit con testo bianco
    # Controlla se val è un numero e se è nel set
    if pd.notna(val) and isinstance(val, (int, np.integer, float)) and int(val) in numeri_da_evidenziare:
        return style
    return ''

# --- Configurazione Pagina e Titolo ---
st.set_page_config(layout="wide")
st.title("📊 Analisi Lotto: Tecnica & Estrazioni con Evidenziazione")

# --- Upload File ---
uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni (es: 24e25.csv)", type="csv")

if uploaded_file:
    # Carica e processa i dati
    df_lotto = load_data(uploaded_file)

    if not df_lotto.empty:
        # Ottieni date uniche (come oggetti date) per i selectbox
        date_uniche_dt = sorted(df_lotto["Data"].dt.date.unique(), reverse=True)

        # Lista delle ruote
        ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
                 "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

        # Inizializza il set dei numeri da evidenziare (sarà popolato in col1)
        numeri_da_evidenziare = set()

        # --- Layout a Colonne ---
        col1, col2 = st.columns(2)

        # --- Colonna 1: Calcolo Tecnica Lotto ---
        with col1:
            st.markdown("### 🔮 Tecnica Lotto (Bari/Cagliari)")
            st.markdown("Seleziona una data per calcolare la previsione:")

            data_scelta_tecnica = st.selectbox(
                "Data per calcolo Tecnica:",
                options=date_uniche_dt,
                format_func=lambda date: date.strftime('%d/%m/%Y'),
                key="select_tecnica"
            )

            if data_scelta_tecnica:
                try:
                    riga_tecnica = df_lotto[df_lotto["Data"].dt.date == data_scelta_tecnica].iloc[0]
                    terzo_bari_val = riga_tecnica['terzo_bari']
                    terzo_cagliari_val = riga_tecnica['terzo_cagliari']

                    if pd.notna(terzo_bari_val) and pd.notna(terzo_cagliari_val):
                        terzo_bari = int(terzo_bari_val)
                        terzo_cagliari = int(terzo_cagliari_val)

                        dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)

                        # --- AGGIORNAMENTO: Popola il set di numeri da evidenziare ---
                        numeri_da_evidenziare = {ambata, terzo_bari, terzo_cagliari}
                        # --- Fine Aggiornamento ---

                        st.markdown("---")
                        st.markdown("#### Numeri di Riferimento (Tecnica)")
                        sub_col_t1, sub_col_t2 = st.columns(2)
                        with sub_col_t1:
                            st.metric(label="3° Estratto BARI", value=terzo_bari)
                            st.caption(f"Decina: {dec_b}")
                        with sub_col_t2:
                            st.metric(label="3° Estratto CAGLIARI", value=terzo_cagliari)
                            st.caption(f"Decina: {dec_c}")

                        st.markdown("---")
                        st.markdown("#### Previsione Calcolata (Tecnica)")
                        st.metric(label="🔥 AMBATA Calcolata", value=ambata)
                        st.caption(f"Derivante da: {dec_b} + {dec_c} = {dec_b + dec_c}" + (f" (poi -90)" if (dec_b + dec_c) > 90 else ""))

                        st.markdown("##### Giocate Suggerite:")
                        st.success(f"**Ambo Secco:** `{terzo_bari} – {terzo_cagliari}`")
                        st.success(f"**Terno Secco:** `{ambata} – {terzo_bari} – {terzo_cagliari}`")
                        st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale. \n*(Valutare anche Tutte)*")

                    else:
                        st.warning(f"Dati del 3° estratto Bari/Cagliari mancanti o non validi per la data {data_scelta_tecnica.strftime('%d/%m/%Y')}.")
                        numeri_da_evidenziare = set() # Assicura che sia vuoto se ci sono problemi

                except IndexError:
                     st.warning(f"Nessun dato trovato nel DataFrame per la data {data_scelta_tecnica.strftime('%d/%m/%Y')}")
                     numeri_da_evidenziare = set()
                except ValueError as ve:
                     st.error(f"Errore nel calcolo della tecnica: {ve}")
                     numeri_da_evidenziare = set()
                except Exception as e_tec:
                     st.error(f"Errore durante l'elaborazione della tecnica: {e_tec}")
                     numeri_da_evidenziare = set()


        # --- Colonna 2: Visualizzatore Estrazioni Complete ---
        with col2:
            st.markdown("### 📅 Visualizzatore Estrazioni Complete")
            st.markdown("Seleziona una data per vedere l'estrazione:")

            data_scelta_visualizzazione = st.selectbox(
                "Data per visualizzazione Tabella:",
                options=date_uniche_dt,
                format_func=lambda date: date.strftime('%d/%m/%Y'),
                key="select_visualizzazione"
            )

            if data_scelta_visualizzazione:
                estrazione_visual = df_lotto[df_lotto["Data"].dt.date == data_scelta_visualizzazione]

                if not estrazione_visual.empty:
                    riga_visual = estrazione_visual.iloc[0]
                    dati_tabella = {}
                    colonne_lette = list(df_lotto.columns)

                    for ruota in ruote:
                        numeri_ruota = []
                        colonne_ruota = [col for col in colonne_lette if col.startswith(ruota)]
                        colonne_da_usare = colonne_ruota[:5]

                        if len(colonne_da_usare) == 5:
                             try:
                                numeri_ruota_raw = riga_visual[colonne_da_usare].tolist()
                                # Tenta la conversione a int, altrimenti lascia il valore originale o None
                                numeri_ruota = []
                                for n in numeri_ruota_raw:
                                    try:
                                        if pd.notna(n):
                                            numeri_ruota.append(int(n))
                                        else:
                                            numeri_ruota.append(None) # Mantieni None se era NaN
                                    except (ValueError, TypeError):
                                         numeri_ruota.append(n) # Lascia come stringa/altro se non convertibile
                             except Exception:
                                numeri_ruota = [None] * 5 # Usa None per errori
                        else:
                            numeri_ruota = [None] * 5 # Usa None per ruote non trovate

                        dati_tabella[ruota] = numeri_ruota

                    # Crea DataFrame per la tabella di visualizzazione (i valori sono int o None/Altro)
                    df_tabella_visualizzazione = pd.DataFrame(dati_tabella, index=["1º", "2º", "3º", "4º", "5º"])

                    st.markdown("---")
                    st.markdown(f"**Estrazione del {data_scelta_visualizzazione.strftime('%d/%m/%Y')}**")

                    # --- MODIFICA: Applica lo Styling ---
                    ruote_da_evidenziare = ["Bari", "Cagliari", "Nazionale"]

                    # Trasponi PRIMA di applicare lo stile per avere le ruote come indice
                    df_visual_transposed = df_tabella_visualizzazione.transpose()

                    # Applica lo stile solo se ci sono numeri da evidenziare
                    if numeri_da_evidenziare:
                         # Crea l'oggetto Styler
                         df_styler = df_visual_transposed.style.applymap(
                              # Funzione lambda che chiama highlight_numbers
                              lambda val: highlight_numbers(val, numeri_da_evidenziare),
                              # Applica solo alle righe (ruote) specificate
                              subset=pd.IndexSlice[ruote_da_evidenziare, :]
                         )
                         # Mostra il DataFrame STILIZZATO
                         st.dataframe(df_styler, use_container_width=True)
                    else:
                         # Mostra il DataFrame NON STILIZZATO se non ci sono numeri da evidenziare
                         # Formatta i None/NaN come "-" per chiarezza
                         st.dataframe(df_visual_transposed.fillna("-"), use_container_width=True)
                    # --- Fine Modifica ---

                else:
                    st.warning("Nessuna estrazione trovata per la data selezionata per la visualizzazione.")
    else:
        st.warning("Impossibile caricare i dati. Verifica il file CSV.")

# --- END OF FILE streamlit_lotto_app.py ---
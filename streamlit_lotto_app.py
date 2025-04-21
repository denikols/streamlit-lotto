# --- START OF FILE streamlit_lotto_app.py ---

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- Funzioni Ausiliarie ---

def calcola_tecnica_lotto(bari: int, cagliari: int) -> tuple[int, int, int]:
    """Calcola le decine e l'ambata sommando le decine."""
    # Assicurati che gli input siano interi validi
    if not isinstance(bari, (int, np.integer)) or not isinstance(cagliari, (int, np.integer)):
        raise ValueError("Input per calcola_tecnica_lotto devono essere interi.")

    dec_b = bari // 10
    dec_c = cagliari // 10
    amb = dec_b + dec_c
    if amb > 90:
        amb -= 90
    # if amb == 0 and (dec_b != 0 or dec_c != 0): amb = 90 # Regola opzionale 0 -> 90
    return dec_b, dec_c, amb

@st.cache_data(ttl=60) # Cache per velocizzare ricaricamenti
def load_data(uploaded_file):
    """
    Carica i dati dal file CSV caricato, li pulisce, estrae i numeri
    per la tecnica e li ordina.
    """
    try:
        # Legge il CSV saltando le prime 3 righe
        df = pd.read_csv(uploaded_file, skiprows=3)

        # Converte la colonna Data, gestendo formati diversi e errori
        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
        df = df.dropna(subset=["Data"]) # Rimuove righe con date non valide

        # --- Estrazione specifica per la Tecnica ---
        # Identifica le colonne del 3° estratto di Bari e Cagliari
        # L'indice della colonna potrebbe variare se il CSV cambia, ma per 24e25.csv sono 3 e 8
        col_bari_3 = df.columns[3]   # Dovrebbe essere la terza colonna "Bari"
        col_cagliari_3 = df.columns[8] # Dovrebbe essere la terza colonna "Cagliari"

        # Estrai e converti i numeri per la tecnica, gestendo errori
        df['terzo_bari'] = pd.to_numeric(df[col_bari_3], errors='coerce')
        df['terzo_cagliari'] = pd.to_numeric(df[col_cagliari_3], errors='coerce')

        # Non rimuovere righe qui basate solo sui numeri della tecnica,
        # potrebbero servire per la visualizzazione completa. Gestiremo i NaN dopo.

        # Ordina per data decrescente (dalla più recente)
        df = df.sort_values("Data", ascending=False).reset_index(drop=True)

        return df

    except pd.errors.EmptyDataError:
        st.error("Errore: Il file CSV caricato è vuoto o non contiene dati dopo le righe iniziali.")
        return pd.DataFrame()
    except IndexError:
         st.error(f"Errore: Impossibile trovare le colonne attese per Bari/Cagliari (colonne indice 3 e 8). Verifica la struttura del file CSV.")
         return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore durante la lettura o l'elaborazione iniziale del file CSV: {str(e)}")
        st.warning("Assicurati che il file CSV sia valido e che l'intestazione sia alla quarta riga.")
        return pd.DataFrame()

# --- Configurazione Pagina e Titolo ---
st.set_page_config(layout="wide")
st.title("📊 Analisi Lotto: Tecnica & Estrazioni")

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

        # --- Layout a Colonne ---
        col1, col2 = st.columns(2) # Colonne di uguale larghezza

        # --- Colonna 1: Calcolo Tecnica Lotto ---
        with col1:
            st.markdown("### 🔮 Tecnica Lotto (Bari/Cagliari)")
            st.markdown("Seleziona una data per calcolare la previsione:")

            # Selectbox per la data della TECNICA
            data_scelta_tecnica = st.selectbox(
                "Data per calcolo Tecnica:",
                options=date_uniche_dt,
                format_func=lambda date: date.strftime('%d/%m/%Y'), # Formato visualizzazione
                key="select_tecnica" # Chiave univoca
            )

            if data_scelta_tecnica:
                # Trova la riga corrispondente alla data scelta per la tecnica
                riga_tecnica = df_lotto[df_lotto["Data"].dt.date == data_scelta_tecnica].iloc[0]

                # Estrai i numeri GIA' PROCESSATI durante il load_data
                terzo_bari_val = riga_tecnica['terzo_bari']
                terzo_cagliari_val = riga_tecnica['terzo_cagliari']

                # Validazione dei numeri estratti
                if pd.notna(terzo_bari_val) and pd.notna(terzo_cagliari_val):
                    try:
                        terzo_bari = int(terzo_bari_val)
                        terzo_cagliari = int(terzo_cagliari_val)

                        # Calcola e visualizza la tecnica
                        dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)

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

                    except ValueError as ve: # Errore dalla funzione di calcolo
                         st.error(f"Errore nel calcolo della tecnica: {ve}")
                    except Exception as e_calc: # Altro errore
                         st.error(f"Errore imprevisto durante il calcolo: {e_calc}")
                else:
                    st.warning(f"Dati del 3° estratto Bari/Cagliari mancanti o non validi per la data {data_scelta_tecnica.strftime('%d/%m/%Y')}.")

        # --- Colonna 2: Visualizzatore Estrazioni Complete ---
        with col2:
            st.markdown("### 📅 Visualizzatore Estrazioni Complete")
            st.markdown("Seleziona una data per vedere l'estrazione completa:")

            # Selectbox INDIPENDENTE per la data di VISUALIZZAZIONE
            data_scelta_visualizzazione = st.selectbox(
                "Data per visualizzazione Tabella:",
                options=date_uniche_dt,
                format_func=lambda date: date.strftime('%d/%m/%Y'),
                key="select_visualizzazione" # Chiave univoca diversa
            )

            if data_scelta_visualizzazione:
                # Trova la riga corrispondente alla data scelta per la VISUALIZZAZIONE
                estrazione_visual = df_lotto[df_lotto["Data"].dt.date == data_scelta_visualizzazione]

                if not estrazione_visual.empty:
                    riga_visual = estrazione_visual.iloc[0]
                    dati_tabella = {}
                    colonne_lette = list(df_lotto.columns) # Nomi colonne originali

                    for ruota in ruote:
                        numeri_ruota = []
                        colonne_ruota = [col for col in colonne_lette if col.startswith(ruota)]
                        colonne_da_usare = colonne_ruota[:5]

                        if len(colonne_da_usare) == 5:
                             try:
                                # Estrai i valori dalla riga filtrata
                                numeri_ruota = riga_visual[colonne_da_usare].tolist()
                                # Converti in int, gestendo NaN/valori non numerici
                                numeri_ruota = [int(n) if pd.notna(n) and isinstance(n, (int, float, np.number)) else "-" for n in numeri_ruota] # Usa "-" per None/NaN
                             except Exception:
                                numeri_ruota = ["-"] * 5
                        else:
                            numeri_ruota = ["-"] * 5 # Usa "-" per ruote non trovate

                        dati_tabella[ruota] = numeri_ruota

                    # Crea DataFrame per la tabella di visualizzazione
                    df_tabella_visualizzazione = pd.DataFrame(dati_tabella, index=["1º", "2º", "3º", "4º", "5º"])

                    st.markdown("---")
                    st.markdown(f"**Estrazione del {data_scelta_visualizzazione.strftime('%d/%m/%Y')}**")

                    # Mostra tabella trasposta
                    st.dataframe(
                        df_tabella_visualizzazione.transpose(),
                        use_container_width=True,
                        # Altezza automatica o fissa se preferisci
                        # height=(len(ruote) + 1) * 38
                    )
                else:
                    # Questo caso non dovrebbe verificarsi se data_scelta_visualizzazione proviene da date_uniche_dt
                    st.warning("Nessuna estrazione trovata per la data selezionata.")

    else:
        # Messaggio se df_lotto è vuoto dopo il caricamento
        st.warning("Impossibile caricare i dati. Verifica il file CSV.")

# --- END OF FILE streamlit_lotto_app.py ---
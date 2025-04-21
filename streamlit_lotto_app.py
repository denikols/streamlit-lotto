# --- START OF FILE streamlit_lotto_app.py ---

import streamlit as st
import pandas as pd
import numpy as np # Necessario per gestire potenziali NaN

# Funzione per calcolare la tecnica (definita globalmente per pulizia)
def calcola_tecnica_lotto(bari: int, cagliari: int) -> tuple[int, int, int]:
    """Calcola le decine e l'ambata sommando le decine."""
    dec_b = bari // 10
    dec_c = cagliari // 10
    amb = dec_b + dec_c
    if amb > 90:
        amb -= 90
    # if amb == 0 and (dec_b != 0 or dec_c != 0): amb = 90 # Regola opzionale 0 -> 90
    return dec_b, dec_c, amb

# --- Configurazione e Titolo ---
st.set_page_config(layout="wide")
st.title("📅 Visualizzatore Estrazioni Lotto & Tecnica")

# --- Upload File ---
uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni (es: 24e25.csv)", type="csv")

if uploaded_file:
    try:
        # --- Lettura e Pulizia Dati ---
        df = pd.read_csv(uploaded_file, skiprows=3) # Salta le prime 3 righe vuote/meta-dati
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce") # Converte la colonna Data
        df = df.dropna(subset=["Data"]) # Rimuove righe con date non valide
        df = df.sort_values("Data", ascending=False) # Ordina dalla più recente

        ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
                 "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

        # --- Selezione Data ---
        date_uniche = df["Data"].dt.date.unique()
        data_scelta = st.selectbox("Scegli una data di estrazione", date_uniche, format_func=lambda date: date.strftime('%d/%m/%Y')) # Mostra date formattate

        # --- Filtro Estrazione ---
        # Confronta solo la parte 'date' per evitare problemi con l'ora
        estrazione = df[df["Data"].dt.date == data_scelta]

        if estrazione.empty:
            st.warning(f"Nessuna estrazione trovata per la data {data_scelta.strftime('%d/%m/%Y')}.")
        else:
            # --- Estrazione Dati per la Tabella ---
            dati = {}
            colonne_lette = list(estrazione.columns) # Ottieni i nomi effettivi delle colonne lette da pandas

            for ruota in ruote:
                numeri_ruota = []
                # Cerca le colonne per la ruota specifica (gestisce nomi duplicati come "Bari", "Bari.1", ...)
                colonne_ruota = [col for col in colonne_lette if col.startswith(ruota)]
                # Prendi le prime 5 colonne trovate per quella ruota
                colonne_da_usare = colonne_ruota[:5]

                if len(colonne_da_usare) == 5:
                     # Estrai i valori dalla prima (e unica) riga filtrata
                     try:
                        numeri_ruota = estrazione[colonne_da_usare].iloc[0].tolist()
                        # Converti in int, gestendo NaN o valori non numerici
                        numeri_ruota = [int(n) if pd.notna(n) and isinstance(n, (int, float, np.number)) else None for n in numeri_ruota]
                     except Exception: # Cattura errori generici nell'estrazione/conversione
                        numeri_ruota = [None] * 5
                else:
                    # Se non trovi 5 colonne, metti None
                    numeri_ruota = [None] * 5

                dati[ruota] = numeri_ruota

            # Crea DataFrame per la tabella di visualizzazione
            df_tabella = pd.DataFrame(dati, index=["1º", "2º", "3º", "4º", "5º"])

            # --- Layout a Colonne ---
            col1, col2 = st.columns([1.5, 2.5]) # Colonna sx più stretta

            # --- Colonna 1: Tabella Estrazioni ---
            with col1:
                st.markdown(f"### 🎯 Numeri estratti del {data_scelta.strftime('%d/%m/%Y')}")

                # Calcola altezza dinamica (circa 38px per riga + header)
                altezza = (len(ruote) + 1) * 38
                st.dataframe(
                    df_tabella.transpose(), # Mostra ruote come righe
                    use_container_width=True, # Adatta alla larghezza colonna
                    height=altezza,
                    # width=600 # Rimosso width fisso per usare container width
                    hide_index=False # Mostra indici (ruote)
                )

            # --- Colonna 2: Calcolo Tecnica Lotto ---
            with col2:
                st.markdown("### 🔮 Previsione Secondo la Tecnica (Bari/Cagliari)")
                st.markdown("---")

                # Prova ad estrarre i numeri necessari dalla tabella già creata
                try:
                    # Accedi usando .loc con gli indici e nomi colonne corretti
                    terzo_bari_val = df_tabella.loc['3º', 'Bari']
                    terzo_cagliari_val = df_tabella.loc['3º', 'Cagliari']

                    # Verifica che i valori siano validi (non None e numerici)
                    if pd.notna(terzo_bari_val) and pd.notna(terzo_cagliari_val) and isinstance(terzo_bari_val, (int, np.integer)) and isinstance(terzo_cagliari_val, (int, np.integer)):
                        terzo_bari = int(terzo_bari_val)
                        terzo_cagliari = int(terzo_cagliari_val)

                        # Calcola i risultati usando la funzione definita sopra
                        dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)

                        # Visualizza i risultati della tecnica
                        st.markdown("#### Numeri Estratti di Riferimento")
                        sub_col1, sub_col2 = st.columns(2)
                        with sub_col1:
                            st.metric(label="3° Estratto BARI", value=terzo_bari)
                            st.caption(f"Decina: {dec_b}")
                        with sub_col2:
                            st.metric(label="3° Estratto CAGLIARI", value=terzo_cagliari)
                            st.caption(f"Decina: {dec_c}")

                        st.markdown("---")
                        st.markdown("#### Previsione Calcolata")
                        st.metric(label="🔥 AMBATA Calcolata", value=ambata)
                        st.caption(f"Derivante da: {dec_b} + {dec_c} = {dec_b + dec_c}" + (f" (poi -90)" if (dec_b + dec_c) > 90 else ""))

                        st.markdown("##### Giocate Suggerite:")
                        st.success(f"**Ambo Secco:** `{terzo_bari} – {terzo_cagliari}`")
                        st.success(f"**Terno Secco:** `{ambata} – {terzo_bari} – {terzo_cagliari}`")

                        st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale. \n*(Valutare anche Tutte per recupero spese)*")

                    else:
                        st.warning("Impossibile calcolare la tecnica: dati mancanti o non validi per il 3° estratto di Bari e/o Cagliari.")

                except KeyError:
                    st.error("Errore: le colonne 'Bari' o 'Cagliari' non sono state trovate correttamente nel file CSV processato.")
                except Exception as e:
                    st.error(f"Errore imprevisto durante il calcolo della tecnica: {str(e)}")

    except pd.errors.EmptyDataError:
        st.error("Errore: Il file CSV caricato è vuoto o non contiene dati dopo le righe iniziali.")
    except Exception as e:
        st.error(f"Errore durante la lettura o l'elaborazione del file CSV: {str(e)}")
        st.warning("Assicurati che il file CSV sia valido e che l'intestazione sia alla quarta riga (riga indice 3).")

# --- END OF FILE streamlit_lotto_app.py ---
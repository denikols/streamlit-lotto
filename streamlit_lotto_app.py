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

# --- Funzione di Styling corretta ---
def highlight_numbers(df):
    """
    Versione corretta della funzione di highlighting che limita 
    i numeri adiacenti (verdi) solo alle ruote specificate.
    """
    try:
        # Inizializza un DataFrame vuoto per lo stile
        style_df = pd.DataFrame('', index=df.index, columns=df.columns)
        
        # Stili definiti
        style_principale = 'background-color: #FF4B4B; color: white; font-weight: bold;'
        style_adiacente = 'background-color: #90EE90; color: black; font-weight: bold;'
        
        # Accedi alle variabili globali per numeri principali e adiacenti
        global numeri_da_evidenziare, numeri_adiacenti, ruote_da_evidenziare
        
        # Applica stili per ogni cella
        for idx, row in df.iterrows():
            nome_ruota = idx  # Il nome della ruota è l'indice nella tabella trasposta
            for col in df.columns:
                val = df.at[idx, col]
                if pd.notna(val) and isinstance(val, (int, float, np.number)):
                    try:
                        num_val = int(val)
                        # Verifica se è un numero principale e in una ruota da evidenziare
                        if num_val in numeri_da_evidenziare and nome_ruota in ruote_da_evidenziare:
                            style_df.at[idx, col] = style_principale
                        # Verifica se è un numero adiacente (SOLO nelle ruote da evidenziare)
                        elif num_val in numeri_adiacenti and nome_ruota in ruote_da_evidenziare:
                            style_df.at[idx, col] = style_adiacente
                    except (ValueError, TypeError):
                        pass
        
        return style_df
    except Exception as e:
        # In caso di errore nella funzione di styling, non applicare stili
        st.error(f"Errore nella funzione highlight_numbers: {e}")
        return pd.DataFrame('', index=df.index, columns=df.columns)

# --- Configurazione Pagina e Titolo ---
st.set_page_config(layout="wide")
st.title("📊 Analisi Lotto: Tecnica & Estrazioni con Navigazione")

# Variabili globali per i numeri da evidenziare
numeri_da_evidenziare = set()  # Numeri principali (rossi)
numeri_adiacenti = set()       # Numeri adiacenti (verdi)
ruote_da_evidenziare = ["Bari", "Cagliari", "Nazionale"]  # Ruote con numeri principali

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
                                
                                # Popola i set globali per l'evidenziazione
                                numeri_da_evidenziare.clear()
                                numeri_adiacenti.clear()
                                
                                # Aggiungi i numeri principali
                                numeri_da_evidenziare.update([ambata, terzo_bari, terzo_cagliari])
                                
                                # Calcola i numeri adiacenti (precedenti e successivi)
                                for num in numeri_da_evidenziare:
                                    # Aggiungi il numero precedente (gestendo il caso dello 0 e 90)
                                    prev_num = 90 if num == 1 else (num - 1)
                                    # Aggiungi il numero successivo (gestendo il caso del 90)
                                    next_num = 1 if num == 90 else (num + 1)
                                    numeri_adiacenti.add(prev_num)
                                    numeri_adiacenti.add(next_num)

                                # --- Visualizzazione risultati tecnica ---
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
                                
                                # Aggiungi legenda per i colori
                                st.markdown("---")
                                st.markdown("##### Legenda Colori nella Tabella:")
                                st.markdown(f"🔴 **Rosso:** Numeri principali ({', '.join(map(str, sorted(numeri_da_evidenziare)))})")
                                st.markdown(f"🟢 **Verde:** Numeri adiacenti ({', '.join(map(str, sorted(numeri_adiacenti)))})")
                                
                                st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale. \n*(Valutare anche Tutte)*")
                                # --- Fine visualizzazione ---

                            except (ValueError, TypeError):
                                st.warning(f"Impossibile usare numeri Bari/Cagliari per la tecnica del {data_scelta_tecnica.strftime('%d/%m/%Y')}. Valori: '{terzo_bari_val}', '{terzo_cagliari_val}'.")
                                numeri_da_evidenziare.clear()
                                numeri_adiacenti.clear()
                        else:
                            st.warning(f"Dati Bari/Cagliari mancanti per la tecnica del {data_scelta_tecnica.strftime('%d/%m/%Y')}.")
                            numeri_da_evidenziare.clear()
                            numeri_adiacenti.clear()
                    else:
                         st.warning(f"Nessun dato trovato nel DataFrame per la data tecnica {data_scelta_tecnica.strftime('%d/%m/%Y')}")
                         numeri_da_evidenziare.clear()
                         numeri_adiacenti.clear()
                except Exception as e_tec:
                     st.error(f"Errore durante l'elaborazione della tecnica: {e_tec}")
                     numeri_da_evidenziare.clear()
                     numeri_adiacenti.clear()

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
                key="select_visualizzazione",
                on_change=sync_index_from_selectbox # Aggiorna l'indice se l'utente cambia qui
            )

            # La data da usare è sempre quella indicata dall'indice nello stato
            data_effettiva_visualizzazione = date_uniche_dt_desc[st.session_state.visual_date_index_desc]

            # --- SPOSTATO QUI: Pulsanti di Navigazione vicino alla tabella ---
            st.markdown("---")
            st.markdown(f"**Estrazione del {data_effettiva_visualizzazione.strftime('%d/%m/%Y')}**")
            
            # Pulsanti di navigazione spostati qui, vicino alla tabella
            btn_cols = st.columns(2)
            # Pulsante Precedente: Aumenta indice DESC (va indietro nel tempo)
            if btn_cols[0].button("⬅️ Estrazione Prec.", use_container_width=True, disabled=(idx_corrente_desc >= max_idx_desc), key="btn_prev"):
                st.session_state.visual_date_index_desc += 1
                st.rerun()  # Forza il refresh per aggiornare subito la visualizzazione

            # Pulsante Successivo: Diminuisce indice DESC (va avanti nel tempo)
            if btn_cols[1].button("Estrazione Succ. ➡️", use_container_width=True, disabled=(idx_corrente_desc <= 0), key="btn_next"):
                st.session_state.visual_date_index_desc -= 1
                st.rerun()  # Forza il refresh per aggiornare subito la visualizzazione

            # --- Logica Visualizzazione Tabella ---
            # Filtra il DataFrame principale per la data effettiva da visualizzare
            estrazione_visual_df = df_lotto[df_lotto["Data"].dt.date == data_effettiva_visualizzazione]

            if not estrazione_visual_df.empty:
                # Prendi la prima (e unica) riga trovata
                riga_visual = estrazione_visual_df.iloc[0]
                dati_tabella = {}
                colonne_lette = list(df_lotto.columns) # Nomi colonne del df caricato

                # Estrai i numeri per ogni ruota
                for ruota in ruote:
                    numeri_ruota = [None] * 5 # Inizializza con None
                    colonne_ruota_trovate = [col for col in colonne_lette if col.startswith(ruota)]
                    colonne_da_usare = colonne_ruota_trovate[:5] # Prendi le prime 5

                    if len(colonne_da_usare) == 5:
                        try:
                            # Estrai i valori dalla riga selezionata usando i nomi delle colonne trovate
                            numeri_ruota_raw = riga_visual[colonne_da_usare].tolist()
                            # Mantieni i tipi come sono per ora (numeri o None)
                            numeri_ruota = [n if pd.notna(n) else None for n in numeri_ruota_raw]
                        except KeyError as ke:
                            st.warning(f"Errore nell'accesso alle colonne per la ruota {ruota}: {ke}. Colonne cercate: {colonne_da_usare}")
                            numeri_ruota = [None] * 5
                        except Exception as e_extr:
                            st.warning(f"Errore imprevisto estrazione ruota {ruota}: {e_extr}")
                            numeri_ruota = [None] * 5
                    # else: lascia numeri_ruota come [None] * 5

                    dati_tabella[ruota] = numeri_ruota

                # Crea DataFrame per la visualizzazione
                df_tabella_visualizzazione = pd.DataFrame(dati_tabella, index=["1º", "2º", "3º", "4º", "5º"])
                # Trasponi per avere Ruote come righe
                df_visual_transposed = df_tabella_visualizzazione.transpose()

                # Converti valori numerici da float a int per visualizzazione migliore
                df_visual_int = df_visual_transposed.copy()
                for col in df_visual_int.columns:
                    df_visual_int[col] = df_visual_int[col].apply(lambda x: int(x) if pd.notna(x) else None)

                # --- Applica Styling e Visualizza ---
                try:
                    # Utilizzo del metodo di styling diretto semplificato
                    if numeri_da_evidenziare:
                        # Applica la funzione di styling aggiornata
                        styled_df = df_visual_int.style.apply(highlight_numbers, axis=None).format(na_rep="-")
                        st.dataframe(styled_df, use_container_width=True)
                    else:
                        # Se non ci sono numeri da evidenziare, mostra senza stile
                        st.dataframe(df_visual_int.fillna("-"), use_container_width=True)
                except Exception as e_style:
                    st.error(f"Errore durante l'applicazione dello stile: {e_style}")
                    # Fallback: mostra tabella non stilizzata
                    st.dataframe(df_visual_int.fillna("-"), use_container_width=True)

            else:
                # Questo messaggio indica un problema se la data selezionata non trova corrispondenza nel df
                st.warning(f"Nessun dato di estrazione trovato nel DataFrame per la data {data_effettiva_visualizzazione.strftime('%d/%m/%Y')}. Verifica coerenza dati.")

    elif df_lotto is not None: # Caricamento riuscito ma df vuoto
        st.warning("Il file CSV caricato non contiene dati validi dopo l'elaborazione.")
    # else: l'errore è già stato mostrato da load_data()

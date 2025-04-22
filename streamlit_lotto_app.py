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

def calcola_antecedente_successivo(numero: int) -> tuple[int | None, int | None]:
    """Calcola l'antecedente e il successivo di un numero."""
    # Assicurati che il numero sia un intero valido tra 1 e 90
    # Aggiunto controllo per 1-90 per evitare calcoli insensati
    if not isinstance(numero, int) or not (1 <= numero <= 90):
        return None, None # Restituisce None se il numero non è valido
        
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
    Tenta di identificare l'intestazione e ordina per data ASCENDENTE.
    """
    try:
        file_content = io.BytesIO(uploaded_file_content)
        
        # Tentativo di identificare la riga dell'intestazione leggendo le prime righe
        # Cerchiamo una riga che contenga 'data' e almeno una ruota nota (es. 'bari')
        header_row = 0
        try:
            # Leggi le prime 10 righe per cercare l'intestazione
            # Prova con delimitatori comuni (;, ,) e encoding (utf-8, latin-1)
            potential_delimiters = [';', ',']
            potential_encodings = ['utf-8', 'latin-1']
            
            header_found = False
            for encoding in potential_encodings:
                for delimiter in potential_delimiters:
                    try:
                        file_content.seek(0) # Resetta il puntatore per ogni tentativo
                        header_check = pd.read_csv(file_content, nrows=10, header=None, encoding=encoding, sep=delimiter)
                        
                        for i in range(len(header_check)):
                             row_text = " ".join(map(str, header_check.iloc[i].dropna().tolist())).lower()
                             if "data" in row_text and ("bari" in row_text or "cagliari" in row_text):
                                 header_row = i
                                 header_found = True
                                 break # Trovata intestazione, esci dal loop delle righe
                        
                        if header_found:
                            st.info(f"Intestazione dati identificata nella riga {header_row + 1} con encoding '{encoding}' e delimitatore '{delimiter}'.")
                            break # Trovata intestazione, esci dal loop dei delimitatori
                    except Exception:
                        # Ignora errori di lettura con questa combinazione e prova la successiva
                        pass
                if header_found:
                    break # Trovata intestazione, esci dal loop degli encoding

            if not header_found:
                 # Fallback: assume l'intestazione sia nella riga 3 (indice 2) o simile se non trovata
                 st.warning("Intestazione dati non identificata automaticamente. Tentativo di leggere a partire dalla riga 4 (indice 3) con delimitatore ';'.")
                 header_row = 3 -1 # CSV tipici spesso hanno 3 righe iniziali prima dell'intestazione vera
                 # Usiamo un delimitatore di default per il fallback, ';' è comune in alcuni formati
                 delimiter = ';' 
                 encoding = 'latin-1' # Un encoding comune per file non standard utf-8


        except Exception as e:
            st.warning(f"Errore generico durante la ricerca dell'intestazione: {e}. Tentativo di leggere a partire dalla riga 4 (indice 3) con delimitatore ';'.")
            header_row = 3 -1 # Fallback
            delimiter = ';'
            encoding = 'latin-1'


        # Leggi il file completo usando l'intestazione trovata o il fallback
        file_content.seek(0) # Resetta il puntatore per la lettura completa
        try:
             df = pd.read_csv(file_content, skiprows=header_row, encoding=encoding, sep=delimiter)
        except Exception as e:
             st.error(f"Errore durante la lettura completa del file con le impostazioni trovate: {e}. Assicurati che il file sia un CSV valido con la struttura attesa.")
             return pd.DataFrame() # Restituisci un DataFrame vuoto in caso di fallimento

        # Rinomina la colonna della data per uniformità (cerca case-insensitive)
        date_col_name = None
        for col in df.columns:
            # Considera anche potenziali spazi bianchi attorno al nome colonna
            if isinstance(col, str) and col.lower().strip() == "data":
                date_col_name = col
                break
        
        if date_col_name is None:
             raise ValueError("Colonna 'Data' non trovata nel file CSV.")
             
        if date_col_name != "Data":
            df = df.rename(columns={date_col_name: "Data"})

        # Converti colonna Data e rimuovi righe non valide
        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
        df = df.dropna(subset=["Data"])

        # Verifica se il DataFrame è vuoto dopo la conversione della data
        if df.empty:
            st.error("Nessuna data valida trovata nel file CSV.")
            return pd.DataFrame()

        # Trova le colonne per Bari e Cagliari cercando nei nomi (case-insensitive)
        # Ordina le colonne trovate per nome per provare a garantire l'ordine 1°, 2°, 3°, ...
        bari_cols = sorted([col for col in df.columns if isinstance(col, str) and col.lower().strip().startswith('bari')])
        cagliari_cols = sorted([col for col in df.columns if isinstance(col, str) and col.lower().strip().startswith('cagliari')])
        
        if len(bari_cols) < 5 or len(cagliari_cols) < 5:
             # Servono 5 estratti per la visualizzazione, e il 3° per la tecnica
            raise ValueError(f"Non sono state trovate almeno 5 colonne per Bari ({len(bari_cols)} trovate) e Cagliari ({len(cagliari_cols)} trovate). Assicurati che i nomi delle colonne inizino con 'Bari'/'Cagliari'.")
            
        # Usa la terza colonna per ciascuna ruota per la tecnica (indice 2 dopo l'ordinamento, che dovrebbe corrispondere al 3° estratto)
        col_bari_3 = bari_cols[2]  
        col_cagliari_3 = cagliari_cols[2]

        # Estrai e converti numeri per la tecnica (NaN se errore)
        # Applica strip() prima della conversione per gestire spazi extra
        df['terzo_bari'] = pd.to_numeric(df[col_bari_3].astype(str).str.strip(), errors='coerce')
        df['terzo_cagliari'] = pd.to_numeric(df[col_cagliari_3].astype(str).str.strip(), errors='coerce')

        # Ordina per data ASCENDENTE (dal più vecchio al più recente)
        df = df.sort_values("Data", ascending=True).reset_index(drop=True)
        return df

    except pd.errors.EmptyDataError:
        st.error("Errore: Il file CSV caricato è vuoto o non contiene dati leggibili dopo le righe iniziali.")
        return pd.DataFrame()
    except IndexError as e:
         st.error(f"Errore nell'accesso alle colonne (indice): {e}. Assicurati che il CSV abbia la struttura attesa (es: 5 colonne per ruota dopo la Data).")
         return pd.DataFrame()
    except ValueError as e:
         st.error(f"Errore nella struttura del file: {e}")
         return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore generico durante la lettura o l'elaborazione iniziale del file CSV: {type(e).__name__}: {e}")
        return pd.DataFrame()

# --- Funzione di Styling aggiornata per due colori ---
def highlight_numbers_conditional(data, main_numbers, antsuc_numbers, target_wheels):
    """
    Applica stili condizionali ai numeri specifici nelle ruote target.
    Restituisce un DataFrame di stringhe CSS.
    """
    # Inizializza un DataFrame vuoto della stessa forma per lo stile
    style_df = pd.DataFrame('', index=data.index, columns=data.columns)
    
    red_style = 'background-color: #FF4B4B; color: white; font-weight: bold;' # Rosso per numeri principali
    green_style = 'background-color: #90EE90;' # Verde chiaro per antecedenti/successivi
    
    # Crea un set di nomi di ruote target in minuscolo per un confronto case-insensitive
    target_wheels_lower = {wheel.lower() for wheel in target_wheels}

    # Itera attraverso le colonne (ruote) e le righe (posizioni) del DataFrame di visualizzazione
    for col_name in data.columns:
        # Controlla se la ruota corrente è tra quelle da evidenziare (case-insensitive comparison)
        # Confronta la versione in minuscolo del nome della colonna con il set target_wheels_lower
        if any(col_name.lower().strip().startswith(target_wheel) for target_wheel in target_wheels_lower):
            for row_index in data.index:
                val = data.loc[row_index, col_name]

                # Assicurati che il valore sia un numero valido prima di controllarlo
                if pd.notna(val):
                     try:
                         num_val = int(val) # Converti in int per il confronto
                         
                         # Controlla prima i numeri principali (priorità)
                         if num_val in main_numbers:
                             style_df.loc[row_index, col_name] = red_style
                         # Poi controlla gli antecedenti/successivi
                         elif num_val in antsuc_numbers:
                             style_df.loc[row_index, col_name] = green_style
                             
                     except (ValueError, TypeError):
                         pass # Ignora valori non numerici o errori di conversione
    
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

        ruote_tutte = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
                 "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
        
        # Ruote su cui applicare l'evidenziazione
        ruote_da_evidenziare = ["Bari", "Cagliari", "Nazionale"]

        # --- Gestione Stato Sessione per Indice Visualizzazione e Numeri Tecnica ---
        # Inizializza l'indice se non esiste, puntando alla data più recente
        if 'visual_date_index_desc' not in st.session_state:
            st.session_state.visual_date_index_desc = 0 
        else:
            # Assicura che l'indice sia valido dopo un possibile ricaricamento/cambio file
            max_idx_valido = len(date_uniche_dt_desc) - 1
            # Clampa l'indice entro i limiti validi [0, max_idx_valido]
            st.session_state.visual_date_index_desc = max(0, min(st.session_state.visual_date_index_desc, max_idx_valido))

        # Stato per memorizzare i numeri da evidenziare calcolati dalla tecnica
        # Inizializza come set vuoti se non esistono
        if 'numeri_tecnica_main' not in st.session_state:
            st.session_state.numeri_tecnica_main = set()
        if 'numeri_tecnica_antsuc' not in st.session_state:
            st.session_state.numeri_tecnica_antsuc = set()


        # Callback per sincronizzare l'indice se si usa il selectbox di destra
        # Questa funzione viene chiamata quando il valore del selectbox con chiave "select_visualizzazione" cambia
        def sync_index_from_selectbox():
            selected_date = st.session_state.select_visualizzazione # Oggetto date selezionato dal selectbox
            try:
                # Trova l'indice di questa data nella lista DESC usata dal selectbox
                st.session_state.visual_date_index_desc = date_uniche_dt_desc.index(selected_date)
                # Streamlit riesegue lo script dopo l'on_change, quindi la visualizzazione si aggiornerà
            except ValueError:
                # Questo caso non dovrebbe accadere se la lista selectbox è stata creata correttamente
                st.error("Errore interno: data selezionata non trovata nell'elenco.")
                st.session_state.visual_date_index_desc = 0 # Reset all'inizio per sicurezza


        # --- Layout a Colonne ---
        col1, col2 = st.columns(2) # Uguale larghezza

        # --- Colonna 1: Calcolo Tecnica Lotto ---
        with col1:
            st.markdown("### 🔮 Tecnica Lotto (Bari/Cagliari)")
            st.markdown("Seleziona una data per calcolare la previsione:")

            # Selectbox per la tecnica (usa la lista DESC)
            # Default index 0 punta alla data più recente
            data_scelta_tecnica = st.selectbox(
                "Data per calcolo Tecnica:",
                options=date_uniche_dt_desc, # Mostra date recenti prima
                index=0, 
                format_func=lambda d: d.strftime('%d/%m/%Y'), # Formato GG/MM/AAAA
                key="select_tecnica" # Aggiunto un key esplicito
            )

            # Calcola la tecnica basata sulla data scelta in col1
            # Questo blocco viene eseguito ogni volta che la data_scelta_tecnica cambia o all'avvio
            # Resettiamo i numeri da evidenziare *prima* di un nuovo calcolo
            st.session_state.numeri_tecnica_main = set()
            st.session_state.numeri_tecnica_antsuc = set()


            if data_scelta_tecnica:
                try:
                    # Filtra il DataFrame per trovare la riga corrispondente alla data scelta per la tecnica
                    riga_tecnica_df = df_lotto[df_lotto["Data"].dt.date == data_scelta_tecnica]

                    if not riga_tecnica_df.empty:
                        riga_tecnica = riga_tecnica_df.iloc[0]
                        # Usa .get per sicurezza e controlla valori numerici
                        terzo_bari_val = riga_tecnica.get('terzo_bari') 
                        terzo_cagliari_val = riga_tecnica.get('terzo_cagliari')

                        # Verifica che i numeri siano validi (non NaN/None), nel range 1-90 e convertibili in int
                        if pd.notna(terzo_bari_val) and isinstance(terzo_bari_val, (int, float, np.number)):
                            try:
                                terzo_bari = int(terzo_bari_val)
                                if not (1 <= terzo_bari <= 90): raise ValueError("Fuori range 1-90")
                            except (ValueError, TypeError):
                                terzo_bari = None # Invalida se non è un int valido 1-90
                        else:
                            terzo_bari = None

                        if pd.notna(terzo_cagliari_val) and isinstance(terzo_cagliari_val, (int, float, np.number)):
                             try:
                                terzo_cagliari = int(terzo_cagliari_val)
                                if not (1 <= terzo_cagliari <= 90): raise ValueError("Fuori range 1-90")
                             except (ValueError, TypeError):
                                terzo_cagliari = None # Invalida se non è un int valido 1-90
                        else:
                             terzo_cagliari = None

                        
                        # Procedi con il calcolo solo se entrambi i numeri sono validi
                        if terzo_bari is not None and terzo_cagliari is not None:
                            try:
                                # Calcola la tecnica
                                dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)
                                
                                # Calcola antecedenti e successivi (la funzione gestisce già input non validi restituendo None)
                                ant_bari, suc_bari = calcola_antecedente_successivo(terzo_bari)
                                ant_cagliari, suc_cagliari = calcola_antecedente_successivo(terzo_cagliari)
                                ant_ambata, suc_ambata = calcola_antecedente_successivo(ambata) # Ambata è sempre tra 1 e 90, quindi questi non saranno None

                                # Popola i set per l'evidenziazione nello stato sessione
                                st.session_state.numeri_tecnica_main = {ambata, terzo_bari, terzo_cagliari}
                                
                                st.session_state.numeri_tecnica_antsuc = set()
                                if ant_bari is not None: st.session_state.numeri_tecnica_antsuc.add(ant_bari)
                                if suc_bari is not None: st.session_state.numeri_tecnica_antsuc.add(suc_bari)
                                if ant_cagliari is not None: st.session_state.numeri_tecnica_antsuc.add(ant_cagliari)
                                if suc_cagliari is not None: st.session_state.numeri_tecnica_antsuc.add(suc_cagliari)
                                # Ambata ant/suc sono sempre validi
                                if ant_ambata is not None: st.session_state.numeri_tecnica_antsuc.add(ant_ambata) 
                                if suc_ambata is not None: st.session_state.numeri_tecnica_antsuc.add(suc_ambata)
                                
                                # Rimuovi eventuali numeri principali dai set di antecedenti/successivi per evitare doppie evidenziazioni
                                st.session_state.numeri_tecnica_antsuc = st.session_state.numeri_tecnica_antsuc - st.session_state.numeri_tecnica_main

                                # --- Visualizzazione risultati tecnica ---
                                st.markdown("---")
                                st.markdown("#### Numeri di Riferimento (Tecnica)")
                                sub_col_t1, sub_col_t2 = st.columns(2)
                                with sub_col_t1: 
                                    st.metric(label="3° Estratto BARI", value=terzo_bari)
                                    st.caption(f"Decina: {dec_b}")
                                    if ant_bari is not None and suc_bari is not None:
                                         st.caption(f"Ant: {ant_bari} | Suc: {suc_bari}")
                                    elif terzo_bari is not None: # Se il numero di bari era valido ma ant/suc no (non dovrebbe succedere con 1-90)
                                         st.caption("Antecedente/Successivo non calcolabili")
                                
                                with sub_col_t2: 
                                    st.metric(label="3° Estratto CAGLIARI", value=terzo_cagliari)
                                    st.caption(f"Decina: {dec_c}")
                                    if ant_cagliari is not None and suc_cagliari is not None:
                                         st.caption(f"Ant: {ant_cagliari} | Suc: {suc_cagliari}")
                                    elif terzo_cagliari is not None: # Se il numero di cagliari era valido ma ant/suc no
                                         st.caption("Antecedente/Successivo non calcolabili")

                                st.markdown("---")
                                st.markdown("#### Previsione Calcolata (Tecnica)")
                                st.metric(label="🔥 AMBATA Calcolata", value=ambata)
                                # Mostra il calcolo esteso solo se c'è stata la sottrazione di 90
                                calc_str = f"{dec_b} + {dec_c} = {dec_b + dec_c}"
                                if (dec_b + dec_c) > 90:
                                     calc_str += f" ({dec_b + dec_c} - 90 = {ambata})"
                                st.caption(f"Derivante da: {calc_str}")

                                if ant_ambata is not None and suc_ambata is not None: # Questi saranno sempre validi per l'ambata 1-90
                                    st.caption(f"Ant: {ant_ambata} | Suc: {suc_ambata}")
                                
                                # Aggiungi informazioni sull'evidenziazione dei numeri nell'estrazione 
                                st.markdown("---")
                                main_list = sorted(list(st.session_state.numeri_tecnica_main))
                                antsuc_list = sorted(list(st.session_state.numeri_tecnica_antsuc))
                                
                                if main_list or antsuc_list:
                                    info_text = f"I numeri evidenziati nell'estrazione a destra (Ruote: {', '.join(ruote_da_evidenziare)}) includono:"
                                    if main_list:
                                        info_text += f"<br>• Numeri principali ({', '.join(map(str, main_list))}) in **<span style='color: #FF4B4B;'>rosso</span>**"
                                    if antsuc_list:
                                         info_text += f"<br>• Antecedenti/Successivi ({', '.join(map(str, antsuc_list))}) in **<span style='color: #90EE90;'>verde chiaro</span>**"
                                    
                                    st.info(info_text, icon="💡")
                                else:
                                    st.info("Nessun numero calcolato dalla tecnica per evidenziare.")

                            except Exception as e:
                                st.error(f"Errore durante il calcolo della tecnica: {type(e).__name__}: {e}")
                                st.session_state.numeri_tecnica_main = set()
                                st.session_state.numeri_tecnica_antsuc = set()

                        else: # Caso in cui terzo_bari o terzo_cagliari non sono validi
                            invalid_reason = []
                            if terzo_bari is None: invalid_reason.append("3° Bari")
                            if terzo_cagliari is None: invalid_reason.append("3° Cagliari")
                            st.warning(f"Dati per {', '.join(invalid_reason)} mancanti o non validi (non nel range 1-90) per la data {data_scelta_tecnica.strftime('%d/%m/%Y')}. Impossibile calcolare la tecnica.")
                            # Assicura che i set siano vuoti se il calcolo fallisce
                            st.session_state.numeri_tecnica_main = set()
                            st.session_state.numeri_tecnica_antsuc = set()


                    else:
                        st.warning(f"Nessun dato di estrazione trovato nel file per la data selezionata ({data_scelta_tecnica.strftime('%d/%m/%Y')}) per il calcolo della tecnica.")
                        st.session_state.numeri_tecnica_main = set()
                        st.session_state.numeri_tecnica_antsuc = set()

                except Exception as e:
                    st.error(f"Errore generico durante l'elaborazione della tecnica: {type(e).__name__}: {e}")
                    st.session_state.numeri_tecnica_main = set()
                    st.session_state.numeri_tecnica_antsuc = set()
            else:
                 # Questo caso dovrebbe essere raro se date_uniche_dt_desc non è vuoto
                 st.info("Seleziona una data per calcolare la tecnica.")


        # --- Colonna 2: Visualizzazione Estrazioni ---
        with col2:
            st.markdown("### 📋 Navigazione Estrazioni")
            
            # Ottieni data corrente per la visualizzazione (dalla lista DESC usando l'indice di stato)
            # Usa try/except per sicurezza se l'indice dovesse essere fuori range per un momento inatteso
            try:
                data_corrente = date_uniche_dt_desc[st.session_state.visual_date_index_desc]  
            except IndexError:
                 st.error("Errore interno: indice data non valido per la visualizzazione. Reset della data.")
                 st.session_state.visual_date_index_desc = 0
                 data_corrente = date_uniche_dt_desc[0] # Usa la prima data disponibile (la più recente)

            # Pulsanti per navigare AVANTI/INDIETRO nel tempo usando la logica dell'indice
            # navigare "Più vecchia" aumenta l'indice nella lista DESC
            # navigare "Più recente" diminuisce l'indice nella lista DESC
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            
            # Pulsante PRECEDENTE (indietro nel tempo = avanti nella lista DESC, indice ++)
            with nav_col1:
                # Disabilitato se siamo già alla data più vecchia (ultimo indice)
                if st.button("◀️ Più vecchia", 
                           disabled=st.session_state.visual_date_index_desc >= len(date_uniche_dt_desc)-1,
                           use_container_width=True):
                    st.session_state.visual_date_index_desc += 1 # Incrementa l'indice per andare indietro nel tempo
                    st.rerun()  # Forza aggiornamento UI
            
            # Selectbox con indice sincronizzato (usa la lista DESC)
            with nav_col2:
                 # Aggiorna l'indice del selectbox per mostrare la data corretta in base allo stato
                current_selectbox_index = st.session_state.visual_date_index_desc

                st.selectbox(
                    "Seleziona Data:", 
                    options=date_uniche_dt_desc,
                    index=current_selectbox_index,
                    format_func=lambda d: d.strftime('%d/%m/%Y'),
                    key="select_visualizzazione", # Aggiunto un key esplicito
                    on_change=sync_index_from_selectbox # Aggiorna l'indice di stato se l'utente cambia via selectbox
                )
                
            # Pulsante SUCCESSIVA (avanti nel tempo = indietro nella lista DESC, indice --)
            with nav_col3:
                # Disabilitato se siamo già alla data più recente (indice 0)
                if st.button("▶️ Più recente", 
                           disabled=st.session_state.visual_date_index_desc <= 0,
                           use_container_width=True):
                    st.session_state.visual_date_index_desc -= 1 # Decrementa l'indice per andare avanti nel tempo
                    st.rerun()  # Forza aggiornamento UI
            
            # Aggiorna UI per visualizzare l'estrazione corrispondente alla data corrente
            # Filtra il DataFrame per la data corrente (dallo stato sessione)
            df_estrazione = df_lotto[df_lotto["Data"].dt.date == data_corrente]
                
            if not df_estrazione.empty:
                # Ottieni la prima riga per questa data (dovrebbe essercene solo una)
                estrazione = df_estrazione.iloc[0]
                data_fmt = estrazione["Data"].strftime('%d/%m/%Y')
                
                st.markdown(f"#### Estrazione del {data_fmt}")
                
                # Estrai valori per la visualizzazione della griglia estrazione
                estratti_ruota = {}
                
                # Cerca le colonne per ogni ruota dinamicamente (case-insensitive e gestendo spazi)
                # Per ogni ruota nella lista completa ruote_tutte
                for ruota in ruote_tutte:
                    # Trova tutte le colonne che iniziano con il nome della ruota (strip per spazi)
                    cols = [col for col in df_estrazione.columns if isinstance(col, str) and col.lower().strip().startswith(ruota.lower())]
                    # Ordina le colonne trovate. Questo aiuta a mantenere l'ordine 1°, 2°, ... se i nomi lo permettono (es. "Bari 1", "Bari 2")
                    # Se i nomi sono solo "Bari", "Bari", l'ordine nel CSV è l'unica garanzia, ma sort non fa danni.
                    cols = sorted(cols)

                    numeri = []
                    # Estrai fino a 5 numeri per questa ruota dalle colonne trovate
                    for i in range(min(5, len(cols))): 
                        try:
                            val = estrazione.get(cols[i]) # Usa .get per sicurezza, default None
                            # Controlla se il valore estratto è numerico e non NaN/None
                            if pd.notna(val) and isinstance(val, (int, float, np.number)):
                                 # Prova a convertire in int (gestisce float come 1.0 -> 1)
                                try:
                                    numeri.append(int(val))
                                except (ValueError, TypeError):
                                    numeri.append(None) # Inserisci None se non convertibile in int
                            else:
                                numeros.append(None) # Inserisci None se NaN o non numerico valido (es. stringa vuota)
                        except IndexError:
                            # Questa eccezione dovrebbe essere rara grazie a min(5, len(cols))
                            numeros.append(None) 
                    
                    # Aggiungi None per le posizioni mancanti se meno di 5 numeri sono stati trovati/estratti
                    while len(numeri) < 5:
                        numeri.append(None)
                        
                    # Aggiungi la lista dei numeri (potrebbe contenere None per valori mancanti o non validi) al dizionario
                    estratti_ruota[ruota] = numeri
                
                # Costruisci un DataFrame per visualizzazione e styling
                # Crea il DataFrame solo con le ruote per cui abbiamo raccolto dati, nell'ordine di ruote_tutte
                # df_visual = pd.DataFrame(estratti_ruota, index=["1°", "2°", "3°", "4°", "5°"]) # Vecchio modo, include ruote senza dati
                
                # Nuovo modo: crea DataFrame solo con le ruote trovate che avevano almeno una colonna, mantenendo l'ordine
                found_ruote = [r for r in ruote_tutte if r in estratti_ruota]
                if found_ruote:
                     df_visual = pd.DataFrame({ruota: estratti_ruota[ruota] for ruota in found_ruote}, 
                                              index=["1°", "2°", "3°", "4°", "5°"])
                else:
                     df_visual = pd.DataFrame() # Nessuna ruota valida trovata per questa estrazione

                # Applica lo styling condizionale se ci sono numeri da evidenziare nello stato sessione
                # Controlla se ALMENO uno dei due set di numeri da evidenziare non è vuoto E se c'è un DataFrame da visualizzare
                if not df_visual.empty and (st.session_state.numeri_tecnica_main or st.session_state.numeri_tecnica_antsuc):
                    styled_df = df_visual.style.apply(
                        highlight_numbers_conditional, 
                        main_numbers=st.session_state.numeri_tecnica_main,
                        antsuc_numbers=st.session_state.numeri_tecnica_antsuc,
                        target_wheels=ruote_da_evidenziare, # Usa la lista definita sopra
                        axis=None # Applica la funzione all'intero DataFrame cell by cell
                    )
                    st.dataframe(styled_df, use_container_width=True)
                elif not df_visual.empty:
                    # Mostra il DataFrame senza stile se non ci sono numeri da evidenziare ma ci sono dati di estrazione
                    st.dataframe(df_visual, use_container_width=True)
                else:
                     st.warning("Nessun dato di estrazione valido trovato per costruire la tabella per questa data.")

            else:
                st.warning(f"Nessun dato di estrazione trovato nel file per la data visualizzata ({data_corrente.strftime('%d/%m/%Y')}).")
                
    else:
        # Questo messaggio appare se df_lotto è None o empty dopo load_data (dopo il caricamento file)
        st.warning("Il file caricato non contiene dati validi o è vuoto dopo l'elaborazione. Carica un file CSV corretto per iniziare.")
else:
    # Messaggio iniziale quando nessun file è caricato
    st.info("Carica un file CSV delle estrazioni del Lotto per iniziare l'analisi.")
    
    # Mostra istruzioni di utilizzo
    with st.expander("📚 Istruzioni di utilizzo"):
        st.markdown("""
        ### Come utilizzare questa applicazione:
        
        1.  **Carica un file CSV** contenente le estrazioni del Lotto.
            -   L'app cercherà di identificare automaticamente l'inizio dei dati e le colonne (es. "Data", "Bari", "Cagliari", ...).
            -   Assicurati che il file contenga una colonna per la "Data" e almeno 5 colonne per le ruote "Bari" e "Cagliari" con i numeri estratti. I numeri devono essere tra 1 e 90.
            -   L'app tenta di leggere il file con delimitatori `;` o `,` e encoding `utf-8` o `latin-1`.
            
        2.  **Tecnica Lotto (Colonna Sinistra)**: Seleziona una data per calcolare la previsione basata sui terzi estratti di Bari e Cagliari.
            -   L'app calcolerà l'ambata sommando le decine dei due numeri.
            -   Verranno mostrati anche i numeri antecedenti e successivi calcolati.
            
        3.  **Navigazione Estrazioni (Colonna Destra)**: Puoi navigare tra le estrazioni con i pulsanti "Più vecchia" / "Più recente" o selezionare una data specifica dal menu a tendina.
            -   I numeri principali della tecnica calcolata (3° Bari, 3° Cagliari, Ambata) saranno evidenziati in **rosso** nella tabella delle estrazioni.
            -   Gli antecedenti e successivi di questi numeri saranno evidenziati in **verde chiaro**.
            -   L'evidenziazione si applica solo alle ruote di **Bari, Cagliari e Nazionale**.
        """)
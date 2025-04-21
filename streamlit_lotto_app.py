import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io
import traceback

# Aggiunto un wrapper per catturare e mostrare errori
def main():
    try:
        # --- Configurazione Pagina e Titolo ---
        st.set_page_config(layout="wide")
        st.title("📊 Analisi Lotto: Tecnica & Estrazioni con Navigazione")

        # Inizializza variabili globali per evitare errori di riferimento
        if 'numeri_da_evidenziare' not in st.session_state:
            st.session_state.numeri_da_evidenziare = set()
        if 'numeri_adiacenti' not in st.session_state:
            st.session_state.numeri_adiacenti = set()
        if 'ruote_da_evidenziare' not in st.session_state:
            st.session_state.ruote_da_evidenziare = ["Bari", "Cagliari", "Nazionale"]

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
                # Prova prima a leggere senza skiprows per vedere la struttura
                preview_df = pd.read_csv(file_content, nrows=5)
                file_content.seek(0)  # Reimposta la posizione nel file
                
                # Determina quante righe saltare in base alla struttura
                skip_rows = 0
                for i in range(min(5, len(preview_df))):
                    if not any(str(x).lower() in ["data", "bari", "cagliari"] for x in preview_df.iloc[i]):
                        skip_rows += 1
                    else:
                        break
                
                # Leggi il CSV con il numero corretto di righe da saltare
                file_content.seek(0)  # Reimposta la posizione nel file
                df = pd.read_csv(file_content, skiprows=skip_rows)
                
                # Converti colonna Data e rimuovi righe non valide
                # Trova la colonna della data cercando "data" nel nome (case insensitive)
                data_col = next((col for col in df.columns if "data" in col.lower()), None)
                if not data_col:
                    st.error("Colonna 'Data' non trovata nel file CSV.")
                    return pd.DataFrame()
                
                df["Data"] = pd.to_datetime(df[data_col], errors='coerce')
                df = df.dropna(subset=["Data"])

                # Verifica se il DataFrame è vuoto dopo la conversione della data
                if df.empty:
                    st.error("Nessuna data valida trovata nel file CSV.")
                    return pd.DataFrame()

                # Trova le colonne per Bari e Cagliari cercando nei nomi
                bari_cols = [col for col in df.columns if "bari" in col.lower()]
                cagliari_cols = [col for col in df.columns if "cagliari" in col.lower()]
                
                if len(bari_cols) < 3 or len(cagliari_cols) < 3:
                    st.warning(f"Attenzione: Non sono state trovate sufficienti colonne per Bari e Cagliari. Trovate: {len(bari_cols)} per Bari e {len(cagliari_cols)} per Cagliari.")
                    # Continuiamo comunque, proveremo a usare quelle disponibili
                
                # Usa la terza colonna per ciascuna ruota, se disponibile
                col_bari_3 = bari_cols[2] if len(bari_cols) >= 3 else (bari_cols[0] if bari_cols else None)
                col_cagliari_3 = cagliari_cols[2] if len(cagliari_cols) >= 3 else (cagliari_cols[0] if cagliari_cols else None)

                # Estrai e converti numeri per la tecnica (NaN se errore)
                if col_bari_3:
                    df['terzo_bari'] = pd.to_numeric(df[col_bari_3], errors='coerce')
                else:
                    df['terzo_bari'] = np.nan
                
                if col_cagliari_3:
                    df['terzo_cagliari'] = pd.to_numeric(df[col_cagliari_3], errors='coerce')
                else:
                    df['terzo_cagliari'] = np.nan

                # Ordina per data ASCENDENTE (dal più vecchio al più recente)
                df = df.sort_values("Data", ascending=True).reset_index(drop=True)
                return df

            except pd.errors.EmptyDataError:
                st.error("Errore: Il file CSV caricato è vuoto o non contiene dati leggibili.")
                return pd.DataFrame()
            except Exception as e:
                st.error(f"Errore durante la lettura del file CSV: {type(e).__name__}: {e}")
                st.code(traceback.format_exc())
                return pd.DataFrame()

        # --- Funzione di Styling corretta ---
        def highlight_numbers(df):
            """
            Versione migliorata della funzione di highlighting che applica stili diversi
            per numeri principali e numeri adiacenti solo nelle ruote specificate.
            """
            # Inizializza un DataFrame vuoto per lo stile
            style_df = pd.DataFrame('', index=df.index, columns=df.columns)
            
            # Stili definiti
            style_principale = 'background-color: #FF4B4B; color: white; font-weight: bold;'
            style_adiacente = 'background-color: #90EE90; color: black; font-weight: bold;'
            
            # Usa i valori dalla session_state
            numeri_da_evidenziare = st.session_state.numeri_da_evidenziare
            numeri_adiacenti = st.session_state.numeri_adiacenti
            ruote_da_evidenziare = st.session_state.ruote_da_evidenziare
            
            # Applica stili per ogni cella
            for idx, row in df.iterrows():
                ruota = idx  # L'indice del DataFrame contiene il nome della ruota
                for col in df.columns:
                    val = df.at[idx, col]
                    if pd.notna(val) and isinstance(val, (int, float, np.number)):
                        try:
                            num_val = int(val)
                            # Verifica se è un numero principale e in una ruota da evidenziare
                            if num_val in numeri_da_evidenziare and ruota in ruote_da_evidenziare:
                                style_df.at[idx, col] = style_principale
                            # Verifica se è un numero adiacente SOLO nelle ruote specificate
                            elif num_val in numeri_adiacenti and ruota in ruote_da_evidenziare:
                                style_df.at[idx, col] = style_adiacente
                        except (ValueError, TypeError):
                            pass
            
            return style_df

        # --- Upload File ---
        uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni (es: 24e25.csv)", type="csv")

        if uploaded_file:
            # Usa il contenuto del file per permettere il caching
            uploaded_file_content = uploaded_file.getvalue()
            df_lotto = load_data(uploaded_file_content)
            
            # Procedi solo se il DataFrame è valido e non vuoto
            if df_lotto is not None and not df_lotto.empty:
                # Ottieni date uniche (oggetti date)
                date_uniche_dt_asc = sorted(df_lotto["Data"].dt.date.unique())
                date_uniche_dt_desc = sorted(date_uniche_dt_asc, reverse=True)

                if not date_uniche_dt_desc:
                    st.error("Non sono state trovate date uniche valide nel file.")
                    st.stop()

                ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
                         "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]

                # --- Gestione Stato Sessione per Indice Visualizzazione ---
                if 'visual_date_index_desc' not in st.session_state:
                    st.session_state.visual_date_index_desc = 0
                
                # Assicura che l'indice sia valido dopo un possibile ricaricamento/cambio file
                max_idx_valido = len(date_uniche_dt_desc) - 1
                if st.session_state.visual_date_index_desc > max_idx_valido:
                    st.session_state.visual_date_index_desc = max_idx_valido
                elif st.session_state.visual_date_index_desc < 0:
                    st.session_state.visual_date_index_desc = 0

                # Callback per sincronizzare l'indice se si usa il selectbox
                def sync_index_from_selectbox():
                    selected_date = st.session_state.select_visualizzazione
                    try:
                        st.session_state.visual_date_index_desc = date_uniche_dt_desc.index(selected_date)
                    except ValueError:
                        st.session_state.visual_date_index_desc = 0

                # --- Layout a Colonne ---
                col1, col2 = st.columns(2)

                # --- Colonna 1: Calcolo Tecnica Lotto ---
                with col1:
                    st.markdown("### 🔮 Tecnica Lotto (Bari/Cagliari)")
                    st.markdown("Seleziona una data per calcolare la previsione:")

                    # Selectbox per la tecnica (usa la lista DESC)
                    data_scelta_tecnica = st.selectbox(
                        "Data per calcolo Tecnica:",
                        options=date_uniche_dt_desc,
                        format_func=lambda d: d.strftime('%d/%m/%Y'),
                        key="select_tecnica"
                    )

                    # Calcola la tecnica basata sulla data scelta
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
                                    try:
                                        terzo_bari = int(terzo_bari_val)
                                        terzo_cagliari = int(terzo_cagliari_val)
                                        
                                        # Calcola la tecnica
                                        dec_b, dec_c, ambata = calcola_tecnica_lotto(terzo_bari, terzo_cagliari)
                                        
                                        # Popola i set nella session_state per l'evidenziazione
                                        st.session_state.numeri_da_evidenziare = {ambata, terzo_bari, terzo_cagliari}
                                        
                                        # Calcola i numeri adiacenti (precedenti e successivi)
                                        adiacenti = set()
                                        for num in st.session_state.numeri_da_evidenziare:
                                            # Aggiungi il numero precedente
                                            prev_num = 90 if num == 1 else (num - 1)
                                            # Aggiungi il numero successivo
                                            next_num = 1 if num == 90 else (num + 1)
                                            adiacenti.add(prev_num)
                                            adiacenti.add(next_num)
                                        
                                        st.session_state.numeri_adiacenti = adiacenti

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
                                        st.markdown(f"🔴 **Rosso:** Numeri principali ({', '.join(map(str, sorted(st.session_state.numeri_da_evidenziare)))})")
                                        st.markdown(f"🟢 **Verde:** Numeri adiacenti ({', '.join(map(str, sorted(st.session_state.numeri_adiacenti)))})")
                                        
                                        st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale. \n*(Valutare anche Tutte)*")

                                    except (ValueError, TypeError) as e:
                                        st.warning(f"Impossibile usare numeri Bari/Cagliari per la tecnica del {data_scelta_tecnica.strftime('%d/%m/%Y')}. Valori: '{terzo_bari_val}', '{terzo_cagliari_val}'.")
                                        st.session_state.numeri_da_evidenziare = set()
                                        st.session_state.numeri_adiacenti = set()
                                else:
                                    st.warning(f"Dati Bari/Cagliari mancanti per la tecnica del {data_scelta_tecnica.strftime('%d/%m/%Y')}.")
                                    st.session_state.numeri_da_evidenziare = set()
                                    st.session_state.numeri_adiacenti = set()
                            else:
                                st.warning(f"Nessun dato trovato nel DataFrame per la data tecnica {data_scelta_tecnica.strftime('%d/%m/%Y')}")
                                st.session_state.numeri_da_evidenziare = set()
                                st.session_state.numeri_adiacenti = set()
                        except Exception as e_tec:
                            st.error(f"Errore durante l'elaborazione della tecnica: {e_tec}")
                            st.code(traceback.format_exc())
                            st.session_state.numeri_da_evidenziare = set()
                            st.session_state.numeri_adiacenti = set()

                # --- Colonna 2: Visualizzatore Estrazioni Complete ---
                with col2:
                    st.markdown("### 📅 Visualizzatore Estrazioni Complete")
                    st.markdown("Seleziona o naviga le date per vedere l'estrazione:")

                    # Indice corrente e massimo
                    idx_corrente_desc = st.session_state.visual_date_index_desc
                    max_idx_desc = len(date_uniche_dt_desc) - 1

                    # Selectbox Visualizzazione
                    data_selezionata_nel_box = st.selectbox(
                        "Data visualizzata:",
                        options=date_uniche_dt_desc,
                        index=st.session_state.visual_date_index_desc,
                        format_func=lambda d: d.strftime('%d/%m/%Y'),
                        key="select_visualizzazione",
                        on_change=sync_index_from_selectbox
                    )

                    # Data da usare per la visualizzazione
                    data_effettiva_visualizzazione = date_uniche_dt_desc[st.session_state.visual_date_index_desc]

                    # Intestazione e pulsanti di navigazione
                    st.markdown("---")
                    st.markdown(f"**Estrazione del {data_effettiva_visualizzazione.strftime('%d/%m/%Y')}**")
                    
                    btn_cols = st.columns(2)
                    if btn_cols[0].button("⬅️ Estrazione Prec.", use_container_width=True, disabled=(idx_corrente_desc >= max_idx_desc), key="btn_prev"):
                        st.session_state.visual_date_index_desc += 1
                        st.rerun()

                    if btn_cols[1].button("Estrazione Succ. ➡️", use_container_width=True, disabled=(idx_corrente_desc <= 0), key="btn_next"):
                        st.session_state.visual_date_index_desc -= 1
                        st.rerun()

                    # Logica Visualizzazione Tabella
                    estrazione_visual_df = df_lotto[df_lotto["Data"].dt.date == data_effettiva_visualizzazione]

                    if not estrazione_visual_df.empty:
                        try:
                            # Prendi la prima riga trovata
                            riga_visual = estrazione_visual_df.iloc[0]
                            dati_tabella = {}
                            colonne_lette = list(df_lotto.columns)

                            # Estrai i numeri per ogni ruota
                            for ruota in ruote:
                                numeri_ruota = [None] * 5
                                # Cerca colonne che contengono il nome della ruota (case insensitive)
                                colonne_ruota_trovate = [col for col in colonne_lette if ruota.lower() in col.lower()]
                                colonne_da_usare = colonne_ruota_trovate[:5]

                                if colonne_da_usare:
                                    try:
                                        # Estrai i valori dalle colonne disponibili
                                        for i, col in enumerate(colonne_da_usare):
                                            if i < len(numeri_ruota):
                                                val = riga_visual[col]
                                                numeri_ruota[i] = val if pd.notna(val) else None
                                    except Exception as e_extr:
                                        st.warning(f"Errore nell'estrazione dati per la ruota {ruota}: {e_extr}")

                                dati_tabella[ruota] = numeri_ruota

                            # Crea DataFrame per la visualizzazione
                            df_tabella_visualizzazione = pd.DataFrame(dati_tabella, index=["1º", "2º", "3º", "4º", "5º"])
                            # Trasponi per avere Ruote come righe
                            df_visual_transposed = df_tabella_visualizzazione.transpose()

                            # Converti valori a int dove possibile
                            df_visual_int = df_visual_transposed.copy()
                            for col in df_visual_int.columns:
                                df_visual_int[col] = df_visual_int[col].apply(
                                    lambda x: int(x) if pd.notna(x) and isinstance(x, (int, float, np.number)) else x
                                )

                            # Applica Styling e Visualizza
                            try:
                                if st.session_state.numeri_da_evidenziare:
                                    # Applica la funzione di styling aggiornata
                                    styled_df = df_visual_int.style.apply(highlight_numbers, axis=None).format(na_rep="-")
                                    st.dataframe(styled_df, use_container_width=True)
                                else:
                                    # Se non ci sono numeri da evidenziare, mostra senza stile
                                    st.dataframe(df_visual_int.fillna("-"), use_container_width=True)
                            except Exception as e_style:
                                st.error(f"Errore durante l'applicazione dello stile: {e_style}")
                                st.code(traceback.format_exc())
                                # Fallback: mostra tabella non stilizzata
                                st.dataframe(df_visual_int.fillna("-"), use_container_width=True)
                        except Exception as e_viz:
                            st.error(f"Errore nella visualizzazione dell'estrazione: {e_viz}")
                            st.code(traceback.format_exc())
                    else:
                        st.warning(f"Nessun dato di estrazione trovato per la data {data_effettiva_visualizzazione.strftime('%d/%m/%Y')}.")
            elif df_lotto is not None:
                st.warning("Il file CSV caricato non contiene dati validi dopo l'elaborazione.")
        else:
            st.info("Carica un file CSV per iniziare l'analisi.")
    
    except Exception as e:
        st.error(f"Si è verificato un errore nell'applicazione: {e}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

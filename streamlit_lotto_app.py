@st.cache_data(ttl=3600) # Cache dati per 1 ora
def load_data(uploaded_file_content):
    """
    Carica e processa i dati dal contenuto del file CSV caricato.
    Versione migliorata con maggiore flessibilità per diversi formati CSV.
    """
    try:
        file_content = io.BytesIO(uploaded_file_content)
        
        # Prima tentativo: leggi le prime righe per analizzare la struttura
        df_preview = pd.read_csv(file_content, nrows=10)
        file_content.seek(0)  # Reimposta la posizione nel file
        
        # Visualizza la struttura per debug
        st.write("Anteprima delle colonne trovate nel CSV:", df_preview.columns.tolist())
        
        # Cerca colonne che potrebbero contenere le date
        potential_date_cols = []
        for col in df_preview.columns:
            # Controlla se il nome della colonna suggerisce che contiene date
            if any(date_keyword in col.lower() for date_keyword in ['data', 'date', 'giorno', 'day']):
                potential_date_cols.append(col)
            # Altrimenti, verifica se la colonna contiene valori che sembrano date
            else:
                sample = df_preview[col].dropna().head(3).astype(str)
                date_patterns = [
                    r'\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}',  # formati come 01/01/2023, 1-1-23
                    r'\d{4}[/.-]\d{1,2}[/.-]\d{1,2}'     # formati come 2023/01/01
                ]
                if any(sample.str.match(pattern).any() for pattern in date_patterns):
                    potential_date_cols.append(col)
        
        # Se abbiamo trovato potenziali colonne per le date
        if potential_date_cols:
            st.success(f"Trovate possibili colonne per le date: {potential_date_cols}")
            
            # Prova a leggere il file usando la prima colonna di data trovata
            date_col = potential_date_cols[0]
            df = pd.read_csv(file_content)
            
            # Converti la colonna trovata in formato data
            df["Data"] = pd.to_datetime(df[date_col], errors='coerce')
            
        else:
            # Nessuna colonna data identificabile, prova a leggere il file e cercare pattern nelle prime colonne
            df = pd.read_csv(file_content)
            
            # Prova le prime colonne per vedere se contengono date
            for i, col in enumerate(df.columns[:3]):  # Prova le prime 3 colonne
                try:
                    df["Data"] = pd.to_datetime(df[col], errors='coerce')
                    if not df["Data"].isna().all():  # Se almeno alcune date sono valide
                        st.success(f"Usata colonna {i+1} ({col}) come colonna Data")
                        break
                except:
                    continue
            
            # Se ancora non abbiamo trovato la colonna data
            if "Data" not in df.columns or df["Data"].isna().all():
                # Ultima risorsa: crea un indice di date fittizie per permettere all'app di funzionare
                st.warning("Non è stata trovata alcuna colonna data valida. Creato un indice temporale fittizio.")
                df["Data"] = pd.date_range(start='2023-01-01', periods=len(df), freq='W-MON')
        
        # Rimuovi righe con date non valide
        df = df.dropna(subset=["Data"])
        
        # Verifica se ci sono ancora righe nel DataFrame
        if df.empty:
            st.error("Nessuna data valida trovata nel file CSV.")
            return pd.DataFrame()
        
        # Trova le colonne per ogni ruota in modo flessibile
        ruote = ["Bari", "Cagliari", "Firenze", "Genova", "Milano",
                "Napoli", "Palermo", "Roma", "Torino", "Venezia", "Nazionale"]
        
        # Trova colonne per ogni ruota
        ruota_columns = {}
        for ruota in ruote:
            # Cerca colonne che contengono il nome della ruota (case insensitive)
            cols = [col for col in df.columns if ruota.lower() in col.lower()]
            ruota_columns[ruota] = cols
        
        # Mostra quali colonne sono state trovate per ciascuna ruota
        for ruota, cols in ruota_columns.items():
            if cols:
                st.success(f"Trovate {len(cols)} colonne per {ruota}: {cols}")
            else:
                st.warning(f"Nessuna colonna trovata per {ruota}")
        
        # Estrai e converti numeri per la tecnica (NaN se errore)
        # Cerca specificamente il terzo estratto per Bari e Cagliari
        
        # Per Bari
        if ruota_columns["Bari"]:
            bari_cols = ruota_columns["Bari"]
            # Prova a trovare la colonna del terzo estratto
            terzo_bari_col = None
            for col in bari_cols:
                if '3' in col or 'terzo' in col.lower() or 'third' in col.lower():
                    terzo_bari_col = col
                    break
            
            # Se non troviamo una colonna esplicitamente marcata come terza, usa la terza colonna se disponibile
            if not terzo_bari_col and len(bari_cols) >= 3:
                terzo_bari_col = bari_cols[2]
            # Altrimenti usa la prima colonna disponibile
            elif not terzo_bari_col and bari_cols:
                terzo_bari_col = bari_cols[0]
                
            if terzo_bari_col:
                df['terzo_bari'] = pd.to_numeric(df[terzo_bari_col], errors='coerce')
                st.success(f"Usata colonna '{terzo_bari_col}' per terzo estratto di Bari")
            else:
                df['terzo_bari'] = np.nan
                st.warning("Non è stata trovata una colonna valida per il terzo estratto di Bari")
        else:
            df['terzo_bari'] = np.nan
            st.warning("Nessuna colonna trovata per Bari")
        
        # Per Cagliari
        if ruota_columns["Cagliari"]:
            cagliari_cols = ruota_columns["Cagliari"]
            # Prova a trovare la colonna del terzo estratto
            terzo_cagliari_col = None
            for col in cagliari_cols:
                if '3' in col or 'terzo' in col.lower() or 'third' in col.lower():
                    terzo_cagliari_col = col
                    break
                    
            # Se non troviamo una colonna esplicitamente marcata come terza, usa la terza colonna se disponibile
            if not terzo_cagliari_col and len(cagliari_cols) >= 3:
                terzo_cagliari_col = cagliari_cols[2]
            # Altrimenti usa la prima colonna disponibile
            elif not terzo_cagliari_col and cagliari_cols:
                terzo_cagliari_col = cagliari_cols[0]
                
            if terzo_cagliari_col:
                df['terzo_cagliari'] = pd.to_numeric(df[terzo_cagliari_col], errors='coerce')
                st.success(f"Usata colonna '{terzo_cagliari_col}' per terzo estratto di Cagliari")
            else:
                df['terzo_cagliari'] = np.nan
                st.warning("Non è stata trovata una colonna valida per il terzo estratto di Cagliari")
        else:
            df['terzo_cagliari'] = np.nan
            st.warning("Nessuna colonna trovata per Cagliari")

        # Ordina per data ASCENDENTE (dal più vecchio al più recente)
        df = df.sort_values("Data", ascending=True).reset_index(drop=True)
        
        # Mostra un'anteprima del DataFrame elaborato
        st.write("Anteprima dei dati elaborati:")
        st.write(df[["Data", "terzo_bari", "terzo_cagliari"]].head())
        
        return df

    except pd.errors.EmptyDataError:
        st.error("Errore: Il file CSV caricato è vuoto o non contiene dati leggibili.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore durante la lettura del file CSV: {type(e).__name__}: {e}")
        st.code(traceback.format_exc())
        return pd.DataFrame()

def highlight_numbers(df):
    """
    Versione migliorata della funzione di highlighting che applica stili diversi
    per numeri principali e numeri adiacenti SOLO nelle ruote specificate.
    """
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

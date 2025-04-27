import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# --- Funzioni Ausiliarie ---

def calcola_tecnica_lotto(bari: int, cagliari: int) -> tuple[int, int, int]:
    """Calcola le decine e l'ambata sommando le decine."""
    dec_b = bari // 10
    dec_c = cagliari // 10
    amb = dec_b + dec_c
    if amb > 90:
        amb -= 90
    return dec_b, dec_c, amb

@st.cache_data(ttl=3600)
def load_data(uploaded_file_content):
    """Carica e processa i dati dal contenuto del file CSV caricato."""
    try:
        bio = io.BytesIO(uploaded_file_content)
        df = pd.read_csv(bio, skiprows=3)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.dropna(subset=['Data'])
        return df.sort_values('Data').reset_index(drop=True)
    except Exception as e:
        st.error(f"Errore caricamento CSV: {e}")
        return pd.DataFrame()

# Funzione di styling per estrazioni complete
def highlight_numbers(df):
    style = pd.DataFrame('', index=df.index, columns=df.columns)
    main = 'background-color: #FF4B4B; color: white; font-weight: bold;'
    adj = 'background-color: #90EE90; color: black; font-weight: bold;'
    global numeri_da_evidenziare, numeri_adiacenti, ruote_da_evidenziare
    for wheel in df.index:
        for col in df.columns:
            val = df.at[wheel, col]
            if pd.notna(val):
                n = int(val)
                if n in numeri_da_evidenziare and wheel in ruote_da_evidenziare:
                    style.at[wheel, col] = main
                elif n in numeri_adiacenti and wheel in ruote_da_evidenziare:
                    style.at[wheel, col] = adj
    return style

# Configurazione pagina
st.set_page_config(layout='wide')
st.title('📊 Analisi Lotto: Tecnica, Estrazioni e Statistiche Mensili')

# Variabili globali
numeri_da_evidenziare = set()
numeri_adiacenti = set()
ruote_da_evidenziare = ['Bari','Cagliari','Nazionale']

# Upload CSV
uploaded_file = st.file_uploader('Carica CSV estrazioni (es: 24e25.csv)', type='csv')
if not uploaded_file:
    st.info('Carica un file CSV per iniziare.')
    st.stop()

df_lotto = load_data(uploaded_file.getvalue())
if df_lotto.empty:
    st.error('Nessun dato valido.')
    st.stop()

# Determina liste date
all_dates = sorted(df_lotto['Data'].dt.date.unique(), reverse=True)

# Colonne layout
col1, col2 = st.columns(2)

# -- Colonna 1: Tecnica --
with col1:
    st.header('🔮 Tecnica Lotto (Bari/Cagliari)')
    primi = [d for d in all_dates if d.day<=7]
    sel = st.selectbox('Prima estrazione mese per tecnica:', primi, format_func=lambda d:d.strftime('%d/%m/%Y'))
    if sel:
        row = df_lotto[df_lotto['Data'].dt.date==sel].iloc[0]
        tb = int(row[[c for c in df_lotto.columns if c.startswith('Bari')][2]])
        tc = int(row[[c for c in df_lotto.columns if c.startswith('Cagliari')][2]])
        dec_b, dec_c, amb = calcola_tecnica_lotto(tb, tc)
        numeri_da_evidenziare = {tb,tc,amb}
        numeri_adiacenti = {(n-1) if n>1 else 90 for n in numeri_da_evidenziare} | {(n+1) if n<90 else 1 for n in numeri_da_evidenziare}
        st.metric('3° Bari',tb); st.metric('3° Cagliari',tc)
        st.metric('🔥 Ambata',amb)
        st.success(f'Ambo secco: {tb}–{tc}')
        st.success(f'Terno secco: {amb}–{tb}–{tc}')
        st.markdown('**Legenda Colori:** 🔴 Principali; 🟢 Adiacenti')
        st.markdown(f'🔴 {sorted(numeri_da_evidenziare)}  🟢 {sorted(numeri_adiacenti)}')

# -- Colonna 2: Estrazioni complete --
with col2:
    st.header('📅 Visualizzatore Estrazioni Complete')
    if 'idx' not in st.session_state: st.session_state.idx=0
    prev, nxt = st.columns(2)
    if prev.button('⬅️ Prec.', disabled=st.session_state.idx>=len(all_dates)-1): st.session_state.idx+=1
    if nxt.button('Succ. ➡️', disabled=st.session_state.idx<=0): st.session_state.idx-=1
    curr = all_dates[st.session_state.idx]
    st.subheader(curr.strftime('%d/%m/%Y'))
    df_row = df_lotto[df_lotto['Data'].dt.date==curr].iloc[0]
    wheels=['Bari','Cagliari','Firenze','Genova','Milano','Napoli','Palermo','Roma','Torino','Venezia','Nazionale']
    data={w: [int(df_row[c]) for c in df_lotto.columns if c.startswith(w)][:5] for w in wheels}
    df_vis = pd.DataFrame(data, index=[1,2,3,4,5]).T
    st.dataframe(df_vis.style.apply(highlight_numbers,axis=None).format(na_rep='-'))

# -- Statistiche Mensili --
st.markdown('---')
st.header('📊 Statistiche Mensili Ambi/Ambetti/Terni')
df_lotto['period'] = df_lotto['Data'].dt.to_period('M')
firsts = df_lotto[df_lotto['Data'].dt.day<=7].groupby('period')['Data'].min()
records=[]

# Debug mode
debug_mode = st.checkbox("Debug Mode")
if debug_mode:
    st.write("Formato del DataFrame:")
    st.write(df_lotto.head(1))
    st.write("Colonne nel DataFrame:")
    st.write(df_lotto.columns.tolist())

# Funzione per ottenere numeri di una ruota da una riga
def get_extracted_numbers(row, wheel):
    """Estrae i numeri di una specifica ruota da una riga di estrazione."""
    wheel_numbers = []
    
    # Trova tutte le colonne pertinenti per questa ruota
    cols = []
    # Prova diversi formati di colonna
    for col in df_lotto.columns:
        # Formato "Ruota Numero"
        if col.startswith(f"{wheel} "):
            cols.append(col)
        # Formato "RuotaNumero"
        elif col.startswith(wheel) and col != wheel and any(c.isdigit() for c in col):
            cols.append(col)
        # Altri formati possibili...
    
    # Ordina le colonne in modo corretto (se hanno un numero alla fine)
    def extract_num(col_name):
        try:
            return int(''.join(filter(str.isdigit, col_name)))
        except:
            return 0
    
    cols = sorted(cols, key=extract_num)[:5]  # Prendi solo le prime 5
    
    # Estrai i numeri
    for col in cols:
        try:
            val = row[col]
            if pd.notna(val):
                n = int(val)
                if 1 <= n <= 90:  # Assicurati che sia un numero valido del lotto
                    wheel_numbers.append(n)
        except (ValueError, TypeError):
            pass
    
    return wheel_numbers

for per, fd in firsts.items():
    row0 = df_lotto[df_lotto['Data']==fd].iloc[0]
    
    # Ottieni i numeri per la tecnica
    bari_cols = [c for c in df_lotto.columns if c.startswith('Bari') and c != 'Bari']
    cagliari_cols = [c for c in df_lotto.columns if c.startswith('Cagliari') and c != 'Cagliari']
    
    # Debug
    if debug_mode:
        st.write(f"Mese: {per.strftime('%Y-%m')}")
        st.write(f"Prima estrazione: {fd.date().strftime('%d/%m/%Y')}")
        st.write(f"Colonne Bari: {bari_cols}")
        st.write(f"Colonne Cagliari: {cagliari_cols}")
    
    # Prendi il terzo numero di Bari e Cagliari (indice 2)
    tb = int(row0[bari_cols[2]])
    tc = int(row0[cagliari_cols[2]])
    
    # Calcola l'ambata
    _, _, amb = calcola_tecnica_lotto(tb, tc)
    
    if debug_mode:
        st.write(f"3° Bari: {tb}, 3° Cagliari: {tc}, Ambata: {amb}")
    
    # Estrazioni successive alla prima del mese
    sub = df_lotto[(df_lotto['period']==per)&(df_lotto['Data']>fd)]
    
    def occ(nums):
        """Cerca i numeri specificati nelle estrazioni delle ruote specificate."""
        occorrenze = []
        numeri_trovati = {}  # Per debug
        
        for _, row in sub.iterrows():
            data_str = row['Data'].date().strftime('%d/%m/%Y')
            
            # Debug speciale per il 17/01/2025
            special_debug = data_str == '17/01/2025' and debug_mode
            if special_debug:
                st.write(f"Analisi estrazione del {data_str}:")
                st.write(f"Numeri cercati: {nums}")
            
            for wheel in ruote_da_evidenziare:
                # Ottieni i numeri estratti per questa ruota in questa estrazione
                extracted = get_extracted_numbers(row, wheel)
                
                if special_debug:
                    st.write(f"Ruota {wheel}: {extracted}")
                
                # Verifica se tutti i numeri cercati sono presenti
                found = all(num in extracted for num in nums)
                if found:
                    occorrenza = f"{wheel} {data_str}"
                    occorrenze.append(occorrenza)
                    
                    # Memorizza per debug
                    if occorrenza not in numeri_trovati:
                        numeri_trovati[occorrenza] = extracted
                
                if special_debug:
                    st.write(f"Trovati tutti i numeri? {found}")
        
        # Debug dei numeri trovati
        if debug_mode and nums == [amb, tb] or nums == [amb, tc]:
            st.write(f"Ambetti {nums} trovati in: {occorrenze}")
            for occ, nums_found in numeri_trovati.items():
                st.write(f"  {occ}: {nums_found}")
        
        return sorted(set(occorrenze)) or ['-']
    
    # Trova le occorrenze
    ambi = occ([tb, tc])
    ambetti_tb = occ([amb, tb])
    ambetti_tc = occ([amb, tc])
    terni = occ([amb, tb, tc])
    
    records.append({
        'Mese': per.strftime('%Y-%m'),
        'Ambi': '; '.join(ambi),
        'Ambetti': '; '.join(ambetti_tb + ambetti_tc),
        'Terni': '; '.join(terni)
    })

stats = pd.DataFrame(records)
st.dataframe(stats.fillna('-'), use_container_width=True)
csv = stats.to_csv(index=False).encode('utf-8')
st.download_button('📥 Scarica Statistiche CSV', csv, 'statistiche.csv', 'text/csv')

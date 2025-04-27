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

for per,fd in firsts.items():
    row0 = df_lotto[df_lotto['Data']==fd].iloc[0]
    tb = int(row0[[c for c in df_lotto.columns if c.startswith('Bari')][2]])
    tc = int(row0[[c for c in df_lotto.columns if c.startswith('Cagliari')][2]])
    # CORREZIONE: prendere l'ambata dal calcolo
    _, _, amb = calcola_tecnica_lotto(tb, tc)
    
    # Estrazioni successive alla prima del mese
    sub = df_lotto[(df_lotto['period']==per)&(df_lotto['Data']>fd)]
    
    def occ(nums):
        """Cerca i numeri specificati nelle estrazioni delle ruote specificate."""
        occurrenze = []
        
        for _, row in sub.iterrows():
            data_str = row['Data'].date().strftime('%d/%m/%Y')
            
            for wheel in ruote_da_evidenziare:
                # Ottieni le colonne numeriche per questa ruota
                wheel_cols = []
                for col in df_lotto.columns:
                    if col.startswith(wheel) and col != wheel:
                        wheel_cols.append(col)
                
                if wheel_cols:
                    # Estrai i numeri per questa ruota dall'estrazione corrente
                    extracted_numbers = []
                    for col in wheel_cols[:5]:  # Solo i primi 5 numeri
                        try:
                            val = row[col]
                            if pd.notna(val):
                                extracted_numbers.append(int(val))
                        except (ValueError, TypeError):
                            pass
                    
                    # Verifica se tutti i numeri cercati sono presenti
                    if all(num in extracted_numbers for num in nums):
                        occurrenze.append(f"{wheel} {data_str}")
        
        return sorted(set(occurrenze)) or ['-']
    
    records.append({
        'Mese': per.strftime('%Y-%m'),
        'Ambi': '; '.join(occ([tb, tc])),
        'Ambetti': '; '.join(occ([amb, tb]) + occ([amb, tc])),
        'Terni': '; '.join(occ([amb, tb, tc]))
    })

stats = pd.DataFrame(records)
st.dataframe(stats.fillna('-'), use_container_width=True)
csv = stats.to_csv(index=False).encode('utf-8')
st.download_button('📥 Scarica Statistiche CSV', csv, 'statistiche.csv', 'text/csv')

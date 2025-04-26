import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
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
        file_content = io.BytesIO(uploaded_file_content)
        df = pd.read_csv(file_content, skiprows=3)
        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
        df = df.dropna(subset=["Data"])
        # Colonne estratti
        return df.sort_values("Data").reset_index(drop=True)
    except Exception as e:
        st.error(f"Errore durante la lettura del CSV: {e}")
        return pd.DataFrame()

def highlight_numbers(df):
    style_df = pd.DataFrame('', index=df.index, columns=df.columns)
    style_main = 'background-color: #FF4B4B; color: white; font-weight: bold;'
    style_adj = 'background-color: #90EE90; color: black; font-weight: bold;'
    global numeri_da_evidenziare, numeri_adiacenti, ruote_da_evidenziare
    for idx, _ in df.iterrows():
        wheel = idx
        for col in df.columns:
            val = df.at[idx, col]
            if pd.notna(val) and isinstance(val, (int, float, np.number)):
                num = int(val)
                if num in numeri_da_evidenziare and wheel in ruote_da_evidenziare:
                    style_df.at[idx, col] = style_main
                elif num in numeri_adiacenti and wheel in ruote_da_evidenziare:
                    style_df.at[idx, col] = style_adj
    return style_df

# --- Configurazione Pagina ---
st.set_page_config(layout="wide")
st.title("📊 Analisi Lotto: Tecnica, Estrazioni e Statistiche Mensili")

# Variabili globali per evidenziazione
numeri_da_evidenziare = set()
numeri_adiacenti = set()
ruote_da_evidenziare = ["Bari", "Cagliari", "Nazionale"]

# Upload
uploaded_file = st.file_uploader("Carica CSV estrazioni (es: 24e25.csv)", type="csv")

if uploaded_file:
    df_lotto = load_data(uploaded_file.getvalue())
    if df_lotto.empty:
        st.warning("Nessun dato valido nel file CSV.")
    else:
        # Prepara date e prime estrazioni
        df_lotto['day'] = df_lotto['Data'].dt.day
        df_lotto['period'] = df_lotto['Data'].dt.to_period('M')
        first_per_month = df_lotto[df_lotto['day'] <= 7].groupby('period')['Data'].min()

        # Costruisci tabella mensile
        records = []
        bari_cols = [c for c in df_lotto.columns if c.startswith('Bari')][:5]
        cagliari_cols = [c for c in df_lotto.columns if c.startswith('Cagliari')][:5]
        for period, first_date in first_per_month.items():
            row0 = df_lotto[df_lotto['Data'] == first_date].iloc[0]
            tb = int(row0[bari_cols[2]])
            tc = int(row0[cagliari_cols[2]])
            _, _, amb = calcola_tecnica_lotto(tb, tc)
            # Filtra estrazioni nello stesso mese dopo la prima
            sub_df = df_lotto[(df_lotto['period'] == period) & (df_lotto['Data'] > first_date)]
            def find_occ(nums):
                occs = []
                for _, r in sub_df.iterrows():
                    for wheel in ruote_da_evidenziare:
                        cols = [c for c in df_lotto.columns if c.startswith(wheel)][:5]
                        vals = [r[c] for c in cols]
                        if all(n in vals for n in nums):
                            occs.append(f"{wheel} {r['Data'].date().strftime('%d/%m/%Y')}")
                return sorted(set(occs)) or ['-']
            ambi = '; '.join(find_occ([tb, tc]))
            ambetti = '; '.join(find_occ([amb, tb]) + find_occ([amb, tc]))
            terni = '; '.join(find_occ([amb, tb, tc]))
            records.append({
                'Data 1ª Estrazione Mese': first_date.strftime('%d/%m/%Y'),
                '3 Numeri': f"{tb}, {tc}, {amb}",
                'Ambi': ambi,
                'Ambetti': ambetti,
                'Terni': terni
            })
        df_stats = pd.DataFrame(records)

        # Layout colonne
        col1, col2 = st.columns(2)

        # Colonna 1: Tecnica
        with col1:
            st.markdown("### 🔮 Tecnica Lotto (Bari/Cagliari)")
            dates = sorted(df_lotto['Data'].dt.date.unique(), reverse=True)
            first_week = [d for d in dates if d.day <= 7]
            sel = st.selectbox("Data tecnica:", options=first_week, format_func=lambda d: d.strftime('%d/%m/%Y'))
            if sel:
                row = df_lotto[df_lotto['Data'].dt.date == sel].iloc[0]
                tb = int(row[bari_cols[2]])
                tc = int(row[cagliari_cols[2]])
                dec_b, dec_c, amb = calcola_tecnica_lotto(tb, tc)
                numeri_da_evidenziare.clear(); numeri_adiacenti.clear()
                numeri_da_evidenziare.update([tb, tc, amb])
                for n in numeri_da_evidenziare:
                    numeri_adiacenti.update([(n-1) if n>1 else 90, (n+1) if n<90 else 1])
                st.markdown("---")
                st.metric("3° Bari", tb); st.metric("3° Cagliari", tc)
                st.metric("🔥 Ambata", amb)
                st.success(f"Ambo Secco: {tb}–{tc}")
                st.success(f"Terno Secco: {amb}–{tb}–{tc}")
                st.markdown("---")
                st.markdown("#### Legenda Colori nella Tabella:")
                st.markdown(f"🔴 Principali: {', '.join(map(str,sorted(numeri_da_evidenziare)))}")
                st.markdown(f"🟢 Adiacenti: {', '.join(map(str,sorted(numeri_adiacenti)))}")

        # Colonna 2: Estrazioni complete
        with col2:
            st.markdown("### 📅 Visualizzatore Estrazioni Complete")
            all_dates = sorted(df_lotto['Data'].dt.date.unique(), reverse=True)
            idx = st.session_state.get('idx_ext', 0)
            sel_ext = st.selectbox("Data estrazione:", options=all_dates, index=idx,
                                   format_func=lambda d: d.strftime('%d/%m/%Y'),
                                   key='sel_ext',
                                   on_change=lambda: st.session_state.update(idx_ext=all_dates.index(st.session_state.sel_ext)))
            date_vis = st.session_state.sel_ext
            df_vis = df_lotto[df_lotto['Data'].dt.date == date_vis]
            if not df_vis.empty:
                r = df_vis.iloc[0]
                data = {}
                ruote = ["Bari","Cagliari","Firenze","Genova","Milano","Napoli","Palermo","Roma","Torino","Venezia","Nazionale"]
                for wheel in ruote:
                    cols = [c for c in df_lotto.columns if c.startswith(wheel)][:5]
                    nums = [int(r[c]) if pd.notna(r[c]) else None for c in cols]
                    data[wheel] = nums
                df_tab = pd.DataFrame(data, index=["1°","2°","3°","4°","5°"]).transpose()
                df_int = df_tab.copy()
                styled = df_int.style.apply(highlight_numbers, axis=None).format(na_rep='-')
                st.dataframe(styled, use_container_width=True)

        # Tabella mensile e download
        st.markdown("---")
        st.markdown("### 📊 Tabella Ambi/Ambetti/Terni Mensili")
        st.dataframe(df_stats.fillna('-'), use_container_width=True)
        csv = df_stats.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Tabella Mensile CSV", data=csv, file_name='tabella_mensile.csv', mime='text/csv')
else:
    st.info("Carica un file CSV per iniziare l'analisi.")

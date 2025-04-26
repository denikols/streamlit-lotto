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

        bari_cols = [col for col in df.columns if col.startswith('Bari')]
        cagliari_cols = [col for col in df.columns if col.startswith('Cagliari')]
        if len(bari_cols) < 3 or len(cagliari_cols) < 3:
            raise ValueError("Non sono state trovate sufficienti colonne per Bari e Cagliari")
        col_bari_3 = bari_cols[2]
        col_cagliari_3 = cagliari_cols[2]
        df['terzo_bari'] = pd.to_numeric(df[col_bari_3], errors='coerce')
        df['terzo_cagliari'] = pd.to_numeric(df[col_cagliari_3], errors='coerce')
        df = df.sort_values("Data", ascending=True).reset_index(drop=True)
        return df

    except Exception as e:
        st.error(f"Errore durante l'elaborazione del file CSV: {type(e).__name__}: {e}")
        return pd.DataFrame()

def highlight_numbers(df):
    """Evidenzia numeri principali (rosso) e adiacenti (verde) nelle ruote specificate."""
    style_df = pd.DataFrame('', index=df.index, columns=df.columns)
    style_principale = 'background-color: #FF4B4B; color: white; font-weight: bold;'
    style_adiacente = 'background-color: #90EE90; color: black; font-weight: bold;'
    global numeri_da_evidenziare, numeri_adiacenti, ruote_da_evidenziare

    for idx, row in df.iterrows():
        nome_ruota = idx
        for col in df.columns:
            val = df.at[idx, col]
            if pd.notna(val) and isinstance(val, (int, float, np.number)):
                num_val = int(val)
                if num_val in numeri_da_evidenziare and nome_ruota in ruote_da_evidenziare:
                    style_df.at[idx, col] = style_principale
                elif num_val in numeri_adiacenti and nome_ruota in ruote_da_evidenziare:
                    style_df.at[idx, col] = style_adiacente
    return style_df

# --- Configurazione Pagina ---
st.set_page_config(layout="wide")
st.title("📊 Analisi Lotto: Tecnica & Statistiche Mensili")

numeri_da_evidenziare = set()
numeri_adiacenti = set()
ruote_da_evidenziare = ["Bari", "Cagliari", "Nazionale"]

uploaded_file = st.file_uploader("Carica il file CSV delle estrazioni (es: 24e25.csv)", type="csv")

if uploaded_file:
    uploaded_file_content = uploaded_file.getvalue()
    df_lotto = load_data(uploaded_file_content)

    if not df_lotto.empty:
        # Date uniche e primi del mese
        date_list = sorted(df_lotto["Data"].dt.date.unique())
        date_list_desc = list(reversed(date_list))

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔮 Tecnica Lotto (Bari/Cagliari)")
            data_prima_settimana = [d for d in date_list_desc if d.day <= 7]
            data_scelta = st.selectbox(
                "Seleziona data (prima estrazione di ogni mese):",
                options=data_prima_settimana,
                format_func=lambda d: d.strftime('%d/%m/%Y'),
                key="select_tecnica"
            )
            if data_scelta:
                riga = df_lotto[df_lotto["Data"].dt.date == data_scelta].iloc[0]
                tb = int(riga['terzo_bari'])
                tc = int(riga['terzo_cagliari'])
                dec_b, dec_c, ambata = calcola_tecnica_lotto(tb, tc)

                numeri_da_evidenziare.clear()
                numeri_adiacenti.clear()
                numeri_da_evidenziare.update([ambata, tb, tc])
                for num in numeri_da_evidenziare:
                    prev_num = 90 if num == 1 else num - 1
                    next_num = 1 if num == 90 else num + 1
                    numeri_adiacenti.update([prev_num, next_num])

                st.markdown("---")
                st.markdown("#### Numeri di Riferimento (Tecnica)")
                st.metric(label="3° Bari", value=tb)
                st.metric(label="3° Cagliari", value=tc)
                st.markdown("#### 🔥 AMBATA Calcolata")
                st.metric(label="Ambata", value=ambata)
                st.success(f"**Ambo Secco:** {tb} – {tc}")
                st.success(f"**Terno Secco:** {ambata} – {tb} – {tc}")

                st.markdown("---")
                st.markdown("##### Legenda Colori nella Tabella:")
                st.markdown(f"🔴 **Rosso:** Numeri principali ({', '.join(map(str, sorted(numeri_da_evidenziare)))})")
                st.markdown(f"🟢 **Verde:** Numeri adiacenti ({', '.join(map(str, sorted(numeri_adiacenti)))})")
                st.info("**Ruote consigliate:** Bari, Cagliari, Nazionale. *(Valutare anche tutte)*")

                # --- Tabella Ambi/Ambetti/Terni Mensili ---
                df_temp = df_lotto.copy()
                primi = df_temp[df_temp['Data'].dt.day <= 7]
                primi['year_month'] = primi['Data'].dt.to_period('M')
                firsts = primi.groupby('year_month')['Data'].min().dt.date

                records = []
                for dat in firsts:
                    r0 = df_lotto[df_lotto['Data'].dt.date == dat].iloc[0]
                    tb0 = int(r0['terzo_bari']); tc0 = int(r0['terzo_cagliari'])
                    dec_b0, dec_c0, amb0 = calcola_tecnica_lotto(tb0, tc0)
                    df_p = df_lotto[df_lotto['Data'].dt.date >= dat]

                    def cerca_occ(combo):
                        occ = []
                        for ruota in ruote_da_evidenziare:
                            cols = [c for c in df_p.columns if c.startswith(ruota)][:5]
                            for _, rowp in df_p.iterrows():
                                vals = [rowp[c] for c in cols]
                                if all(x in vals for x in combo):
                                    occ.append(f"{ruota} {rowp['Data'].date().strftime('%d/%m/%Y')}")
                        return occ or ["-"]                    

                    ambi_list = cerca_occ([tb0, tc0])
                    ambetti_list = cerca_occ([amb0, tb0]) + cerca_occ([amb0, tc0])
                    terna_list = cerca_occ([amb0, tb0, tc0])

                    records.append({
                        'Data 1ª Estrazione Mese': dat.strftime('%d/%m/%Y'),
                        '3 Numeri': f"{tb0}, {tc0}, {amb0}",
                        'Ambi': '; '.join(ambi_list),
                        'Ambetti': '; '.join(ambetti_list),
                        'Terni': '; '.join(terna_list)
                    })

                df_stats = pd.DataFrame(records)
                st.markdown("### 📊 Tabella Ambi/Ambetti/Terni Mensili")
                st.dataframe(df_stats.fillna('-'), use_container_width=True)

        with col2:
            st.markdown("### 📅 Visualizzatore Estrazioni Complete")
            data_sel = st.selectbox(
                "Data estrazione:", options=date_list_desc,
                format_func=lambda d: d.strftime('%d/%m/%Y'), key='sel_ext'
            )
            # (Logica di visualizzazione estrazioni come da versione originale)

    else:
        st.warning("Il file caricato non contiene dati validi.")
else:
    st.info("Carica un file CSV per iniziare l'analisi.")



import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="Le Mie Ricette", layout="wide")

# Funzione per caricare o creare il database delle ricette
def load_or_create_data():
    if os.path.exists("ricette.json"):
        with open("ricette.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # Inizializza sempre la chiave "ricette" come lista vuota
        data = {"ricette": []}
    return data

# Funzione per salvare il database delle ricette
def save_data(data):
    with open("ricette.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Carica i dati all'avvio dell'app
data = load_or_create_data()

# Inizializza le variabili di stato
if 'mostra_form_ricetta' not in st.session_state:
    st.session_state.mostra_form_ricetta = False
if 'modo_modifica' not in st.session_state:
    st.session_state.modo_modifica = False
if 'ricetta_da_modificare' not in st.session_state:
    st.session_state.ricetta_da_modificare = None

# Funzioni di utilità per gestire lo stato
def reset_form_state():
    st.session_state.mostra_form_ricetta = False
    st.session_state.modo_modifica = False
    st.session_state.ricetta_da_modificare = None

# Callback per mostrare il form di nuova ricetta
def mostra_form_nuova_ricetta():
    st.session_state.mostra_form_ricetta = True
    st.session_state.modo_modifica = False
    st.session_state.ricetta_da_modificare = None

# Callback per modificare una ricetta
def modifica_ricetta(ricetta_id):
    st.session_state.mostra_form_ricetta = True
    st.session_state.modo_modifica = True
    st.session_state.ricetta_da_modificare = ricetta_id

# Callback per eliminare una ricetta
def elimina_ricetta(ricetta_id):
    data['ricette'] = [r for r in data['ricette'] if r['id'] != ricetta_id]
    save_data(data)
    reset_form_state()
    st.experimental_rerun()

# Titolo dell'app
st.title("Le Mie Ricette")

# Sidebar per il menu
with st.sidebar:
    st.header("Menu")
    st.button("Nuova Ricetta", on_click=mostra_form_nuova_ricetta)

# Form per creazione o modifica
if st.session_state.mostra_form_ricetta:
    with st.form(key="form_ricetta"):
        if st.session_state.modo_modifica:
            ric_id = st.session_state.ricetta_da_modificare
            ric = next((r for r in data['ricette'] if r['id'] == ric_id), {})
            nome = st.text_input("Nome ricetta", ric.get('nome', ''))
            ingredienti = st.text_area("Ingredienti (separati da virgola)", ', '.join(ric.get('ingredienti', [])))
            procedura = st.text_area("Procedura", ric.get('procedura', ''))
        else:
            nome = st.text_input("Nome ricetta", '')
            ingredienti = st.text_area("Ingredienti (separati da virgola)", '')
            procedura = st.text_area("Procedura", '')
        submitted = st.form_submit_button("Salva ricetta")
        if submitted:
            ing_list = [i.strip() for i in ingredienti.split(',') if i.strip()]
            if st.session_state.modo_modifica:
                for r in data['ricette']:
                    if r['id'] == ric_id:
                        r['nome'] = nome
                        r['ingredienti'] = ing_list
                        r['procedura'] = procedura
                        r['modificato'] = datetime.now().isoformat()
            else:
                new_id = max([r['id'] for r in data['ricette']], default=0) + 1
                data['ricette'].append({
                    'id': new_id,
                    'nome': nome,
                    'ingredienti': ing_list,
                    'procedura': procedura,
                    'creato': datetime.now().isoformat()
                })
            save_data(data)
            reset_form_state()
            st.success("Ricetta salvata!")
            st.experimental_rerun()

# Visualizzazione elenco ricette
if not st.session_state.mostra_form_ricetta:
    st.subheader("Elenco delle ricette")
    if data['ricette']:
        for r in data['ricette']:
            st.markdown(f"### {r['nome']}")
            st.write("**Ingredienti:**", ', '.join(r['ingredienti']))
            st.write("**Procedura:**", r['procedura'])
            col1, col2 = st.columns(2)
            col1.button("Modifica", key=f"mod_{r['id']}", on_click=modifica_ricetta, args=(r['id'],))
            col2.button("Elimina", key=f"del_{r['id']}", on_click=elimina_ricetta, args=(r['id'],))
    else:
        st.info("Non ci sono ancora ricette. Aggiungine una nuova dal menu a sinistra!")

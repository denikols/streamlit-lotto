
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

# Funzioni per gestire gli eventi
def visualizza_ricetta(ricetta_id):
    st.session_state.ricetta_selezionata = ricetta_id
    st.session_state.mostra_form_ricetta = False
    st.session_state.modo_modifica = False

def mostra_form_nuova_ricetta():
    st.session_state.mostra_form_ricetta = True
    st.session_state.ricetta_selezionata = None
    st.session_state.modo_modifica = False

def modifica_ricetta(ricetta_id):
    st.session_state.ricetta_da_modificare = ricetta_id
    st.session_state.mostra_form_ricetta = True
    st.session_state.modo_modifica = True

def elimina_ricetta(ricetta_id):
    data["ricette"] = [r for r in data["ricette"] if r["id"] != ricetta_id]
    save_data(data)
    st.session_state.ricetta_selezionata = None

# TODO: Inserisci qui il resto del codice (CSS, layout, visualizzazione e gestione delle ricette)

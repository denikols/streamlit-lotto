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
        # Dati iniziali
        data = {
            "categorie": [
                {"id": 1, "nome": "Primi Piatti"},
                {"id": 2, "nome": "Secondi Piatti"},
                {"id": 3, "nome": "Contorni"},
                {"id": 4, "nome": "Dolci"},
                {"id": 5, "nome": "Conserve"}
            ],
            "ricette": [
                {
                    "id": 1,
                    "titolo": "Carne Salada",
                    "categoria_id": 2,
                    "ingredienti": [
                        "600g sottofesa di manzo",
                        "25g sale grosso marino",
                        "5g sale fino",
                        "3g pepe nero macinato",
                        "2 bacche di ginepro",
                        "1 spicchio d'aglio",
                        "2 foglie di alloro",
                        "1 rametto di rosmarino",
                        "1 cucchiaino di zucchero di canna"
                    ],
                    "procedimento": "Pulire la sottofesa rimuovendo il grasso in eccesso. Mescolare tutti i sali e le spezie. Massaggiare bene la carne con il mix. Inserire in un sacchetto sottovuoto con tutti gli aromi. Sigillare e refrigerare per 5 giorni, girando ogni giorno. Risciacquare e asciugare prima di servire.",
                    "tempo_preparazione": "20 minuti",
                    "tempo_cottura": "5 giorni",
                    "difficolta": "Media",
                    "data_creazione": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        }
    return data

# Funzione per salvare i dati
def save_data(data):
    with open("ricette.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Inizializzazione dello stato della sessione
if 'ricetta_selezionata' not in st.session_state:
    st.session_state.ricetta_selezionata = None
if 'mostra_form_ricetta' not in st.session_state:
    st.session_state.mostra_form_ricetta = False
if 'modo_modifica' not in st.session_state:
    st.session_state.modo_modifica = False
if 'ricetta_da_modificare' not in st.session_state:
    st.session_state.ricetta_da_modificare = None
# Inizializza la categoria selezionata
if 'categoria_selezionata' not in st.session_state:
    st.session_state.categoria_selezionata = None

# Carica dati
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
    st.experimental_rerun()

# Stile CSS personalizzato
st.markdown("""
<style>
    .recipe-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: white;
    }
    .recipe-card:hover {
        background-color: #f0f0f0;
        cursor: pointer;
    }
    .recipe-selected {
        background-color: #e6f3ff;
        border-left: 4px solid #1e90ff;
    }
    .ingredient-list li {
        margin-bottom: 5px;
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .btn-add {
        background-color: #4CAF50;
        color: white;
        border-radius: 4px;
        padding: 10px 15px;
        border: none;
    }
    .btn-edit {
        background-color: #FFA500;
        color: white;
        border-radius: 4px;
        padding: 5px 10px;
        border: none;
        margin-right: 5px;
    }
    .btn-delete {
        background-color: #FF5733;
        color: white;
        border-radius: 4px;
        padding: 5px 10px;
        border: none;
    }
    .difficulty-easy {
        color: green;
        font-weight: bold;
    }
    .difficulty-medium {
        color: orange;
        font-weight: bold;
    }
    .difficulty-hard {
        color: red;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Titolo
st.markdown("<div class='header-container'><h1>Le Mie Ricette</h1></div>", unsafe_allow_html=True)

# Layout principale con colonna
col_sidebar, col_ricette, col_dettaglio = st.columns([1, 1, 2])

# Colonna sidebar: Categorie
with col_sidebar:
    st.markdown("## Categorie")
    
    # Form per aggiungere categoria
    with st.expander("Aggiungi categoria", expanded=False):
        nuova_categoria = st.text_input("Nome categoria", key="input_nuova_categoria")
        if st.button("Aggiungi", key="btn_add_cat"):
            if nuova_categoria:
                nuovo_id = max([c["id"] for c in data["categorie"]]) + 1 if data["categorie"] else 1
                data["categorie"].append({"id": nuovo_id, "nome": nuova_categoria})
                save_data(data)
                st.success(f"Categoria '{nuova_categoria}' aggiunta!")
                st.experimental_rerun()
    
    # Opzione per visualizzare tutte le ricette
    if st.button("Tutte le ricette", key="btn_all_recipes", use_container_width=True):
        st.session_state.categoria_selezionata = None
        st.experimental_rerun()
    
    # Lista categorie
    for categoria in data["categorie"]:
        if st.button(categoria["nome"], key="cat_{0}".format(categoria["id"]), use_container_width=True):
            st.session_state.categoria_selezionata = categoria["id"]
            st.experimental_rerun()

# Colonna ricette: Lista ricette
with col_ricette:
    st.markdown("<div class='header-container'><h2>Ricette</h2><button class='btn-add' onclick="document.getElementById('hidden_submit').click()">+ Nuova</button></div>", unsafe_allow_html=True)
    with st.form(key="hidden_form", clear_on_submit=False):
        hidden_submit = st.form_submit_button("Hidden", key="hidden_submit", on_click=mostra_form_nuova_ricetta)
    
    ricette = data["ricette"]
    if st.session_state.categoria_selezionata is not None:
        ricette = [r for r in ricette if r["categoria_id"] == st.session_state.categoria_selezionata]
    if not ricette:
        st.info("Nessuna ricetta trovata in questa categoria")
    
    for ricetta in ricette:
        categoria_nome = next((c["nome"] for c in data["categorie"] if c["id"] == ricetta["categoria_id"]), "")
        is_selected = st.session_state.ricetta_selezionata == ricetta["id"]
        recipe_class = "recipe-card recipe-selected" if is_selected else "recipe-card"
        st.markdown(f"<div class='{recipe_class}' onclick="document.getElementById('btn_{ricetta['id']}').click()"><h3>{ricetta['titolo']}</h3><p style='color: gray; font-size: 0.8em;'>{categoria_nome}</p></div>", unsafe_allow_html=True)
        if st.button("Visualizza", key="btn_{0}".format(ricetta['id']), on_click=lambda rid=ricetta['id']: visualizza_ricetta(rid)):
            pass

# Colonna dettaglio: Dettagli ricetta o form
with col_dettaglio:
    # (resto identico a quanto già fornito)
    pass

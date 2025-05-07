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

# Layout principale con colonne
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
        if st.button(categoria["nome"], key=f"cat_{categoria['id']}", use_container_width=True):
            st.session_state.categoria_selezionata = categoria["id"]
            st.experimental_rerun()

# Colonna ricette: Lista ricette
with col_ricette:
    st.markdown("<div class='header-container'><h2>Ricette</h2><button class='btn-add' id='btn-add-recipe' onclick='document.querySelector(\"[data-testid=stFormSubmitButton]\").click()'>+ Nuova</button></div>", unsafe_allow_html=True)
    
    # Form nascosto per attivare il bottone personalizzato
    with st.form(key="hidden_form", clear_on_submit=False):
        submit = st.form_submit_button("Hidden Submit", on_click=mostra_form_nuova_ricetta)
    
    # Filtra ricette in base alla categoria selezionata
    ricette = data["ricette"]
    if hasattr(st.session_state, 'categoria_selezionata') and st.session_state.categoria_selezionata is not None:
        ricette = [r for r in ricette if r["categoria_id"] == st.session_state.categoria_selezionata]
    
    # Se non ci sono ricette
    if not ricette:
        st.info("Nessuna ricetta trovata in questa categoria")
    
    # Mostra lista ricette
    for ricetta in ricette:
        categoria_nome = next((c["nome"] for c in data["categorie"] if c["id"] == ricetta["categoria_id"]), "")
        
        # Determina se la ricetta è selezionata
        is_selected = st.session_state.ricetta_selezionata == ricetta["id"]
        recipe_class = "recipe-card recipe-selected" if is_selected else "recipe-card"
        
        st.markdown(f"""
        <div class='{recipe_class}' id='recipe_{ricetta["id"]}' onclick='
            document.getElementById("btn_{ricetta["id"]}").click();
        '>
            <h3>{ricetta["titolo"]}</h3>
            <p style='color: gray; font-size: 0.8em;'>{categoria_nome}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Bottone nascosto per gestire il click sulla scheda
        if st.button(f"Visualizza", key=f"btn_{ricetta['id']}", on_click=lambda rid=ricetta["id"]: visualizza_ricetta(rid), help="Visualizza dettagli ricetta"):
            pass

# Colonna dettaglio: Dettagli ricetta o form
with col_dettaglio:
    # Form per aggiungere o modificare ricetta
    if st.session_state.mostra_form_ricetta:
        if st.session_state.modo_modifica:
            ricetta_da_modificare = next((r for r in data["ricette"] if r["id"] == st.session_state.ricetta_da_modificare), None)
            st.markdown("## Modifica Ricetta")
            titolo_default = ricetta_da_modificare["titolo"]
            categoria_default = ricetta_da_modificare["categoria_id"]
            ingredienti_default = "\n".join(ricetta_da_modificare["ingredienti"])
            procedimento_default = ricetta_da_modificare["procedimento"]
            tempo_prep_default = ricetta_da_modificare.get("tempo_preparazione", "")
            tempo_cottura_default = ricetta_da_modificare.get("tempo_cottura", "")
            difficolta_default = ricetta_da_modificare.get("difficolta", "")
        else:
            st.markdown("## Nuova Ricetta")
            titolo_default = ""
            categoria_default = list(data["categorie"])[0]["id"] if data["categorie"] else None
            ingredienti_default = ""
            procedimento_default = ""
            tempo_prep_default = ""
            tempo_cottura_default = ""
            difficolta_default = ""
        
        # Form di inserimento
        with st.form(key="form_ricetta"):
            titolo = st.text_input("Titolo", value=titolo_default)
            
            # Scelta categoria
            opzioni_categorie = {c["id"]: c["nome"] for c in data["categorie"]}
            categoria_id = st.selectbox(
                "Categoria",
                options=list(opzioni_categorie.keys()),
                format_func=lambda x: opzioni_categorie[x],
                index=list(opzioni_categorie.keys()).index(categoria_default) if categoria_default in opzioni_categorie else 0
            )
            
            ingredienti = st.text_area("Ingredienti (uno per riga)", value=ingredienti_default, height=150)
            procedimento = st.text_area("Procedimento", value=procedimento_default, height=200)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                tempo_prep = st.text_input("Tempo di preparazione", value=tempo_prep_default, placeholder="es. 30 minuti")
            with col2:
                tempo_cottura = st.text_input("Tempo di cottura", value=tempo_cottura_default, placeholder="es. 1 ora")
            with col3:
                difficolta = st.selectbox(
                    "Difficoltà", 
                    ["Facile", "Media", "Difficile"],
                    index=["Facile", "Media", "Difficile"].index(difficolta_default) if difficolta_default in ["Facile", "Media", "Difficile"] else 0
                )
            
            # Pulsanti di salvataggio/annullamento
            col_save, col_cancel = st.columns(2)
            with col_save:
                invia = st.form_submit_button("Salva Ricetta")
            with col_cancel:
                if st.form_submit_button("Annulla"):
                    st.session_state.mostra_form_ricetta = False
                    st.session_state.modo_modifica = False
                    st.experimental_rerun()
            
            # Elaborazione del salvataggio
            if invia:
                if titolo and categoria_id and ingredienti:
                    if st.session_state.modo_modifica:
                        # Aggiorna la ricetta esistente
                        for i, r in enumerate(data["ricette"]):
                            if r["id"] == st.session_state.ricetta_da_modificare:
                                data["ricette"][i].update({
                                    "titolo": titolo,
                                    "categoria_id": categoria_id,
                                    "ingredienti": [ing.strip() for ing in ingredienti.split("\n") if ing.strip()],
                                    "procedimento": procedimento,
                                    "tempo_preparazione": tempo_prep,
                                    "tempo_cottura": tempo_cottura,
                                    "difficolta": difficolta,
                                    "data_modifica": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                break
                        st.session_state.ricetta_selezionata = st.session_state.ricetta_da_modificare
                    else:
                        # Crea una nuova ricetta
                        nuovo_id = max([r["id"] for r in data["ricette"]]) + 1 if data["ricette"] else 1
                        nuova_ricetta = {
                            "id": nuovo_id,
                            "titolo": titolo,
                            "categoria_id": categoria_id,
                            "ingredienti": [ing.strip() for ing in ingredienti.split("\n") if ing.strip()],
                            "procedimento": procedimento,
                            "tempo_preparazione": tempo_prep,
                            "tempo_cottura": tempo_cottura,
                            "difficolta": difficolta,
                            "data_creazione": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        data["ricette"].append(nuova_ricetta)
                        st.session_state.ricetta_selezionata = nuovo_id
                    
                    save_data(data)
                    st.session_state.mostra_form_ricetta = False
                    st.session_state.modo_modifica = False
                    st.experimental_rerun()
                else:
                    st.error("Inserisci almeno titolo, categoria e ingredienti")
    
    # Visualizzazione dettaglio ricetta
    elif st.session_state.ricetta_selezionata is not None:
        ricetta = next((r for r in data["ricette"] if r["id"] == st.session_state.ricetta_selezionata), None)
        if ricetta:
            categoria_nome = next((c["nome"] for c in data["categorie"] if c["id"] == ricetta["categoria_id"]), "")
            
            # Pulsanti di modifica e eliminazione
            col_titolo, col_azioni = st.columns([3, 1])
            with col_titolo:
                st.markdown(f"## {ricetta['titolo']}")
                st.markdown(f"<p style='color: gray;'>{categoria_nome}</p>", unsafe_allow_html=True)
            
            with col_azioni:
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("✏️", key=f"edit_{ricetta['id']}", help="Modifica ricetta"):
                        modifica_ricetta(ricetta["id"])
                with col_delete:
                    if st.button("🗑️", key=f"delete_{ricetta['id']}", help="Elimina ricetta"):
                        if st.button(f"Conferma eliminazione di '{ricetta['titolo']}'?", key=f"confirm_delete_{ricetta['id']}"):
                            elimina_ricetta(ricetta["id"])
            
            st.markdown("---")
            
            # Informazioni ricetta
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.markdown(f"**Preparazione:** {ricetta.get('tempo_preparazione', 'N/D')}")
            with info_col2:
                st.markdown(f"**Cottura:** {ricetta.get('tempo_cottura', 'N/D')}")
            with info_col3:
                difficolta = ricetta.get('difficolta', 'N/D')
                difficolta_class = ""
                if difficolta == "Facile":
                    difficolta_class = "difficulty-easy"
                elif difficolta == "Media":
                    difficolta_class = "difficulty-medium"
                elif difficolta == "Difficile":
                    difficolta_class = "difficulty-hard"
                
                st.markdown(f"**Difficoltà:** <span class='{difficolta_class}'>{difficolta}</span>", unsafe_allow_html=True)
            
            st.markdown("### Ingredienti")
            st.markdown("<ul class='ingredient-list'>", unsafe_allow_html=True)
            for ingrediente in ricetta["ingredienti"]:
                st.markdown(f"<li>{ingrediente}</li>", unsafe_allow_html=True)
            st.markdown("</ul>", unsafe_allow_html=True)
            
            st.markdown("### Procedimento")
            st.markdown(f"<p style='white-space: pre-line;'>{ricetta['procedimento']}</p>", unsafe_allow_html=True)
            
            # Data creazione/modifica
            st.markdown("---")
            if "data_creazione" in ricetta:
                st.markdown(f"<p style='color: gray; font-size: 0.8em;'>Creata il: {ricetta['data_creazione']}</p>", unsafe_allow_html=True)
            if "data_modifica" in ricetta:
                st.markdown(f"<p style='color: gray; font-size: 0.8em;'>Ultima modifica: {ricetta['data_modifica']}</p>", unsafe_allow_html=True)
    else:
        # Messaggio quando nessuna ricetta è selezionata
        st.info("Seleziona una ricetta dalla lista o crea una nuova ricetta")
        
        # Immagine o suggerimento
        st.markdown("""
        ### Suggerimenti per l'uso
        - Usa il menu a sinistra per filtrare le ricette per categoria
        - Clicca sul pulsante '+ Nuova' per aggiungere una ricetta
        - Puoi aggiungere nuove categorie dall'apposito menu espandibile
        - Seleziona una ricetta per visualizzare i dettagli e modificarla
        """)

import streamlit as st
import os
import json
from datetime import datetime

# Configurazione pagina
st.set_page_config(page_title="Recipe App", layout="wide")

# Paths
DATA_FILE = "data.json"
UPLOAD_DIR = "uploads"

# Inizializza cartella upload
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Carica o crea dati
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        default = {"categories": [], "recipes": []}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=4)
        return default

# Salva dati
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Dati
data = load_data()

# Stato sessione
ss = st.session_state
if 'selected_cat' not in ss:
    ss.selected_cat = None
if 'selected_recipe' not in ss:
    ss.selected_recipe = None
if 'mode' not in ss:
    ss.mode = None  # 'add_cat','add_rec','edit_rec'

# Callback functions
def add_category():
    ss.mode = 'add_cat'

def delete_category(cat_id):
    data['categories'] = [c for c in data['categories'] if c['id'] != cat_id]
    data['recipes'] = [r for r in data['recipes'] if r['category_id'] != cat_id]
    save_data(data)
    ss.selected_cat = None
    ss.selected_recipe = None

def select_category(cat_id):
    ss.selected_cat = cat_id
    ss.selected_recipe = None
    ss.mode = None

def add_recipe():
    ss.mode = 'add_rec'
    ss.selected_recipe = None

def edit_recipe(recipe_id):
    ss.mode = 'edit_rec'
    ss.selected_recipe = recipe_id

def delete_recipe(rec_id):
    data['recipes'] = [r for r in data['recipes'] if r['id'] != rec_id]
    save_data(data)
    ss.selected_recipe = None

def select_recipe(recipe_id):
    ss.selected_recipe = recipe_id
    ss.mode = None

# Layout
sidebar, main = st.columns([1,3])

with sidebar:
    st.header("Categorie")
    for cat in data['categories']:
        col1, col2 = st.columns([4,1])
        col1.button(cat['name'], key=f"cat_{cat['id']}", on_click=select_category, args=(cat['id'],))
        col2.button("🗑", key=f"delcat_{cat['id']}", on_click=delete_category, args=(cat['id'],))
    st.button("+ Aggiungi Categoria", on_click=add_category)

with main:
    # Aggiungi categoria
    if ss.mode == 'add_cat':
        st.subheader("Aggiungi Categoria")
        with st.form("form_cat"):
            name = st.text_input("Nome Categoria")
            if st.form_submit_button("Salva"):
                if name:
                    new_id = max([c['id'] for c in data['categories']], default=0) + 1
                    data['categories'].append({"id": new_id, "name": name})
                    save_data(data)
                ss.mode = None

    # Elenco e gestione ricette
    elif ss.selected_cat:
        st.header("Ricette")
        st.button("+ Aggiungi Ricetta", on_click=add_recipe)
        recs = [r for r in data['recipes'] if r['category_id'] == ss.selected_cat]
        for rec in recs:
            col1, col2, col3 = st.columns([3,1,1])
            col1.button(rec['title'], key=f"rec_{rec['id']}", on_click=select_recipe, args=(rec['id'],))
            col2.button("✏️", key=f"edit_{rec['id']}", on_click=edit_recipe, args=(rec['id'],))
            col3.button("🗑", key=f"delrec_{rec['id']}", on_click=delete_recipe, args=(rec['id'],))

        # Visualizza form di aggiunta/modifica o dettagli
        if ss.mode in ['add_rec','edit_rec'] or ss.selected_recipe:
            rec = None
            if ss.mode == 'edit_rec':
                rec = next(r for r in data['recipes'] if r['id'] == ss.selected_recipe)
            if ss.mode in ['add_rec','edit_rec']:
                st.subheader("Recetta")
                with st.form("form_rec"):
                    title = st.text_input("Titolo", value=rec['title'] if rec else "")
                    ingredients = st.text_area("Ingredienti", value=rec['ingredients'] if rec else "")
                    procedure = st.text_area("Procedura", value=rec['procedure'] if rec else "")
                    # Mostra immagine corrente se esiste
                    if rec and rec.get('image'):
                        st.image(rec['image'], caption="Foto attuale", use_column_width=True)
                    img = st.file_uploader("Foto", type=["png","jpg"], accept_multiple_files=False)
                    if st.form_submit_button("Salva Ricetta"):
                        img_path = rec['image'] if rec and 'image' in rec else None
                        if img:
                            img_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{img.name}")
                            with open(img_path, "wb") as f:
                                f.write(img.getbuffer())
                        if rec:
                            rec.update({
                                'title': title,
                                'ingredients': ingredients,
                                'procedure': procedure,
                                'image': img_path,
                                'modified': datetime.now().isoformat()
                            })
                        else:
                            new_id = max([r['id'] for r in data['recipes']], default=0) + 1
                            data['recipes'].append({
                                'id': new_id,
                                'category_id': ss.selected_cat,
                                'title': title,
                                'ingredients': ingredients,
                                'procedure': procedure,
                                'image': img_path,
                                'created': datetime.now().isoformat()
                            })
                        save_data(data)
                        ss.mode = None
                        ss.selected_recipe = None
            else:
                # Visualizza dettagli ricetta selezionata
                rec = next(r for r in data['recipes'] if r['id'] == ss.selected_recipe)
                st.subheader(rec['title'])
                if rec.get('image'):
                    st.image(rec['image'], caption=rec['title'], use_column_width=True)
                st.write("**Ingredienti:**", rec['ingredients'])
                st.write("**Procedura:**", rec['procedure'])

    else:
        st.info("Seleziona o crea una categoria a sinistra per iniziare.")
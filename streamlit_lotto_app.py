# SISTEMA DI CALCOLO TECNICA DEL LOTTO
# Basato sulla prima estrazione di ogni mese
# -----------------------------------------------------
# ISTRUZIONI:
# 1. Modifica i valori sotto dove è indicato "INSERISCI I TUOI DATI QUI"
# 2. Esegui il programma
# 3. Leggi i risultati
# -----------------------------------------------------

# INSERISCI I TUOI DATI QUI
# -------------------------
# Data della prima estrazione del mese
giorno = 3       # Inserisci qui il giorno dell'estrazione
mese = 4         # Inserisci qui il mese (1-12)
anno = 2025      # Inserisci qui l'anno

# Numeri estratti
terzo_bari = 62      # Inserisci qui il terzo estratto della ruota di Bari
terzo_cagliari = 38  # Inserisci qui il terzo estratto della ruota di Cagliari
# -------------------------

# NON MODIFICARE IL CODICE SOTTO QUESTA RIGA
# ------------------------------------------

def calcola_tecnica_lotto():
    """
    Calcola la tecnica del Lotto basata sui terzi estratti della prima estrazione del mese.
    """
    # Controllo validità dei numeri
    if not (1 <= terzo_bari <= 90 and 1 <= terzo_cagliari <= 90):
        print("ERRORE: I numeri del lotto devono essere compresi tra 1 e 90.")
        return
        
    # Estrazione delle decine
    decina_bari = terzo_bari // 10
    decina_cagliari = terzo_cagliari // 10
    
    # Calcolo dell'ambata
    ambata = decina_bari + decina_cagliari
    
    # Se l'ambata è maggiore di 90 (il numero massimo del lotto), si sottrae 90
    if ambata > 90:
        ambata = ambata - 90
    
    # Mostra risultati
    print("\n" + "=" * 60)
    print(f"TECNICA DEL LOTTO - Prima estrazione del {giorno:02d}/{mese:02d}/{anno}")
    print("=" * 60)
    print(f"\nTerzo estratto Bari: {terzo_bari} (decina: {decina_bari})")
    print(f"Terzo estratto Cagliari: {terzo_cagliari} (decina: {decina_cagliari})")
    print(f"\nAmbata: {ambata} (derivante da {decina_bari} + {decina_cagliari})")
    print(f"Ambi da giocare: {terzo_bari}-{terzo_cagliari}")
    print(f"Terna da giocare: {ambata}-{terzo_bari}-{terzo_cagliari}")
    print(f"\nRuote consigliate: Bari, Cagliari, Nazionale")
    print("\n" + "=" * 60)

# Esecuzione del programma
calcola_tecnica_lotto()

# Questo mantiene aperta la console nei sistemi Windows
# quando si esegue il programma facendo doppio clic sul file
try:
    input("\nPremi INVIO per chiudere il programma...")
except:
    pass

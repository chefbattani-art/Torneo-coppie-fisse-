import streamlit as st

# Configurazione della pagina e stile CSS personalizzato per renderla professionale
st.set_page_config(
    page_title="Torneo Live", page_icon="⚽", layout="centered"
)

st.markdown(
    """
    <style>
    /* Stile generale e colori */
    .main-title {
        font-size: 28px;
        font-weight: 800;
        color: #1E293B;
        text-align: center;
        margin-bottom: 5px;
    }
    .card {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    .rule-box {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 15px;
        border-radius: 4px;
        color: #991B1B;
        font-size: 14px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Titolo principale
st.markdown(
    '<div class="main-title">🏆 Torneo a Coppie Fisse Live</div>',
    unsafe_allow_html=True,
)

# --- ICONA OCCHIO / FILTRO PERSONALE ---
# Utilizziamo un toggle o un pulsante per attivare la vista esclusiva della propria coppia
col_title, col_eye = st.columns([4, 1])
with col_eye:
  vista_personale = st.toggle("👁️ Solo miei", value=False)

# Sezione Informazioni Iniziali e Regole
with st.expander("ℹ️ Come funziona il torneo & Regole", expanded=True):
  st.markdown(
      """
        * L'app gestisce il torneo in autonomia. I gironi sono casuali, le fasi finali seguono il tabellone.
        * **Regola fondamentale:** La coppia vincitrice deve inserire il risultato esatto a fine partita.
        * Aggiorna la pagina dal browser per sincronizzare i dati in tempo reale.
        """
  )

# Lista fittizia delle coppie (gestita dall'amministratore)
elenco_coppie = [
    "-- Seleziona la tua coppia --",
    "Rossi / Bianchi",
    "Verdi / Neri",
    "Ferrari / Rossi",
]

# Selezione obbligatoria della coppia
st.markdown("### 📱 Seleziona la tua coppia per accedere:")
coppia_selezionata = st.selectbox(
    "Coppie partecipanti", elenco_coppie, label_visibility="collapsed"
)

if coppia_selezionata == "-- Seleziona la tua coppia --":
  st.warning(
      "⚠️ Devi selezionare la tua coppia dal menu qui sopra per sbloccare"
      " l'inserimento dei risultati e le funzioni della tua squadra."
  )
else:
  st.success(f"✅ Accesso effettuato come: **{coppia_selezionata}**")

  # Se l'utente ha attivato l'occhio ("Solo miei"), mostriamo solo i suoi dati
  if vista_personale:
    st.info(
        f"🔍 Stai visualizzando esclusivamente le partite e la classifica di:"
        f" **{coppia_selezionata}**"
    )
    # [Qui inserisci la logica per filtrare e mostrare solo le partite della coppia_selezionata]
  else:
    st.markdown("### 📊 Panoramica generale del Torneo")
    # [Qui mostri il tabellone completo per tutti]

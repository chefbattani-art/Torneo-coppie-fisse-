import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Torneo a Coppie Fisse Live", page_icon="⚽", layout="centered"
)

# Stile CSS personalizzato per grafica moderna e colorata
st.markdown(
    """
    <style>
    .main-title {
        font-size: 26px;
        font-weight: 800;
        color: #1E293B;
        text-align: center;
        margin-bottom: 2px;
    }
    .subtitle {
        font-size: 14px;
        color: #64748B;
        text-align: center;
        margin-bottom: 15px;
    }
    .card-info {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    .rule-box {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 12px;
        border-radius: 6px;
        color: #991B1B;
        font-size: 13px;
        margin-bottom: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- TITOLO E FILTRO OCCHIO ---
st.markdown(
    '<div class="main-title">🏆 Torneo a Coppie Fisse Live</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Gestione autonoma e in tempo reale</div>',
    unsafe_allow_html=True,
)

# Riga superiore con il toggle dell'occhio per la vista personale
col_testo, col_occhio = st.columns([3, 1])
with col_occhio:
  vista_personale = st.toggle("👁️ Solo miei", value=False)

# --- SEZIONE REGOLE (COLLAPSED O VISIBILE) ---
with st.expander("ℹ️ Come funziona il torneo & Regole", expanded=False):
  st.markdown("""
    * **Autonomia:** L'app gestisce i gironi e le classifiche in automatico.
    * **Aggiornamento:** Ricarica la pagina dal browser per vedere i risultati degli altri campi.
    """)

st.markdown(
    """
    <div class="rule-box">
    <b>⚠️ Regola fondamentale:</b> Chi vince è pregato di inserire subito il risultato esatto! La squadra in coda si tenga pronta a bordo campo.
    </div>
""",
    unsafe_allow_html=True,
)

# --- GESTIONE DATI COPPIE (Simulata in session_state) ---
if "elenco_coppie" not in st.session_state:
  st.session_state.elenco_coppie = [
      "Rossi / Bianchi",
      "Verdi / Neri",
      "Ferrari / Rossi",
      "Gialli / Blu",
  ]

# --- SELEZIONE DELLA COPPIA (OBBLIGATORIA) ---
st.markdown("### 📱 Seleziona la tua coppia:")

# Aggiungiamo un'opzione vuota iniziale
opzioni_select = ["-- Seleziona la tua coppia --"] + st.session_state.elenco_coppie

coppia_selezionata = st.selectbox(
    "Coppie partecipanti", opzioni_select, label_visibility="collapsed"
)

# Controllo accesso
if coppia_selezionata == "-- Seleziona la tua coppia --":
  st.warning(
      "👆 Seleziona la tua coppia dal menu a tendina per sbloccare l'accesso e"
      " inserire i risultati."
  )
else:
  st.success(f"✅ Accesso effettuato come: **{coppia_selezionata}**")

  # Se l'utente ha attivato l'occhio ("Solo miei")
  if vista_personale:
    st.info(
        f"🔍 **Modalità Vista Personale attiva:** Stai visualizzando solo le"
        f" partite e la classifica di {coppia_selezionata}."
    )
    # [INSERISCI QUI IL CODICE PER FILTRARE E MOSTRARE SOLO LE PARTITE DI QUESTA COPPIA]
  else:
    st.markdown("### 📊 Tabellone e Partite del Torneo")
    st.write(
        "(Qui viene mostrato l'andamento generale di tutte le coppie del"
        " torneo)"
    )
    # [INSERISCI QUI IL TABELLONE GENERALE]


# --- 🛠️ AREA AMMINISTRATORE (IN FONDO ALLA PAGINA) ---
st.markdown("---")
with st.expander("🛠️ Area Riservata Amministratore (Gestione Torneo)"):
  password_inserita = st.text_input(
      "Password di amministrazione", type="password"
  )

  # Scegli la password che preferisci qui sotto (es. "admin123")
  if password_inserita == "admin123":
    st.success("🔓 Accesso amministratore consentito.")

    st.markdown("#### Gestione Elenco Coppie")
    nuova_coppia = st.text_input("Aggiungi nuova coppia (es. Cognome1 / Cognome2)")
    if st.button("Aggiungi alla lista"):
      if nuova_coppia and nuova_coppia not in st.session_state.elenco_coppie:
        st.session_state.elenco_coppie.append(nuova_coppia)
        st.success(f"Coppia '{nuova_coppia}' aggiunta con successo!")
        st.rerun()
      else:
        st.error("Inserisci un nome valido o la coppia esiste già.")

    st.markdown("#### Coppie attualmente registrate:")
    for idx, c in enumerate(st.session_state.elenco_coppie):
      col_c1, col_c2 = st.columns([4, 1])
      with col_c1:
        st.text(f"{idx+1}. {c}")
      with col_c2:
        if st.button("Elimina", key=f"del_{idx}"):
          st.session_state.elenco_coppie.pop(idx)
          st.rerun()

  elif password_inserita != "":
    st.error("❌ Password errata.")
  else:
    st.info("Inserisci la password per sbloccare la gestione delle coppie.")

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Torneo Biliardino", page_icon="⚽", layout="centered"
)

# --- Inizializzazione dello Stato della Sessione ---
if "partite" not in st.session_state:
  st.session_state.partite = [
      {
          "id": 1,
          "tavolo": "Biliardino 1",
          "girone": "Girone A",
          "giocatore1": "Lorenzo Casanova",
          "giocatore2": "Carlo Pensionato",
          "gol1": 0,
          "gol2": 0,
          "giocata": False,
      },
      {
          "id": 2,
          "tavolo": "Biliardino 2",
          "girone": "Girone B",
          "giocatore1": "Fiore Gaffo",
          "giocatore2": "Cortesi Cai",
          "gol1": 0,
          "gol2": 0,
          "giocata": False,
      },
  ]

# --- Menu di Navigazione ---
menu = st.sidebar.selectbox(
    "Menu Principale", ["Incontri & Risultati", "Classifiche", "Gestione Torneo"]
)

# ==========================================
# 1. INCONTRI & RISULTATI
# ==========================================
if menu == "Incontri & Risultati":
  st.title("Incontri")
  st.markdown("### 🔥 Partite in Corso ai Tavoli")

  for p in st.session_state.partite:
    if not p["giocata"]:
      with st.container():
        # Box principale con CSS per evitare che i nomi vadano a capo
        st.markdown(
            f"""
                <div class="match-card">
                    <div class="match-header">⚽ {p['tavolo']} - {p['girone']}</div>
                    <div class="match-teams">{p['giocatore1']} vs {p['giocatore2']}</div>
                </div>
                """,
            unsafe_allow_html=True,
        )

        with st.expander(
            f"📝 Inserisci Risultato {p['tavolo']}", expanded=True
        ):
          st.markdown(
              f"<div class='expander-title'>{p['giocatore1']} vs"
              f" {p['giocatore2']}</div>",
              unsafe_allow_html=True,
          )

          st.markdown(f"**Gol {p['giocatore1']}**")
          gol_p1 = st.pills(
              f"Gol {p['giocatore1']}",
              options=[0, 1, 2, 3, 4, 5, 6, 7],
              default=0,
              key=f"pills_g1_{p['id']}",
              label_visibility="collapsed",
          )

          st.markdown(f"**Gol {p['giocatore2']}**")
          gol_p2 = st.pills(
              f"Gol {p['giocatore2']}",
              options=[0, 1, 2, 3, 4, 5, 6, 7],
              default=0,
              key=f"pills_g2_{p['id']}",
              label_visibility="collapsed",
          )

          st.markdown("<br>", unsafe_allow_html=True)
          if st.button(
              f"✅ Conferma Risultato {p['tavolo']}",
              use_container_width=True,
              key=f"btn_{p['id']}",
          ):
            p["gol1"] = int(gol_p1) if gol_p1 is not None else 0
            p["gol2"] = int(gol_p2) if gol_p2 is not None else 0
            p["giocata"] = True
            st.success(
                f"Risultato registrato: {p['giocatore1']} {p['gol1']} -"
                f" {p['gol2']} {p['giocatore2']}"
            )
            st.rerun()

  partite_concluse = [p for p in st.session_state.partite if p["giocata"]]
  if partite_concluse:
    st.markdown("---")
    st.markdown("### ✅ Partite Concluse")
    for p in partite_concluse:
      st.info(
          f"**{p['tavolo']} ({p['girone']})**: {p['giocatore1']} **{p['gol1']}"
          f" - {p['gol2']}** {p['giocatore2']}"
      )

# ==========================================
# 2. CLASSIFICHE
# ==========================================
elif menu == "Classifiche":
  st.title("🏆 Classifiche Gironi")

  giocatori_set = set()
  for p in st.session_state.partite:
    giocatori_set.add(p["giocatore1"])
    giocatori_set.add(p["giocatore2"])

  stats = {
      g: {
          "Punti": 0,
          "Giocate": 0,
          "Vinte": 0,
          "Perse": 0,
          "Gol Fatti": 0,
      }
      for g in giocatori_set
  }

  for p in st.session_state.partite:
    if p["giocata"]:
      g1, g2 = p["giocatore1"], p["giocatore2"]
      s1, s2 = p["gol1"], p["gol2"]

      stats[g1]["Giocate"] += 1
      stats[g2]["Giocate"] += 1
      stats[g1]["Gol Fatti"] += s1
      stats[g2]["Gol Fatti"] += s2

      if s1 > s2:
        stats[g1]["Punti"] += 3
        stats[g1]["Vinte"] += 1
        stats[g2]["Perse"] += 1
      elif s2 > s1:
        stats[g2]["Punti"] += 3
        stats[g2]["Vinte"] += 1
        stats[g1]["Perse"] += 1
      else:
        stats[g1]["Punti"] += 1
        stats[g2]["Punti"] += 1

  if stats:
    df_classifica = pd.DataFrame.from_dict(stats, orient="index").reset_index()
    df_classifica = df_classifica.rename(columns={"index": "Giocatore"})
    df_classifica = df_classifica.sort_values(
        by=["Punti", "Gol Fatti"], ascending=False
    )
    st.dataframe(df_classifica, use_container_width=True)
  else:
    st.info("Nessuna partita giocata al momento.")

# ==========================================
# 3. GESTIONE TORNEO
# ==========================================
elif menu == "Gestione Torneo":
  st.title("⚙️ Gestione Torneo")
  st.markdown("Aggiungi una nuova partita al calendario:")

  with st.form("form_nuova_partita"):
    tavolo = st.selectbox(
        "Tavolo", ["Biliardino 1", "Biliardino 2", "Biliardino 3"]
    )
    girone = st.selectbox("Girone", ["Girone A", "Girone B", "Girone Unico"])
    g1 = st.text_input("Giocatore 1")
    g2 = st.text_input("Giocatore 2")

    submit = st.form_submit_button("Aggiungi Partita")
    if submit and g1 and g2:
      nuovo_id = len(st.session_state.partite) + 1
      st.session_state.partite.append({
          "id": nuovo_id,
          "tavolo": tavolo,
          "girone": girone,
          "giocatore1": g1,
          "giocatore2": g2,
          "gol1": 0,
          "gol2": 0,
          "giocata": False,
      })
      st.success(f"Partita aggiunta tra {g1} e {g2}!")
      st.rerun()

  if st.button("🗑️ Reset di tutte le partite"):
    st.session_state.partite = []
    st.rerun()

# --- CSS Personalizzato per compattare i nomi su una riga ---
st.markdown(
    """
<style>
    .match-card {
        background-color: #fffde7;
        border: 2px solid #ffca28;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 15px;
    }
    .match-header {
        text-align: center;
        font-weight: bold;
        color: #d84315;
        font-size: 15px;
    }
    .match-teams {
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 4px;
    }
    .expander-title {
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

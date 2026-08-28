import json
import os
import random
import re
from datetime import datetime
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Aggiornato a 3 secondi per una fluidità e reattività elevata con tanti utenti
st_autorefresh(interval=3000, debounce=False, key="auto_refresh_tornei")
st.set_page_config(
    page_title="Gestione Tornei di Calcetto",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- STILE GRAFICO GLOBALE (CYBER / NEON AZZURRO-VIOLETTO) ---
st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0d091e 50%, #030712 100%);
            color: #f0f6fc;
            font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #130f26, #070510);
            border-right: 1px solid #2e1a47;
        }
        .cyber-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 27, 75, 0.7) 100%);
            border: 1px solid #00f0ff;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 14px;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
        }
        .cyber-card-gold {
            background: linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(60, 40, 10, 0.8) 100%);
            border: 1.5px solid #ffd700;
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.3);
            text-align: center;
        }
        .match-live-card {
            background: linear-gradient(135deg, #2b1f07 0%, #120d02 100%);
            border: 2px solid #f59e0b;
            border-radius: 16px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 0 25px rgba(245, 158, 11, 0.4);
        }
        h1, h2, h3, h4 {
            color: #ffffff !important;
            letter-spacing: 0.8px;
        }
        h1 {
            text-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
        }
        div.stButton > button {
            border-radius: 10px;
            font-weight: 700;
            border: 1px solid #00f0ff;
            background: linear-gradient(180deg, #1e3a8a, #0f172a);
            color: #f3e8ff;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            border-color: #38bdf8;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.6);
            color: #ffffff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_FILE = "tornei_data.json"


def carica_dati():
  dati_default = {"tornei": {}, "admin_pin": "0000"}
  if os.path.exists(DB_FILE):
    try:
      with open(DB_FILE, "r") as f:
        return json.load(f)
    except:
      pass
  return dati_default


def salva_dati(data):
  with open(DB_FILE, "w") as f:
    json.dump(data, f, indent=4)


if "db" not in st.session_state:
  st.session_state.db = carica_dati()

db = st.session_state.db


def pulisci_testo_whatsapp_e_Estrai_coppie(testo):
  """Estrae le coppie da un testo in stile WhatsApp rimuovendo emoji, numeri iniziali,

  simboli e righe di intestazione/prezzi.
  """
  coppie_estratte = []
  righe = testo.split("\n")
  for riga in righe:
    riga_pulita = riga.strip()
    if not riga_pulita:
      continue

    # Filtra righe che sembrano intestazioni, prezzi o note di servizio
    riga_lower = riga_pulita.lower()
    if any(
        parola in riga_lower
        for word in [
            "torneo",
            "iscrizion",
            "inizio",
            "ore",
            "tassativo",
            "donne",
            "uomini",
            "coppie fisse",
            "euro",
            "€",
            "-_",
        ]
        if (parola := word) in riga_lower
    ):
      # Se la riga contiene esplicitamente la parola "coppie" o simili ma ha anche nomi, controlliamo meglio,
      # ma solitamente le intestazioni non hanno i nomi dei giocatori.
      if not any(
          x in riga_lower for x in ["denny", "stani", "higuain", "carlos", "carlo"]
      ):  # Esempio di controllo per evitare falsi positivi se c'è testo misto
        if (
            "iscrizion" in riga_lower
            or "ore" in riga_lower
            or "€" in riga_lower
            or "donne" in riga_lower
            or "uomini" in riga_lower
        ):
          continue

    # Rimuove emoji comuni e simboli grafici
    riga_sanificata = (
        riga_pulita.replace("🤝", "")
        .replace("⚽", "")
        .replace("🏆", "")
        .replace("🏓", "")
        .replace("🥅", "")
        .replace("🔥", "")
        .replace("⭐", "")
        .replace("🌟", "")
        .replace("📍", "")
        .replace("‼️", "")
        .replace("*-", "")
        .replace("-*", "")
        .replace("*", "")
    )

    # Rimuove numerazione iniziale tipo "1.", "10-", "1)", ecc.
    riga_sanificata = re.sub(r"^\d+[\.\-\)]?\s*", "", riga_sanificata)
    riga_sanificata = riga_sanificata.strip()

    # Se dopo la pulizia la stringa è valida e contiene almeno uno spazio (separatore tra i due nomi della coppia)
    if riga_sanificata and len(riga_sanificata) > 2:
      # Controllo di sicurezza: se la riga è solo una parola chiave residua, la scartiamo
      if riga_sanificata.lower() not in [
          "coppie",
          "coppie fisse",
          "torneo",
          "iscrizioni",
      ]:
        coppie_estratte.append(riga_sanificata)

  return list(dict.fromkeys(coppie_estratte))  # Rimuove eventuali duplicati


def ricalcola_classifiche_gironi(torneo):
  for g_nome, coppie_lista in torneo["gironi"].items():
    stats = {
        c: {
            "punti": 0,
            "gf": 0,
            "gs": 0,
            "dr": 0,
            "scontri_diretti_pt": {},
        }
        for c in coppie_lista
    }

    if g_nome in torneo["calendario_gironi"]:
      for turno_obj in torneo["calendario_gironi"][g_nome]:
        for m in turno_obj["partite"]:
          if m.get("giocata", False):
            c1, c2 = m["c1"], m["c2"]
            g1, g2 = m["gol1"], m["gol2"]
            diff = abs(g1 - g2)

            if g1 > g2:
              pt_s1, pt_s2 = (3, 0) if diff >= 2 else (2, 1)
            elif g2 > g1:
              pt_s1, pt_s2 = (0, 3) if diff >= 2 else (1, 2)
            else:
              pt_s1, pt_s2 = 2, 2

            if c1 in stats:
              stats[c1]["punti"] += pt_s1
              stats[c1]["gf"] += g1
              stats[c1]["gs"] += g2
            if c2 in stats:
              stats[c2]["punti"] += pt_s2
              stats[c2]["gf"] += g2
              stats[c2]["gs"] += g1

      for c in coppie_lista:
        if c in stats:
          stats[c]["dr"] = stats[c]["gf"] - stats[c]["gs"]

      punti_gruppo = {}
      for c in coppie_lista:
        if c in stats:
          p = stats[c]["punti"]
          if p not in punti_gruppo:
            punti_gruppo[p] = []
          punti_gruppo[p].append(c)

      for p, gruppo in punti_gruppo.items():
        if len(gruppo) > 1:
          mini_punti = {c: 0 for c in gruppo}
          for turno_obj in torneo["calendario_gironi"][g_nome]:
            for m in turno_obj["partite"]:
              if m.get("giocata", False):
                c1, c2 = m["c1"], m["c2"]
                if c1 in gruppo and c2 in gruppo:
                  g1, g2 = m["gol1"], m["gol2"]
                  if g1 > g2:
                    mini_punti[c1] += 3
                  elif g2 > g1:
                    mini_punti[c2] += 3
                  else:
                    mini_punti[c1] += 1
                    mini_punti[c2] += 1
          for c in gruppo:
            if c in stats:
              stats[c]["scontri_diretti_pt"] = mini_punti[c]
        else:
          for c in gruppo:
            if c in stats:
              stats[c]["scontri_diretti_pt"] = 0

    torneo["punti_gironi"][g_nome] = stats


def renderizza_classifica_stile_card(torneo, g_nome):
  if g_nome not in torneo["punti_gironi"]:
    return
  dati_girone = torneo["punti_gironi"][g_nome]
  sorted_c = sorted(
      dati_girone.items(),
      key=lambda x: (
          x[1]["punti"],
          x[1]["scontri_diretti_pt"],
          x[1]["dr"],
          x[1]["gf"],
      ),
      reverse=True,
  )

  for idx, (coppia, info) in enumerate(sorted_c):
    is_fascia_a = idx < 4
    border_color = "#4ade80" if is_fascia_a else "#f87171"
    bg_gradient = (
        "linear-gradient(135deg, rgba(6, 36, 26, 0.8) 0%, rgba(3, 15, 10, 0.8) 100%)"
        if is_fascia_a
        else "linear-gradient(135deg, rgba(36, 6, 15, 0.8) 0%, rgba(15, 3, 7, 0.8) 100%)"
    )
    shadow_color = (
        "rgba(74, 222, 128, 0.2)" if is_fascia_a else "rgba(248, 113, 113, 0.2)"
    )
    dot_color = "#4ade80" if is_fascia_a else "#f87171"

    st.markdown(
        f"""
        <div style="background: {bg_gradient}; border: 1.5px solid {border_color}; border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; box-shadow: 0 0 15px {shadow_color}; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 10px; height: 10px; background-color: {dot_color}; border-radius: 50%; box-shadow: 0 0 8px {dot_color};"></div>
                <span style="font-size: 16px; font-weight: 800; color: {dot_color}; min-width: 30px;">{idx+1}°</span>
                <span style="font-size: 15px; font-weight: bold; color: #ffffff;">⚽🏆 {coppia}</span>
            </div>
            <div style="display: flex; gap: 14px; text-align: right; font-size: 13px;">
                <div>
                    <span style="font-size: 9px; color: #94a3b8; display: block;">PT</span>
                    <span style="font-weight: 800; color: #ffd700; font-size: 15px;">{info['punti']}</span>
                </div>
                <div>
                    <span style="font-size: 9px; color: #94a3b8; display: block;">DR</span>
                    <span style="color: {"#4ade80" if info['dr'] >= 0 else "#f87171"}; font-weight: 600;">{info['dr']:+d}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def genera_pdf_coppie(torneo):
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 16)
  pdf.cell(
      0,
      10,
      f"Torneo: {torneo.get('titolo', 'Calcetto')} - Schema Gironi",
      0,
      1,
      "C",
  )
  pdf.ln(5)

  for g_nome, turni in torneo["calendario_gironi"].items():
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"--- {g_nome} ---", 0, 1, "L")
    for turno_obj in turni:
      pdf.set_font("Arial", "B", 11)
      pdf.cell(0, 7, f"Turno {turno_obj['turno']}", 0, 1, "L")
      pdf.set_font("Arial", "", 10)
      for m in turno_obj["partite"]:
        risultato = (
            f"{m['gol1']} - {m['gol2']}"
            if m.get("giocata", False)
            else "Da giocare"
        )
        riga = f"  {m['c1']} VS {m['c2']} -> {risultato}"
        pdf.cell(
            0,
            6,
            riga.encode("latin-1", "ignore").decode("latin-1"),
            0,
            1,
            "L",
        )
      pdf.ln(2)
  return bytes(pdf.output())


def posticipa_partita_coda(torneo, match_id_da_spostare):
  for g_nome, turni in torneo["calendario_gironi"].items():
    tutte_partite_girone = []
    for turno_obj in turni:
      tutte_partite_girone.extend(turno_obj["partite"])

    idx_trovato = -1
    for i, m in enumerate(tutte_partite_girone):
      if m["id"] == match_id_da_spostare:
        idx_trovato = i
        break

    if idx_trovato != -1:
      if idx_trovato + 2 < len(tutte_partite_girone):
        partita = tutte_partite_girone.pop(idx_trovato)
        tutte_partite_girone.insert(idx_trovato + 2, partita)

        it = iter(tutte_partite_girone)
        for turno_obj in turni:
          turno_obj["partite"] = [
              next(it) for _ in range(len(turno_obj["partite"]))
          ]

        for t_obj in turni:
          for m in t_obj["partite"]:
            if m["id"] == match_id_da_spostare:
              m["in_corso"] = False
              m["tavolo"] = None

        salva_dati(db)
        return True
  return False


# --- BARRA LATERALE ---
st.sidebar.header("⚙️ Pannello di Controllo")

admin_param = st.query_params.get("admin", "false")
is_admin_autenticato = admin_param == "true"

modalita_admin = st.sidebar.checkbox(
    "Modalità Amministratore (PIN)", value=is_admin_autenticato
)
is_admin = False

if modalita_admin:
  if is_admin_autenticato:
    is_admin = True
    st.sidebar.success("Accesso Admin Attivo ✅")
    if st.sidebar.button("🔒 Logout Admin", use_container_width=True):
      st.query_params["admin"] = "false"
      st.rerun()
  else:
    pin_inserito = st.sidebar.text_input("Inserisci PIN Admin", type="password")
    if pin_inserito == db["admin_pin"]:
      st.query_params["admin"] = "true"
      st.rerun()
    elif pin_inserito:
      st.sidebar.error("PIN errato.")
else:
  if is_admin_autenticato:
    st.query_params["admin"] = "false"
    st.rerun()

st.sidebar.markdown("---")

# Gestione Tornei nella Sidebar per Admin
if is_admin:
  st.sidebar.subheader("🛠️ Crea Nuovo Torneo")
  with st.sidebar.form("form_nuovo_torneo"):
    titolo_nuovo = st.text_input(
        "Titolo Torneo", value="Torneo Calcino Agostino"
    )
    num_tav = st.number_input("N. Biliardini", min_value=1, max_value=10, value=6)
    num_gir = st.number_input("N. Gironi", min_value=1, max_value=8, value=4)
    submit_crea = st.form_submit_button("Crea Torneo")

    if submit_crea:
      torneo_id = (
          titolo_nuovo.lower().replace(" ", "_")
          + "_"
          + datetime.now().strftime("%d%m%Y")
      )
      if torneo_id not in db["tornei"]:
        db["tornei"][torneo_id] = {
            "titolo": titolo_nuovo,
            "stato": "setup",
            "coppie": [],
            "num_tavoli": num_tav,
            "num_gironi": num_gir,
            "gironi": {},
            "calendario_gironi": {},
            "punti_gironi": {},
            "fasi_finali_configurate": False,
            "tabellone_a": [],
            "tabellone_b": [],
            "terzo_quarto_a": [],
            "terzo_quarto_b": [],
        }
        salva_dati(db)
        st.success(f"Torneo '{titolo_nuovo}' creato!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("⚠️ Zona Pericolo")
if is_admin:
  conferma_reset = st.sidebar.checkbox(
      "Conferma reset database totale", key="checkbox_reset_db"
  )
  if st.sidebar.button("🔄 Elimina tutti i tornei", use_container_width=True):
    if conferma_reset:
      if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
      for key in list(st.session_state.keys()):
        del st.session_state[key]
      st.success("Database azzerato!")
      st.rerun()
    else:
      st.sidebar.warning("Spunta la casella di conferma.")
else:
  st.sidebar.info("Accedi come admin per gestire i tornei.")

# --- SELETTORE TORNEI E COPPIA GLOBALE ---
st.markdown(
    """
    <div style="text-align: left; margin-bottom: 10px;">
        <span style="color: #00f0ff; font-size: 11px; letter-spacing: 2px; font-weight: bold;">CIRCUITO UFFICIALE</span>
        <h1 style="font-size: 28px; margin: 2px 0 0 0; color: #ffffff; text-shadow: 0 0 20px rgba(0,240,255,0.4);">
            🏆 Gestione Tornei Coppie Fisse
        </h1>
    </div>
    """,
    unsafe_allow_html=True,
)

if not db["tornei"]:
  st.warning(
      "⚠️ Non ci sono tornei attivi al momento. Accedi come Amministratore dalla"
      " barra laterale per crearne uno."
  )
  st.stop()

# Selezione Torneo attivo tramite Parametri URL o Selectbox
lista_tornei_ids = list(db["tornei"].keys())
torneo_url = st.query_params.get("torneo", lista_tornei_ids[0])
if torneo_url not in lista_tornei_ids:
  torneo_url = lista_tornei_ids[0]

torneo_selezionato_id = st.selectbox(
    "🎯 Seleziona il Torneo a cui partecipare:",
    options=lista_tornei_ids,
    format_func=lambda x: db["tornei"][x]["titolo"],
    index=lista_tornei_ids.index(torneo_url),
)

if torneo_selezionato_id != torneo_url:
  st.query_params["torneo"] = torneo_selezionato_id
  # Rimuove la coppia dall'URL quando si cambia torneo per evitare conflitti
  if "coppia" in st.query_params:
    del st.query_params["coppia"]
  st.rerun()

torneo = db["tornei"][torneo_selezionato_id]

# --- SELETTORE COPPIA PERSISTENTE ---
tutte_le_coppie = []
for g_lst in torneo["gironi"].values():
  tutte_le_coppie.extend(g_lst)
if not tutte_le_coppie and torneo.get("coppie"):
  tutte_le_coppie = torneo["coppie"]

opzioni_selettore = ["-- Seleziona la tua coppia per accedere --"] + sorted(
    tutte_le_coppie
)

coppia_url = st.query_params.get(
    "coppia", "-- Seleziona la tua coppia per accedere --"
)
if coppia_url not in opzioni_selettore:
  coppia_url = "-- Seleziona la tua coppia per accedere --"

coppia_selezionata = st.selectbox(
    "📱 Seleziona la tua coppia per entrare nel torneo:",
    options=opzioni_selettore,
    index=opzioni_selettore.index(coppia_url),
    key="widget_selezione_coppia",
)

if coppia_selezionata != coppia_url:
  st.query_params["coppia"] = coppia_selezionata
  st.rerun()

if is_admin:
  st.success("🛡️ **Modalità Admin attiva:** Accesso completo sbloccato.")
elif coppia_selezionata == "-- Seleziona la tua coppia per accedere --":
  st.warning(
      "⚠️ **Attenzione:** Seleziona la tua coppia dal menu a tendina per"
      " sbloccare la tua dashboard personale, visualizzare le partite e"
      " inserire i risultati."
  )
else:
  st.success(
      f"✅ Accesso effettuato con successo come: **{coppia_selezionata}**"
  )

st.markdown("---")

# --- PANNELLO SETUP / GESTIONE ADMIN PER IL TORNEO SELEZIONATO ---
if torneo["stato"] == "setup" or is_admin:
  with st.expander(
      "⚙️ Configurazione e Inserimento Lista WhatsApp (Admin)",
      expanded=torneo["stato"] == "setup",
  ):
    if not is_admin:
      st.warning(
          "Il torneo è in fase di configurazione da parte dell'organizzatore."
      )
    else:
      whatsapp_text = st.text_area(
          "Incolla qui la lista WhatsApp del torneo:",
          value=("\n".join(torneo["coppie"]) if torneo["coppie"] else ""),
          height=180,
          placeholder=(
              "🏆*TORNEO calcino agostino*🏆\n1. denny luigi\n2. stani gardo..."
          ),
      )

      col1, col2 = st.columns(2)
      with col1:
        torneo["num_tavoli"] = st.number_input(
            "Numero biliardini",
            min_value=1,
            max_value=10,
            value=int(torneo["num_tavoli"]),
        )
      with col2:
        torneo["num_gironi"] = st.number_input(
            "Numero gironi",
            min_value=1,
            max_value=8,
            value=int(torneo["num_gironi"]),
        )

      if st.button("🚀 Estrai Coppie e Avvia Torneo", use_container_width=True):
        coppie_pulite = pulisci_testo_whatsapp_e_Estrai_coppie(whatsapp_text)
        num_g = int(torneo["num_gironi"])

        if len(coppie_pulite) < (num_g * 2):
          st.error(
              f"Trovate {len(coppie_pulite)} coppie valide. Con {num_g} gironi"
              f" ne servono almeno {num_g * 2}."
          )
        else:
          torneo["coppie"] = coppie_pulite
          random.shuffle(coppie_pulite)

          nomi_gironi = [chr(65 + i) for i in range(num_g)]
          gironi_dict = {f"Girone {g}": [] for g in nomi_gironi}

          for idx, c in enumerate(coppie_pulite):
            g_scelto = f"Girone {nomi_gironi[idx % num_g]}"
            gironi_dict[g_scelto].append(c)

          torneo["gironi"] = gironi_dict
          torneo["punti_gironi"] = {
              g: {
                  c: {
                      "punti": 0,
                      "gf": 0,
                      "gs": 0,
                      "dr": 0,
                      "scontri_diretti_pt": 0,
                  }
                  for c in lst
              }
              for g, lst in gironi_dict.items()
          }

          calendario_totale = {}
          for g_nome, lista_c in gironi_dict.items():
            squadre = lista_c.copy()
            if len(squadre) % 2 != 0:
              squadre.append("RIPOSO")

            n = len(squadre)
            turni_girone = []

            for t in range(n - 1):
              partite_turno = []
              for i in range(n // 2):
                s1 = squadre[i]
                s2 = squadre[n - 1 - i]
                if s1 != "RIPOSO" and s2 != "RIPOSO":
                  match_id = f"{g_nome}_t{t+1}_m{i}"
                  partite_turno.append({
                      "id": match_id,
                      "girone": g_nome,
                      "c1": s1,
                      "c2": s2,
                      "giocata": False,
                      "in_corso": False,
                      "tavolo": None,
                      "gol1": 0,
                      "gol2": 0,
                  })
              turni_girone.append({"turno": t + 1, "partite": partite_turno})
              squadre = [squadre[0]] + [squadre[-1]] + squadre[1:-1]

            calendario_totale[g_nome] = turni_girone

          torneo["calendario_gironi"] = calendario_totale
          torneo["stato"] = "gironi"
          salva_dati(db)
          st.success(
              f"Estratte {len(coppie_pulite)} coppie e avviato il torneo!"
          )
          st.rerun()

# --- SE LA COPPIA È SELEZIONATA, MOSTRA LA SUA DASHBOARD PERSONALE ---
if (
    coppia_selezionata != "-- Seleziona la tua coppia per accedere --"
    and torneo["stato"] == "gironi"
):
  with st.expander(
      f"👁️ Dashboard Personale: {coppia_selezionata}", expanded=True
  ):
    girone_mio = None
    pos_mia = None
    info_mie = None
    for g_nome, lista_c in torneo["gironi"].items():
      if coppia_selezionata in lista_c:
        girone_mio = g_nome
        ricalcola_classifiche_gironi(torneo)
        if g_nome in torneo["punti_gironi"]:
          dati_g = torneo["punti_gironi"][g_nome]
          sorted_c = sorted(
              dati_g.items(),
              key=lambda x: (
                  x[1]["punti"],
                  x[1]["scontri_diretti_pt"],
                  x[1]["dr"],
                  x[1]["gf"],
              ),
              reverse=True,
          )
          for idx, (c_nome, stats) in enumerate(sorted_c):
            if c_nome == coppia_selezionata:
              pos_mia = idx + 1
              info_mie = stats
        break

    st.markdown(
        f"""
        <div class="cyber-card" style="border-color: #00f0ff; text-align: left; padding: 20px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #00f0ff; font-weight: bold;">LA TUA COPPIA</div>
            <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-bottom: 14px;">🤝 {coppia_selezionata}</div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #1e3a8a; border-radius: 10px; padding: 10px; flex: 1; min-width: 100px; text-align: center;">
                    <div style="font-size: 10px; color: #94a3b8; font-weight: bold;">POSIZIONE</div>
                    <div style="font-size: 16px; font-weight: 700; color: #4ade80; margin-top: 2px;">{str(pos_mia) + '° POSTO' if pos_mia else 'N.D.'}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #1e3a8a; border-radius: 10px; padding: 10px; flex: 1; min-width: 100px; text-align: center;">
                    <div style="font-size: 10px; color: #94a3b8; font-weight: bold;">GIRONE</div>
                    <div style="font-size: 16px; font-weight: 700; color: #00f0ff; margin-top: 2px;">{girone_mio if girone_mio else 'N.D.'}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #1e3a8a; border-radius: 10px; padding: 10px; flex: 1; min-width: 100px; text-align: center;">
                    <div style="font-size: 10px; color: #94a3b8; font-weight: bold;">PUNTI / DR</div>
                    <div style="font-size: 16px; font-weight: 700; color: #fbbf24; margin-top: 2px;">{info_mie['punti'] if info_mie else 0} PT <span style="font-size: 11px; font-weight: normal; color: #94a3b8;">(DR: {info_mie['dr'] if info_mie else 0})</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- 2. FASE A GIRONI (VISUALIZZAZIONE PRINCIPALE) ---
if torneo["stato"] == "gironi":
  ricalcola_classifiche_gironi(torneo)
  num_tavoli = torneo.get("num_tavoli", 6)

  max_turni = (
      max([len(turni) for turni in torneo["calendario_gironi"].values()])
      if torneo["calendario_gironi"]
      else 0
  )
  partite_per_girone_dict = {}
  for t_num in range(1, max_turni + 1):
    for g_nome, turni_girone in torneo["calendario_gironi"].items():
      for t_obj in turni_girone:
        if t_obj["turno"] == t_num:
          if g_nome not in partite_per_girone_dict:
            partite_per_girone_dict[g_nome] = []
          partite_per_girone_dict[g_nome].extend(t_obj["partite"])

  partite_miste_totali = []
  max_len_partite = (
      max([len(v) for v in partite_per_girone_dict.values()])
      if partite_per_girone_dict
      else 0
  )
  for idx_misto in range(max_len_partite):
    for g_chiave in sorted(partite_per_girone_dict.keys()):
      lista_p = partite_per_girone_dict[g_chiave]
      if idx_misto < len(lista_p):
        partite_miste_totali.append(lista_p[idx_misto])

  partite_in_corso = []
  partite_da_giocare = []

  for m in partite_miste_totali:
    if not m.get("giocata", False):
      if m.get("in_corso", False):
        partite_in_corso.append(m)
      else:
        partite_da_giocare.append(m)

  tavoli_occupati_ids = [
      p.get("tavolo") for p in partite_in_corso if p.get("tavolo") is not None
  ]
  tavoli_liberi_disponibili = [
      t for t in range(1, num_tavoli + 1) if t not in tavoli_occupati_ids
  ]

  if tavoli_liberi_disponibili and partite_da_giocare:
    cambiato = False
    for tavolo_libero in tavoli_liberi_disponibili:
      if partite_da_giocare:
        prossima_partita = partite_da_giocare.pop(0)
        prossima_partita["in_corso"] = True
        prossima_partita["tavolo"] = tavolo_libero
        partite_in_corso.append(prossima_partita)
        cambiato = True
    if cambiato:
      salva_dati(db)

  partite_in_corso = sorted(
      partite_in_corso,
      key=lambda x: x.get("tavolo") if x.get("tavolo") is not None else 999,
  )

  st.subheader("⚡ Stato dei Biliardini e Coda Incontri")

  col_ic, col_coda = st.columns(2)

  with col_ic:
    st.markdown("#### 🔥 Partite in Corso ai Tavoli")
    if not partite_in_corso:
      st.info("Nessuna partita in corso al momento.")
    else:
      for m in partite_in_corso:
        tavolo_str = (
            f"<b>🏟️ Biliardino {m.get('tavolo')} - {m['girone']}</b>"
            if m.get("tavolo")
            else f"<b>🏟️ In campo - {m['girone']}</b>"
        )
        match_id = m["id"]
        fa_al_caso_nostro = (
            is_admin
            or coppia_selezionata == m["c1"]
            or coppia_selezionata == m["c2"]
        )

        st.markdown(
            f"""
            <div class="match-live-card" style="margin-bottom: 12px;">
                <div style="font-size: 14px; color: #f59e0b; font-weight: bold; margin-bottom: 8px;">{tavolo_str}</div>
                <div style="font-size: 16px; font-weight: bold; color: #ffffff;">🤝 {m['c1']}</div>
                <div style="margin: 4px 0; font-size: 12px; font-weight: bold; color: #94a3b8;">VS</div>
                <div style="font-size: 16px; font-weight: bold; color: #ffffff;">🤝 {m['c2']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🔄 Posticipa di 2 partite",
            key=f"posticipa_{match_id}",
            use_container_width=True,
        ):
          if posticipa_partita_coda(torneo, match_id):
            st.success("Partita posticipata di 2 turni!")
            st.rerun()

        if fa_al_caso_nostro:
          with st.expander(
              f"📝 Inserisci Risultato Tavolo {m.get('tavolo', '')}"
          ):
            gol_p1 = st.number_input(
                f"Gol {m['c1']}",
                min_value=0,
                max_value=10,
                value=int(m.get("gol1", 0)),
                key=f"g1_{match_id}",
            )
            gol_p2 = st.number_input(
                f"Gol {m['c2']}",
                min_value=0,
                max_value=10,
                value=int(m.get("gol2", 0)),
                key=f"g2_{match_id}",
            )
            if st.button(
                "✅ Conferma Risultato",
                key=f"save_{match_id}",
                use_container_width=True,
            ):
              m["gol1"] = int(gol_p1)
              m["gol2"] = int(gol_p2)
              m["giocata"] = True
              m["in_corso"] = False
              m["tavolo"] = None
              ricalcola_classifiche_gironi(torneo)
              salva_dati(db)
              st.success("Risultato salvato!")
              st.rerun()

  with col_coda:
    partite_in_coda_correnti = partite_da_giocare[:num_tavoli]
    st.markdown("#### ⏳ In Coda (Prossimi Incontri)")
    if not partite_in_coda_correnti:
      st.info("La coda è vuota.")
    else:
      for idx, m in enumerate(partite_in_coda_correnti):
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #06241a 0%, #030f0a 100%); border: 1.5px solid #10b981; padding: 14px; border-radius: 10px; margin-bottom: 10px; color: #34d399; text-align: center;">
                <b style="font-size: 13px;">⏳ {idx+1}. {m['girone']}</b><br>
                <b style="color: #ffffff; font-size: 14px;">{m['c1']} vs {m['c2']}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

  st.markdown("---")
  st.subheader("📊 Classifiche dei Gironi")
  nomi_gironi_chiavi = list(torneo["gironi"].keys())
  for i in range(0, len(nomi_gironi_chiavi), 2):
    col_gironi = st.columns(2)
    for j in range(2):
      if i + j < len(nomi_gironi_chiavi):
        g_nome = nomi_gironi_chiavi[i + j]
        with col_gironi[j]:
          st.markdown(
              f"<h3 style='text-align: center; font-size: 22px; color:"
              f" #00f0ff;'>📁 {g_nome}</h3>",
              unsafe_allow_html=True,
          )
          renderizza_classifica_stile_card(torneo, g_nome)

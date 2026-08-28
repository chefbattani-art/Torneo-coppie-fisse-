from datetime import datetime
import json
import os
import random
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=3000, debounce=False, key="auto_refresh_tornei")
st.set_page_config(
    page_title="Gestione Tornei di Calcetto",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- STILE GRAFICO GLOBALE ---
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
        
        /* TRCCO CSS: Forza le 8 colonne dei numeri a restare affiancate orizzontalmente anche su mobile */
        [data-testid="column"] {
            width: 12.5% !important;
            flex: 1 1 12.5% !important;
            min-width: 32px !important;
        }
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 2px !important;
        }

        div.stButton > button {
            border-radius: 6px;
            font-weight: 700;
            border: 1px solid #00f0ff;
            background: linear-gradient(180deg, #1e3a8a, #0f172a);
            color: #f3e8ff;
            width: 100% !important;
            min-width: 0px !important;
            padding: 4px 0px !important;
            font-size: 12px !important;
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
  coppie_estratte = []
  righe = testo.split("\n")
  for riga in righe:
    riga_pulita = riga.strip()
    if not riga_pulita:
      continue
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
      if not any(
          x in riga_lower for x in ["denny", "stani", "higuain", "carlos", "carlo"]
      ):
        if (
            "iscrizion" in riga_lower
            or "ore" in riga_lower
            or "€" in riga_lower
            or "donne" in riga_lower
            or "uomini" in riga_lower
        ):
          continue

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
    riga_sanificata = re.sub(r"^\d+[\.\-\)]?\s*", "", riga_sanificata)
    riga_sanificata = riga_sanificata.strip()

    if riga_sanificata and len(riga_sanificata) > 2:
      if riga_sanificata.lower() not in [
          "coppie",
          "coppie fisse",
          "torneo",
          "iscrizioni",
      ]:
        coppie_estratte.append(riga_sanificata)

  return list(dict.fromkeys(coppie_estratte))


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
        else "linear-gradient(135deg, rgba(36, 6, 15, 0.8) 15%, rgba(15, 3, 7, 0.8) 100%)"
    )
    dot_color = "#4ade80" if is_fascia_a else "#f87171"

    st.markdown(
        f"""
        <div style="background: {bg_gradient}; border: 1.5px solid {border_color}; border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 10px; height: 10px; background-color: {dot_color}; border-radius: 50%;"></div>
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
                    <span style="color: {'#4ade80' if info['dr'] >= 0 else '#f87171'}; font-weight: 600;">{info['dr']:+d}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

# --- GESTIONE AUTOMATICA TORNEO E COPPIA DA URL ---
if not db["tornei"]:
  st.warning(
      "⚠️ Non ci sono tornei attivi al momento. Accedi come Amministratore dalla"
      " barra laterale per crearne uno."
  )
  st.stop()

lista_tornei_ids = list(db["tornei"].keys())
torneo_url = st.query_params.get("torneo", lista_tornei_ids[0])
if torneo_url not in lista_tornei_ids:
  torneo_url = lista_tornei_ids[0]

torneo = db["tornei"][torneo_url]

tutte_le_coppie = []
for g_lst in torneo["gironi"].values():
  tutte_le_coppie.extend(g_lst)
if not tutte_le_coppie and torneo.get("coppie"):
  tutte_le_coppie = torneo["coppie"]

coppia_url = st.query_params.get("coppia", "")

if not is_admin and coppia_url in tutte_le_coppie:
  coppia_selezionata = coppia_url
  st.markdown(
      f"""
        <div style="text-align: left; margin-bottom: 10px;">
            <span style="color: #00f0ff; font-size: 11px; letter-spacing: 2px; font-weight: bold;">{torneo['titolo'].upper()}</span>
            <h1 style="font-size: 24px; margin: 2px 0 0 0; color: #ffffff; text-shadow: 0 0 20px rgba(0,240,255,0.4); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                🏆 Benvenuto, {coppia_selezionata}
            </h1>
        </div>
        """,
      unsafe_allow_html=True,
  )
else:
  st.markdown(
      """
        <div style="text-align: left; margin-bottom: 10px;">
            <span style="color: #00f0ff; font-size: 11px; letter-spacing: 2px; font-weight: bold;">CIRCUITO UFFICIALE</span>
            <h1 style="font-size: 26px; margin: 2px 0 0 0; color: #ffffff; text-shadow: 0 0 20px rgba(0,240,255,0.4);">
                🏆 Gestione Tornei Coppie Fisse
            </h1>
        </div>
        """,
      unsafe_allow_html=True,
  )

  torneo_selezionato_id = st.selectbox(
      "🎯 Seleziona il Torneo:",
      options=lista_tornei_ids,
      format_func=lambda x: db["tornei"][x]["titolo"],
      index=lista_tornei_ids.index(torneo_url),
  )

  if torneo_selezionato_id != torneo_url:
    st.query_params["torneo"] = torneo_selezionato_id
    if "coppia" in st.query_params:
      del st.query_params["coppia"]
    st.rerun()

  torneo = db["tornei"][torneo_selezionato_id]
  tutte_le_coppie = []
  for g_lst in torneo["gironi"].values():
    tutte_le_coppie.extend(g_lst)
  if not tutte_le_coppie and torneo.get("coppie"):
    tutte_le_coppie = torneo["coppie"]

  opzioni_selettore = ["-- Seleziona la tua coppia per accedere --"] + sorted(
      tutte_le_coppie
  )
  coppia_url_current = st.query_params.get(
      "coppia", "-- Seleziona la tua coppia per accedere --"
  )
  if coppia_url_current not in opzioni_selettore:
    coppia_url_current = "-- Seleziona la tua coppia per accedere --"

  coppia_selezionata = st.selectbox(
      "📱 Seleziona la tua coppia per entrare nel torneo:",
      options=opzioni_selettore,
      index=opzioni_selettore.index(coppia_url_current),
  )

  if coppia_selezionata != coppia_url_current:
    st.query_params["coppia"] = coppia_selezionata
    st.rerun()

if is_admin:
  st.success("🛡️ **Modalità Admin attiva:** Accesso completo sbloccato.")
elif (
    coppia_selezionata == "-- Seleziona la tua coppia per accedere --"
    and not coppia_url
):
  st.warning(
      "⚠️ **Attenzione:** Seleziona la tua coppia dal menu a tendina o usa il"
      " link personale per accedere alla tua dashboard."
  )
  st.stop()
elif not is_admin:
  coppia_selezionata = (
      coppia_url if coppia_url in tutte_le_coppie else coppia_selezionata
  )

st.markdown("---")

# --- PANNELLO SETUP ADMIN ---
if torneo["stato"] == "setup" or is_admin:
  with st.expander(
      "⚙️ Configurazione e Inserimento Lista WhatsApp (Admin)",
      expanded=torneo["stato"] == "setup",
  ):
    if is_admin:
      whatsapp_text = st.text_area(
          "Incolla qui la lista WhatsApp del torneo:",
          value=("\n".join(torneo["coppie"]) if torneo["coppie"] else ""),
          height=180,
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
              f"Trovate {len(coppie_pulite)} coppie. Ne servono almeno"
              f" {num_g * 2}."
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
          st.success("Torneo avviato con successo!")
          st.rerun()

# --- PREPARAZIONE DATI PARTITE IN CORSO E IN CODA ---
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

  # --- DASHBOARD PERSONALE CON SELETTORE GOL DA 0 A 7 ---
  if (
      coppia_selezionata
      and coppia_selezionata != "-- Seleziona la tua coppia per accedere --"
  ):
    girone_mio = None
    pos_mia = None
    info_mie = None
    for g_nome, lista_c in torneo["gironi"].items():
      if coppia_selezionata in lista_c:
        girone_mio = g_nome
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

    mia_partita_in_corso = None
    for p in partite_in_corso:
      if p["c1"] == coppia_selezionata or p["c2"] == coppia_selezionata:
        mia_partita_in_corso = p
        break

    mia_posizione_in_coda = None
    for idx_coda, p in enumerate(partite_da_giocare):
      if p["c1"] == coppia_selezionata or p["c2"] == coppia_selezionata:
        mia_posizione_in_coda = idx_coda + 1
        break

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 27, 75, 0.7) 100%); border: 1px solid #00f0ff; border-radius: 14px; padding: 18px; margin-bottom: 14px; box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);">
            <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #f472b6; font-weight: bold; margin-bottom: 4px;">RIEPILOGO SQUADRA</div>
            <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-bottom: 14px; text-shadow: 0 0 10px rgba(255,255,255,0.3);">🤝 {coppia_selezionata}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_col1, c_col2 = st.columns(2)
    with c_col1:
      st.metric(
          label="📁 GIRONE", value=str(girone_mio) if girone_mio else "N.D."
      )
    with c_col2:
      st.metric(
          label="🏆 POSIZIONE",
          value=(str(pos_mia) + "° posto" if pos_mia else "N.D."),
      )

    st.metric(
        label="⭐ PUNTI / DR",
        value=f"{info_mie['punti'] if info_mie else 0} pt",
        delta=(f"DR: {info_mie['dr']:+d}" if info_mie else "DR: 0"),
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if mia_partita_in_corso:
      avversario = (
          mia_partita_in_corso["c2"]
          if mia_partita_in_corso["c1"] == coppia_selezionata
          else mia_partita_in_corso["c1"]
      )
      match_id_mio = mia_partita_in_corso["id"]

      st.markdown(
          f"""
            <div style="background: linear-gradient(135deg, #2b1f07 0%, #120d02 100%); border: 1.5px solid #f59e0b; padding: 14px; border-radius: 12px; margin-bottom: 10px; text-align: center;">
                <div style="font-size: 12px; color: #f59e0b; font-weight: bold; margin-bottom: 4px;">🔥 PARTITA IN CORSO</div>
                <div style="font-size: 14px; color: #ffffff;">Sei in campo al <b>Tavolo {mia_partita_in_corso.get('tavolo')}</b> contro <b>{avversario}</b>!</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

      with st.expander("📝 Inserisci il Risultato Finale", expanded=True):
        st.markdown(f"**Gol {mia_partita_in_corso['c1']}**")
        cols_g1 = st.columns(8)
        val_prec_g1 = int(mia_partita_in_corso.get("gol1", 0))
        for i in range(8):
          with cols_g1[i]:
            is_selected = val_prec_g1 == i
            btn_type = "primary" if is_selected else "secondary"
            if st.button(
                str(i),
                key=f"m_btn_g1_{match_id_mio}_{i}",
                use_container_width=True,
                type=btn_type,
            ):
              mia_partita_in_corso["gol1"] = i
              salva_dati(db)
              st.rerun()

        st.markdown(f"**Gol {mia_partita_in_corso['c2']}**")
        cols_g2 = st.columns(8)
        val_prec_g2 = int(mia_partita_in_corso.get("gol2", 0))
        for i in range(8):
          with cols_g2[i]:
            is_selected = val_prec_g2 == i
            btn_type = "primary" if is_selected else "secondary"
            if st.button(
                str(i),
                key=f"m_btn_g2_{match_id_mio}_{i}",
                use_container_width=True,
                type=btn_type,
            ):
              mia_partita_in_corso["gol2"] = i
              salva_dati(db)
              st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "💾 Salva Risultato",
            key=f"m_save_{match_id_mio}",
            use_container_width=True,
        ):
          mia_partita_in_corso["giocata"] = True
          mia_partita_in_corso["in_corso"] = False
          mia_partita_in_corso["tavolo"] = None
          ricalcola_classifiche_gironi(torneo)
          salva_dati(db)
          st.success("Risultato salvato con successo! Il torneo è stato aggiornato.")
          st.rerun()

    elif mia_posizione_in_coda:
      st.markdown(
          f"""
            <div style="background: linear-gradient(135deg, #06241a 0%, #030f0a 100%); border: 1.5px solid #10b981; padding: 14px; border-radius: 12px; margin-bottom: 14px; text-align: center;">
                <div style="font-size: 12px; color: #34d399; font-weight: bold; margin-bottom: 4px;">⏳ PARTITE IN CODA</div>
                <div style="font-size: 14px; color: #ffffff;"> La tua coppia è in posizione <b>#{mia_posizione_in_coda}</b> nella coda d'attesa per il prossimo biliardino libero. Teniti pronto!</div>
            </div>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.markdown(
          """
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #1e3a8a; padding: 14px; border-radius: 12px; margin-bottom: 14px; text-align: center;">
                <span style="color: #94a3b8; font-size: 13px;">🟢 Nessuna partita attiva o in coda al momento per questa coppia.</span>
            </div>
            """,
          unsafe_allow_html=True,
      )

  # --- VISUALIZZAZIONE PARTITE IN CORSO E IN CODA ---
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

        sono_interessato = (
            coppia_selezionata == m["c1"] or coppia_selezionata == m["c2"]
        )

        st.markdown(
            f"""
            <div class="match-live-card" style="margin-bottom: 12px;">
                <div style="font-size: 13px; color: #f59e0b; font-weight: bold; margin-bottom: 8px;">{tavolo_str}</div>
                <div style="font-size: 15px; font-weight: bold; color: #ffffff;">🤝 {m['c1']}</div>
                <div style="margin: 4px 0; font-size: 11px; font-weight: bold; color: #94a3b8;">VS</div>
                <div style="font-size: 15px; font-weight: bold; color: #ffffff;">🤝 {m['c2']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if is_admin or sono_interessato:
          if st.button(
              "🔄 Posticipa di 2 partite",
              key=f"posticipa_{match_id}",
              use_container_width=True,
          ):
            if posticipa_partita_coda(torneo, match_id):
              st.success("Partita posticipata di 2 turni!")
              st.rerun()

        if is_admin or sono_interessato:
          with st.expander(f"⚙️ Gestisci: {m['c1']} vs {m['c2']}"):
            st.markdown(f"**Gol {m['c1']}**")
            cols_g1 = st.columns(8)
            val_prec_g1 = int(m.get("gol1", 0))
            for i in range(8):
              with cols_g1[i]:
                is_selected = val_prec_g1 == i
                btn_type = "primary" if is_selected else "secondary"
                if st.button(
                    str(i),
                    key=f"btn_g1_{match_id}_{i}",
                    use_container_width=True,
                    type=btn_type,
                ):
                  m["gol1"] = i
                  salva_dati(db)
                  st.rerun()

            st.markdown(f"**Gol {m['c2']}**")
            cols_g2 = st.columns(8)
            val_prec_g2 = int(m.get("gol2", 0))
            for i in range(8):
              with cols_g2[i]:
                is_selected = val_prec_g2 == i
                btn_type = "primary" if is_selected else "secondary"
                if st.button(
                    str(i),
                    key=f"btn_g2_{match_id}_{i}",
                    use_container_width=True,
                    type=btn_type,
                ):
                  m["gol2"] = i
                  salva_dati(db)
                  st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(
                "💾 Salva Risultato",
                key=f"save_{match_id}",
                use_container_width=True,
            ):
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
            <div style="background: linear-gradient(135deg, #06241a 0%, #030f0a 100%); border: 1.5px solid #10b981; padding: 12px; border-radius: 10px; margin-bottom: 10px; color: #34d399; text-align: center;">
                <b style="font-size: 12px;">⏳ {idx+1}. {m['girone']}</b><br>
                <b style="color: #ffffff; font-size: 13px;">{m['c1']} vs {m['c2']}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

  st.markdown("---")

  # --- ELENCO COMPLETO DI TUTTE LE PARTITE DI TUTTI I GIRONI ---
  st.subheader("📅 Elenco Completo di Tutte le Partite")
  for g_nome, turni_lista in torneo["calendario_gironi"].items():
    with st.expander(f"📁 Calendario {g_nome}", expanded=False):
      for turno_obj in turni_lista:
        st.markdown(f"**Turno {turno_obj['turno']}**")
        for m in turno_obj["partite"]:
          ris_str = (
              f"<span style='color: #4ade80; font-weight:"
              f" bold;'>{m['gol1']} - {m['gol2']}</span>"
              if m.get("giocata", False)
              else "<span style='color: #f59e0b;'>Da giocare</span>"
          )
          st.markdown(
              f"""
              <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 8px 12px; border-radius: 8px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-size: 13px;"><b>{m['c1']}</b> vs <b>{m['c2']}</b></span>
                  <span>{ris_str}</span>
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
              f"<h3 style='text-align: center; font-size: 20px; color:"
              f" #00f0ff;'>📁 {g_nome}</h3>",
              unsafe_allow_html=True,
          )
          renderizza_classifica_stile_card(torneo, g_nome)

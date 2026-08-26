import json
import os
import random
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=5000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(
    page_title="Torneo Coppie Fisse Live",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STILE GRAFICO GLOBALE (DARK / GAMING NEON AZZURRO ELETTRICO LUMINOSO) ---
st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at 50% 0%, #0a1128 0%, #030712 50%, #010206 100%);
            color: #f0f6fc !important;
            font-family: 'Inter', sans-serif;
        }
        div.stMarkdown, div.stText, p, span, label, div[data-baseweb="select"] span {
            color: #f0f6fc !important;
        }
        table, th, td {
            background-color: #0d1629 !important;
            color: #f0f6fc !important;
        }
        thead th {
            background-color: #132247 !important;
            color: #00f0ff !important;
            border-bottom: 2px solid #00f0ff !important;
            text-shadow: 0 0 8px rgba(0, 240, 255, 0.6);
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070d1a, #030712);
            border-right: 1px solid #00f0ff;
            box-shadow: 2px 0 15px rgba(0, 240, 255, 0.15);
        }
        section[data-testid="stSidebar"] * {
            color: #f0f6fc !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            letter-spacing: 0.5px;
        }
        div.stButton > button {
            border-radius: 10px;
            font-weight: 700;
            border: 1px solid #00f0ff;
            background: linear-gradient(180deg, #0e2a47, #071120);
            color: #00f0ff !important;
            padding: 12px 20px;
            font-size: 16px;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.25);
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            border-color: #00f0ff;
            background: linear-gradient(180deg, #163d66, #0e2a47);
            color: #ffffff !important;
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.7);
        }
        div[data-baseweb="select"] > div {
            background-color: #0d1629 !important;
            color: #f0f6fc !important;
            border-color: #00f0ff !important;
            border-radius: 10px !important;
            box-shadow: 0 0 8px rgba(0, 240, 255, 0.2);
        }
        div[data-testid="stPills"] button {
            background-color: #0d1629 !important;
            color: #f0f6fc !important;
            border: 1px solid #1d4ed8 !important;
            font-weight: bold !important;
        }
        div[data-testid="stPills"] button[aria-selected="true"] {
            background-color: #0284c7 !important;
            color: #ffffff !important;
            border-color: #00f0ff !important;
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.6);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_FILE = "coppie_data.json"


def carica_dati():
  dati_default = {
      "stato": "setup",
      "coppie": [],
      "num_tavoli": 6,
      "num_gironi": 4,
      "num_giorni": 1,
      "squadre_che_passano": 4,
      "admin_pin": "0000",
      "gironi": {},
      "calendario_gironi": {},
      "punti_gironi": {},
      "fasi_finali_configurate": False,
      "tabellone_a": [],
  }
  if os.path.exists(DB_FILE):
    try:
      with open(DB_FILE, "r") as f:
        dati_salvati = json.load(f)
        for k, v in dati_default.items():
          if k not in dati_salvati:
            dati_salvati[k] = v
        return dati_salvati
    except:
      pass
  return dati_default


def salva_dati(data):
  with open(DB_FILE, "w") as f:
    json.dump(data, f, indent=4)


if "db" not in st.session_state:
  st.session_state.db = carica_dati()

db = st.session_state.db


def pulisci_nome(testo):
  testo = testo.replace("🤝", "").replace("⚽", "").replace("🏆", "")
  testo = re.sub(r"^\d+[\.\-\)]?\s*", "", testo)
  return testo.strip()


def evidenzia_nome_coppia(testo_match, mia_coppia):
  return testo_match.replace(
      mia_coppia,
      f"<span style='color: #00f0ff; font-weight: 800; text-shadow: 0 0 12px rgba(0,240,255,0.8);'>{mia_coppia}</span>",
  )


def ricalcola_classifiche_gironi():
  for g_nome, coppie_lista in db["gironi"].items():
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

    if g_nome in db["calendario_gironi"]:
      for turno_obj in db["calendario_gironi"][g_nome]:
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

            stats[c1]["punti"] += pt_s1
            stats[c2]["punti"] += pt_s2
            stats[c1]["gf"] += g1
            stats[c1]["gs"] += g2
            stats[c2]["gf"] += g2
            stats[c2]["gs"] += g1

      for c in coppie_lista:
        stats[c]["dr"] = stats[c]["gf"] - stats[c]["gs"]

      punti_gruppo = {}
      for c in coppie_lista:
        p = stats[c]["punti"]
        if p not in punti_gruppo:
          punti_gruppo[p] = []
        punti_gruppo[p].append(c)

      for p, gruppo in punti_gruppo.items():
        if len(gruppo) > 1:
          mini_punti = {c: 0 for c in gruppo}
          for turno_obj in db["calendario_gironi"][g_nome]:
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
            stats[c]["scontri_diretti_pt"] = mini_punti[c]
        else:
          for c in gruppo:
            stats[c]["scontri_diretti_pt"] = 0

    db["punti_gironi"][g_nome] = stats


def calcola_partite_giocate_coppia(g_nome, coppia):
  giocate = 0
  totali = 0
  if g_nome in db["calendario_gironi"]:
    for turno_obj in db["calendario_gironi"][g_nome]:
      for m in turno_obj["partite"]:
        if m["c1"] == coppia or m["c2"] == coppia:
          totali += 1
          if m.get("giocata", False):
            giocate += 1
  return giocate, totali


def genera_pdf_coppie():
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 16)
  pdf.cell(0, 10, "Torneo a Coppie Fisse - Schema Gironi", 0, 1, "C")
  pdf.ln(5)

  for g_nome, turni in db["calendario_gironi"].items():
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"--- {g_nome} ---", 0, 1, "L")
    for turno_obj in turni:
      pdf.set_font("Arial", "B", 11)
      pdf.cell(0, 7, f"Turno {turno_obj['turno']}", 0, 1, "L")
      pdf.set_font("Arial", "", 10)
      for idx, m in enumerate(turno_obj["partite"]):
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


# --- BARRA LATERALE ---
st.sidebar.header("⚙️ Pannello di Controllo")
st.sidebar.markdown(
    f"📅 **Giorni di Torneo:** `{db.get('num_giorni', 1)}` impostati"
)
st.sidebar.markdown(
    f"🎯 **Squadre che passano:** `{db.get('squadre_che_passano', 4)}` per"
    " girone"
)
st.sidebar.markdown("---")

if db["stato"] != "setup":
  pdf_data = genera_pdf_coppie()
  st.sidebar.download_button(
      label="📥 Scarica Schema in PDF",
      data=pdf_data,
      file_name="schema_gironi_torneo.pdf",
      mime="application/pdf",
      use_container_width=True,
  )
  st.sidebar.markdown("---")

modalita_admin = st.sidebar.checkbox("Modalità Amministratore (PIN)")
is_admin = False
if modalita_admin:
  pin_inserito = st.sidebar.text_input("Inserisci PIN Admin", type="password")
  if pin_inserito == db["admin_pin"]:
    is_admin = True
    st.sidebar.success("Accesso Admin Autorizzato ✅")
  else:
    st.sidebar.error("PIN errato.")

st.sidebar.markdown("---")

if is_admin:
  if st.sidebar.button(
      "⚙️ Mostra / Nascondi Setup Iniziale", use_container_width=True
  ):
    st.session_state["mostra_setup"] = not st.session_state.get(
        "mostra_setup", False
    )

if is_admin and db["stato"] == "fasi_finali":
  if st.sidebar.button(
      "🔙 Torna temporaneamente ai Gironi", use_container_width=True
  ):
    db["stato"] = "gironi"
    salva_dati(db)
    st.rerun()
  st.sidebar.markdown("---")

st.sidebar.subheader("⚠️ Zona Pericolo")
if is_admin:
  conferma_reset = st.sidebar.checkbox(
      "Spunta per confermare il reset totale", key="checkbox_reset_gara"
  )
  if st.sidebar.button("🔄 Ricomincia la gara da zero", use_container_width=True):
    if conferma_reset:
      if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
      for key in list(st.session_state.keys()):
        del st.session_state[key]
      st.success("Torneo azzerato con successo! Ricarico...")
      st.rerun()
    else:
      st.sidebar.warning(
          "⚠️ Spunta la casella di conferma sopra per procedere."
      )
else:
  st.sidebar.info("🔐 Accedi come admin per resettare la gara.")

st.sidebar.markdown("---")

# --- INTERFACCIA PRINCIPALE ---
st.markdown(
    """
    <div style="text-align: left; margin-bottom: 10px;">
        <h1 style="font-size: 28px; white-space: nowrap; margin: 0; padding: 0; color: #ffffff; text-shadow: 0 0 15px rgba(0,240,255,0.7), 0 0 30px rgba(0,240,255,0.4);">
            🏆 Torneo Coppie Fisse Live
        </h1>
        <p style="font-size: 15px; color: #00f0ff; margin: 6px 0 0 0; font-weight: 600; text-shadow: 0 0 8px rgba(0,240,255,0.5);">
            Regolamento 3 Tocchi Uisp • Modalità Gaming Neon Azzurro Elettrico
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("ℹ️ Come funziona il torneo"):
  st.markdown(
      """
        L'app è strutturata per far sì che il torneo vada avanti in maniera autonoma e automatica. Chi organizza può modificare eventuali errori di gol o partite segnate. I giorni e le qualificazioni si impostano all'inizio.
        """
  )

st.markdown(
    """
    <div style="padding: 12px 14px; background: linear-gradient(135deg, #0d234a 0%, #030b1c 100%); border: 2px solid #00f0ff; border-radius: 10px; font-size: 14px; color: #ffffff; margin-bottom: 15px; font-weight: bold; line-height: 1.5; box-shadow: 0 0 20px rgba(0,240,255,0.4);">
        🚨 <span style="color: #00f0ff; text-shadow: 0 0 8px rgba(0,240,255,0.8);">REGOLA CHIAVE:</span> Chi vince inserisce il risultato esatto e chi è in coda deve essere pronto a salire al primo calcetto libero.
    </div>
    """,
    unsafe_allow_html=True,
)

tutte_le_coppie = []
for g_lst in db["gironi"].values():
  tutte_le_coppie.extend(g_lst)
if not tutte_le_coppie and db.get("coppie"):
  tutte_le_coppie = db["coppie"]

opzioni_selettore = ["-- Seleziona la tua coppia per accedere --"] + sorted(
    tutte_le_coppie
)
coppia_url = st.query_params.get(
    "coppia", "-- Seleziona la tua coppia per accedere --"
)
if coppia_url not in opzioni_selettore:
  coppia_url = "-- Seleziona la tua coppia per accedere --"

coppia_selezionata = st.selectbox(
    "📱 Seleziona la tua coppia:",
    options=opzioni_selettore,
    index=opzioni_selettore.index(coppia_url),
    key="widget_selezione_coppia",
)

if coppia_selezionata != coppia_url:
  st.query_params["coppia"] = coppia_selezionata
  st.rerun()

if is_admin:
  st.success(
      "🛡️ **Modalità Amministratore attiva:** Accesso completo sbloccato."
  )
elif coppia_selezionata == "-- Seleziona la tua coppia per accedere --":
  st.warning(
      "⚠️ **Attenzione:** Seleziona la tua coppia dal menu a tendina per"
      " sbloccare l'accesso e inserire i risultati."
  )
  st.stop()
else:
  st.success(f"✅ Accesso effettuato come: **{coppia_selezionata}**")

if not is_admin or coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
  if coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
    with st.expander(
        f"👁️ Segui la tua coppia: {coppia_selezionata}", expanded=True
    ):
      girone_mio = None
      pos_mia = None
      info_mie = None
      for g_nome, lista_c in db["gironi"].items():
        if coppia_selezionata in lista_c:
          girone_mio = g_nome
          ricalcola_classifiche_gironi()
          if g_nome in db["punti_gironi"]:
            dati_g = db["punti_gironi"][g_nome]
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
          <div style="background: linear-gradient(135deg, #081b33 0%, #030712 100%); border: 2.5px solid #00f0ff; border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 0 30px rgba(0,240,255,0.4);">
              <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; color: #00f0ff; font-weight: bold; margin-bottom: 4px; text-shadow: 0 0 6px rgba(0,240,255,0.6);">Riepilogo Squadra</div>
              <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-bottom: 14px; text-shadow: 0 0 15px rgba(0,240,255,0.8);">🤝 {coppia_selezionata}</div>
              <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                  <div style="background: #040914; border: 1.5px solid #00f0ff; border-radius: 10px; padding: 12px 16px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 10px rgba(0,240,255,0.2);">
                      <div style="font-size: 11px; color: #93c5fd; font-weight: bold;">GIRONE</div>
                      <div style="font-size: 18px; font-weight: 700; color: #00f0ff; margin-top: 2px; text-shadow: 0 0 8px rgba(0,240,255,0.6);">{girone_mio if girone_mio else 'N.D.'}</div>
                  </div>
                  <div style="background: #040914; border: 1.5px solid #00f0ff; border-radius: 10px; padding: 12px 16px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 10px rgba(0,240,255,0.2);">
                      <div style="font-size: 11px; color: #93c5fd; font-weight: bold;">POSIZIONE</div>
                      <div style="font-size: 18px; font-weight: 700; color: #3fb950; margin-top: 2px; text-shadow: 0 0 8px rgba(63,185,80,0.6);">{str(pos_mia) + '° posto' if pos_mia else 'N.D.'}</div>
                  </div>
                  <div style="background: #040914; border: 1.5px solid #00f0ff; border-radius: 10px; padding: 12px 16px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 10px rgba(0,240,255,0.2);">
                      <div style="font-size: 11px; color: #93c5fd; font-weight: bold;">PUNTI / DR</div>
                      <div style="font-size: 18px; font-weight: 700; color: #fbbf24; margin-top: 2px; text-shadow: 0 0 8px rgba(251,191,36,0.6);">{info_mie['punti'] if info_mie else 0} pt <span style="font-size: 12px; font-weight: normal; color: #93c5fd;">(DR: {info_mie['dr'] if info_mie else 0})</span></div>
                  </div>
              </div>
          </div>
          """,
          unsafe_allow_html=True,
      )

# --- 1. SETUP ---
if db["stato"] == "setup" or st.session_state.get("mostra_setup", False):
  st.markdown(
      "<h3 style='color: #00f0ff; text-shadow: 0 0 10px"
      " rgba(0,240,255,0.6);'>1. Configurazione Iniziale Torneo a Coppie</h3>",
      unsafe_allow_html=True,
  )

  if not is_admin:
    st.warning("⚠️ Configurazione bloccata. Accedi come amministratore.")
  else:
    whatsapp_text = st.text_area(
        "Incolla qui la lista delle coppie da WhatsApp:", height=150
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
      db["num_tavoli"] = st.number_input(
          "Num. Biliardini",
          min_value=1,
          max_value=10,
          value=int(db.get("num_tavoli", 6)),
      )
    with col2:
      db["num_gironi"] = st.number_input(
          "Num. Gironi",
          min_value=1,
          max_value=8,
          value=int(db.get("num_gironi", 4)),
      )
    with col3:
      db["num_giorni"] = st.number_input(
          "Num. Giorni Torneo",
          min_value=1,
          max_value=30,
          value=int(db.get("num_giorni", 1)),
      )
    with col4:
      db["squadre_che_passano"] = st.number_input(
          "Quante passano/girone",
          min_value=1,
          max_value=16,
          value=int(db.get("squadre_che_passano", 4)),
      )

    db["admin_pin"] = st.text_input(
        "Cambia PIN Admin", value=db.get("admin_pin", "0000")
    )

    if st.button("🚀 Crea Gironi e Sorteggia Coppie", use_container_width=True):
      coppie = []
      for line in whatsapp_text.split("\n"):
        nome_c = pulisci_nome(line)
        if nome_c:
          coppie.append(nome_c)

      num_g = int(db["num_gironi"])

      if len(coppie) < (num_g * 2):
        st.error(
            f"Hai inserito {len(coppie)} coppie. Con {num_g} gironi servono"
            f" almeno {num_g * 2} coppie."
        )
      else:
        db["coppie"] = coppie
        random.shuffle(coppie)

        nomi_gironi = [chr(65 + i) for i in range(num_g)]
        gironi_dict = {f"Girone {g}": [] for g in nomi_gironi}

        for idx, c in enumerate(coppie):
          g_scelto = f"Girone {nomi_gironi[idx % num_g]}"
          gironi_dict[g_scelto].append(c)

        db["gironi"] = gironi_dict
        db["punti_gironi"] = {
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
          turni_turno = []

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
            turni_turno.append({"turno": t + 1, "partite": partite_turno})
            squadre = [squadre[0]] + [squadre[-1]] + squadre[1:-1]

          calendario_totale[g_nome] = turni_turno

        db["calendario_gironi"] = calendario_totale
        db["stato"] = "gironi"
        db["fasi_finali_configurate"] = False
        db["tabellone_a"] = []
        salva_dati(db)
        st.success(f"Creati con successo {num_g} gironi!")
        st.session_state["mostra_setup"] = False
        st.rerun()
  st.markdown("---")

# --- 2. FASE A GIRONI ---
if db["stato"] == "gironi":
  ricalcola_classifiche_gironi()
  num_tavoli = db.get("num_tavoli", 6)

  max_turni = (
      max([len(turni) for turni in db["calendario_gironi"].values()])
      if db["calendario_gironi"]
      else 0
  )

  partite_per_girone_dict = {}
  for t_num in range(1, max_turni + 1):
    for g_nome, turni_girone in db["calendario_gironi"].items():
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

  st.markdown(
      "<h3 style='color: #00f0ff; text-shadow: 0 0 10px"
      " rgba(0,240,255,0.6);'>⚡ Stato dei Biliardini e Coda Incontri</h3>",
      unsafe_allow_html=True,
  )

  col_ic, col_coda = st.columns(2)

  with col_ic:
    st.markdown(
        "<h4 style='color: #ffae00; text-shadow: 0 0 8px"
        " rgba(255,174,0,0.6);'>🔥 Partite in Corso ai Tavoli</h4>",
        unsafe_allow_html=True,
    )
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

        with st.container():
          st.markdown(
              f"""
                        <div style="background: linear-gradient(135deg, #261e08 0%, #100c02 100%); border: 3px solid #ffae00; padding: 18px; border-radius: 14px; margin-bottom: 12px; text-align: center; box-shadow: 0 4px 20px rgba(255,174,0,0.3);">
                            <div style="font-size: 15px; color: #ffae00; font-weight: bold; margin-bottom: 8px; text-shadow: 0 0 8px rgba(255,174,0,0.6);">{tavolo_str}</div>
                            <div style="font-size: 17px; font-weight: bold; color: #ffffff; line-height: 1.4;">🤝 {m['c1']}</div>
                            <div style="margin: 4px 0; font-size: 13px; font-weight: bold; color: #00f0ff;">VS</div>
                            <div style="font-size: 17px; font-weight: bold; color: #ffffff; line-height: 1.4;">🤝 {m['c2']}</div>
                        </div>
                        """,
              unsafe_allow_html=True,
          )

          if fa_al_caso_nostro:
            with st.expander(
                f"📝 Inserisci Risultato Tavolo {m.get('tavolo', '')}"
            ):
              gol_p1 = st.pills(
                  f"Gol {m['c1']}",
                  options=[0, 1, 2, 3, 4, 5, 6, 7],
                  default=int(m.get("gol1", 0)),
                  key=f"user_g1_{match_id}",
              )
              gol_p2 = st.pills(
                  f"Gol {m['c2']}",
                  options=[0, 1, 2, 3, 4, 5, 6, 7],
                  default=int(m.get("gol2", 0)),
                  key=f"user_g2_{match_id}",
              )
              if st.button(
                  "✅ Conferma e Registra Risultato",
                  key=f"user_save_{match_id}",
                  use_container_width=True,
              ):
                m["gol1"] = int(gol_p1) if gol_p1 is not None else 0
                m["gol2"] = int(gol_p2) if gol_p2 is not None else 0
                m["giocata"] = True
                m["in_corso"] = False
                m["tavolo"] = None
                ricalcola_classifiche_gironi()
                salva_dati(db)
                st.success("Risultato registrato! Tavolo liberato.")
                st.rerun()

          if is_admin:
            if st.button(
                f"🛑 Libera Tavolo {m.get('tavolo')} (Admin)",
                key=f"admin_libera_{match_id}",
            ):
              m["in_corso"] = False
              m["tavolo"] = None
              salva_dati(db)
              st.rerun()

  with col_coda:
    st.markdown(
        "<h4 style='color: #00f0ff; text-shadow: 0 0 8px"
        " rgba(0,240,255,0.6);'>⏳ In Coda (Prossimi Incontri)</h4>",
        unsafe_allow_html=True,
    )
    partite_in_coda_correnti = partite_da_giocare[:num_tavoli]
    if not partite_in_coda_correnti:
      st.info("La coda è vuota.")
    else:
      for idx, m in enumerate(partite_in_coda_correnti):
        st.markdown(
            f"""
                    <div style="background: linear-gradient(135deg, #081b33 0%, #030712 100%); border: 2px solid #00f0ff; padding: 14px; border-radius: 10px; margin-bottom: 10px; color: #00f0ff; text-align: center; box-shadow: 0 0 15px rgba(0,240,255,0.3);">
                        <b style="font-size: 13px; text-shadow: 0 0 6px rgba(0,240,255,0.8);">⏳ {idx+1}. {m['girone']}</b><br>
                        <div style="font-weight: bold; font-size: 14px; margin-top: 4px; color: #ffffff;">{m['c1']} vs {m['c2']}</div>
                    </div>
                    """,
            unsafe_allow_html=True,
        )

  st.markdown("---")

  # --- CLASSIFICHE DEI GIRONI ---
  st.markdown(
      "<h3 style='color: #00f0ff; text-shadow: 0 0 10px"
      " rgba(0,240,255,0.6);'>📊 Classifiche e Risultati Gironi</h3>",
      unsafe_allow_html=True,
  )

  tab_gironi = st.tabs(list(db["gironi"].keys()))

  for idx, (g_nome, tab) in enumerate(zip(db["gironi"].keys(), tab_gironi)):
    with tab:
      st.markdown(
          f"<h4 style='color: #00f0ff;'>Classifica - {g_nome}</h4>",
          unsafe_allow_html=True,
      )
      ricalcola_classifiche_gironi()
      dati_g = db["punti_gironi"].get(g_nome, {})

      righe = []
      sorted_coppie = sorted(
          dati_g.items(),
          key=lambda x: (
              x[1]["punti"],
              x[1]["scontri_diretti_pt"],
              x[1]["dr"],
              x[1]["gf"],
          ),
          reverse=True,
      )

      squadre_che_passano = db.get("squadre_che_passano", 4)

      for pos, (c_nome, stats) in enumerate(sorted_coppie):
        giocate_fatte, giocate_tot = calcola_giocate = (
            calcola_partite_giocate_coppia(g_nome, c_nome)
        )
        passa_turno = "🟢 Sì" if pos < squadre_che_passano else "🔴 No"
        righe.append({
            "Pos": f"{pos+1}°",
            "Coppia": c_nome,
            "Pt": stats["punti"],
            "G": f"{giocate_fatte}/{giocate_tot}",
            "GF": stats["gf"],
            "GS": stats["gs"],
            "DR": stats["dr"],
            "Passa": passa_turno,
        })

      if righe:
        df_classifica = pd.DataFrame(righe)
        st.dataframe(df_classifica, use_container_width=True, hide_index=True)
      else:
        st.info("Nessuna squadra in questo girone.")

      with st.expander(f"Calendario e Risultati completi - {g_nome}"):
        if g_nome in db["calendario_gironi"]:
          for turno_obj in db["calendario_gironi"][g_nome]:
            st.markdown(f"**Turno {turno_obj['turno']}**")
            for m in turno_obj["partite"]:
              c1_testo = evidenzia_nome_coppia(m["c1"], coppia_selezionata)
              c2_testo = evidenzia_nome_coppia(m["c2"], coppia_selezionata)

              col_m1, col_m2, col_m3 = (
                  st.columns([3, 1, 1]) if is_admin else st.columns([4, 1, 0.1])
              )
              with col_m1:
                st.markdown(
                    f"{c1_testo} vs {c2_testo}", unsafe_allow_html=True
                )
              with col_m2:
                ris = (
                    f"{m['gol1']} - {m['gol2']}"
                    if m.get("giocata", False)
                    else "Da giocare"
                )
                st.text(ris)

              if is_admin:
                with col_m3:
                  if st.button("Mod", key=f"mod_{m['id']}"):
                    m["giocata"] = not m.get("giocata", False)
                    ricalcola_classifiche_gironi()
                    salva_dati(db)
                    st.rerun()
            st.markdown("---")

  # --- GESTIONE ADMIN: AVVIO FASI FINALI ---
  st.markdown("---")
  if is_admin:
    st.markdown(
        "<h3 style='color: #ffae00; text-shadow: 0 0 10px"
        " rgba(255,174,0,0.6);'>⚙️ Pannello Fasi Finali (Admin)</h3>",
        unsafe_allow_html=True,
    )
    if st.button("🏆 Genera Tabellone Fasi Finali", use_container_width=True):
      squadre_passate_totali = []
      squadre_che_passano = db.get("squadre_che_passano", 4)
      ricalcola_classifiche_gironi()

      for g_nome, dati_g in db["punti_gironi"].items():
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
        passano_girone = [c[0] for c in sorted_c[:squadre_che_passano]]
        squadre_passate_totali.extend(passano_girone)

      random.shuffle(squadre_passate_totali)
      db["tabellone_a"] = []
      for i in range(0, len(squadre_passate_totali) - 1, 2):
        db["tabellone_a"].append({
            "c1": squadre_passate_totali[i],
            "c2": squadre_passate_totali[i + 1],
            "gol1": 0,
            "gol2": 0,
            "giocata": False,
        })

      db["stato"] = "fasi_finali"
      db["fasi_finali_configurate"] = True
      salva_dati(db)
      st.success("Fasi finali generate con successo!")
      st.rerun()

# --- 3. FASI FINALI ---
elif db["stato"] == "fasi_finali":
  st.markdown(
      "<h3 style='color: #00f0ff; text-shadow: 0 0 10px"
      " rgba(0,240,255,0.6);'>🏆 Fasi Finali del Torneo</h3>",
      unsafe_allow_html=True,
  )
  for idx, m in enumerate(db["tabellone_a"]):
    st.markdown(
        f"**Match {idx+1}:** {m['c1']} vs {m['c2']} — Risultato: {m['gol1']} -"
        f" {m['gol2']}"
    )
    if is_admin:
      g1 = st.number_input(
          f"Gol {m['c1']} (Match {idx+1})",
          value=m["gol1"],
          key=f"ff_g1_{idx}",
      )
      g2 = st.number_input(
          f"Gol {m['c2']} (Match {idx+1})",
          value=m["gol2"],
          key=f"ff_g2_{idx}",
      )
      if st.button(f"Salva Match {idx+1}", key=f"btn_ff_{idx}"):
        m["gol1"] = g1
        m["gol2"] = g2
        m["giocata"] = True
        salva_dati(db)
        st.success("Salvato!")
        st.rerun()

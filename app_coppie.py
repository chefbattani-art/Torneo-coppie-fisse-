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
    page_title="Torneo Coppie Fisse Live - Cyber Gaming Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STILE GRAFICO GLOBALE: CYBERPUNK & NEON ARCADE ESPORTS (CON FIX SELECTBOX & SAFARI) ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Orbitron:wght@600;800;900&family=Inter:wght@400;600;800&display=swap');

        /* --- BLOCCO ANTI-SFONDO BIANCO (SAFARI & DARK MODE) --- */
        :root {
            color-scheme: dark !important;
        }

        .stApp {
            background-color: #05070f;
            background-image: 
                radial-gradient(circle at 50% 10%, rgba(0, 242, 254, 0.08) 0%, transparent 60%),
                radial-gradient(circle at 10% 90%, rgba(255, 0, 127, 0.06) 0%, transparent 50%),
                linear-gradient(to right, rgba(0, 242, 254, 0.03) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(0, 242, 254, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
            color: #f0f6fc;
            font-family: 'Inter', sans-serif;
            color-scheme: dark !important;
        }
        
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070a17, #020408);
            border-right: 2px solid rgba(0, 242, 254, 0.2);
            box-shadow: 8px 0 30px rgba(0, 242, 254, 0.08);
        }

        /* --- FORZA SFONDO E TESTO SCURO PER I SELECTBOX (MENU A TENDINA) --- */
        div[data-baseweb="select"] > div {
            background-color: #161f30 !important;
            color: white !important;
            border-color: #00f2fe !important;
        }
        div[data-baseweb="select"] span {
            color: white !important;
        }
        div[data-baseweb="popover"] div {
            background-color: #161f30 !important;
            color: white !important;
        }
        ul[data-baseweb="menu"] {
            background-color: #161f30 !important;
        }
        li[data-baseweb="option"] {
            background-color: #161f30 !important;
            color: white !important;
        }
        li[data-baseweb="option"]:hover {
            background-color: #1d3557 !important;
            color: #00f2fe !important;
        }

        /* Correzione per componenti nativi che Safari inverte in bianco */
        .streamlit-expanderHeader, 
        [data-testid="stExpander"], 
        [data-testid="stContainer"],
        [data-testid="stVerticalBlock"] div {
            color-scheme: dark !important;
        }

        .neon-title-box {
            border: 2px solid #00f2fe;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.4), inset 0 0 15px rgba(0, 242, 254, 0.1);
            border-radius: 18px;
            padding: 24px;
            text-align: center;
            background: linear-gradient(135deg, rgba(16, 22, 36, 0.95) 0%, rgba(8, 12, 20, 0.98) 100%);
            margin-bottom: 20px;
        }
        .neon-title-text {
            color: #00ff66 !important;
            font-family: 'Rajdhani', sans-serif !important;
            font-size: 34px;
            font-weight: 900;
            text-shadow: 0 0 15px rgba(0,255,102,0.9), 0 0 30px rgba(0,255,102,0.5);
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .neon-subtitle {
            color: #8b949e;
            font-size: 14px;
            margin-top: 6px;
            font-weight: 600;
        }

        .neon-box-main {
            background: linear-gradient(135deg, rgba(16, 22, 36, 0.95) 0%, rgba(8, 12, 20, 0.98) 100%);
            border: 2px solid #00f2fe;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.25), inset 0 0 15px rgba(0, 242, 254, 0.08);
            position: relative;
        }

        .match-live-card {
            background: linear-gradient(135deg, rgba(30, 20, 10, 0.95) 0%, rgba(12, 8, 4, 0.98) 100%);
            border: 2px solid #ffaa00;
            border-radius: 16px;
            padding: 22px;
            text-align: center;
            box-shadow: 0 0 30px rgba(255, 170, 0, 0.35), inset 0 0 15px rgba(255, 170, 0, 0.1);
        }

        .neon-gold { color: #ffaa00 !important; text-shadow: 0 0 12px rgba(255,170,0,0.8), 0 0 25px rgba(255,170,0,0.4); }
        .neon-blue { color: #00f2fe !important; text-shadow: 0 0 12px rgba(0,242,254,0.8), 0 0 25px rgba(0,242,254,0.4); }
        .neon-purple { color: #d946ef !important; text-shadow: 0 0 12px rgba(217,70,239,0.8), 0 0 25px rgba(217,70,239,0.4); }
        .neon-red { color: #ff3366 !important; text-shadow: 0 0 12px rgba(255,51,102,0.8), 0 0 25px rgba(255,51,102,0.4); }
        .neon-green { color: #00ff66 !important; text-shadow: 0 0 12px rgba(0,255,102,0.8), 0 0 25px rgba(0,255,102,0.4); }
        .neon-silver { color: #e2e8f0 !important; text-shadow: 0 0 12px rgba(226,232,240,0.7), 0 0 25px rgba(226,232,240,0.3); }

        h1, h2, h3, h4 {
            font-family: 'Rajdhani', sans-serif !important;
            color: #ffffff !important;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 800;
            font-family: 'Rajdhani', sans-serif;
            font-size: 20px;
            height: 55px !important;
            letter-spacing: 1px;
            border: 1.5px solid rgba(0, 242, 254, 0.5);
            background: linear-gradient(180deg, #132238, #0a111c);
            color: #00f2fe;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div.stButton > button:hover {
            border-color: #00f2fe;
            background: linear-gradient(180deg, #1d3557, #0f2038);
            color: #ffffff;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.8), inset 0 0 12px rgba(0, 242, 254, 0.3);
            transform: translateY(-2px);
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
      "admin_pin": "0000",
      "gironi": {},
      "calendario_gironi": {},
      "punti_gironi": {},
      "fasi_finali_configurate": False,
      "num_qualificate_knockout": 4,
      "tabellone_a": [],
      "tabellone_b": [],
      "terzo_quarto_a": [],
      "terzo_quarto_b": [],
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


def ricalcola_classifiche_gironi():
  for g_nome, coppie_lista in db["gironi"].items():
    stats = {
        c: {
            "punti": 0,
            "partite_giocate": 0,
            "vinte": 0,
            "perse": 0,
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

            stats[c1]["partite_giocate"] += 1
            stats[c2]["partite_giocate"] += 1

            if g1 > g2:
              pt_s1, pt_s2 = (3, 0) if diff >= 2 else (2, 1)
              stats[c1]["vinte"] += 1
              stats[c2]["perse"] += 1
            elif g2 > g1:
              pt_s1, pt_s2 = (0, 3) if diff >= 2 else (1, 2)
              stats[c2]["vinte"] += 1
              stats[c1]["perse"] += 1
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


def ottieni_nome_turno_dinamico(num_partite_turno):
  if num_partite_turno == 1:
    return "🏆 FINALE SUPREMA"
  elif num_partite_turno == 2:
    return "⚔️ SEMIFINALI EPICHE"
  elif num_partite_turno == 4:
    return "🔥 QUARTI DI FINALE"
  else:
    return f"Fase a Eliminazione ({num_partite_turno * 2} Coppie)"


def crea_abbinamenti_fascia_a_6_squadre(classificate_lista):
  # Gestione sicura per qualsiasi numero di squadre qualificate (evita IndexError)
  if len(classificate_lista) >= 6:
    s3, s4, s5, s6 = (
        classificate_lista[2],
        classificate_lista[3],
        classificate_lista[4],
        classificate_lista[5],
    )
    return [(s3, s6), (s4, s5)]
  elif len(classificate_lista) >= 4:
    s3, s4 = classificate_lista[2], classificate_lista[3]
    return [(s3, s4)]
  else:
    abbinamenti = []
    for i in range(0, len(classificate_lista) - 1, 2):
      abbinamenti.append((classificate_lista[i], classificate_lista[i+1]))
    return abbinamenti


def crea_turno_eliminazione_diretta(lista_squadre, prefix_id):
  partite = []
  squadre_temp = lista_squadre.copy()
  
  if len(squadre_temp) % 2 != 0:
    squadre_temp.append("RIPOSO")
    
  n = len(squadre_temp)
  for i in range(n // 2):
    s1 = squadre_temp[i]
    s2 = squadre_temp[n - 1 - i]
    partite.append({
        "id": f"{prefix_id}_m{i}",
        "s1": s1 if isinstance(s1, str) else s1[0],
        "g1": "",
        "p1": 0,
        "s2": s2 if isinstance(s2, str) else s2[0],
        "g2": "",
        "p2": 0,
        "giocata": False,
        "vincente": None,
    })
  return partite


def selettore_gol_bottoni(prefix, default_val=0):
  if prefix not in st.session_state:
    st.session_state[prefix] = int(default_val)

  val_corrente = st.session_state[prefix]
  st.markdown(
      f"<div style='font-size: 14px; color: #8b949e; margin-bottom: 6px;'>Gol selezionati: <b class='neon-blue' style='font-size: 18px;'>{val_corrente}</b></div>",
      unsafe_allow_html=True,
  )

  cols = st.columns(8)
  for g in range(8):
    with cols[g]:
      btn_label = f"✨ {g}" if val_corrente == g else str(g)
      if st.button(
          btn_label, key=f"btn_gol_{prefix}_{g}", use_container_width=True
      ):
        st.session_state[prefix] = g
        st.rerun()

  return st.session_state[prefix]


# --- BARRA LATERALE CYBER ---
st.sidebar.header("⚙️ Pannello Controllo")

if db["stato"] != "setup":
  pdf_data = genera_pdf_coppie()
  st.sidebar.download_button(
      label="📥 Scarica Schema PDF",
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
  if st.sidebar.button(
      "🔄 Ricomincia la gara da zero", use_container_width=True
  ):
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
    <div class="neon-title-box">
        <div class="neon-title-text">⚡ TORNEO COPPIE FISSE LIVE</div>
        <div class="neon-subtitle">Regolamento 3 Tocchi Uisp • Cyber Gaming & Esports Edition</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("ℹ️ Come funziona il torneo"):
  st.markdown(
      """
        L'app è strutturata per gestire in autonomia la fase a gironi e le fasi finali con scontro diretto, differenza reti e scontri diretti. 
        Le prime posizioni si qualificano in verde (accedendo alle semifinali o turni decisivi), mentre le ultime posizioni in rosso lottano nella fase di eliminazione o Fascia B.
        """,
      unsafe_allow_html=True,
  )

st.markdown(
    """
    <div style="padding: 16px 20px; background: linear-gradient(135deg, rgba(48, 16, 26, 0.95) 0%, rgba(24, 6, 12, 0.98) 100%); border: 2px solid #ff3366; border-radius: 16px; font-size: 14px; color: #ff3366; margin-bottom: 20px; font-weight: bold; line-height: 1.5; box-shadow: 0 0 30px rgba(255,51,102,0.35);">
        🚨 Chi vince è pregato di inserire il risultato esatto tramite i comodi pulsanti e chi è in coda alle partite di tenersi pronto a salire al primo calcetto libero.
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
  st.markdown(
      """
      <div style="padding: 12px 18px; background: linear-gradient(135deg, rgba(10, 36, 20, 0.95) 0%, rgba(4, 16, 8, 0.98) 100%); border: 2px solid #00ff66; border-radius: 14px; font-size: 14px; color: #00ff66; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 25px rgba(0,255,102,0.3);">
          🛡️ Modalità Amministratore attiva: Accesso completo sbloccato senza obbligo di selezione coppia.
      </div>
      """,
      unsafe_allow_html=True,
  )
elif coppia_selezionata == "-- Seleziona la tua coppia per accedere --":
  st.markdown(
      """
      <div style="padding: 14px 18px; background: linear-gradient(135deg, rgba(40, 32, 10, 0.95) 0%, rgba(16, 12, 4, 0.98) 100%); border: 2px solid #ffaa00; border-radius: 14px; font-size: 14px; color: #ffaa00; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 25px rgba(255,170,0,0.3);">
          ⚠️ Attenzione: Devi selezionare la tua coppia dal menu a tendina qui sopra per sbloccare l'accesso al torneo, vedere le partite e inserire i risultati.
      </div>
      """,
      unsafe_allow_html=True,
  )
  st.stop()
else:
  st.markdown(
      f"""
      <div style="padding: 12px 18px; background: linear-gradient(135deg, rgba(10, 36, 20, 0.95) 0%, rgba(4, 16, 8, 0.98) 100%); border: 2px solid #00ff66; border-radius: 14px; font-size: 14px; color: #00ff66; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 25px rgba(0,255,102,0.3);">
          ✅ Accesso effettuato come: <b>{coppia_selezionata}</b>
      </div>
      """,
      unsafe_allow_html=True,
  )

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

      match_in_corso_coppia = None
      pos_in_coda = None

      if db["stato"] == "gironi":
        num_tavoli = db.get("num_tavoli", 6)
        max_turni = (
            max([len(turni) for turni in db["calendario_gironi"].values()])
            if db["calendario_gironi"]
            else 0
        )
        for t_num in range(1, max_turni + 1):
          for g_n, turni_girone in db["calendario_gironi"].items():
            for t_obj in turni_girone:
              if t_obj["turno"] == t_num:
                for m in t_obj["partite"]:
                  if not m.get("giocata", False):
                    if (
                        m["c1"] == coppia_selezionata
                        or m["c2"] == coppia_selezionata
                    ):
                      if m.get("in_corso", False):
                        match_in_corso_coppia = m

        all_da_giocare = []
        for t_num in range(1, max_turni + 1):
          for g_n in sorted(db["calendario_gironi"].keys()):
            for t_obj in db["calendario_gironi"][g_n]:
              if t_obj["turno"] == t_num:
                for m in t_obj["partite"]:
                  if not m.get("giocata", False) and not m.get(
                      "in_corso", False
                  ):
                    all_da_giocare.append(m)

        for idx_coda, m_coda in enumerate(all_da_giocare[:num_tavoli]):
          if (
              m_coda["c1"] == coppia_selezionata
              or m_coda["c2"] == coppia_selezionata
          ):
            pos_in_coda = idx_coda + 1

      st.markdown(
          f"""
          <div class="neon-box-main">
              <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #d946ef; font-weight: bold; margin-bottom: 6px;">Riepilogo Squadra</div>
              <div style="font-size: 24px; font-weight: 800; color: #ffffff; margin-bottom: 16px; text-shadow: 0 0 15px rgba(0,242,254,0.6);">🤝 {coppia_selezionata}</div>
              <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                  <div style="background: rgba(8, 12, 20, 0.85); border: 1.5px solid rgba(0, 242, 254, 0.5); border-radius: 12px; padding: 14px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 15px rgba(0,242,254,0.2);">
                      <div style="font-size: 11px; color: #8b949e; font-weight: bold;">GIRONE</div>
                      <div class="neon-blue" style="font-size: 20px; font-weight: 700; margin-top: 4px;">{girone_mio if girone_mio else 'N.D.'}</div>
                  </div>
                  <div style="background: rgba(8, 12, 20, 0.85); border: 1.5px solid rgba(0, 255, 102, 0.5); border-radius: 12px; padding: 14px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 15px rgba(0,255,102,0.2);">
                      <div style="font-size: 11px; color: #8b949e; font-weight: bold;">POSIZIONE</div>
                      <div class="neon-green" style="font-size: 20px; font-weight: 700; margin-top: 4px;">{str(pos_mia) + '° posto' if pos_mia else 'N.D.'}</div>
                  </div>
                  <div style="background: rgba(8, 12, 20, 0.85); border: 1.5px solid rgba(255, 170, 0, 0.5); border-radius: 12px; padding: 14px; flex: 1; min-width: 110px; text-align: center; box-shadow: 0 0 15px rgba(255,170,0,0.2);">
                      <div style="font-size: 11px; color: #8b949e; font-weight: bold;">PUNTI / DR</div>
                      <div class="neon-gold" style="font-size: 20px; font-weight: 700; margin-top: 4px;">{info_mie['punti'] if info_mie else 0} pt <span style="font-size: 12px; font-weight: normal; color: #8b949e;">(DR: {info_mie['dr'] if info_mie else 0})</span></div>
                  </div>
              </div>
          </div>
          """,
          unsafe_allow_html=True,
      )

      if match_in_corso_coppia:
        avversario = (
            match_in_corso_coppia["c2"]
            if match_in_corso_coppia["c1"] == coppia_selezionata
            else match_in_corso_coppia["c1"]
        )
        tavolo_num = match_in_corso_coppia.get("tavolo", "N.D.")
        match_id = match_in_corso_coppia["id"]

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(30, 20, 10, 0.95) 0%, rgba(12, 8, 4, 0.98) 100%); border: 2px solid #ffaa00; border-radius: 14px; padding: 16px; margin-bottom: 20px; text-align: center; box-shadow: 0 0 25px rgba(255,170,0,0.3);">
                <div class="neon-gold" style="font-size: 15px; font-weight: bold; margin-bottom: 6px;">🔴 PARTITA IN CORSO AL BILIARDINO {tavolo_num}!</div>
                <div style="font-size: 16px; color: #ffffff;">Stai giocando contro: <b>{avversario}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(
            "⚙️ Inserisci Risultato con i Bottoni", expanded=True
        ):
          st.markdown(f"**⚽ Gol per {match_in_corso_coppia['c1']}**")
          gol_p1 = selettore_gol_bottoni(
              f"riep_g1_{match_id}", int(match_in_corso_coppia.get("gol1", 0))
          )

          st.markdown(f"**⚽ Gol per {match_in_corso_coppia['c2']}**")
          gol_p2 = selettore_gol_bottoni(
              f"riep_g2_{match_id}", int(match_in_corso_coppia.get("gol2", 0))
          )

          if st.button(
              "✅ Salva e Registra Risultato",
              key=f"riepilogo_save_{match_id}",
              use_container_width=True,
          ):
            match_in_corso_coppia["gol1"] = int(gol_p1)
            match_in_corso_coppia["gol2"] = int(gol_p2)
            match_in_corso_coppia["giocata"] = True
            match_in_corso_coppia["in_corso"] = False
            match_in_corso_coppia["tavolo"] = None
            ricalcola_classifiche_gironi()
            salva_dati(db)
            st.success("Risultato salvato con successo!")
            st.rerun()

      elif pos_in_coda is not None:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(8, 36, 20, 0.9) 0%, rgba(2, 16, 8, 0.95) 100%); border: 1.5px solid #00ff66; border-radius: 14px; padding: 14px; margin-bottom: 20px; text-align: center; box-shadow: 0 0 20px rgba(0,255,102,0.2);">
                <div class="neon-green" style="font-size: 14px; font-weight: bold;">⏳ PARTITE IN CODA</div>
                <div style="font-size: 14px; color: #ffffff; margin-top: 4px;">La tua coppia è in posizione <b>#{pos_in_coda}</b> nella coda d'attesa per il prossimo biliardino libero. Teniti pronto!</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
      else:
        st.markdown(
            """
            <div style="background: rgba(16, 22, 36, 0.7); border: 1.5px solid rgba(0, 242, 254, 0.2); border-radius: 12px; padding: 12px; text-align: center; color: #8b949e; font-size: 13px; margin-bottom: 20px;">
                🟢 Nessuna partita attiva o in coda al momento per questa coppia.
            </div>
            """,
            unsafe_allow_html=True,
        )

# 1. SETUP INIZIALE
if db["stato"] == "setup" or st.session_state.get("mostra_setup", False):
  st.subheader("1. Configurazione Iniziale Torneo a Coppie")

  if not is_admin:
    st.markdown(
        """
        <div style="padding: 12px 18px; background: linear-gradient(135deg, rgba(40, 32, 10, 0.95) 0%, rgba(16, 12, 4, 0.98) 100%); border: 2px solid #ffaa00; border-radius: 14px; font-size: 14px; color: #ffaa00; margin-bottom: 20px; font-weight: bold; box-shadow: 0 0 25px rgba(255,170,0,0.3);">
            ⚠️ Configurazione bloccata. Accedi come amministratore dalla barra laterale con il PIN.
        </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    whatsapp_text = st.text_area(
        "Incolla qui la lista delle coppie da WhatsApp (es. 1 Fiore Gaffo):",
        height=150,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
      db["num_tavoli"] = st.number_input(
          "Numero di biliardini disponibili",
          min_value=1,
          max_value=10,
          value=int(db["num_tavoli"]),
      )
    with col2:
      db["num_gironi"] = st.number_input(
          "Numero di gironi da creare",
          min_value=1,
          max_value=8,
          value=int(db["num_gironi"]),
      )
    with col3:
      db["num_qualificate_knockout"] = st.number_input(
          "Coppie che si qualificano (Zona Verde)",
          min_value=1,
          max_value=8,
          value=int(db.get("num_qualificate_knockout", 4)),
      )

    db["admin_pin"] = st.text_input("Cambia PIN Admin", value=db["admin_pin"])

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
                    "partite_giocate": 0,
                    "vinte": 0,
                    "perse": 0,
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

        db["calendario_gironi"] = calendario_totale
        db["stato"] = "gironi"
        db["fasi_finali_configurate"] = False
        db["tabellone_a"] = []
        db["tabellone_b"] = []
        db["terzo_quarto_a"] = []
        db["terzo_quarto_b"] = []
        salva_dati(db)
        st.success(f"Creati con successo {num_g} gironi!")
        st.session_state["mostra_setup"] = False
        st.rerun()
  st.markdown("---")

# 2. FASE A GIRONI
if db["stato"] == "gironi":
  ricalcola_classifiche_gironi()
  num_tavoli = db.get("num_tavoli", 6)

  if db.get("fasi_finali_configurate", False) and is_admin:
    if st.button(
        "⬅️ Torna alla schermata delle Fasi Finali", use_container_width=True
    ):
      db["stato"] = "fasi_finali"
      salva_dati(db)
      st.rerun()
    st.markdown("---")

  if is_admin:
    with st.expander(
        "⚙️ Pannello Admin: Modifica Parametri Passaggio Turno", expanded=False
    ):
      db["num_qualificate_knockout"] = st.number_input(
          "Numero di coppie in Zona Verde (Qualificate):",
          min_value=1,
          max_value=10,
          value=int(db.get("num_qualificate_knockout", 4)),
          step=1,
      )
      salva_dati(db)

  soglia_passaggio = db.get("num_qualificate_knockout", 4)

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

  partite_in_corso, partite_da_giocare = [], []

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
      st.markdown(
          """
          <div style="background: rgba(16, 22, 36, 0.7); border: 1.5px solid rgba(0, 242, 254, 0.3); padding: 14px; border-radius: 12px; text-align: center; color: #8b949e; font-size: 13px;">
              Nessuna partita in corso al momento.
          </div>
          """,
          unsafe_allow_html=True,
      )
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
                        <div class="match-live-card" style="margin-bottom: 14px;">
                            <div class="neon-gold" style="font-size: 14px; font-weight: bold; margin-bottom: 8px;">{tavolo_str}</div>
                            <div style="font-size: 18px; font-weight: bold; color: #ffffff; line-height: 1.4;">🤝 {m['c1']}</div>
                            <div style="margin: 4px 0; font-size: 13px; font-weight: bold; color: #8b949e;">VS</div>
                            <div style="font-size: 18px; font-weight: bold; color: #ffffff; line-height: 1.4;">🤝 {m['c2']}</div>
                        </div>
                        """,
              unsafe_allow_html=True,
          )

          if fa_al_caso_nostro:
            with st.expander(
                f"📝 Inserisci Risultato Tavolo {m.get('tavolo', '')}"
            ):
              st.markdown(f"**⚽ Gol {m['c1']}**")
              gol_p1 = selettore_gol_bottoni(
                  f"live_g1_{match_id}", int(m.get("gol1", 0))
              )

              st.markdown(f"**⚽ Gol {m['c2']}**")
              gol_p2 = selettore_gol_bottoni(
                  f"live_g2_{match_id}", int(m.get("gol2", 0))
              )

              if st.button(
                  "✅ Conferma e Registra Risultato",
                  key=f"user_save_{match_id}",
                  use_container_width=True,
              ):
                m["gol1"] = int(gol_p1)
                m["gol2"] = int(gol_p2)
                m["giocata"] = True
                m["in_corso"] = False
                m["tavolo"] = None
                ricalcola_classifiche_gironi()
                salva_dati(db)
                st.success("Risultato registrato con successo!")
                st.rerun()

          if is_admin:
            with st.expander(f"⚙️ Opzioni Admin Tavolo {m.get('tavolo', '')}"):
              if st.button(
                  "🛑 Libera tavolo senza salvare",
                  key=f"admin_libera_{match_id}",
                  use_container_width=True,
              ):
                m["in_corso"] = False
                m["tavolo"] = None
                salva_dati(db)
                st.success("Tavolo liberato con successo!")
                st.rerun()

  with col_coda:
    partite_in_coda_correnti = partite_da_giocare[:num_tavoli]
    st.markdown("#### ⏳ In Coda (Prossimi Incontri)")
    if not partite_in_coda_correnti:
      st.markdown(
          """
          <div style="background: rgba(16, 22, 36, 0.7); border: 1.5px solid rgba(0, 242, 254, 0.3); padding: 14px; border-radius: 12px; text-align: center; color: #8b949e; font-size: 13px;">
              La coda è vuota.
          </div>
          """,
          unsafe_allow_html=True,
      )
    else:
      for idx, m in enumerate(partite_in_coda_correnti):
        st.markdown(
            f"""
                    <div style="background: linear-gradient(135deg, rgba(8, 36, 20, 0.9) 0%, rgba(2, 16, 8, 0.95) 100%); border: 2px solid #00ff66; padding: 14px; border-radius: 14px; margin-bottom: 12px; text-align: center; box-shadow: 0 0 25px rgba(0,255,102,0.3);">
                        <b class="neon-green" style="font-size: 13px;">⏳ {idx+1}. {m['girone']}</b><br>
                        <div style="font-weight: bold; font-size: 15px; margin-top: 6px; color: #ffffff;">{m['c1']} vs {m['c2']}</div>
                    </div>
                    """,
            unsafe_allow_html=True,
        )

  st.markdown("---")
  st.subheader("📊 Classifiche Ufficiali dei Gironi")
  st.markdown(
      '<div style="background: rgba(16,22,36,0.8); border: 1px solid #00f2fe; padding: 10px 14px; border-radius: 10px; margin-bottom: 15px; font-size: 13px; color: #8b949e; text-align: center;"><b>Legenda:</b> <span style="color: #00ff66; font-weight: bold;">🟢 Zona Qualificazione</span> | <span style="color: #ff3366; font-weight: bold;">🔴 Zona Eliminazione</span></div>',
      unsafe_allow_html=True,
  )

  nomi_gironi_chiavi = list(db["gironi"].keys())
  for g_nome in nomi_gironi_chiavi:
    with st.container():
      st.markdown(
          f"""
                <div style="background: linear-gradient(135deg, rgba(16, 22, 36, 0.95) 0%, rgba(8, 12, 20, 0.98) 100%); border: 2px solid #00f2fe; border-radius: 14px; padding: 14px; margin-bottom: 18px; box-shadow: 0 0 20px rgba(0,242,254,0.2);">
                    <div style="font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 900; color: #00f2fe; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">📁 {g_nome}</div>
                """,
          unsafe_allow_html=True,
      )

      dati_girone = db["punti_gironi"][g_nome]
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
        posizione = idx + 1
        in_zona_verde = posizione <= soglia_passaggio

        colore_bordo = (
            "rgba(0, 255, 102, 0.6)"
            if in_zona_verde
            else "rgba(255, 51, 102, 0.4)"
        )
        colore_sfondo = (
            "linear-gradient(135deg, rgba(0, 255, 102, 0.12) 0%, rgba(8, 12, 20, 0.9) 100%)"
            if in_zona_verde
            else "linear-gradient(135deg, rgba(255, 51, 102, 0.08) 0%, rgba(8, 12, 20, 0.9) 100%)"
        )
        simbolo_stato = "🟢" if in_zona_verde else "🔴"
        testo_colore_pos = "#00ff66" if in_zona_verde else "#ff3366"

        st.markdown(
            f"""
                <div style="background: {colore_sfondo}; border: 1.5px solid {colore_bordo}; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 15px; font-weight: 900; color: {testo_colore_pos}; min-width: 28px;">{posizione}° {simbolo_stato}</span>
                        <span style="font-size: 15px; font-weight: 700; color: #ffffff;">{coppia}</span>
                    </div>
                    <div style="display: flex; gap: 10px; font-size: 13px; text-align: right;">
                        <div><span style="color: #8b949e; font-size: 10px; display: block;">PT</span><b style="color: #ffaa00; font-size: 15px;">{info['punti']}</b></div>
                        <div><span style="color: #8b949e; font-size: 10px; display: block;">G</span>{info['partite_giocate']}</div>
                        <div><span style="color: #8b949e; font-size: 10px; display: block;">V/P</span>{info['vinte']}/{info['perse']}</div>
                        <div><span style="color: #8b949e; font-size: 10px; display: block;">DR</span><span style="color: {'#00ff66' if info['dr']>=0 else '#ff3366'};">{info['dr']:+d}</span></div>
                    </div>
                </div>
                """,
            unsafe_allow_html=True,
        )

      st.markdown("</div>", unsafe_allow_html=True)

  st.markdown("---")
  st.subheader("📅 Incontri per Girone")
  nomi_gironi_lista = list(db["calendario_gironi"].keys())
  if nomi_gironi_lista:
    tabs_gironi = st.tabs(nomi_gironi_lista)
    for idx_tab, g_nome in enumerate(nomi_gironi_lista):
      with tabs_gironi[idx_tab]:
        for turno_obj in db["calendario_gironi"][g_nome]:
          st.markdown(f"**Turno {turno_obj['turno']}**")
          for m in turno_obj["partite"]:
            match_id = m["id"]
            stato_testo = (
                f"<b class='neon-green'>{m['gol1']} - {m['gol2']}</b>"
                if m["giocata"]
                else "<span style='color: #8b949e;'>VS</span>"
            )
            st.markdown(
                f"""
                        <div style="background: linear-gradient(135deg, rgba(16, 22, 36, 0.9) 0%, rgba(8, 12, 20, 0.95) 100%); border: 1.5px solid rgba(0, 242, 254, 0.3); border-radius: 12px; padding: 14px; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.4);">
                            <b>{m['c1']}</b> vs <b>{m['c2']}</b><br>{stato_testo}
                        </div>
                        """,
                unsafe_allow_html=True,
            )
            if is_admin:
              with st.expander(f"⚙️ Gestisci: {m['c1']} vs {m['c2']}"):
                st.markdown(f"**⚽ Gol {m['c1']}**")
                rg1 = selettore_gol_bottoni(
                    f"admin_g1_{match_id}", int(m.get("gol1", 0))
                )
                st.markdown(f"**⚽ Gol {m['c2']}**")
                rg2 = selettore_gol_bottoni(
                    f"admin_g2_{match_id}", int(m.get("gol2", 0))
                )

                if st.button("💾 Salva Risultato", key=f"save_{match_id}", use_container_width=True):
                  m["gol1"] = int(rg1)
                  m["gol2"] = int(rg2)
                  m["giocata"] = True
                  m["in_corso"] = False
                  m["tavolo"] = None
                  ricalcola_classifiche_gironi()
                  salva_dati(db)
                  st.rerun()

  if is_admin:
    st.markdown("---")
    btn_text = (
        "🔄 Ricrea / Resetta Fasi Finali"
        if db.get("fasi_finali_configurate", False)
        else "🏆 Genera Fasi Finali"
    )
    if st.button(btn_text, use_container_width=True):
      classificate_a = {}
      squadre_fascia_b = []
      num_passano = db.get("num_qualificate_knockout", 4)

      for g_nome in db["gironi"]:
        dati_girone = db["punti_gironi"][g_nome]
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
        squadre_girone = [c[0] for c in sorted_c]
        
        classificate_a[g_nome] = squadre_girone[:num_passano]
        
        if len(squadre_girone) > num_passano:
          squadre_fascia_b.extend(squadre_girone[num_passano:])

      for g_nome, lista_squadre in classificate_a.items():
        abbinamenti_raw = crea_abbinamenti_fascia_a_6_squadre(lista_squadre)
        turno_a_iniziale = [
            {
                "id": f"fa_{g_nome}_t1_m{i}",
                "s1": s1,
                "g1": "",
                "p1": 0,
                "s2": s2,
                "g2": "",
                "p2": 0,
                "giocata": False,
                "vincente": None,
            }
            for i, (s1, s2) in enumerate(abbinamenti_raw)
        ]
        db["tabellone_a"] = [{"turno": 1, "partite": turno_a_iniziale}]
        break

      if squadre_fascia_b:
        partite_b_iniziali = crea_turno_eliminazione_diretta(squadre_fascia_b, "fa_b")
        db["tabellone_b"] = [{"turno": 1, "partite": partite_b_iniziali}]
      else:
        db["tabellone_b"] = []

      db["terzo_quarto_a"] = []
      db["terzo_quarto_b"] = []
      db["stato"] = "fasi_finali"
      db["fasi_finali_configurate"] = True
      salva_dati(db)
      st.success("Fasi finali e Tabellone Fascia B generati correttamente!")
      st.rerun()

# 3. FASI FINALI
elif db["stato"] == "fasi_finali":
  st.subheader("🏆 Fasi Finali: Tabelloni a Eliminazione Diretta")
  tab_a_view, tab_b_view = st.tabs(["⭐ Tabellone Principale", "🔻 Fascia B"])


  def gestisci_tabellone(chiave_tabellone, chiave_34, titolo_tab):
    st.markdown(f"### 📋 {titolo_tab}")
    turni_tab = db[chiave_tabellone]

    mappa_girone_pos = {}
    for g_nome, lista_sq in db["gironi"].items():
      dati_girone = db["punti_gironi"][g_nome]
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
      for idx, (sq, info) in enumerate(sorted_c):
        mappa_girone_pos[sq] = (g_nome, idx + 1)

    campione, secondo_posto, terzo_posto, quarto_posto = None, None, None, None

    for t_idx, turno_obj in enumerate(turni_tab):
      t_num = turno_obj["turno"]
      partite_turno = turno_obj["partite"]

      if t_num == 1 and chiave_tabellone == "tabellone_a":
        nome_etichetta = "🔥 Play-in (3° vs 6° e 4° vs 5°)"
      elif t_num == 2 and chiave_tabellone == "tabellone_a":
        nome_etichetta = "⚔️ SEMIFINALI EPICHE (1° e 2° in campo)"
      elif t_num == 3 or len(partite_turno) == 1:
        nome_etichetta = "🏆 FINALE SUPREMA (1° / 2° Posto)"
      else:
        nome_etichetta = ottieni_nome_turno_dinamico(len(partite_turno))

      st.markdown(
          f"""
                <div style="background: linear-gradient(90deg, #00f2fe 0%, #d946ef 100%); padding: 14px 20px; border-radius: 12px; margin: 24px 0 16px 0; color: white; text-align: center; box-shadow: 0 0 25px rgba(0,242,254,0.4);">
                    <h3 style="margin: 0; font-size: 19px; font-weight: bold; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">⚡ {nome_etichetta}</h3>
                </div>
                """,
          unsafe_allow_html=True,
      )

      tutti_giocati = True
      vincitori_turno, perdenti_turno = [], []

      for idx, m in enumerate(partite_turno):
        match_id = m["id"]
        s1_nome, s2_nome = m["s1"], m["s2"]

        if s2_nome == "RIPOSO":
          m["giocata"] = True
          m["vincente"] = s1_nome
          vincitori_turno.append(s1_nome)
          continue
        elif s1_nome == "RIPOSO":
          m["giocata"] = True
          m["vincente"] = s2_nome
          vincitori_turno.append(s2_nome)
          continue

        if m["giocata"]:
          vincitori_turno.append(m["vincente"])
          perdente = s2_nome if m["vincente"] == s1_nome else s1_nome
          perdenti_turno.append(perdente)
          centro_testo = f"<b class='neon-green'>Vince: {m['vincente']}</b>"
        else:
          tutti_giocati = False
          centro_testo = "<span style='color: #8b949e;'>VS</span>"

        st.markdown(
            f"""
                    <div style="background: linear-gradient(135deg, rgba(16, 22, 36, 0.9) 0%, rgba(8, 12, 20, 0.95) 100%); border: 1.5px solid rgba(0, 242, 254, 0.3); border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.4);">
                        <b>{s1_nome}</b> vs <b>{s2_nome}</b><br>{centro_testo}
                    </div>
                    """,
            unsafe_allow_html=True,
        )

        if is_admin:
          with st.expander(f"⚙️ Assegna Vincitore: {s1_nome} vs {s2_nome}"):
            col_v1, col_v2 = st.columns(2)
            with col_v1:
              if st.button(f"🏆 {s1_nome}", key=f"win_s1_{match_id}", use_container_width=True):
                m["giocata"] = True
                m["vincente"] = s1_nome
                salva_dati(db)
                st.rerun()
            with col_v2:
              if st.button(f"🏆 {s2_nome}", key=f"win_s2_{match_id}", use_container_width=True):
                m["giocata"] = True
                m["vincente"] = s2_nome
                salva_dati(db)
                st.rerun()

      if (
          "FINALE" in nome_etichetta
          and tutti_giocati
          and len(partite_turno) == 1
      ):
        fin_m = partite_turno[0]
        if fin_m["giocata"] and fin_m.get("vincente"):
          campione = fin_m["vincente"]
          secondo_posto = (
              fin_m["s2"] if campione == fin_m["s1"] else fin_m["s1"]
          )

      if (
          tutti_giocati
          and "SEMIFINALI" in nome_etichetta
          and len(perdenti_turno) == 2
          and not db[chiave_34]
      ):
        if is_admin:
          p1, p2 = perdenti_turno[0], perdenti_turno[1]
          if p1 != p2:
            g_p1, pos_p1 = mappa_girone_pos.get(p1, ("", ""))
            g_p2, pos_p2 = mappa_girone_pos.get(p2, ("", ""))
            db[chiave_34] = [{
                "id": f"{chiave_tabellone}_terzo_quarto",
                "s1": p1,
                "g1": g_p1,
                "p1": pos_p1,
                "s2": p2,
                "g2": g_p2,
                "p2": pos_p2,
                "giocata": False,
                "vincente": None,
            }]
            salva_dati(db)

      if tutti_giocati and t_num == 1 and chiave_tabellone == "tabellone_a":
        prossimo_turno_num = t_num + 1
        squadre_girone_ordinate = []
        for g_n in db["gironi"]:
          dati_g = db["punti_gironi"][g_n]
          sorted_g = sorted(
              dati_g.items(),
              key=lambda x: (
                  x[1]["punti"],
                  x[1]["scontri_diretti_pt"],
                  x[1]["dr"],
                  x[1]["gf"],
              ),
              reverse=True,
          )
          squadre_girone_ordinate = [item[0] for item in sorted_g]
          break

        prima = (
            squadre_girone_ordinate[0] if len(squadre_girone_ordinate) > 0 else ""
        )
        seconda = (
            squadre_girone_ordinate[1] if len(squadre_girone_ordinate) > 1 else ""
        )

        vincenti_playin = vincitori_turno

        semifinali_partite = []
        if len(vincenti_playin) >= 2:
          semifinali_partite.append({
              "id": f"{chiave_tabellone}_t2_m0",
              "s1": prima,
              "g1": "",
              "p1": 1,
              "s2": vincenti_playin[0],
              "g2": "",
              "p2": 0,
              "giocata": False,
              "vincente": None,
          })
          semifinali_partite.append({
              "id": f"{chiave_tabellone}_t2_m1",
              "s1": seconda,
              "g1": "",
              "p1": 2,
              "s2": vincenti_playin[1],
              "g2": "",
              "p2": 0,
              "giocata": False,
              "vincente": None,
          })

        turno_esistente = next(
            (t for t in turni_tab if t["turno"] == prossimo_turno_num), None
        )
        if not turno_esistente and is_admin and semifinali_partite:
          turni_tab.append(
              {"turno": prossimo_turno_num, "partite": semifinali_partite}
          )
          salva_dati(db)
          st.rerun()

      elif tutti_giocati and t_num == 2 and chiave_tabellone == "tabellone_a":
        prossimo_turno_num = t_num + 1
        vincitori_semi = vincitori_turno
        if len(vincitori_semi) == 2:
          finale_partite = [{
              "id": f"{chiave_tabellone}_t3_finale",
              "s1": vincitori_semi[0],
              "g1": "",
              "p1": 0,
              "s2": vincitori_semi[1],
              "g2": "",
              "p2": 0,
              "giocata": False,
              "vincente": None,
          }]
          turno_esistente = next(
              (t for t in turni_tab if t["turno"] == prossimo_turno_num), None
          )
          if not turno_esistente and is_admin and finale_partite:
            turni_tab.append(
                {"turno": prossimo_turno_num, "partite": finale_partite}
            )
            salva_dati(db)
            st.rerun()
            
      elif tutti_giocati and len(vincitori_turno) > 1 and len(partite_turno) > 1:
        prossimo_turno_num = t_num + 1
        turno_esistente = next((t for t in turni_tab if t["turno"] == prossimo_turno_num), None)
        if not turno_esistente and is_admin:
          nuove_partite = crea_turno_eliminazione_diretta(vincitori_turno, f"{chiave_tabellone}_t{prossimo_turno_num}")
          turni_tab.append({"turno": prossimo_turno_num, "partite": nuove_partite})
          salva_dati(db)
          st.rerun()

    if db[chiave_34]:
      st.markdown("### 🥉 FINALE 3° / 4° POSTO")
      tq_match = db[chiave_34][0]
      if tq_match["giocata"]:
        terzo_posto = tq_match["vincente"]
        quarto_posto = (
            tq_match["s2"] if terzo_posto == tq_match["s1"] else tq_match["s1"]
        )
        st.markdown(f"**3° Posto Assegnato a: {terzo_posto}**")
      elif is_admin:
        if st.button(f"🥉 Vince 3° Posto: {tq_match['s1']}", key=f"tq_s1_{chiave_tabellone}", use_container_width=True):
          tq_match["giocata"] = True
          tq_match["vincente"] = tq_match["s1"]
          salva_dati(db)
          st.rerun()
        if st.button(f"🥉 Vince 3° Posto: {tq_match['s2']}", key=f"tq_t2_{chiave_tabellone}", use_container_width=True):
          tq_match["giocata"] = True
          tq_match["vincente"] = tq_match["s2"]
          salva_dati(db)
          st.rerun()

    if campione:
      st.markdown(
          f"""
            <div style="background: linear-gradient(135deg, rgba(16, 22, 36, 0.95) 0%, rgba(8, 12, 20, 0.98) 100%); border: 2px solid #ffaa00; border-radius: 18px; padding: 24px; text-align: center; margin-top: 24px; box-shadow: 0 0 35px rgba(255,170,0,0.35);">
                <h2 class="neon-gold">🏆 PODIO {titolo_tab.upper()}</h2>
                <p style="font-size: 18px; margin: 10px 0;"><b>🥇 1° Posto:</b> <span class="neon-gold">{campione}</span></p>
                <p style="font-size: 17px; margin: 8px 0;"><b>🥈 2° Posto:</b> <span class="neon-silver">{secondo_posto}</span></p>
                <p style="font-size: 17px; margin: 8px 0;"><b>🥉 3° Posto:</b> <span class="neon-purple">{terzo_posto if terzo_posto else 'Da assegnare'}</span></p>
                <p style="font-size: 16px; margin: 8px 0; color: #8b949e;"><b>4° Posto:</b> {quarto_posto if quarto_posto else 'Da assegnare'}</p>
            </div>
            """,
          unsafe_allow_html=True,
      )


  with tab_a_view:
    gestisci_tabellone("tabellone_a", "terzo_quarto_a", "Tabellone Principale")
  with tab_b_view:
    gestisci_tabellone("tabellone_b", "terzo_quarto_b", "Fascia B")

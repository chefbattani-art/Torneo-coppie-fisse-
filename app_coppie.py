import json
import os
import random
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=3000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(
    page_title="Veneruso Calciobalilla - Torneo Live",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- STILE GRAFICO GLOBALE (CYBER / ESPORT HUD ESTREMO) ---
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
        
        /* Header Banner Principale con Effetto Gamer Lucente */
        .esport-header {
            background: linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
            border: 2.5px solid #00f0ff;
            border-radius: 20px;
            padding: 25px 20px;
            text-align: center;
            margin-bottom: 22px;
            box-shadow: 0 0 35px rgba(0, 240, 255, 0.35), inset 0 0 20px rgba(168, 85, 247, 0.2);
            position: relative;
            overflow: hidden;
        }

        /* Testo in stile Gamer con gradiente lucente ed effetti neon */
        .gamer-title {
            font-size: 34px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 8px 0;
            background: linear-gradient(180deg, #ffffff 20%, #38bdf8 60%, #00f0ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(0, 240, 255, 0.6);
        }

        .hud-stat-card {
            border-radius: 14px;
            padding: 16px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            margin-bottom: 10px;
        }
        
        .cyber-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 27, 75, 0.7) 100%);
            border: 1px solid #00f0ff;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 14px;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
        }
        
        .match-live-card {
            background: linear-gradient(135deg, #2b1f07 0%, #120d02 100%);
            border: 2px solid #f59e0b;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
        }

        h1, h2, h3, h4 {
            color: #ffffff !important;
            letter-spacing: 0.8px;
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 700;
            border: 1px solid #00f0ff;
            background: linear-gradient(180deg, #1e3a8a, #0f172a);
            color: #f3e8ff;
            transition: all 0.3s ease;
            padding: 10px 16px;
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

DB_FILE = "coppie_data.json"


def carica_dati():
  dati_default = {
      "stato": "setup",
      "titolo_torneo": "VENERUSO CALCIOBALILLA",
      "sottotitolo_torneo": "🏆 TORNEO LIVE • 3 TOCCHI UISP 🏆",
      "coppie": [],
      "num_tavoli": 6,
      "num_gironi": 4,
      "admin_pin": "0000",
      "gironi": {},
      "calendario_gironi": {},
      "punti_gironi": {},
      "fasi_finali_configurate": False,
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
  testo = (
      testo.replace("🤝", "")
      .replace("⚽", "")
      .replace("🏆", "")
      .replace("🏓", "")
  )
  testo = re.sub(r"^\d+[\.\-\)]?\s*", "", testo)
  return testo.strip()


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


def renderizza_classifica_stile_card(g_nome):
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
    gioc, tot = calcola_partite_giocate_coppia(g_nome, coppia)
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
                    <span style="font-size: 9px; color: #94a3b8; display: block;">G</span>
                    <span style="color: #f0f6fc; font-weight: 600;">{gioc}/{tot}</span>
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
  tot_squadre = num_partite_turno * 2
  if num_partite_turno == 1:
    return "🏆 FINALE"
  elif num_partite_turno == 2:
    return "⚔️ SEMIFINALI"
  elif num_partite_turno == 4:
    return "🔥 QUARTI DI FINALE"
  elif num_partite_turno == 8:
    return "⭐ OTTAVI DI FINALE"
  else:
    return f"Eliminazione Diretta ({tot_squadre} Coppie)"


def crea_abbinamenti_fascia_a_perfetti(classificate_per_girone):
  nomi_g = list(classificate_per_girone.keys())
  if len(nomi_g) < 4:
    return crea_abbinamenti_rigorosi_generico(classificate_per_girone)
  g0, g1, g2, g3 = nomi_g[0], nomi_g[1], nomi_g[2], nomi_g[3]
  squadre_g = {g: classificate_per_girone[g] for g in nomi_g}

  def get_sq(g_nome, pos_idx):
    lst = squadre_g.get(g_nome, [])
    if pos_idx < len(lst):
      return (lst[pos_idx], g_nome, pos_idx + 1)
    return ("RIPOSO", g_nome, pos_idx + 1)

  return [
      (get_sq(g0, 0), get_sq(g1, 3)),
      (get_sq(g2, 2), get_sq(g3, 1)),
      (get_sq(g2, 1), get_sq(g3, 2)),
      (get_sq(g1, 0), get_sq(g0, 3)),
      (get_sq(g0, 1), get_sq(g1, 2)),
      (get_sq(g2, 3), get_sq(g3, 0)),
      (get_sq(g2, 0), get_sq(g3, 3)),
      (get_sq(g1, 1), get_sq(g0, 2)),
  ]


def crea_abbinamenti_rigorosi_generico(classificate_per_girone):
  nomi_gironi = list(classificate_per_girone.keys())
  prime, seconde, terze, quarte = [], [], [], []
  for g_n in nomi_gironi:
    lst = classificate_per_girone[g_n]
    if len(lst) > 0:
      prime.append((lst[0], g_n, 1))
    if len(lst) > 1:
      seconde.append((lst[1], g_n, 2))
    if len(lst) > 2:
      terze.append((lst[2], g_n, 3))
    if len(lst) > 3:
      quarte.append((lst[3], g_n, 4))
  abbinamenti = []
  for i in range(len(prime)):
    p = prime[i]
    q = (
        quarte[(i + 1) % len(quarte)]
        if len(quarte) > 0
        else ("RIPOSO", "", 4)
    )
    abbinamenti.append((p, q))
  return abbinamenti


def crea_abbinamenti_fascia_b(classificate_per_girone):
  tutte_b = []
  for g_n, lista in classificate_per_girone.items():
    for idx in range(4, len(lista)):
      tutte_b.append((lista[idx], g_n, idx + 1))
  random.shuffle(tutte_b)
  abbinamenti = []
  for i in range(0, len(tutte_b), 2):
    if i + 1 < len(tutte_b):
      abbinamenti.append((tutte_b[i], tutte_b[i + 1]))
    else:
      abbinamenti.append((tutte_b[i], ("RIPOSO", "", 0)))
  return abbinamenti


def posticipa_partita_coda(match_id_da_spostare):
  for g_nome, turni in db["calendario_gironi"].items():
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


# --- HEADER PRINCIPALE IN STILE ESPORT/GAMER LUCENTE ---
titolo_corrente = db.get("titolo_torneo", "VENERUSO CALCIOBALILLA")
sottotitolo_corrente = db.get(
    "sottotitolo_torneo", "🏆 TORNEO LIVE • 3 TOCCHI UISP 🏆"
)

st.markdown(
    f"""
    <div class="esport-header">
        <span style="color: #00f0ff; font-size: 11px; letter-spacing: 4px; font-weight: bold;">⚡ TOURNAMENT CIRCUIT ⚡</span>
        <div class="gamer-title">{titolo_corrente}</div>
        <p style="font-size: 15px; color: #e2e8f0; margin: 0; font-weight: 700; text-shadow: 0 0 10px rgba(255,255,255,0.3);">
            {sottotitolo_corrente}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- BARRA STATISTICHE SUPERIORE (HUD STYLE) ---
tot_coppie_iscritte = len(db.get("coppie", []))
tot_biliardini = db.get("num_tavoli", 6)
tot_gironi_count = len(db.get("gironi", {}))

partite_giocate_count = 0
partite_totali_count = 0
for g_n, turni in db.get("calendario_gironi", {}).items():
  for t_obj in turni:
    for m in t_obj["partite"]:
      partite_totali_count += 1
      if m.get("giocata", False):
        partite_giocate_count += 1

col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns(5)
with col_h1:
  st.markdown(
      f"""
        <div class="hud-stat-card" style="background: linear-gradient(135deg, #3b0764 0%, #1e1b4b 100%); border: 1px solid #a855f7;">
            <div style="font-size: 10px; color: #d8b4fe; font-weight: bold;">ISCRITTE</div>
            <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-top: 4px;">{tot_coppie_iscritte}</div>
        </div>
        """,
      unsafe_allow_html=True,
  )
with col_h2:
  st.markdown(
      f"""
        <div class="hud-stat-card" style="background: linear-gradient(135deg, #0369a1 0%, #0f172a 100%); border: 1px solid #38bdf8;">
            <div style="font-size: 10px; color: #bae6fd; font-weight: bold;">TAVOLI</div>
            <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-top: 4px;">{tot_biliardini}</div>
        </div>
        """,
      unsafe_allow_html=True,
  )
with col_h3:
  st.markdown(
      f"""
        <div class="hud-stat-card" style="background: linear-gradient(135deg, #15803d 0%, #064e3b 100%); border: 1px solid #4ade80;">
            <div style="font-size: 10px; color: #bbf7d0; font-weight: bold;">GIRONI</div>
            <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-top: 4px;">{tot_gironi_count}</div>
        </div>
        """,
      unsafe_allow_html=True,
  )
with col_h4:
  st.markdown(
      f"""
        <div class="hud-stat-card" style="background: linear-gradient(135deg, #c2410c 0%, #7c2d12 100%); border: 1px solid #fb923c;">
            <div style="font-size: 10px; color: #fed7aa; font-weight: bold;">GIOCATE</div>
            <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-top: 4px;">{partite_giocate_count}/{partite_totali_count}</div>
        </div>
        """,
      unsafe_allow_html=True,
  )
with col_h5:
  st.markdown(
      f"""
        <div class="hud-stat-card" style="background: linear-gradient(135deg, #9f1239 0%, #4c0519 100%); border: 1px solid #fb7185;">
            <div style="font-size: 10px; color: #fecdd3; font-weight: bold;">FASE</div>
            <div style="font-size: 13px; font-weight: 800; color: #ffffff; margin-top: 8px; text-transform: uppercase;">{db.get('stato', 'Gironi')}</div>
        </div>
        """,
      unsafe_allow_html=True,
  )

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- SELETTORE COPPIA & AVVISO ---
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
    "📱 Seleziona la tua coppia per gestire i risultati in tempo reale:",
    options=opzioni_selettore,
    index=opzioni_selettore.index(coppia_url),
    key="widget_selezione_coppia",
)

if coppia_selezionata != coppia_url:
  st.query_params["coppia"] = coppia_selezionata
  st.rerun()

if is_admin:
  st.success(
      "🛡️ **Modalità Amministratore attiva:** Accesso completo sbloccato senza"
      " obbligo di selezione coppia."
  )
elif coppia_selezionata == "-- Seleziona la tua coppia per accedere --":
  st.warning(
      "⚠️ **Attenzione:** Seleziona la tua coppia dal menu a tendina sopra per"
      " sbloccare la tua dashboard dedicata, visualizzare le tue partite e"
      " inserire i risultati."
  )
else:
  st.success(f"✅ Accesso effettuato come: **{coppia_selezionata}**")

st.markdown(
    """
    <div style="padding: 12px 14px; background: linear-gradient(135deg, #3b112a 0%, #1a0815 100%); border-left: 5px solid #f43f5e; border-radius: 8px; font-size: 13px; color: #fda4af; margin: 15px 0; font-weight: bold; line-height: 1.5; box-shadow: 0 0 20px rgba(244,63,94,0.2);">
        🚨 CHI VINCE È PREGATO DI INSERIRE IL RISULTATO ESATTO • CHI È IN CODA DEVE ESSERE PRONTO A SALIRE AL PRIMO TAVOLO LIBERO!
    </div>
    """,
    unsafe_allow_html=True,
)

if not is_admin or coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
  if coppia_selezionata != "-- Seleziona la tua coppia per accedere --":
    with st.expander(
        f"👁️ Pannello Rapido - Segui la tua coppia: {coppia_selezionata}",
        expanded=True,
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
          <div class="cyber-card" style="border-color: #00f0ff; text-align: left; padding: 20px;">
              <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #00f0ff; font-weight: bold; margin-bottom: 2px;">LA TUA COPPIA</div>
              <div style="font-size: 22px; font-weight: 800; color: #ffffff; margin-bottom: 14px; text-shadow: 0 0 10px rgba(0,240,255,0.4);">🤝 {coppia_selezionata}</div>
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

# 1. SETUP
if db["stato"] == "setup" or st.session_state.get("mostra_setup", False):
  st.subheader("1. Configurazione Iniziale Torneo a Coppie")

  if not is_admin:
    st.warning(
        "⚠️ Configurazione bloccata. Accedi come amministratore dalla barra"
        " laterale con il PIN."
    )
  else:
    # Campi personalizzazione Titolo e Sottotitolo della serata
    db["titolo_torneo"] = st.text_input(
        "🏷️ Nome del Torneo (es. TORNEO SPECIALE VENERDÌ / EPIC BATTLE)",
        value=db.get("titolo_torneo", "VENERUSO CALCIOBALILLA"),
    )
    db["sottotitolo_torneo"] = st.text_input(
        "📝 Sottotitolo / Descrizione Serata",
        value=db.get("sottotitolo_torneo", "🏆 TORNEO LIVE • 3 TOCCHI UISP 🏆"),
    )

    whatsapp_text = st.text_area(
        "Incolla qui la lista delle coppie da WhatsApp (es. 1 Rossi / Bianchi):",
        height=150,
    )

    col1, col2 = st.columns(2)
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

# 2. FASE A GIRONI & LIVE DASHBOARD
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

  col_ic, col_coda = st.columns(2)

  with col_ic:
    st.markdown("#### 🔥 IN CAMPO ORA")
    if not partite_in_corso:
      st.info("Nessuna partita in corso al momento.")
    else:
      for m in partite_in_corso:
        tavolo_num = m.get("tavolo", "N/D")
        match_id = m["id"]

        fa_al_caso_nostro = (
            is_admin
            or coppia_selezionata == m["c1"]
            or coppia_selezionata == m["c2"]
        )

        st.markdown(
            f"""
            <div class="match-live-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="background: #10b981; color: white; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">TAV. {tavolo_num}</span>
                    <span style="font-size: 11px; color: #fbbf24; font-weight: bold;">{m['girone']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); padding: 8px 12px; border-radius: 8px; margin-bottom: 6px;">
                    <span style="font-weight: bold; color: #ffffff; font-size: 14px;">{m['c1']}</span>
                    <span style="font-size: 12px; color: #94a3b8; font-weight: bold;">VS</span>
                    <span style="font-weight: bold; color: #ffffff; font-size: 14px;">{m['c2']}</span>
                </div>
                <div style="text-align: center; font-size: 16px; font-weight: 800; color: #4ade80;">
                    {m.get('gol1', 0)} - {m.get('gol2', 0)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🔄 Posticipa di 2",
            key=f"post_ic_{match_id}",
            use_container_width=True,
        ):
          if posticipa_partita_coda(match_id):
            st.success("Partita posticipata!")
            st.rerun()

        if fa_al_caso_nostro:
          with st.expander(
              f"📝 Inserisci Risultato (Tav. {tavolo_num})"
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
              ricalcola_classifiche_gironi()
              salva_dati(db)
              st.success("Registrato!")
              st.rerun()

  with col_coda:
    partite_in_coda_correnti = partite_da_giocare[:num_tavoli]
    st.markdown("#### ⏳ PROSSIME IN CODA")
    if not partite_in_coda_correnti:
      st.info("Coda vuota.")
    else:
      for idx, m in enumerate(partite_in_coda_correnti):
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #06241a 0%, #030f0a 100%); border: 1px solid #10b981; padding: 12px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 0 10px rgba(16,185,129,0.15);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="background: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">#{idx+1}</span>
                    <span style="font-size: 10px; color: #34d399; font-weight: bold;">{m['girone']}</span>
                </div>
                <div style="font-size: 13px; font-weight: bold; color: #ffffff; text-align: center;">
                    {m['c1']} <span style="color: #34d399; font-size: 11px;">VS</span> {m['c2']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

  st.markdown("---")
  st.subheader("📊 Classifiche dei Gironi")
  nomi_gironi_chiavi = list(db["gironi"].keys())
  for i in range(0, len(nomi_gironi_chiavi), 2):
    col_gironi = st.columns(2)
    for j in range(2):
      if i + j < len(nomi_gironi_chiavi):
        g_nome = nomi_gironi_chiavi[i + j]
        with col_gironi[j]:
          st.markdown(
              f"<h3 style='text-align: center; font-size: 20px; color:"
              f" #00f0ff; margin-bottom: 10px;'>📁 {g_nome}</h3>",
              unsafe_allow_html=True,
          )
          renderizza_classifica_stile_card(g_nome)

  if is_admin:
    st.markdown("---")
    btn_testo = (
        "🔄 Ricrea / Resetta Fasi Finali da Zero"
        if db.get("fasi_finali_configurate", False)
        else "🏆 Genera Fasi Finali (Fascia A e Fascia B)"
    )
    if st.button(btn_testo, use_container_width=True):
      classificate_a = {}
      classificate_b_raw = {}
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
        classificate_a[g_nome] = squadre_girone[:4]
        classificate_b_raw[g_nome] = squadre_girone

      abbinamenti_a = crea_abbinamenti_fascia_a_perfetti(classificate_a)
      abbinamenti_b = crea_abbinamenti_fascia_b(classificate_b_raw)

      turno_a_iniziale = []
      for i, (s1_info, s2_info) in enumerate(abbinamenti_a):
        turno_a_iniziale.append({
            "id": f"fa_t1_m{i}",
            "s1": s1_info[0],
            "g1": s1_info[1],
            "p1": s1_info[2],
            "s2": s2_info[0],
            "g2": s2_info[1],
            "p2": s2_info[2],
            "giocata": False,
            "vincente": None,
        })

      turno_b_iniziale = []
      for i, (s1_info, s2_info) in enumerate(abbinamenti_b):
        turno_b_iniziale.append({
            "id": f"fb_t1_m{i}",
            "s1": s1_info[0],
            "g1": s1_info[1],
            "p1": s1_info[2],
            "s2": s2_info[0],
            "g2": s2_info[1],
            "p2": s2_info[2],
            "giocata": False,
            "vincente": None,
        })

      db["tabellone_a"] = [{"turno": 1, "partite": turno_a_iniziale}]
      db["tabellone_b"] = [{"turno": 1, "partite": turno_b_iniziale}]
      db["terzo_quarto_a"] = []
      db["terzo_quarto_b"] = []

      db["stato"] = "fasi_finali"
      db["fasi_finali_configurate"] = True
      salva_dati(db)
      st.success("Fasi finali generate correttamente!")
      st.rerun()

# 3. FASI FINALI
elif db["stato"] == "fasi_finali":
  st.subheader("🏆 Fasi Finali: Tabelloni a Eliminazione Diretta")
  tab_a_view, tab_b_view = st.tabs(
      ["⭐ Fascia A (Torneo Principale)", "🔻 Fascia B (Torneo Secondario)"]
  )


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

    tot_partite_turno_1 = len(turni_tab[0]["partite"])
    num_totale_squadre_tab = tot_partite_turno_1 * 2

    import math

    num_turni_totali = (
        math.ceil(math.log2(num_totale_squadre_tab))
        if num_totale_squadre_tab > 1
        else 1
    )

    while len(turni_tab) < num_turni_totali:
      ultimo_t_num = len(turni_tab)
      prossimo_t_num = ultimo_t_num + 1
      num_match_prossimo = len(turni_tab[-1]["partite"]) // 2
      if num_match_prossimo < 1:
        num_match_prossimo = 1

      partite_nuovo_turno = []
      for m_idx in range(num_match_prossimo):
        partite_nuovo_turno.append({
            "id": f"{chiave_tabellone}_t{prossimo_t_num}_m{m_idx}",
            "s1": "In attesa...",
            "g1": "",
            "p1": "",
            "s2": "In attesa...",
            "g2": "",
            "p2": "",
            "giocata": False,
            "vincente": None,
        })
      turni_tab.append({"turno": prossimo_t_num, "partite": partite_nuovo_turno})
    salva_dati(db)

    for t_idx, turno_obj in enumerate(turni_tab):
      t_num = turno_obj["turno"]
      partite_turno = turno_obj["partite"]
      num_part = len(partite_turno)
      nome_etichetta = ottieni_nome_turno_dinamico(num_part)

      st.markdown(
          f"""
                <div style="background: linear-gradient(90deg, #1e3a8a 0%, #00f0ff 100%); padding: 10px 16px; border-radius: 10px; margin: 20px 0 10px 0; color: white; text-align: center;">
                    <h3 style="margin: 0; font-size: 16px; font-weight: bold; color: white;">⚡ {nome_etichetta}</h3>
                </div>
                """,
          unsafe_allow_html=True,
      )

      if t_idx + 1 < len(turni_tab):
        turno_successivo = turni_tab[t_idx + 1]
        for m_i, match_corrente in enumerate(partite_turno):
          if match_corrente["giocata"] and match_corrente.get("vincente"):
            vincitore_corrente = match_corrente["vincente"]
            g_v, p_v = mappa_girone_pos.get(vincitore_corrente, ("", ""))

            target_match_idx = m_i // 2
            slot_squadra = "s1" if (m_i % 2 == 0) else "s2"
            slot_g = "g1" if (m_i % 2 == 0) else "g2"
            slot_p = "p1" if (m_i % 2 == 0) else "p2"

            if target_match_idx < len(turno_successivo["partite"]):
              dest_match = turno_successivo["partite"][target_match_idx]
              if dest_match[slot_squadra] in ["In attesa...", ""]:
                dest_match[slot_squadra] = vincitore_corrente
                dest_match[slot_g] = g_v
                dest_match[slot_p] = p_v
                salva_dati(db)

      for idx, m in enumerate(partite_turno):
        match_id = m["id"]
        s1_nome = m["s1"]
        s2_nome = m["s2"]

        if m["giocata"]:
          box_bg = "linear-gradient(135deg, #06241a 0%, #030f0a 100%)"
          border_c = "#10b981"
          centro_testo = (
              f"<b style='color: #34d399;'>Vincitore: {m['vincente']}</b>"
          )
        else:
          box_bg = "rgba(15, 23, 42, 0.9)"
          border_c = "#1e3a8a"
          centro_testo = "<span style='color: #94a3b8;'>VS</span>"

        st.markdown(
            f"""
                <div class="cyber-card" style="background: {box_bg}; border: 1.5px solid {border_c}; padding: 14px; text-align: center;">
                    <div style="font-size: 15px; font-weight: bold; color: #ffffff;">{s1_nome}</div>
                    <div style="margin: 4px 0; font-size: 11px; color: #94a3b8; font-weight: bold;">VS</div>
                    <div style="font-size: 15px; font-weight: bold; color: #ffffff;">{s2_nome}</div>
                    <div style="margin-top: 8px; font-size: 13px;">{centro_testo}</div>
                </div>
                """,
            unsafe_allow_html=True,
        )

        if is_admin:
          with st.expander(f"⚙️ Gestisci Scontro: {s1_nome} vs {s2_nome}"):
            col_v1, col_v2 = st.columns(2)
            with col_v1:
              if st.button(
                  f"🏆 Vince: {s1_nome}",
                  key=f"win_s1_{match_id}",
                  use_container_width=True,
              ):
                m["giocata"] = True
                m["vincente"] = s1_nome
                salva_dati(db)
                st.rerun()
            with col_v2:
              if st.button(
                  f"🏆 Vince: {s2_nome}",
                  key=f"win_s2_{match_id}",
                  use_container_width=True,
              ):
                m["giocata"] = True
                m["vincente"] = s2_nome
                salva_dati(db)
                st.rerun()

  with tab_a_view:
    gestisci_tabellone(
        "tabellone_a", "terzo_quarto_a", "Tabellone Principale - Fascia A"
    )

  with tab_b_view:
    gestisci_tabellone(
        "tabellone_b", "terzo_quarto_b", "Tabellone Secondario - Fascia B"
    )

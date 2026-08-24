import json
import os
import random
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=5000, debounce=False, key="auto_refresh_coppie")
st.set_page_config(page_title="Torneo Coppie Fisse Live", layout="wide")

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

  abbinamenti = [
      (get_sq(g0, 0), get_sq(g3, 3)),
      (get_sq(g1, 1), get_sq(g2, 2)),
      (get_sq(g1, 0), get_sq(g2, 3)),
      (get_sq(g0, 1), get_sq(g3, 2)),
      (get_sq(g2, 0), get_sq(g0, 3)),
      (get_sq(g3, 1), get_sq(g1, 2)),
      (get_sq(g2, 1), get_sq(g0, 2)),
      (get_sq(g3, 0), get_sq(g1, 3)),
  ]
  return abbinamenti


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
  for i in range(len(seconde)):
    s = seconde[i]
    t = (
        terze[(i + 1) % len(terze)] if len(terze) > 0 else ("RIPOSO", "", 3)
    )
    abbinamenti.append((s, t))
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


def verifica_conflitto_stesso_girone(s1_nome, s2_nome, mappa_girone_pos):
  g1, p1 = mappa_girone_pos.get(s1_nome, ("", 0))
  g2, p2 = mappa_girone_pos.get(s2_nome, ("", 0))
  if g1 and g2 and g1 == g2:
    if {p1, p2} == {1, 2}:
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
        <h1 style="font-size: 26px; white-space: nowrap; margin: 0; padding: 0; color: #262730;">
            🏆 Torneo Coppie Fisse Live
        </h1>
        <p style="font-size: 16px; color: #666; margin: 4px 0 0 0; font-weight: 500;">
            Regolamento 3 Tocchi Uisp
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="padding: 10px; background-color: #f0f2f6; border-radius: 8px; text-align: center; margin-bottom: 15px;">
        🔄 <a href="javascript:window.location.reload(true)" style="text-decoration: none; color: #262730; font-weight: bold; font-size: 15px;">
            Aggiorna pagina browser per vedere i risultati in tempo reale
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# SELETTORE COPPIA (VISIBILE SOLO SE NON SIAMO NELLE FASI FINALI)
coppia_selezionata = "-- Nessuna (Solo Visualizzazione) --"

if db["stato"] != "fasi_finali":
  tutte_le_coppie = []
  for g_lst in db["gironi"].values():
    tutte_le_coppie.extend(g_lst)

  opzioni_selettore = ["-- Nessuna (Solo Visualizzazione) --"] + sorted(
      tutte_le_coppie
  )

  if "coppia_selezionata" not in st.session_state:
    st.session_state["coppia_selezionata"] = (
        "-- Nessuna (Solo Visualizzazione) --"
    )

  coppia_selezionata = st.selectbox(
      "📱 Seleziona la tua coppia:",
      options=opzioni_selettore,
      key="coppia_selezionata",
      bind="query-params",
  )

  st.info(
      "💡 **Seleziona la tua coppia** dall'elenco qui sopra per poter inserire"
      " direttamente il tuo risultato quando giochi la tua partita! La scelta"
      " rimarrà memorizzata anche se aggiorni la pagina."
  )

  st.markdown(
      "<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True
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
    whatsapp_text = st.text_area(
        "Incolla qui la lista delle coppie da WhatsApp (es. 🤝 Mario / Luigi):",
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

        with st.container():
          st.markdown(
              f"""
                        <div style="background-color: #fffde7; border: 3px solid #ffae00; padding: 16px; border-radius: 12px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.08);">
                            <div style="font-size: 15px; color: #b78103; font-weight: bold; margin-bottom: 6px;">{tavolo_str}</div>
                            <div style="font-size: 16px; font-weight: bold; color: #111; line-height: 1.4;">🤝 {m['c1']}</div>
                            <div style="margin: 4px 0; font-size: 13px; font-weight: bold; color: #666;">VS</div>
                            <div style="font-size: 16px; font-weight: bold; color: #111; line-height: 1.4;">🤝 {m['c2']}</div>
                        </div>
                        """,
              unsafe_allow_html=True,
          )

          if fa_al_caso_nostro:
            with st.expander(
                f"📝 Inserisci Risultato Tavolo {m.get('tavolo', '')}"
            ):
              st.markdown(
                  f"<div style='font-weight: bold; font-size: 15px; color:"
                  f" #111; margin-bottom: 4px;'>⚽ {m['c1']}</div>",
                  unsafe_allow_html=True,
              )
              gol_p1 = st.pills(
                  f"Gol {m['c1']}",
                  options=[0, 1, 2, 3, 4, 5, 6, 7],
                  default=int(m.get("gol1", 0)),
                  key=f"user_g1_{match_id}",
                  label_visibility="collapsed",
              )

              st.markdown(
                  f"<div style='font-weight: bold; font-size: 15px; color:"
                  f" #111; margin-top: 12px; margin-bottom: 4px;'>⚽ {m['c2']}</div>",
                  unsafe_allow_html=True,
              )
              gol_p2 = st.pills(
                  f"Gol {m['c2']}",
                  options=[0, 1, 2, 3, 4, 5, 6, 7],
                  default=int(m.get("gol2", 0)),
                  key=f"user_g2_{match_id}",
                  label_visibility="collapsed",
              )

              st.markdown(
                  "<div style='margin-top: 15px;'></div>",
                  unsafe_allow_html=True,
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
                st.success(
                    "Risultato registrato con successo! Tavolo liberato."
                )
                st.rerun()

          if is_admin:
            with st.expander(f"⚙️ Opzioni Admin Tavolo {m.get('tavolo', '')}"):
              if st.button(
                  "🛑 Libera tavolo senza salvare (Annulla/Sposta)",
                  key=f"admin_libera_{match_id}",
                  use_container_width=True,
              ):
                m["in_corso"] = False
                m["tavolo"] = None
                salva_dati(db)
                st.rerun()

          st.markdown(
              "<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True
          )

  with col_coda:
    partite_in_coda_correnti = partite_da_giocare[:num_tavoli]

    st.markdown(f"#### ⏳ In Coda (Prossimi Incontri)")
    if not partite_in_coda_correnti:
      st.info("La coda è vuota o tutte le partite sono in corso/giocate.")
    else:
      for idx, m in enumerate(partite_in_coda_correnti):
        st.markdown(
            f"""
                    <div style="background-color: #d4edda; border: 1.5px solid #c3e6cb; padding: 12px; border-radius: 8px; margin-bottom: 8px; color: #155724; text-align: center;">
                        <b>⏳ {idx+1}. {m['girone']}</b><br>
                        <div style="font-weight: bold; font-size: 14px; margin-top: 4px;">{m['c1']}</div>
                        <div style="font-size: 11px; color: #155724;">VS</div>
                        <div style="font-weight: bold; font-size: 14px;">{m['c2']}</div>
                    </div>
                    """,
            unsafe_allow_html=True,
        )

  st.markdown("---")

  st.subheader(
      "📊 Classifiche dei Gironi (Verde: Fascia A | Rosso: Fascia B)"
  )
  nomi_gironi_chiavi = list(db["gironi"].keys())
  for i in range(0, len(nomi_gironi_chiavi), 2):
    col_gironi = st.columns(2)
    for j in range(2):
      if i + j < len(nomi_gironi_chiavi):
        g_nome = nomi_gironi_chiavi[i + j]
        with col_gironi[j]:
          st.markdown(f"**📁 {g_nome}**")

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

          data_g = []
          for idx, (coppia, info) in enumerate(sorted_c):
            gioc, tot = calcola_partite_giocate_coppia(g_nome, coppia)
            fascia_assegnata = "⭐ A" if idx < 4 else "🔻 B"
            data_g.append({
                "Pos": f"{idx+1}°",
                "Coppia": coppia,
                "Pt": info["punti"],
                "DR": info["dr"],
                "GF": info["gf"],
                "Gioc": f"{gioc}/{tot}",
                "Fascia": fascia_assegnata,
            })

          df_g = pd.DataFrame(data_g)

          def colora_fasce(val):
            try:
              pos = int(str(val).replace("°", ""))
              if pos <= 4:
                return (
                    "background-color: #d4edda; color: #155724; font-weight:"
                    " bold;"
                )
              else:
                return "background-color: #f8d7da; color: #721c24;"
            except:
              return ""

          if not df_g.empty:
            df_styled = df_g.style.map(colora_fasce, subset=["Pos"])
            st.dataframe(
                df_styled, hide_index=True, use_container_width=True
            )
          else:
            st.dataframe(df_g, hide_index=True, use_container_width=True)

  st.markdown("---")

  st.subheader("📅 Incontri per Girone")
  nomi_gironi_lista = list(db["calendario_gironi"].keys())
  if nomi_gironi_lista:
    tabs_gironi = st.tabs(nomi_gironi_lista)

    for idx_tab, g_nome in enumerate(nomi_gironi_lista):
      with tabs_gironi[idx_tab]:
        st.markdown(f"### Partite - {g_nome}")
        turni_girone = db["calendario_gironi"][g_nome]

        for turno_obj in turni_girone:
          t_num = turno_obj["turno"]
          st.markdown(f"**Turno {t_num}**")

          for m in turno_obj["partite"]:
            match_id = m["id"]

            if m["giocata"]:
              bg_color = "#e8f5e9"
              border_color = "#c8e6c9"
              stato_testo = f"<b>{m['gol1']} - {m['gol2']}</b>"
            elif m.get("in_corso", False):
              bg_color = "#fffde7"
              border_color = "#ffae00"
              stato_testo = f"🔥 In corso (Tav. {m.get('tavolo', 'N/D')})"
            else:
              bg_color = "#f8f9fa"
              border_color = "#e9ecef"
              stato_testo = "VS"

            st.markdown(
                f"""
                            <div style="background-color: {bg_color}; border: 1.5px solid {border_color}; padding: 12px 14px; border-radius: 8px; margin-bottom: 8px; text-align: center;">
                                <div style="font-weight: bold; color: #212529; font-size: 15px; line-height: 1.4;">
                                    🤝 {m['c1']}
                                </div>
                                <div style="margin: 3px 0; font-size: 12px; color: #666; font-weight: bold;">
                                    VS
                                </div>
                                <div style="font-weight: bold; color: #212529; font-size: 15px; line-height: 1.4;">
                                    {m['c2']} 🤝
                                </div>
                                <div style="margin-top: 6px; font-weight: bold; color: #495057; font-size: 14px;">
                                    {stato_testo}
                                </div>
                            </div>
                            """,
                unsafe_allow_html=True,
            )

            if is_admin:
              with st.expander(
                  f"⚙️ Gestisci Risultato: {m['c1']} vs {m['c2']}"
              ):
                st.markdown(
                    f"<div style='font-weight: bold; font-size: 15px; color:"
                    f" #111; margin-bottom: 4px;'>⚽ {m['c1']}</div>",
                    unsafe_allow_html=True,
                )
                rg1 = st.pills(
                    f"Gol S1 {match_id}",
                    options=[0, 1, 2, 3, 4, 5, 6, 7],
                    default=int(m.get("gol1", 0)),
                    key=f"admin_g1_{match_id}",
                    label_visibility="collapsed",
                )

                st.markdown(
                    f"<div style='font-weight: bold; font-size: 15px; color:"
                    f" #111; margin-top: 12px; margin-bottom: 4px;'>⚽ {m['c2']}</div>",
                    unsafe_allow_html=True,
                )
                rg2 = st.pills(
                    f"Gol S2 {match_id}",
                    options=[0, 1, 2, 3, 4, 5, 6, 7],
                    default=int(m.get("gol2", 0)),
                    key=f"admin_g2_{match_id}",
                    label_visibility="collapsed",
                )

                st.markdown(
                    "<div style='margin-top: 15px;'></div>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    "💾 Salva Risultato (Admin)",
                    key=f"save_{match_id}",
                    use_container_width=True,
                ):
                  m["gol1"] = int(rg1) if rg1 is not None else 0
                  m["gol2"] = int(rg2) if rg2 is not None else 0
                  m["giocata"] = True
                  m["in_corso"] = False
                  m["tavolo"] = None
                  ricalcola_classifiche_gironi()
                  salva_dati(db)
                  st.success("Salvato e aggiornato!")
                  st.rerun()

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
      st.success("Fasi finali generate correttamente con le regole richieste!")
      st.rerun()

# 3. FASI FINALI
elif db["stato"] == "fasi_finali":
  st.subheader("🏆 Fasi Finali: Tabelloni a Eliminazione Diretta")
  st.info(
      "💡 Nessun inserimento di gol richiesto: decidi direttamente la coppia"
      " vincitrice di ogni scontro con un semplice click!"
  )

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

    campione = None
    secondo_posto = None
    terzo_posto = None
    quarto_posto = None

    for t_idx, turno_obj in enumerate(turni_tab):
      t_num = turno_obj["turno"]
      partite_turno = turno_obj["partite"]
      num_part = len(partite_turno)

      nome_etichetta = ottieni_nome_turno_dinamico(num_part)

      st.markdown(
          f"""
                <div style="background: linear-gradient(90deg, #1f77b4 0%, #4682b4 100%); padding: 10px 16px; border-radius: 8px; margin: 20px 0 12px 0; color: white; text-align: center;">
                    <h3 style="margin: 0; font-size: 18px; font-weight: bold; color: white;">⚡ {nome_etichetta}</h3>
                </div>
                """,
          unsafe_allow_html=True,
      )

      tutti_giocati = True
      vincitori_turno = []
      perdenti_turno = []

      for idx, m in enumerate(partite_turno):
        match_id = m["id"]
        s1_nome = m["s1"]
        s2_nome = m["s2"]

        g1_val, p1_val = mappa_girone_pos.get(s1_nome, ("", ""))
        g2_val, p2_val = mappa_girone_pos.get(s2_nome, ("", ""))

        s1_sottotitolo = f"{p1_val}° del {g1_val}" if g1_val and p1_val else ""
        s2_sottotitolo = f"{p2_val}° del {g2_val}" if g2_val and p2_val else ""

        if s2_nome == "RIPOSO":
          m["giocata"] = True
          m["vincente"] = s1_nome
          vincitori_turno.append(s1_nome)
          st.success(f"🟢 **{s1_nome}** passa il turno automaticamente (Bye).")
          continue
        elif s1_nome == "RIPOSO":
          m["giocata"] = True
          m["vincente"] = s2_nome
          vincitori_turno.append(s2_nome)
          st.success(f"🟢 **{s2_nome}** passa il turno automaticamente (Bye).")
          continue

        if m["giocata"]:
          box_bg = "#f1f8e9"
          border_c = "#81c784"
          centro_testo = f"<span style='font-size: 14px; font-weight: bold; background-color: #2e7d32; color: white; padding: 6px 12px; border-radius: 6px;'>Vince: {m['vincente']}</span>"
          vincitori_turno.append(m["vincente"])
          perdente_match = s2_nome if m["vincente"] == s1_nome else s1_nome
          perdenti_turno.append(perdente_match)
        else:
          tutti_giocati = False
          box_bg = "#f8f9fa"
          border_c = "#ced4da"
          centro_testo = "<span style='font-size: 14px; font-weight: bold; background-color: #e9ecef; color: #495057; padding: 6px 10px; border-radius: 6px;'>VS</span>"

        st.markdown(
            f"""
                    <div style="background-color: {box_bg}; border: 2px solid {border_c}; padding: 16px 20px; border-radius: 12px; margin-bottom: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <div style="font-size: 16px; font-weight: bold; color: #212529; line-height: 1.4;">
                            🤝 {s1_nome} <span style="font-size: 12px; color: #666; font-weight: normal; display: block;">({s1_sottotitolo})</span>
                        </div>
                        <div style="margin: 6px 0; font-size: 13px; font-weight: bold; color: #666;">
                            VS
                        </div>
                        <div style="font-size: 16px; font-weight: bold; color: #212529; line-height: 1.4;">
                            🤝 {s2_nome} <span style="font-size: 12px; color: #666; font-weight: normal; display: block;">({s2_sottotitolo})</span>
                        </div>
                        <div style="margin-top: 10px;">
                            {centro_testo}
                        </div>
                    </div>
                    """,
            unsafe_allow_html=True,
        )

        if is_admin:
          with st.expander(
              f"⚙️ Decreta Vincitore Scontro: {s1_nome} vs {s2_nome}"
          ):
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
                st.success(f"Vittoria assegnata a {s1_nome}!")
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
                st.success(f"Vittoria assegnata a {s2_nome}!")
                st.rerun()

      if (
          nome_etichetta == "🏆 FINALE"
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
          and nome_etichetta == "⚔️ SEMIFINALI"
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

      if tutti_giocati and len(partite_turno) > 1:
        prossimo_turno_num = t_num + 1
        vincitori_dettagli = []
        for v in vincitori_turno:
          g_v, p_v = mappa_girone_pos.get(v, ("", ""))
          vincitori_dettagli.append((v, g_v, p_v))

        if len(vincitori_dettagli) == 4 and chiave_tabellone == "tabellone_a":
          sq1, sq2, sq3, sq4 = vincitori_dettagli
          if verifica_conflitto_stesso_girone(sq1[0], sq2[0], mappa_girone_pos):
            vincitori_dettagli = [sq1, sq3, sq2, sq4]

        nuove_partite = []
        for i in range(0, len(vincitori_dettagli), 2):
          if i + 1 < len(vincitori_dettagli):
            s1_info = vincitori_dettagli[i]
            s2_info = vincitori_dettagli[i + 1]
            nuove_partite.append({
                "id": f"{chiave_tabellone}_t{prossimo_turno_num}_m{i//2}",
                "s1": s1_info[0],
                "g1": s1_info[1],
                "p1": s1_info[2],
                "s2": s2_info[0],
                "g2": s2_info[1],
                "p2": s2_info[2],
                "giocata": False,
                "vincente": None,
            })

        turno_esistente = next(
            (t for t in turni_tab if t["turno"] == prossimo_turno_num), None
        )
        if not turno_esistente and is_admin and nuove_partite:
          turni_tab.append(
              {"turno": prossimo_turno_num, "partite": nuove_partite}
          )
          salva_dati(db)
          st.success("🎉 Turno successivo generato con successo!")
          st.rerun()

    if db[chiave_34]:
      st.markdown(
          """
                <div style="background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%); padding: 10px 16px; border-radius: 8px; margin: 25px 0 12px 0; color: white; text-align: center;">
                    <h3 style="margin: 0; font-size: 18px; font-weight: bold; color: white;">🥉 FINALE 3° / 4° POSTO</h3>
                </div>
                """,
          unsafe_allow_html=True,
      )
      tq_match = db[chiave_34][0]
      tq_id = tq_match["id"]

      tq_g1, tq_p1 = mappa_girone_pos.get(tq_match["s1"], ("", ""))
      tq_g2, tq_p2 = mappa_girone_pos.get(tq_match["s2"], ("", ""))

      tq_s1_sub = f"{tq_p1}° del {tq_g1}" if tq_g1 and tq_p1 else ""
      tq_s2_sub = f"{tq_p2}° del {tq_g2}" if tq_g2 and tq_p2 else ""

      if tq_match["giocata"]:
        tq_bg = "#fef3c7"
        tq_border = "#f59e0b"
        tq_centro = f"<span style='font-size: 14px; font-weight: bold; background-color: #d97706; color: white; padding: 6px 12px; border-radius: 6px;'>3° Posto: {tq_match['vincente']}</span>"
        terzo_posto = tq_match["vincente"]
        quarto_posto = (
            tq_match["s2"]
            if terzo_posto == tq_match["s1"]
            else tq_match["s1"]
        )
      else:
        tq_bg = "#f8f9fa"
        tq_border = "#ced4da"
        tq_centro = "<span style='font-size: 14px; font-weight: bold; background-color: #e9ecef; color: #495057; padding: 6px 10px; border-radius: 6px;'>VS</span>"

      st.markdown(
          f"""
                <div style="background-color: {tq_bg}; border: 2px solid {tq_border}; padding: 16px 20px; border-radius: 12px; margin-bottom: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="font-size: 16px; font-weight: bold; line-height: 1.4;">
                        🤝 {tq_match['s1']} <span style="font-size: 12px; color: #666; font-weight: normal; display: block;">({tq_s1_sub})</span>
                    </div>
                    <div style="margin: 6px 0; font-size: 13px; font-weight: bold; color: #666;">
                        VS
                    </div>
                    <div style="font-size: 16px; font-weight: bold; line-height: 1.4;">
                        🤝 {tq_match['s2']} <span style="font-size: 12px; color: #666; font-weight: normal; display: block;">({tq_s2_sub})</span>
                    </div>
                    <div style="margin-top: 10px;">
                        {tq_centro}
                    </div>
                </div>
                """,
          unsafe_allow_html=True,
      )

      if is_admin:
        with st.expander(f"⚙️ Decreta Vincitore 3°/4° Posto"):
          col_tq1, col_tq2 = st.columns(2)
          with col_tq1:
            if st.button(
                f"🥉 Vince 3° Posto: {tq_match['s1']}",
                key=f"tq_win_s1_{tq_id}",
                use_container_width=True,
            ):
              tq_match["giocata"] = True
              tq_match["vincente"] = tq_match["s1"]
              salva_dati(db)
              st.success(f"Assegnato 3° posto a {tq_match['s1']}!")
              st.rerun()
          with col_tq2:
            if st.button(
                f"🥉 Vince 3° Posto: {tq_match['s2']}",
                key=f"tq_win_s2_{tq_id}",
                use_container_width=True,
            ):
              tq_match["giocata"] = True
              tq_match["vincente"] = tq_match["s2"]
              salva_dati(db)
              st.success(f"Assegnato 3° posto a {tq_match['s2']}!")
              st.rerun()

    if campione:
      st.markdown("---")
      st.markdown(
          f"""
                <div style="background: linear-gradient(135deg, #fef08a 0%, #fde047 100%); border: 3px solid #eab308; padding: 25px; border-radius: 16px; text-align: center; color: #713f12; margin-top: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0 0 15px 0; color: #713f12; font-size: 24px;">🏆 PODIO FINALE - {titolo_tab} 🏆</h2>
                    <p style="font-size: 22px; margin: 10px 0; font-weight: bold;">🥇 1° POSTO (Campioni): {campione}</p>
                    <p style="font-size: 19px; margin: 8px 0; font-weight: 600;">🥈 2° POSTO: {secondo_posto if secondo_posto else 'N.D.'}</p>
                    <p style="font-size: 19px; margin: 8px 0; font-weight: 600;">🥉 3° POSTO: {terzo_posto if terzo_posto else 'N.D.'}</p>
                    <p style="font-size: 16px; margin: 10px 0; color: #854d0e;">4° Posto: {quarto_posto if quarto_posto else 'N.D.'}</p>
                </div>
                """,
          unsafe_allow_html=True,
      )


  with tab_a_view:
    gestisci_tabellone(
        "tabellone_a",
        "terzo_quarto_a",
        "Tabellone Eliminazione Diretta - Fascia A",
    )

  with tab_b_view:
    gestisci_tabellone(
        "tabellone_b",
        "terzo_quarto_b",
        "Tabellone Eliminazione Diretta - Fascia B",
    )

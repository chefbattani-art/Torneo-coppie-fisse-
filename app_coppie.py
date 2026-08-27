import json
import os
import random
import re
from datetime import datetime

from fpdf import FPDF
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# ============================================================
# TORNEO COPPIE FISSE LIVE — CYBER ARENA v2
# ============================================================
# Mantiene:
# - coppie fisse
# - gironi round-robin
# - punteggio 3/0, 2/1, 2/2
# - biliardini live + coda automatica
# - accesso coppia tramite selectbox
# - admin PIN
# - salvataggio JSON
# - PDF
#
# Miglioramenti:
# - Main bracket dinamico fino a 32 qualificate
# - Play-in automatico quando le qualificate non sono una potenza di 2
# - Fascia B completa per tutte le non qualificate
# - tabelloni persistenti e progressivi
# - gestione robusta dei pareggi in classifica
# - dashboard più moderna e animata
# - risultati eliminazione diretta con gol opzionali
# - podio finale
# ============================================================

st_autorefresh(interval=5000, debounce=False, key="auto_refresh_cyber_arena")

st.set_page_config(
    page_title="Cyber Arena — Torneo Coppie Fisse Live",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = "coppie_data.json"
DEFAULT_PIN = "0000"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800;900&family=Rajdhani:wght@500;600;700&display=swap');

:root { color-scheme: dark !important; }

html, body, [data-testid="stAppViewContainer"] {
    background: #03050b !important;
}

.stApp {
    background:
        radial-gradient(circle at 15% 5%, rgba(0,242,254,.11), transparent 30%),
        radial-gradient(circle at 85% 15%, rgba(217,70,239,.10), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(0,255,102,.06), transparent 35%),
        linear-gradient(rgba(0,242,254,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,242,254,.025) 1px, transparent 1px),
        #03050b !important;
    background-size: auto, auto, auto, 36px 36px, 36px 36px;
    color: #f5f7fb !important;
    font-family: Inter, sans-serif !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#080c18,#020309) !important;
    border-right: 1px solid rgba(0,242,254,.28);
    box-shadow: 8px 0 40px rgba(0,242,254,.08);
}

h1,h2,h3,h4 {
    font-family: Rajdhani, sans-serif !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #fff !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(14,22,38,.95), rgba(5,9,17,.98));
    border: 1px solid rgba(0,242,254,.24);
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 0 22px rgba(0,242,254,.08);
}

div[data-baseweb="select"] > div,
div[data-baseweb="popover"] div,
ul[data-baseweb="menu"],
li[data-baseweb="option"] {
    background: #111a2b !important;
    color: white !important;
}

li[data-baseweb="option"]:hover {
    background: #1a3150 !important;
    color: #00f2fe !important;
}

div.stButton > button {
    min-height: 48px;
    border-radius: 12px;
    border: 1px solid rgba(0,242,254,.42);
    background: linear-gradient(180deg,#12233a,#08111e);
    color: #00f2fe;
    font-family: Rajdhani, sans-serif;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: .6px;
    transition: .22s ease;
    box-shadow: 0 5px 18px rgba(0,0,0,.35);
}
div.stButton > button:hover {
    transform: translateY(-2px);
    border-color: #00f2fe;
    color: #fff;
    box-shadow: 0 0 24px rgba(0,242,254,.38);
}

.neon-title {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(0,242,254,.7);
    border-radius: 24px;
    padding: 28px 24px;
    margin-bottom: 20px;
    text-align: center;
    background:
        linear-gradient(135deg,rgba(10,18,32,.97),rgba(5,8,16,.98));
    box-shadow: 0 0 35px rgba(0,242,254,.16), inset 0 0 35px rgba(0,242,254,.04);
}
.neon-title:after {
    content: "";
    position: absolute;
    left: -20%;
    top: 0;
    width: 40%;
    height: 100%;
    background: linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);
    transform: skewX(-20deg);
    animation: sweep 5s infinite;
}
@keyframes sweep {
    0%,70% { left:-30%; }
    100% { left:120%; }
}
.neon-title-main {
    font-family: Orbitron, sans-serif;
    color: #00ff66;
    font-size: clamp(26px,4vw,42px);
    font-weight: 900;
    text-shadow: 0 0 16px rgba(0,255,102,.75), 0 0 35px rgba(0,255,102,.3);
}
.neon-title-sub {
    margin-top: 8px;
    color: #8b98aa;
    font-size: 13px;
    letter-spacing: 1px;
}

.card {
    border-radius: 18px;
    padding: 18px;
    margin: 0 0 14px 0;
    background: linear-gradient(145deg,rgba(14,22,38,.94),rgba(5,9,17,.98));
    border: 1px solid rgba(0,242,254,.20);
    box-shadow: 0 10px 30px rgba(0,0,0,.24);
}
.live-card {
    border: 1px solid rgba(255,170,0,.72);
    background: linear-gradient(145deg,rgba(39,26,8,.97),rgba(12,8,3,.98));
    box-shadow: 0 0 28px rgba(255,170,0,.15);
    animation: pulseLive 2.2s infinite;
}
@keyframes pulseLive {
    0%,100% { box-shadow: 0 0 18px rgba(255,170,0,.12); }
    50% { box-shadow: 0 0 30px rgba(255,170,0,.28); }
}
.green-card {
    border-color: rgba(0,255,102,.35);
    background: linear-gradient(145deg,rgba(0,255,102,.075),rgba(5,9,17,.98));
}
.red-card {
    border-color: rgba(255,51,102,.30);
    background: linear-gradient(145deg,rgba(255,51,102,.055),rgba(5,9,17,.98));
}
.purple-card {
    border-color: rgba(217,70,239,.32);
    background: linear-gradient(145deg,rgba(217,70,239,.07),rgba(5,9,17,.98));
}

.kicker {
    color:#8b98aa;
    font-size:10px;
    font-weight:800;
    letter-spacing:2px;
    text-transform:uppercase;
}
.value {
    color:#fff;
    font-size:24px;
    font-weight:800;
}
.cyan { color:#00f2fe !important; text-shadow:0 0 12px rgba(0,242,254,.45); }
.green { color:#00ff66 !important; text-shadow:0 0 12px rgba(0,255,102,.45); }
.gold { color:#ffaa00 !important; text-shadow:0 0 12px rgba(255,170,0,.45); }
.pink { color:#d946ef !important; text-shadow:0 0 12px rgba(217,70,239,.45); }
.red { color:#ff3366 !important; text-shadow:0 0 12px rgba(255,51,102,.45); }
.muted { color:#8b98aa; }

.badge {
    display:inline-block;
    border-radius:999px;
    padding:5px 10px;
    margin:2px;
    font-size:11px;
    font-weight:800;
    letter-spacing:.5px;
    border:1px solid rgba(0,242,254,.25);
    background:rgba(0,242,254,.07);
}
.badge.green-b { border-color:rgba(0,255,102,.45); color:#00ff66; background:rgba(0,255,102,.08); }
.badge.red-b { border-color:rgba(255,51,102,.45); color:#ff6688; background:rgba(255,51,102,.07); }
.badge.gold-b { border-color:rgba(255,170,0,.45); color:#ffaa00; background:rgba(255,170,0,.07); }

.queue {
    border-left:3px solid #00ff66;
    padding:12px 14px;
    border-radius:12px;
    margin-bottom:8px;
    background:rgba(0,255,102,.045);
}
.match {
    border:1px solid rgba(0,242,254,.20);
    border-radius:14px;
    padding:14px;
    margin-bottom:10px;
    text-align:center;
    background:rgba(8,14,25,.9);
}
.match:hover { border-color:rgba(0,242,254,.55); }

.bracket-title {
    font-family: Orbitron, sans-serif;
    font-size:13px;
    color:#00f2fe;
    letter-spacing:1px;
    text-transform:uppercase;
    margin:18px 0 10px;
}
.small { font-size:12px; }
.center { text-align:center; }
hr { border-color: rgba(0,242,254,.12) !important; }

[data-testid="stDataFrame"] {
    border-radius:14px;
    overflow:hidden;
}

@media (max-width: 700px) {
    .neon-title { padding:20px 12px; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

def default_db():
    return {
        "stato": "setup",
        "coppie": [],
        "num_tavoli": 6,
        "num_gironi": 4,
        "admin_pin": DEFAULT_PIN,
        "gironi": {},
        "calendario_gironi": {},
        "punti_gironi": {},
        "fasi_finali_configurate": False,
        "num_qualificate_knockout": 4,
        "tabellone_a": [],
        "tabellone_b": [],
        "terzo_quarto_a": [],
        "terzo_quarto_b": [],
        "podio": {},
        "meta_torneo": {
            "creato_il": None,
            "qualificate_totali": 0,
            "non_qualificate_totali": 0,
        },
    }


def carica_dati():
    base = default_db()
    if not os.path.exists(DB_FILE):
        return base
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        for k, v in base.items():
            if k not in saved:
                saved[k] = v
        return saved
    except Exception:
        return base


def salva_dati(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if "db" not in st.session_state:
    st.session_state.db = carica_dati()

db = st.session_state.db


# ============================================================
# HELPERS
# ============================================================

def pulisci_nome(testo):
    testo = testo.replace("🤝", "").replace("⚽", "").replace("🏆", "")
    testo = re.sub(r"^\s*\d+[\.\-\)]?\s*", "", testo)
    return testo.strip()


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def classifica_girone(g_nome):
    dati = db["punti_gironi"].get(g_nome, {})
    return sorted(
        dati.items(),
        key=lambda x: (
            x[1].get("punti", 0),
            x[1].get("scontri_diretti_pt", 0),
            x[1].get("dr", 0),
            x[1].get("gf", 0),
            x[0].lower(),
        ),
        reverse=True,
    )


def ricalcola_classifiche_gironi():
    for g_nome, coppie_lista in db["gironi"].items():
        stats = {
            c: {
                "punti": 0,
                "partite_giocate": 0,
                "vinte": 0,
                "pareggiate": 0,
                "perse": 0,
                "gf": 0,
                "gs": 0,
                "dr": 0,
                "scontri_diretti_pt": 0,
            }
            for c in coppie_lista
        }

        for turno_obj in db["calendario_gironi"].get(g_nome, []):
            for m in turno_obj["partite"]:
                if not m.get("giocata", False):
                    continue

                c1, c2 = m["c1"], m["c2"]
                if c1 not in stats or c2 not in stats:
                    continue

                g1, g2 = int(m.get("gol1", 0)), int(m.get("gol2", 0))
                diff = abs(g1 - g2)

                stats[c1]["partite_giocate"] += 1
                stats[c2]["partite_giocate"] += 1
                stats[c1]["gf"] += g1
                stats[c1]["gs"] += g2
                stats[c2]["gf"] += g2
                stats[c2]["gs"] += g1

                if g1 > g2:
                    stats[c1]["punti"] += 3 if diff >= 2 else 2
                    stats[c2]["punti"] += 0 if diff >= 2 else 1
                    stats[c1]["vinte"] += 1
                    stats[c2]["perse"] += 1
                elif g2 > g1:
                    stats[c2]["punti"] += 3 if diff >= 2 else 2
                    stats[c1]["punti"] += 0 if diff >= 2 else 1
                    stats[c2]["vinte"] += 1
                    stats[c1]["perse"] += 1
                else:
                    stats[c1]["punti"] += 2
                    stats[c2]["punti"] += 2
                    stats[c1]["pareggiate"] += 1
                    stats[c2]["pareggiate"] += 1

        for c in coppie_lista:
            stats[c]["dr"] = stats[c]["gf"] - stats[c]["gs"]

        # Spareggio scontri diretti per squadre a pari punti.
        punti_gruppo = {}
        for c in coppie_lista:
            punti_gruppo.setdefault(stats[c]["punti"], []).append(c)

        for gruppo in punti_gruppo.values():
            if len(gruppo) < 2:
                continue

            mini = {c: 0 for c in gruppo}
            for turno_obj in db["calendario_gironi"].get(g_nome, []):
                for m in turno_obj["partite"]:
                    if not m.get("giocata", False):
                        continue
                    c1, c2 = m["c1"], m["c2"]
                    if c1 not in mini or c2 not in mini:
                        continue
                    g1, g2 = int(m.get("gol1", 0)), int(m.get("gol2", 0))
                    if g1 > g2:
                        mini[c1] += 3 if abs(g1 - g2) >= 2 else 2
                        mini[c2] += 0 if abs(g1 - g2) >= 2 else 1
                    elif g2 > g1:
                        mini[c2] += 3 if abs(g1 - g2) >= 2 else 2
                        mini[c1] += 0 if abs(g1 - g2) >= 2 else 1
                    else:
                        mini[c1] += 2
                        mini[c2] += 2

            for c in gruppo:
                stats[c]["scontri_diretti_pt"] = mini[c]

        db["punti_gironi"][g_nome] = stats


def classifica_globale(coppie):
    righe = []
    for c in coppie:
        trovato = None
        for g_nome in db["gironi"]:
            if c in db["gironi"][g_nome]:
                stats = db["punti_gironi"].get(g_nome, {}).get(c, {})
                trovato = {
                    "coppia": c,
                    "girone": g_nome,
                    "posizione": classifica_girone(g_nome).index((c, stats)) + 1
                    if (c, stats) in classifica_girone(g_nome)
                    else 0,
                    **stats,
                }
                break
        if trovato:
            righe.append(trovato)
    return sorted(
        righe,
        key=lambda x: (
            x.get("posizione", 99),
            -x.get("punti", 0),
            -x.get("scontri_diretti_pt", 0),
            -x.get("dr", 0),
            -x.get("gf", 0),
            x["coppia"].lower(),
        ),
    )


def crea_calendario_round_robin(lista):
    squadre = list(lista)
    if len(squadre) % 2:
        squadre.append("RIPOSO")

    n = len(squadre)
    turni = []

    for t in range(n - 1):
        partite = []
        for i in range(n // 2):
            a = squadre[i]
            b = squadre[n - 1 - i]
            if a != "RIPOSO" and b != "RIPOSO":
                partite.append(
                    {
                        "id": f"t{t+1}_m{i}_{abs(hash((a,b,t))) % 1000000}",
                        "girone": "",
                        "c1": a,
                        "c2": b,
                        "giocata": False,
                        "in_corso": False,
                        "tavolo": None,
                        "gol1": 0,
                        "gol2": 0,
                    }
                )
        turni.append({"turno": t + 1, "partite": partite})
        squadre = [squadre[0]] + [squadre[-1]] + squadre[1:-1]

    return turni


def tutte_partite_gironi():
    per_girone = {}
    max_len = 0
    for g, turni in db["calendario_gironi"].items():
        lista = []
        for t in turni:
            lista.extend(t["partite"])
        per_girone[g] = lista
        max_len = max(max_len, len(lista))

    # Interleave tra gironi per mantenere il flusso globale equilibrato.
    out = []
    for i in range(max_len):
        for g in sorted(per_girone):
            if i < len(per_girone[g]):
                out.append(per_girone[g][i])
    return out


def selettore_gol_bottoni(prefix, default_val=0):
    if prefix not in st.session_state:
        st.session_state[prefix] = int(default_val)

    value = int(st.session_state[prefix])
    cols = st.columns(8)
    for g in range(8):
        with cols[g]:
            label = f"✨ {g}" if value == g else str(g)
            if st.button(label, key=f"goal_{prefix}_{g}", use_container_width=True):
                st.session_state[prefix] = g
                st.rerun()

    st.markdown(
        f"<div class='center small muted'>Gol selezionati: <b class='cyan' style='font-size:18px'>{st.session_state[prefix]}</b></div>",
        unsafe_allow_html=True,
    )
    return int(st.session_state[prefix])


def potenza_di_2_successiva(n):
    p = 1
    while p < max(1, n):
        p *= 2
    return p


def seed_order(n):
    # Ordine standard per costruire un bracket da n teste di serie.
    if n == 1:
        return [1]
    order = [1, 2]
    size = 2
    while size < n:
        size *= 2
        new = []
        for x in order:
            new.extend([x, size + 1 - x])
        order = new
    return order


def genera_round_primo_turno(squadre, prefix):
    """
    Crea un primo turno a eliminazione:
    - se n è potenza di 2: bracket diretto
    - altrimenti: le migliori ricevono bye
    - le altre giocano un play-in per ridurre al bracket successivo
    """
    squadre = list(squadre)
    n = len(squadre)

    if n <= 1:
        return [], "FINALISSIMA"

    target = potenza_di_2_successiva(n)

    if n == target:
        incontri = []
        order = seed_order(target)
        for i in range(0, target, 2):
            a = squadre[order[i] - 1]
            b = squadre[order[i + 1] - 1]
            incontri.append(
                crea_match_ko(prefix, 1, i // 2, a, b)
            )
        return incontri, f"ROUND OF {target}" if target > 2 else "FINALE"

    bye = target - n
    non_bye_count = n - bye
    incontri_count = non_bye_count // 2

    # Le prime 'bye' teste di serie passano automaticamente.
    # Gli altri giocano per i posti mancanti.
    playin = squadre[bye:]
    incontri = []
    for i in range(incontri_count):
        a = playin[i]
        b = playin[-1 - i]
        incontri.append(crea_match_ko(prefix, 1, i, a, b))

    return incontri, f"PLAY-IN → {target // 2}"


def crea_match_ko(prefix, turno, indice, a, b):
    return {
        "id": f"{prefix}_t{turno}_m{indice}",
        "s1": a,
        "s2": b,
        "giocata": False,
        "vincente": None,
        "gol1": 0,
        "gol2": 0,
    }


def vincitori_turno(turno):
    return [m["vincente"] for m in turno.get("partite", []) if m.get("giocata") and m.get("vincente")]


def perdenti_turno(turno):
    out = []
    for m in turno.get("partite", []):
        if m.get("giocata") and m.get("vincente"):
            perdente = m["s2"] if m["vincente"] == m["s1"] else m["s1"]
            if perdente and perdente != "RIPOSO":
                out.append(perdente)
    return out


def genera_prossimo_turno(tabellone):
    if not tabellone:
        return

    corrente = tabellone[-1]
    if not corrente.get("partite"):
        return
    if not all(m.get("giocata") for m in corrente["partite"]):
        return
    if len(tabellone) >= 12:
        return

    vincitori = vincitori_turno(corrente)
    if len(vincitori) <= 1:
        return

    # Il primo turno può essere un play-in: le teste con bye vanno aggiunte
    # ai vincitori del play-in. Sono memorizzate nel turno.
    byes = corrente.get("bye", [])
    qualificati = byes + vincitori

    if len(qualificati) == 2:
        nuovo = {
            "turno": corrente["turno"] + 1,
            "nome": "FINALE",
            "partite": [crea_match_ko("main", corrente["turno"] + 1, 0, qualificati[0], qualificati[1])],
        }
        tabellone.append(nuovo)
        return

    # Per ogni turno successivo, ordine di bracket deterministico.
    incontri = []
    for i in range(0, len(qualificati), 2):
        if i + 1 < len(qualificati):
            incontri.append(
                crea_match_ko(
                    "main",
                    corrente["turno"] + 1,
                    i // 2,
                    qualificati[i],
                    qualificati[i + 1],
                )
            )

    if incontri:
        if len(incontri) == 1:
            nome = "FINALE"
        elif len(incontri) == 2:
            nome = "SEMIFINALI"
        else:
            nome = f"ROUND OF {len(incontri) * 2}"
        tabellone.append(
            {
                "turno": corrente["turno"] + 1,
                "nome": nome,
                "partite": incontri,
            }
        )


def costruisci_tabellone_da_squadre(squadre, prefix):
    squadre = list(squadre)
    if not squadre:
        return []

    # Le squadre arrivano già ordinate per ranking.
    target = potenza_di_2_successiva(len(squadre))
    if len(squadre) == 1:
        return [{
            "turno": 1,
            "nome": "FINALE",
            "partite": [{
                "id": f"{prefix}_winner",
                "s1": squadre[0],
                "s2": "RIPOSO",
                "giocata": True,
                "vincente": squadre[0],
                "gol1": 0,
                "gol2": 0,
            }],
        }]

    if len(squadre) == target:
        order = seed_order(target)
        partite = []
        for i in range(0, target, 2):
            a = squadre[order[i] - 1]
            b = squadre[order[i + 1] - 1]
            partite.append(crea_match_ko(prefix, 1, i // 2, a, b))
        nome = "FINALE" if target == 2 else ("SEMIFINALI" if target == 4 else f"ROUND OF {target}")
        return [{"turno": 1, "nome": nome, "partite": partite}]

    bye = target - len(squadre)
    playin = squadre[bye:]
    partite = []
    for i in range(len(playin) // 2):
        a = playin[i]
        b = playin[-1 - i]
        partite.append(crea_match_ko(prefix, 1, i, a, b))

    return [{
        "turno": 1,
        "nome": f"PLAY-IN → ROUND OF {target // 2}",
        "partite": partite,
        "bye": squadre[:bye],
    }]


def aggiorna_tabellone(tabellone, prefix):
    if not tabellone:
        return

    corrente = tabellone[-1]
    if not corrente.get("partite"):
        return
    if not all(m.get("giocata") for m in corrente["partite"]):
        return

    qualificati = corrente.get("bye", []) + vincitori_turno(corrente)
    if len(qualificati) <= 1:
        return

    if len(qualificati) == 2:
        nome = "FINALE"
    elif len(qualificati) == 4:
        nome = "SEMIFINALI"
    else:
        nome = f"ROUND OF {len(qualificati)}"

    if len(tabellone) > 1 and tabellone[-1].get("_generato_da") == corrente["turno"]:
        return

    nuovo = {
        "turno": corrente["turno"] + 1,
        "nome": nome,
        "partite": [],
        "_generato_da": corrente["turno"],
    }

    for i in range(0, len(qualificati), 2):
        if i + 1 < len(qualificati):
            nuovo["partite"].append(
                crea_match_ko(prefix, nuovo["turno"], i // 2, qualificati[i], qualificati[i + 1])
            )

    if nuovo["partite"]:
        tabellone.append(nuovo)


def assegna_podio(tabellone, terzo_quarto):
    risultato = {}
    if not tabellone:
        return risultato

    ultima = tabellone[-1]
    if len(ultima.get("partite", [])) != 1:
        return risultato

    m = ultima["partite"][0]
    if not m.get("giocata") or not m.get("vincente"):
        return risultato

    risultato["1"] = m["vincente"]
    risultato["2"] = m["s2"] if m["vincente"] == m["s1"] else m["s1"]

    if terzo_quarto:
        tq = terzo_quarto[0]
        if tq.get("giocata") and tq.get("vincente"):
            risultato["3"] = tq["vincente"]
            risultato["4"] = tq["s2"] if tq["vincente"] == tq["s1"] else tq["s1"]

    return risultato


def genera_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 17)
    pdf.cell(0, 10, "TORNEO COPPIE FISSE - CYBER ARENA", 0, 1, "C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 7, datetime.now().strftime("Aggiornato il %d/%m/%Y %H:%M"), 0, 1, "C")
    pdf.ln(5)

    for g_nome, turni in db["calendario_gironi"].items():
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, f"{g_nome}", 0, 1)
        for turno in turni:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, f"Turno {turno['turno']}", 0, 1)
            pdf.set_font("Arial", "", 9)
            for m in turno["partite"]:
                risultato = (
                    f"{m['gol1']} - {m['gol2']}"
                    if m.get("giocata")
                    else "Da giocare"
                )
                testo = f"{m['c1']} VS {m['c2']} -> {risultato}"
                testo = testo.encode("latin-1", "ignore").decode("latin-1")
                pdf.cell(0, 5, testo, 0, 1)
        pdf.ln(2)

    return bytes(pdf.output())


def reset_torneo():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    st.session_state.clear()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="neon-title">
    <div class="neon-title-main">⚡ CYBER ARENA</div>
    <div class="neon-title-sub">TORNEO COPPIE FISSE LIVE • 3 TOCCHI UISP • LIVE ESPORTS EXPERIENCE</div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR / ADMIN
# ============================================================

st.sidebar.markdown("## ⚙️ CONTROL CENTER")

if db["stato"] != "setup":
    st.sidebar.download_button(
        "📥 Scarica calendario PDF",
        data=genera_pdf(),
        file_name="cyber_arena_calendario.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

admin_mode = st.sidebar.checkbox("🛡️ Modalità Amministratore")
is_admin = False

if admin_mode:
    pin = st.sidebar.text_input("PIN Admin", type="password")
    if pin == db.get("admin_pin", DEFAULT_PIN):
        is_admin = True
        st.sidebar.success("Admin autorizzato")
    elif pin:
        st.sidebar.error("PIN errato")

st.sidebar.divider()

st.sidebar.markdown(
    f"""
<div class="card">
<div class="kicker">Stato torneo</div>
<div class="value cyan">{esc(db["stato"].upper())}</div>
<div class="small muted">Tavoli: {db.get("num_tavoli", 0)} • Gironi: {db.get("num_gironi", 0)}</div>
</div>
""",
    unsafe_allow_html=True,
)

if is_admin:
    if st.sidebar.button("⚙️ Mostra / nascondi setup", use_container_width=True):
        st.session_state["mostra_setup"] = not st.session_state.get("mostra_setup", False)
        st.rerun()

    if db["stato"] == "fasi_finali":
        if st.sidebar.button("🔙 Torna ai gironi", use_container_width=True):
            db["stato"] = "gironi"
            salva_dati(db)
            st.rerun()

    st.sidebar.markdown("### ⚠️ Zona pericolo")
    conferma = st.sidebar.checkbox("Confermo reset totale")
    if st.sidebar.button("🔄 Reset completo torneo", use_container_width=True):
        if conferma:
            reset_torneo()
            st.rerun()
        else:
            st.sidebar.warning("Conferma prima il reset.")
else:
    st.sidebar.info("Accedi come admin per le funzioni di gestione.")


# ============================================================
# SELETTORE COPPIA
# ============================================================

tutte_le_coppie = []
for lista in db.get("gironi", {}).values():
    tutte_le_coppie.extend(lista)
if not tutte_le_coppie:
    tutte_le_coppie = db.get("coppie", [])

opzioni = ["-- Seleziona la tua coppia --"] + sorted(set(tutte_le_coppie))
query_coppia = st.query_params.get("coppia", "-- Seleziona la tua coppia --")
if query_coppia not in opzioni:
    query_coppia = "-- Seleziona la tua coppia --"

coppia_selezionata = st.selectbox(
    "📱 Accedi come coppia",
    opzioni,
    index=opzioni.index(query_coppia),
)

if coppia_selezionata != query_coppia:
    st.query_params["coppia"] = coppia_selezionata
    st.rerun()

if not is_admin and coppia_selezionata == "-- Seleziona la tua coppia --":
    st.markdown(
        """
<div class="card purple-card center">
    <div class="value pink">👋 BENVENUTO</div>
    <div class="muted" style="margin-top:8px">
        Seleziona la tua coppia per vedere girone, classifica, coda e partita live.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    if coppia_selezionata != "-- Seleziona la tua coppia --":
        st.markdown(
            f"<span class='badge green-b'>● ONLINE</span> Accesso: <b>{esc(coppia_selezionata)}</b>",
            unsafe_allow_html=True,
        )


# ============================================================
# SETUP
# ============================================================

if db["stato"] == "setup" or st.session_state.get("mostra_setup", False):
    st.header("🚀 Setup torneo")

    if not is_admin:
        st.warning("Configurazione bloccata. Accedi come amministratore.")
    else:
        whatsapp_text = st.text_area(
            "Incolla la lista delle coppie da WhatsApp",
            height=170,
            placeholder="1 Fiore Gaffo\n2 Rossi Bianchi\n3 ...",
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            db["num_tavoli"] = st.number_input(
                "Biliardini",
                min_value=1,
                max_value=10,
                value=int(db.get("num_tavoli", 6)),
            )
        with c2:
            db["num_gironi"] = st.number_input(
                "Gironi",
                min_value=1,
                max_value=16,
                value=int(db.get("num_gironi", 4)),
            )
        with c3:
            db["num_qualificate_knockout"] = st.number_input(
                "Qualificate per girone",
                min_value=1,
                max_value=8,
                value=int(db.get("num_qualificate_knockout", 4)),
                help="Il totale viene calcolato come gironi × qualificate. Massimo tabellone principale: 32.",
            )

        db["admin_pin"] = st.text_input(
            "PIN Admin",
            value=db.get("admin_pin", DEFAULT_PIN),
        )

        totale_preview = int(db["num_gironi"]) * int(db["num_qualificate_knockout"])
        st.markdown(
            f"""
<div class="card">
    <div class="kicker">Anteprima qualificazioni</div>
    <div class="value green">{totale_preview} QUALIFICATE</div>
    <div class="small muted">
        {db["num_gironi"]} gironi × {db["num_qualificate_knockout"]} qualificate.
        Il Main Event supporta fino a 32 coppie.
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if totale_preview > 32:
            st.error("Con questa configurazione superi le 32 qualificate del Tabellone Principale.")

        if st.button("🚀 CREA GIRONI E SORTEGGIA", use_container_width=True):
            coppie = []
            viste = set()

            for line in whatsapp_text.splitlines():
                nome = pulisci_nome(line)
                if nome and nome.lower() not in viste:
                    coppie.append(nome)
                    viste.add(nome.lower())

            num_g = int(db["num_gironi"])
            qual_per_girone = int(db["num_qualificate_knockout"])

            if len(coppie) < num_g * 2:
                st.error(f"Servono almeno {num_g * 2} coppie per {num_g} gironi.")
            elif num_g * qual_per_girone > 32:
                st.error("Le qualificate per il Main Event non possono essere più di 32.")
            else:
                random.shuffle(coppie)

                gironi = {f"Girone {chr(65+i)}": [] for i in range(num_g)}
                for i, coppia in enumerate(coppie):
                    gironi[f"Girone {chr(65 + (i % num_g))}"].append(coppia)

                calendari = {}
                for g, lista in gironi.items():
                    turni = crea_calendario_round_robin(lista)
                    for turno in turni:
                        for m in turno["partite"]:
                            m["girone"] = g
                    calendari[g] = turni

                db["coppie"] = coppie
                db["gironi"] = gironi
                db["calendario_gironi"] = calendari
                db["punti_gironi"] = {}
                db["tabellone_a"] = []
                db["tabellone_b"] = []
                db["terzo_quarto_a"] = []
                db["terzo_quarto_b"] = []
                db["podio"] = {}
                db["fasi_finali_configurate"] = False
                db["stato"] = "gironi"
                db["meta_torneo"] = {
                    "creato_il": datetime.now().isoformat(),
                    "qualificate_totali": 0,
                    "non_qualificate_totali": 0,
                }

                ricalcola_classifiche_gironi()
                salva_dati(db)
                st.success("Gironi creati. Il torneo è LIVE.")
                st.session_state["mostra_setup"] = False
                st.rerun()

    st.stop()


# ============================================================
# LIVE DASHBOARD
# ============================================================

ricalcola_classifiche_gironi()
salva_dati(db)

num_tavoli = int(db.get("num_tavoli", 6))
partite = tutte_partite_gironi()

in_corso = [m for m in partite if not m.get("giocata") and m.get("in_corso")]
da_giocare = [m for m in partite if not m.get("giocata") and not m.get("in_corso")]

occupati = {m.get("tavolo") for m in in_corso if m.get("tavolo") is not None}
liberi = [x for x in range(1, num_tavoli + 1) if x not in occupati]

if db["stato"] == "gironi" and liberi and da_giocare:
    for tavolo in liberi:
        if not da_giocare:
            break
        m = da_giocare.pop(0)
        m["in_corso"] = True
        m["tavolo"] = tavolo
    salva_dati(db)

in_corso = sorted(
    [m for m in partite if not m.get("giocata") and m.get("in_corso")],
    key=lambda m: m.get("tavolo", 999),
)
da_giocare = [m for m in partite if not m.get("giocata") and not m.get("in_corso")]


# ============================================================
# PERSONAL CARD
# ============================================================

if coppia_selezionata != "-- Seleziona la tua coppia --":
    mio_girone = next(
        (g for g, lista in db["gironi"].items() if coppia_selezionata in lista),
        None,
    )
    mio_pos = None
    mie_stats = None

    if mio_girone:
        class_g = classifica_girone(mio_girone)
        for i, (c, stats) in enumerate(class_g, 1):
            if c == coppia_selezionata:
                mio_pos = i
                mie_stats = stats
                break

    mio_match = next(
        (
            m for m in in_corso
            if coppia_selezionata in (m["c1"], m["c2"])
        ),
        None,
    )
    mia_coda = next(
        (
            i + 1 for i, m in enumerate(da_giocare[:num_tavoli])
            if coppia_selezionata in (m["c1"], m["c2"])
        ),
        None,
    )

    st.markdown("### 👤 La tua dashboard")
    cols = st.columns(4)
    with cols[0]:
        st.metric("Girone", mio_girone or "—")
    with cols[1]:
        st.metric("Posizione", f"{mio_pos}°" if mio_pos else "—")
    with cols[2]:
        st.metric("Punti", mie_stats.get("punti", 0) if mie_stats else 0)
    with cols[3]:
        st.metric("DR", f"{mie_stats.get('dr', 0):+d}" if mie_stats else "0")

    if mio_match:
        avv = mio_match["c2"] if mio_match["c1"] == coppia_selezionata else mio_match["c1"]
        st.markdown(
            f"""
<div class="card live-card center">
    <div class="gold" style="font-size:13px;font-weight:900">🔴 LIVE • BILIARDINO {mio_match.get("tavolo")}</div>
    <div class="value" style="margin:8px 0">{esc(coppia_selezionata)} <span class="muted">VS</span> {esc(avv)}</div>
    <div class="small muted">Inserisci il risultato quando avete terminato.</div>
</div>
""",
            unsafe_allow_html=True,
        )

        with st.expander("🎯 Inserisci risultato", expanded=True):
            g1 = selettore_gol_bottoni(
                f"user_g1_{mio_match['id']}",
                mio_match.get("gol1", 0),
            )
            g2 = selettore_gol_bottoni(
                f"user_g2_{mio_match['id']}",
                mio_match.get("gol2", 0),
            )
            if st.button("✅ CONFERMA RISULTATO", use_container_width=True):
                mio_match["gol1"] = g1
                mio_match["gol2"] = g2
                mio_match["giocata"] = True
                mio_match["in_corso"] = False
                mio_match["tavolo"] = None
                ricalcola_classifiche_gironi()
                salva_dati(db)
                st.success("Risultato registrato.")
                st.rerun()
    elif mia_coda:
        st.markdown(
            f"""
<div class="card green-card center">
    <div class="green" style="font-weight:900">⏳ SEI IN CODA</div>
    <div class="value">POSIZIONE #{mia_coda}</div>
    <div class="small muted">Preparati: il prossimo biliardino libero sarà assegnato automaticamente.</div>
</div>
""",
            unsafe_allow_html=True,
        )


# ============================================================
# LIVE TABLES
# ============================================================

if db["stato"] == "gironi":
    st.header("🔥 Arena Live")
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("🎮 Tavoli occupati")
        if not in_corso:
            st.markdown("<div class='card center muted'>Nessuna partita in corso.</div>", unsafe_allow_html=True)
        else:
            for m in in_corso:
                coinvolto = (
                    is_admin
                    or coppia_selezionata in (m["c1"], m["c2"])
                )
                st.markdown(
                    f"""
<div class="card live-card">
    <div class="gold small">🏟️ BILIARDINO {m.get("tavolo")} • {esc(m["girone"])}</div>
    <div style="text-align:center;font-size:18px;font-weight:800;margin-top:8px">
        {esc(m["c1"])}<br><span class="muted">VS</span><br>{esc(m["c2"])}
    </div>
</div>
""",
                    unsafe_allow_html=True,
                )

                if coinvolto:
                    with st.expander(f"📝 Risultato • Tavolo {m.get('tavolo')}"):
                        g1 = selettore_gol_bottoni(f"live_{m['id']}_g1", m.get("gol1", 0))
                        g2 = selettore_gol_bottoni(f"live_{m['id']}_g2", m.get("gol2", 0))
                        if st.button("💾 REGISTRA", key=f"live_save_{m['id']}", use_container_width=True):
                            m["gol1"], m["gol2"] = g1, g2
                            m["giocata"] = True
                            m["in_corso"] = False
                            m["tavolo"] = None
                            ricalcola_classifiche_gironi()
                            salva_dati(db)
                            st.rerun()

                if is_admin:
                    if st.button("🛑 Libera tavolo", key=f"free_{m['id']}", use_container_width=True):
                        m["in_corso"] = False
                        m["tavolo"] = None
                        salva_dati(db)
                        st.rerun()

    with right:
        st.subheader("⏳ Prossime partite")
        coda = da_giocare[:num_tavoli]
        if not coda:
            st.markdown("<div class='card center muted'>Coda vuota.</div>", unsafe_allow_html=True)
        else:
            for i, m in enumerate(coda, 1):
                st.markdown(
                    f"""
<div class="queue">
    <span class="green">#{i}</span>
    <b>{esc(m["c1"])}</b> <span class="muted">vs</span> <b>{esc(m["c2"])}</b>
    <div class="small muted">{esc(m["girone"])}</div>
</div>
""",
                    unsafe_allow_html=True,
                )


# ============================================================
# CLASSIFICHE
# ============================================================

st.divider()
st.header("📊 Classifiche")

for g_nome in db["gironi"]:
    class_g = classifica_girone(g_nome)
    rows = []
    for pos, (c, info) in enumerate(class_g, 1):
        rows.append(
            {
                "#": pos,
                "Coppia": c,
                "PT": info.get("punti", 0),
                "G": info.get("partite_giocate", 0),
                "V": info.get("vinte", 0),
                "N": info.get("pareggiate", 0),
                "P": info.get("perse", 0),
                "GF": info.get("gf", 0),
                "GS": info.get("gs", 0),
                "DR": info.get("dr", 0),
            }
        )

    with st.expander(f"📁 {g_nome}", expanded=True):
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn(width="small"),
                "PT": st.column_config.NumberColumn(width="small"),
                "DR": st.column_config.NumberColumn(width="small"),
            },
        )


# ============================================================
# CALENDARIO
# ============================================================

st.divider()
st.header("📅 Calendario gironi")

tabs = st.tabs(list(db["calendario_gironi"].keys()))
for idx, g_nome in enumerate(db["calendario_gironi"]):
    with tabs[idx]:
        for turno in db["calendario_gironi"][g_nome]:
            st.markdown(f"**Turno {turno['turno']}**")
            for m in turno["partite"]:
                stato = (
                    f"<span class='green'><b>{m['gol1']} - {m['gol2']}</b></span>"
                    if m.get("giocata")
                    else ("<span class='gold'>LIVE</span>" if m.get("in_corso") else "<span class='muted'>VS</span>")
                )
                st.markdown(
                    f"""
<div class="match">
    <b>{esc(m["c1"])}</b> &nbsp; {stato} &nbsp; <b>{esc(m["c2"])}</b>
</div>
""",
                    unsafe_allow_html=True,
                )

                if is_admin:
                    with st.expander(f"⚙️ Admin • {m['c1']} vs {m['c2']}"):
                        g1 = selettore_gol_bottoni(f"adm_{m['id']}_g1", m.get("gol1", 0))
                        g2 = selettore_gol_bottoni(f"adm_{m['id']}_g2", m.get("gol2", 0))
                        if st.button("💾 SALVA", key=f"adm_save_{m['id']}", use_container_width=True):
                            m["gol1"], m["gol2"] = g1, g2
                            m["giocata"] = True
                            m["in_corso"] = False
                            m["tavolo"] = None
                            ricalcola_classifiche_gironi()
                            salva_dati(db)
                            st.rerun()


# ============================================================
# GENERAZIONE FASI FINALI
# ============================================================

if db["stato"] == "gironi":
    st.divider()

    if is_admin:
        st.header("🏆 Qualificazione e fasi finali")

        qual_per_girone = int(db.get("num_qualificate_knockout", 4))
        totale_qual = len(db["gironi"]) * qual_per_girone
        totale_coppie = len(db["coppie"])

        st.markdown(
            f"""
<div class="card green-card">
    <div class="kicker">Main Event</div>
    <div class="value green">{totale_qual} QUALIFICATE</div>
    <div class="small muted">
        {qual_per_girone} per girone • {totale_coppie - totale_qual} verso la Fascia B
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # Si può generare solo quando tutte le partite dei gironi sono terminate.
        tutte_finite = all(m.get("giocata") for m in tutte_partite_gironi())

        if not tutte_finite:
            st.warning("Le fasi finali saranno generabili quando tutte le partite dei gironi saranno concluse.")
        elif totale_qual > 32:
            st.error("Il Main Event supporta massimo 32 qualificate.")
        else:
            if st.button(
                "🏆 GENERA / RIGENERA MAIN EVENT + FASCIA B",
                use_container_width=True,
            ):
                ricalcola_classifiche_gironi()

                qualificate = []
                non_qualificate = []

                for g_nome in db["gironi"]:
                    class_g = classifica_girone(g_nome)
                    qualificate.extend([c for c, _ in class_g[:qual_per_girone]])
                    non_qualificate.extend([c for c, _ in class_g[qual_per_girone:]])

                # Ranking globale per le teste di serie.
                qualificate_rank = classifica_globale(qualificate)
                qualificate_ordinate = [r["coppia"] for r in qualificate_rank]

                # Fascia B: stesse regole a eliminazione, con bye se necessario.
                nonq_rank = classifica_globale(non_qualificate)
                nonq_ordinate = [r["coppia"] for r in nonq_rank]

                db["tabellone_a"] = costruisci_tabellone_da_squadre(
                    qualificate_ordinate, "main"
                )
                db["tabellone_b"] = costruisci_tabellone_da_squadre(
                    nonq_ordinate, "fasciaB"
                )
                db["terzo_quarto_a"] = []
                db["terzo_quarto_b"] = []
                db["podio"] = {}
                db["meta_torneo"]["qualificate_totali"] = len(qualificate_ordinate)
                db["meta_torneo"]["non_qualificate_totali"] = len(nonq_ordinate)
                db["stato"] = "fasi_finali"
                db["fasi_finali_configurate"] = True
                salva_dati(db)
                st.success(
                    f"Main Event: {len(qualificate_ordinate)} coppie • Fascia B: {len(nonq_ordinate)} coppie."
                )
                st.rerun()


# ============================================================
# RENDER BRACKET
# ============================================================

def render_bracket(tabellone, titolo, chiave, terzo_quarto_key):
    st.subheader(titolo)

    if not tabellone:
        st.markdown(
            "<div class='card center muted'>Tabellone non disponibile.</div>",
            unsafe_allow_html=True,
        )
        return

    # Generazione progressiva del turno successivo.
    aggiorna_tabellone(tabellone, "main" if chiave == "tabellone_a" else "fasciaB")
    salva_dati(db)

    for turno_idx, turno in enumerate(tabellone):
        nome = turno.get("nome", f"Turno {turno.get('turno')}")
        partite_turno = turno.get("partite", [])

        st.markdown(
            f"<div class='bracket-title'>⚡ {esc(nome)}</div>",
            unsafe_allow_html=True,
        )

        if turno.get("bye"):
            st.markdown(
                "<span class='badge green-b'>BYE / QUALIFICAZIONE AUTOMATICA</span> "
                + " ".join(f"<span class='badge'>{esc(x)}</span>" for x in turno["bye"]),
                unsafe_allow_html=True,
            )

        tutti_giocati = True
        perdenti = []

        for m in partite_turno:
            if m.get("s2") == "RIPOSO":
                m["giocata"] = True
                m["vincente"] = m["s1"]

            if m.get("giocata"):
                winner = m.get("vincente")
                loser = m["s2"] if winner == m["s1"] else m["s1"]
                if loser != "RIPOSO":
                    perdenti.append(loser)

                if winner:
                    centro = f"<span class='green'><b>🏆 {esc(winner)}</b></span>"
                else:
                    centro = "<span class='muted'>Da assegnare</span>"
            else:
                tutti_giocati = False
                centro = "<span class='muted'>VS</span>"

            st.markdown(
                f"""
<div class="match">
    <div style="font-size:17px;font-weight:800">{esc(m["s1"])}</div>
    <div style="margin:5px 0">{centro}</div>
    <div style="font-size:17px;font-weight:800">{esc(m["s2"])}</div>
    {"<div class='small muted'>Risultato: " + str(m.get("gol1",0)) + " - " + str(m.get("gol2",0)) + "</div>" if m.get("giocata") else ""}
</div>
""",
                unsafe_allow_html=True,
            )

            if is_admin and not m.get("giocata") and m.get("s2") != "RIPOSO":
                with st.expander(f"⚙️ Gestisci • {m['s1']} vs {m['s2']}"):
                    st.markdown("**Gol / risultato**")
                    g1 = selettore_gol_bottoni(f"ko_{m['id']}_g1", m.get("gol1", 0))
                    g2 = selettore_gol_bottoni(f"ko_{m['id']}_g2", m.get("gol2", 0))

                    a, b = st.columns(2)
                    with a:
                        if st.button(f"🏆 Vince {m['s1']}", key=f"ko_win1_{m['id']}", use_container_width=True):
                            m["gol1"], m["gol2"] = g1, g2
                            m["giocata"] = True
                            m["vincente"] = m["s1"]
                            salva_dati(db)
                            st.rerun()
                    with b:
                        if st.button(f"🏆 Vince {m['s2']}", key=f"ko_win2_{m['id']}", use_container_width=True):
                            m["gol1"], m["gol2"] = g1, g2
                            m["giocata"] = True
                            m["vincente"] = m["s2"]
                            salva_dati(db)
                            st.rerun()

        if tutti_giocati:
            aggiorna_tabellone(tabellone, "main" if chiave == "tabellone_a" else "fasciaB")

    # Finale 3/4 del Main: quando sono terminate le semifinali.
    if chiave == "tabellone_a" and tabellone:
        ultima = tabellone[-1]
        if len(ultima.get("partite", [])) == 1 and ultima.get("nome") == "FINALE":
            if len(tabellone) >= 2:
                semi = tabellone[-2]
                if len(semi.get("partite", [])) == 2 and all(m.get("giocata") for m in semi["partite"]):
                    if not db["terzo_quarto_a"]:
                        perd = perdenti_turno(semi)
                        if len(perd) == 2:
                            db["terzo_quarto_a"] = [{
                                "id": "main_terzo_quarto",
                                "s1": perd[0],
                                "s2": perd[1],
                                "giocata": False,
                                "vincente": None,
                                "gol1": 0,
                                "gol2": 0,
                            }]
                            salva_dati(db)

    if chiave == "tabellone_a" and db["terzo_quarto_a"]:
        tq = db["terzo_quarto_a"][0]
        st.markdown("<div class='bracket-title'>🥉 FINALE 3° / 4° POSTO</div>", unsafe_allow_html=True)
        if tq.get("giocata"):
            st.markdown(
                f"<div class='card purple-card center'><div class='value pink'>🥉 {esc(tq['vincente'])}</div></div>",
                unsafe_allow_html=True,
            )
        elif is_admin:
            a, b = st.columns(2)
            with a:
                if st.button(f"🥉 Vince {tq['s1']}", key="tq_a", use_container_width=True):
                    tq["giocata"] = True
                    tq["vincente"] = tq["s1"]
                    salva_dati(db)
                    st.rerun()
            with b:
                if st.button(f"🥉 Vince {tq['s2']}", key="tq_b", use_container_width=True):
                    tq["giocata"] = True
                    tq["vincente"] = tq["s2"]
                    salva_dati(db)
                    st.rerun()

    if chiave == "tabellone_a":
        podio = assegna_podio(tabellone, db["terzo_quarto_a"])
        if podio.get("1"):
            db["podio"] = podio
            salva_dati(db)
            st.markdown(
                f"""
<div class="card" style="border-color:rgba(255,170,0,.65);text-align:center">
    <div class="gold" style="font-family:Orbitron;font-size:14px">🏆 PODIO CYBER ARENA</div>
    <div style="font-size:28px;font-weight:900;margin-top:12px">🥇 {esc(podio["1"])}</div>
    <div style="font-size:21px;margin-top:8px">🥈 {esc(podio["2"])}</div>
    <div style="font-size:19px;margin-top:8px">🥉 {esc(podio["3"]) if podio.get("3") else "Da assegnare"}</div>
    <div class="muted" style="margin-top:6px">4° {esc(podio["4"]) if podio.get("4") else "Da assegnare"}</div>
</div>
""",
                unsafe_allow_html=True,
            )


if db["stato"] == "fasi_finali":
    st.divider()
    st.header("🏆 FASI FINALI")
    st.caption(
        f"Main Event: {db['meta_torneo'].get('qualificate_totali', 0)} qualificate • "
        f"Fascia B: {db['meta_torneo'].get('non_qualificate_totali', 0)} coppie"
    )

    tab_main, tab_b = st.tabs(["⭐ MAIN EVENT", "🔻 FASCIA B"])

    with tab_main:
        render_bracket(db["tabellone_a"], "⭐ Tabellone Principale", "tabellone_a", "terzo_quarto_a")

    with tab_b:
        render_bracket(db["tabellone_b"], "🔻 Fascia B", "tabellone_b", "terzo_quarto_b")


# ============================================================
# ADMIN INFO
# ============================================================

if is_admin:
    with st.expander("🧪 Stato tecnico / debug"):
        st.json(
            {
                "stato": db["stato"],
                "coppie": len(db.get("coppie", [])),
                "gironi": len(db.get("gironi", {})),
                "tavoli": db.get("num_tavoli"),
                "qualificate_per_girone": db.get("num_qualificate_knockout"),
                "main_qualificate": db.get("meta_torneo", {}).get("qualificate_totali", 0),
                "fascia_b": db.get("meta_torneo", {}).get("non_qualificate_totali", 0),
                "partite_in_corso": len(in_corso),
                "partite_in_coda": len(da_giocare),
            }
        )

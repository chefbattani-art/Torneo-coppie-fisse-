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
      giocate_fatte, giocate_tot = calcola_partite_giocate_coppia(g_nome, c_nome)
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

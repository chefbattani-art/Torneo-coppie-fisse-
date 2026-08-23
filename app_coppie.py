        if st.button("🚀 Crea Gironi e Sorteggia Coppie"):
            coppie = []
            for line in whatsapp_text.split("\n"):
                nome_c = pulisci_nome(line)
                if nome_c:
                    coppie.append(nome_c)
            
            num_g = int(db["num_gironi"])
            
            if len(coppie) < (num_g * 2):
                st.error(f"Hai inserito {len(coppie)} coppie. Con {num_g} gironi servono almeno {num_g * 2} coppie.")
            else:
                db["coppie"] = coppie
                random.shuffle(coppie)
                
                # Crea esattamente i gironi richiesti (es. A, B, C, D se sono 4)
                nomi_gironi = [chr(65 + i) for i in range(num_g)]
                gironi_dict = {f"Girone {g}": [] for g in nomi_gironi}
                
                # Distribuzione equa e pulita delle coppie in tutti i gironi stabiliti
                for idx, c in enumerate(coppie):
                    g_scelto = f"Girone {nomi_gironi[idx % num_g]}"
                    gironi_dict[g_scelto].append(c)
                
                db["gironi"] = gironi_dict
                db["punti_gironi"] = {g: {c: 0 for c in lst} for g, lst in gironi_dict.items()}
                
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
                                    "c1": s1, "c2": s2,
                                    "giocata": False, "in_corso": False,
                                    "gol1": 0, "gol2": 0
                                })
                        turni_turno.append({"turno": t + 1, "partite": partite_turno})
                        squadre = [squadre[0]] + [squadre[-1]] + squadre[1:-1]
                    
                    calendario_totale[g_nome] = turni_turno
                
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

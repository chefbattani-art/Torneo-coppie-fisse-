st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@700&display=swap');
    
    :root {
        --bg: #050510;
        --panel: rgba(14, 14, 30, 0.85);
        --cyan: #00F0FF;
        --magenta: #FF00E5;
        --acid: #00FF88;
        --orange: #FF8A00;
        --text: #EAF0FF;
        --muted: #7A7FB5;
        --border: rgba(0, 240, 255, 0.25);
    }

    .stApp {
        background: 
          linear-gradient(0deg, rgba(5,5,16,1) 0%, rgba(11,8,32,1) 100%),
          repeating-linear-gradient(90deg, rgba(0,240,255,0.03) 0 1px, transparent 1px 60px);
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Header HUD */
    h1 { 
        font-family: 'Space Grotesk' !important;
        letter-spacing: 3px !important;
        text-transform: uppercase;
        color: #fff !important;
        text-shadow: 0 0 15px var(--cyan), 0 0 30px var(--cyan);
    }

    /* Card base - angolo tagliato cyber */
    .cyber-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-left: 3px solid var(--cyan);
        border-radius: 4px 16px 4px 16px;
        backdrop-filter: blur(12px);
        box-shadow: 0 0 20px rgba(0,240,255,0.12), inset 0 0 20px rgba(0,240,255,0.04);
        padding: 18px !important;
    }

    /* LIVE match - la killer card */
    .match-live-card {
        background: linear-gradient(135deg, rgba(20,20,40,0.95) 0%, rgba(10,10,25,0.95) 100%);
        border: 1.5px solid var(--cyan);
        border-radius: 4px 18px 4px 18px;
        box-shadow: 0 0 30px rgba(0,240,255,0.25), 0 0 60px rgba(255,0,229,0.15);
        position: relative;
        overflow: hidden;
    }
    .match-live-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, var(--cyan), var(--magenta), var(--cyan));
        animation: scan 2s linear infinite;
    }

    /* Bottoni cyber */
    div.stButton > button {
        background: linear-gradient(180deg, #16162E 0%, #0E0E22 100%) !important;
        border: 1.2px solid var(--cyan) !important;
        color: var(--cyan) !important;
        border-radius: 6px 14px 6px 14px !important;
        font-family: 'JetBrains Mono' !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        height: 56px !important;
        font-size: 14px !important;
        box-shadow: 0 0 15px rgba(0,240,255,0

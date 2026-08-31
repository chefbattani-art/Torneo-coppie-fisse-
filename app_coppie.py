CYBER_CSS = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@700&display=swap');
:root {
  --bg: #050510;
  --panel: rgba(14,14,30,0.88);
  --cyan: #00F0FF;
  --magenta: #FF00E5;
  --acid: #00FF88;
  --orange: #FF8A00;
  --text: #EAF0FF;
  --muted: #7A7FB5;
  --border: rgba(0,240,255,0.25);
}
.stApp {
  background: radial-gradient(120% 80% at 50% 0%, #1a1440 0%, #0a0a1e 45%, #050510 100%);
  color: var(--text);
  font-family: 'Space Grotesk', sans-serif;
}
h1 {
  font-family: 'Space Grotesk'!important;
  letter-spacing: 3px!important;
  text-transform: uppercase;
  text-shadow: 0 0 15px var(--cyan)!important;
}
.cyber-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-left: 3px solid var(--cyan);
  border-radius: 4px 16px 4px 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 0 20px rgba(0,240,255,0.12);
  padding: 18px!important;
  margin-bottom: 10px;
}
.match-live-card {
  background: linear-gradient(135deg, rgba(20,20,45,0.98), rgba(10,10,25,0.98));
  border: 1.5px solid var(--cyan);
  border-radius: 6px 18px;
  box-shadow: 0 0 30px rgba(0,240,255,0.25);
  position: relative;
  overflow: hidden;
  margin-bottom: 12px;
}
.match-live-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--cyan), var(--magenta));
  animation: scan 2s linear infinite;
}
.rank-row {
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(15,15,35,0.65);
  border-left: 3px solid transparent;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 12px 14px;
}
.rank-row.top4 { border-left-color: var(--acid); background: rgba(0,255,136,0.08); }
div.stButton > button {
  background: linear-gradient(180deg, #16162E, #0E0E22)!important;
  border: 1.2px solid var(--cyan)!important;
  color: var(--cyan)!important;
  border-radius: 6px 14px!important;
  font-family: 'JetBrains Mono'!important;
  height: 54px!important;
}
div.stButton > button:hover {
  background: var(--cyan)!important;
  color: #000!important;
}
@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>
'''
st.markdown(CYBER_CSS, unsafe_allow_html=True)

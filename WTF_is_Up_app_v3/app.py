
import streamlit as st, json, os, random

st.set_page_config(page_title="WTF is Up?", page_icon="💬", layout="centered")

DATA_DIR = os.path.dirname(__file__)
with open(os.path.join(DATA_DIR, "content.json"), "r", encoding="utf-8") as f:
    CONTENT = json.load(f)

def init_state():
    ss = st.session_state
    ss.setdefault("phase", "welcome")
    ss.setdefault("handle", "")
    ss.setdefault("age_bracket", "13-15")
    ss.setdefault("adjective", "")
    ss.setdefault("animal", "")
    ss.setdefault("selected_moods", set())
    ss.setdefault("selected_scenarios", set())
    ss.setdefault("technique", None)
    ss.setdefault("time_choice", None)
    ss.setdefault("theme_color", "#AAB7F8")

init_state()

PRIMARY = "#AAB7F8"
TEXT = "#333333"

TECH_COLORS = {
    "Breath Work": "#CFE8FF",
    "Mindfulness": "#FFFACD",
    "Thinking Techniques": "#F8CFE3",
    "Other": "#E6E6FA"
}

def apply_css(bg_color=None, radial=False):
    theme = st.session_state.get("theme_color", PRIMARY)
    accent = theme
    if bg_color: accent = bg_color
    gradient_css = ""
    if radial:
        gradient_css = f"background: radial-gradient(circle at 50% 30%, #FFFFFF 0%, {accent} 60%, {accent} 100%) !important;"
    st.markdown(f"""
    <style>
      .stApp {{
        background: {accent};
        {gradient_css}
      }}
      h1,h2,h3,p, label, div, span {{ color: {TEXT}; }}
      .header-bar {{
        text-align:center;
        margin-bottom: 10px;
      }}
      .header-title {{
        display:inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(0,0,0,0.05);
      }}
      .center-card {{
        background: white;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.12);
        border: 1px solid rgba(0,0,0,0.05);
      }}
      .floating-wrap {{
        position: relative;
        width: 100%;
        height: 540px;
        overflow: hidden;
      }}
      .float {{
        position: absolute;
        padding: 12px 16px;
        border-radius: 14px;
        background: rgba(255,255,255,0.85);
        border: 2px solid rgba(0,0,0,0.05);
        box-shadow: 0 10px 20px rgba(0,0,0,0.10);
        font-weight: 700;
        cursor: pointer;
        user-select: none;
        transition: transform .15s ease, background .15s ease;
        color: #2d2d2d;
      }}
      .float:hover {{
        transform: translateY(-2px) scale(1.02);
      }}
      .float.selected {{
        background: rgba(255,250,205,0.95);
      }}
      @keyframes orbit {{
        from {{ transform: rotate(0deg) translateX(var(--radius)) rotate(0deg); }}
        to   {{ transform: rotate(360deg) translateX(var(--radius)) rotate(-360deg); }}
      }}
      .orbiter {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform-origin: center;
        animation: orbit var(--duration) linear infinite;
      }}
      .question {{
        position:absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%,-50%);
        background: rgba(255,255,255,0.95);
        padding: 16px 22px;
        border-radius: 18px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.12);
        border: 1px solid rgba(0,0,0,0.05);
        font-weight: 800;
      }}
      .pill {{
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.9);
        color: #333;
        font-weight: 600;
        margin: 6px 6px 0 0;
        border: 1px solid rgba(0,0,0,0.05);
      }}
      .time-grid {{
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 10px;
      }}
      .time-btn {{
        width: 100%;
        background: white;
        border: 2px solid rgba(0,0,0,0.05);
        border-radius: 12px;
        padding: 14px 10px;
        font-weight: 700;
        color: #333;
      }}
      .time-btn:hover {{ background: rgba(255,255,255,0.9); }}
      .tech-btn {{
        width: 100%; padding: 16px 12px; border-radius: 12px; border:2px solid rgba(0,0,0,0.05);
        font-weight:800;
      }}
    </style>
    """, unsafe_allow_html=True)

def header():
    st.markdown("<div class='header-bar'><span class='header-title'>💬 WTF is Up?</span></div>", unsafe_allow_html=True)

def recommend(tags, minutes, age_bracket):
    items = CONTENT["items"]
    def ok_age(item_age):
        if age_bracket == "13-15" and item_age.startswith("16"):
            return False
        return True
    def s(it):
        if not ok_age(it.get("age_range","13-18")):
            return -1e9
        if minutes is not None and it.get("minutes", 10) > minutes:
            return -1e9
        overlap = len(set(it.get("tags", [])) & set(tags))
        time_fit = 1.0 if it.get("minutes", 10) <= minutes else 0.0
        return overlap*2 + time_fit
    ranked = sorted(items, key=lambda x: s(x), reverse=True)
    out = [x for x in ranked if s(x) > -1e5]
    return out[:3] if out else ranked[:2]

def feelings_orbit(question_text, options, state_set_name):
    apply_css(bg_color="#AAB7F8", radial=True)
    header()
    st.markdown("<div class='floating-wrap'>", unsafe_allow_html=True)
    st.markdown(f"<div class='question'>{question_text}</div>", unsafe_allow_html=True)
    chosen = st.session_state.get(state_set_name, set())
    for i, opt in enumerate(options):
        radius = 170 + (i % 3)*34
        dur = 14 + (i % 5)*2
        st.markdown(f"<div class='orbiter' style='--radius:{radius}px; --duration:{dur}s;'>", unsafe_allow_html=True)
        k = f"{state_set_name}_{i}"
        if st.button(opt, key=k):
            if opt in chosen: chosen.remove(opt)
            else: chosen.add(opt)
            st.session_state[state_set_name] = chosen
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if chosen:
        st.markdown("".join([f\"<span class='pill'>{x}</span>\" for x in chosen]), unsafe_allow_html=True)

# Flow
header()

if st.session_state.phase == "welcome":
    st.markdown("<div class='center-card'><h2>Welcome</h2><p>This app shares supportive, clinician-approved self-help resources for teens. It is educational and not a diagnosis or a substitute for professional care. If you are in crisis in the US, call or text 988.</p></div>", unsafe_allow_html=True)
    adjs = ["Ferocious","Curious","Gentle","Bold","Radiant","Calm","Brave","Witty","Kind","Steady","Swift","Bright"]
    animals = ["Penguin","Otter","Hawk","Dolphin","Panda","Tiger","Koala","Falcon","Fox","Seal","Heron","Lynx"]
    c1,c2,c3 = st.columns(3)
    with c1:
        st.session_state.adjective = st.selectbox("Pick an adjective", adjs, index=0)
    with c2:
        st.session_state.animal = st.selectbox("Pick an animal", animals, index=0)
    with c3:
        st.session_state.age_bracket = st.selectbox("Age range", ["13-15","16-18"], index=0)
    if st.button("Continue"):
        st.session_state.handle = f"{st.session_state.adjective} {st.session_state.animal}"
        st.session_state.phase = "feelings"
        st.rerun()

elif st.session_state.phase == "feelings":
    moods = ["anxious","sad","angry","stressed","panic","overwhelmed","lonely","sleep problems","school pressure","family conflict","bullying","sports pressure","focus","motivation","breakup","friend drama","body image","social media","rumination","worry"]
    feelings_orbit("How Do You Feel Today?", [m.title() for m in moods], "selected_moods")
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("⬅ Back"): st.session_state.phase = "welcome"; st.rerun()
    with c2:
        if st.button("Clear feelings"): st.session_state.selected_moods = set(); st.rerun()
    with c3:
        if st.button("Next ➜", disabled=not bool(st.session_state.selected_moods)): st.session_state.phase = "scenarios"; st.rerun()

elif st.session_state.phase == "scenarios":
    scenarios = ["Argument with a friend","Got a bad grade","Sports pressure","Family conflict","Online drama","Felt left out"]
    feelings_orbit("Did Something Happen Today?", scenarios, "selected_scenarios")
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("⬅ Back"): st.session_state.phase = "feelings"; st.rerun()
    with c2:
        if st.button("Clear scenarios"): st.session_state.selected_scenarios = set(); st.rerun()
    with c3:
        if st.button("Next ➜"): st.session_state.phase = "techniques"; st.rerun()

elif st.session_state.phase == "techniques":
    apply_css(bg_color="#AAB7F8", radial=False)
    header()
    st.markdown("### How Should We Fix This?")
    opts = ["Breath Work","Mindfulness","Thinking Techniques","Other"]
    cols = st.columns(4)
    for i,opt in enumerate(opts):
        with cols[i]:
            color = TECH_COLORS[opt]
            style = f"background:{color}; border:2px solid rgba(0,0,0,0.05); border-radius:12px; padding:12px; font-weight:800;"
            st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)
            if st.button(f"Select {opt}", key=f"tech_{i}", use_container_width=True):
                st.session_state.technique = opt
                st.session_state.theme_color = color
                st.session_state.phase = "time"
                st.rerun()
    if st.button("⬅ Back"): st.session_state.phase = "scenarios"; st.rerun()

elif st.session_state.phase == "time":
    apply_css(bg_color=st.session_state.get("theme_color", PRIMARY), radial=False)
    header()
    st.markdown("### How much time do you have?")
    for row in [ [2,5,10,15,20] ]:
        cols = st.columns(5)
        for i,t in enumerate(row):
            with cols[i]:
                if st.button(f"{t} min", key=f"time_{t}", use_container_width=True):
                    st.session_state.time_choice = t
                    st.session_state.phase = "plan"; st.rerun()
    if st.button("⬅ Back"): st.session_state.phase = "techniques"; st.rerun()

elif st.session_state.phase == "plan":
    apply_css(bg_color=st.session_state.get("theme_color", PRIMARY), radial=False)
    header()
    st.markdown("### Your plan")
    tags = [m.lower() for m in st.session_state.selected_moods]
    recs = recommend(tags, st.session_state.time_choice or 10, st.session_state.age_bracket)
    if not recs:
        st.info("Here are a few safe starters.")
        recs = CONTENT["items"][:2]
    for it in recs:
        with st.container(border=True):
            st.markdown(f"**{it['title']}**")
            st.caption(it["summary"])
            st.write("Modality:", it.get("modality","text"), " • Minutes:", it.get("minutes",5))
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Start over"):
            for k in ["phase","selected_moods","selected_scenarios","technique","time_choice"]:
                if k=="phase": st.session_state[k] = "welcome"
                elif isinstance(st.session_state.get(k), set): st.session_state[k] = set()
                else: st.session_state[k]=None
            st.session_state.theme_color = PRIMARY
            st.rerun()
    with c2:
        if st.button("Pick different moods"):
            st.session_state.phase = "feelings"; st.rerun()
    with c3:
        if st.button("Back to time"):
            st.session_state.phase = "time"; st.rerun()

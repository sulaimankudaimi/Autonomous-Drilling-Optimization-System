import streamlit as st
import pandas as pd
import time

# --- 1. المحرك الفيزيائي الموحد (The Unified Engine) ---
def run_physics(wob, rpm, hardness, wear):
    rop = (wob * 0.6) * (rpm * 0.02) / (hardness * 0.1)
    rop = rop * (1 - (wear / 100))
    vib = (rpm * 0.1) + (wob * 0.2) + (hardness * 0.05)
    torque = (wob * 0.8) + (vib * 0.5)
    mse = (wob / 0.1) + (120 * 3.14 * rpm * torque) / (rop + 0.1)
    wear_inc = (mse / 1000000) * (hardness / 50)
    return round(rop, 2), round(mse, 2), round(vib, 2), wear_inc

# --- 2. إعدادات الصفحة والتنقل ---
st.set_page_config(page_title="PrecisionDrill AI Pro", layout="wide")

st.sidebar.title("🛡️ PrecisionDrill AI")
app_mode = st.sidebar.selectbox("Select System Mode", 
    ["Live Field Monitor", "Strategy Comparison (Showdown)"])

st.sidebar.markdown("---")
hardness = st.sidebar.slider("Formation Hardness", 20, 200, 100)
safety_limit = st.sidebar.slider("Vibration Safety Limit", 10, 50, 25)

# --- 3. الوضع الأول: المراقبة الميدانية (Asset Tracking) ---
if app_mode == "Live Field Monitor":
    st.header("📊 Real-Time Field Monitor & Asset Tracking")
    
    if 'field_log' not in st.session_state:
        st.session_state.field_log = []
        st.session_state.f_wob, st.session_state.f_rpm = 25.0, 70.0
        st.session_state.f_wear = 0.0

    m1, m2, m3, m4 = st.columns(4)
    r_metric = m1.empty()
    e_metric = m2.empty()
    v_metric = m3.empty()
    w_metric = m4.empty()

    if st.button("🚀 Start Drilling Mission"):
        for i in range(1, 16):
            rop, mse, vib, wear_inc = run_physics(st.session_state.f_wob, st.session_state.f_rpm, hardness, st.session_state.f_wear)
            st.session_state.f_wear = min(100.0, st.session_state.f_wear + wear_inc)
            
            # منطق الأمان
            if vib > safety_limit:
                st.session_state.f_wob -= 2; st.session_state.f_rpm -= 5
            else:
                st.session_state.f_wob += 0.5; st.session_state.f_rpm += 1

            st.session_state.field_log.append({"Step": i, "ROP": rop, "MSE": mse, "Vib": vib, "Wear": st.session_state.f_wear})
            
            r_metric.metric("ROP", f"{rop} m/h")
            e_metric.metric("MSE", f"{int(mse)}")
            v_metric.metric("Vib", f"{vib}")
            w_metric.metric("Bit Wear", f"{round(st.session_state.f_wear, 1)}%")
            time.sleep(0.3)
        
        st.dataframe(pd.DataFrame(st.session_state.field_log).tail(5))
        st.download_button("📥 Download Technical Report", pd.DataFrame(st.session_state.field_log).to_csv().encode('utf-8'), "report.csv")

# --- 4. الوضع الثاني: المقارنة الاستراتيجية (Showdown) ---
elif app_mode == "Strategy Comparison (Showdown)":
    st.header("🥊 Strategic Benchmarking: AI vs Manual")
    
    if st.button("🏁 Start Head-to-Head Challenge"):
        ai = {'wob': 25.0, 'rpm': 70.0, 'wear': 0.0, 'depth': 0.0}
        man = {'wob': 35.0, 'rpm': 90.0, 'wear': 0.0, 'depth': 0.0}
        
        c_man, c_vs, c_ai = st.columns([2, 1, 2])
        
        for t in range(1, 16):
            # محاكاة الطرفين
            m_rop, _, m_vib, m_w_inc = run_physics(man['wob'], man['rpm'], hardness, man['wear'])
            man['wear'] = min(100.0, man['wear'] + m_w_inc); man['depth'] += (m_rop/60)
            
            a_rop, a_mse, a_vib, a_w_inc = run_physics(ai['wob'], ai['rpm'], hardness, ai['wear'])
            if a_vib > safety_limit: ai['wob'] -= 2; ai['rpm'] -= 5
            else: ai['wob'] += 0.5; ai['rpm'] += 1
            ai['wear'] = min(100.0, ai['wear'] + a_w_inc); ai['depth'] += (a_rop/60)

            with c_man: st.error("👨‍🔧 Manual Driller"); st.metric("Depth", f"{round(man['depth'],2)}m"); st.metric("Wear", f"{round(man['wear'],1)}%")
            with c_ai: st.success("🤖 AI Autopilot"); st.metric("Depth", f"{round(ai['depth'],2)}m"); st.metric("Wear", f"{round(ai['wear'],1)}%")
            time.sleep(0.3)
        st.balloons()
import streamlit as st

def app_header():
    with st.container():
        st.markdown('<div class="app-title">🩺 看護診断/看護計画アシスタント <span class="pill">教育・支援用途</span></div>', unsafe_allow_html=True)
        st.write("**モデル**：gpt-4o-mini｜**役割**：臨床現場での豊富な経験を持つベテランの看護師｜**温度**：0.1（再現性重視）")

def disclaimer():
    st.info("本アプリは支援目的であり、最終判断は医療従事者に委ねられるものとなります。対象は成人一般です。")

def patient_input_form():
    return st.text_area(
        "患者情報（例：主訴・既往歴・バイタル・身体所見・検査値・ADL・心理社会面 など）",
        height=180, placeholder="自由記載。実際の臨床現場の密度でご入力ください。"
    )

def format_selector():
    return st.radio(
        "出力形式を選択",
        options=["SOAP形式", "看護計画表形式", "両方"],
        horizontal=True
    )

def output_section_soap(soap_dict):
    if not soap_dict: return
    st.markdown("### 🧩 SOAP（抜粋）", help="S:患者発言/O:客観所見は入力から暗黙参照。ここではA/Pに絞って表示します。")
    with st.container():
        st.markdown("#### A（Assessment）")
        st.markdown(render_bullets(soap_dict.get("assessment")))
        st.markdown("#### P（Plan）")
        st.markdown(render_bullets(soap_dict.get("plan")))

def output_section_plan_table(plan_table):
    if not plan_table: return
    st.markdown("### 📋 看護計画表", help="NANDA-I/NIC/NOC 準拠（教育・支援目的）")
    # 行数を最大長で合わせ、空セルを補完
    rows = []
    n = max_len(plan_table)
    for i in range(n):
        rows.append({
            "看護問題（NANDA-I）": safe_get(plan_table, "problems", i),
            "アセスメント（根拠）": safe_get(plan_table, "assessments", i),
            "目標（NOC）": safe_get(plan_table, "goals", i),
            "看護介入（NIC）": safe_get(plan_table, "interventions", i),
            "評価": safe_get(plan_table, "evaluation", i),
        })
    st.table(rows)

def followup_box():
    return st.text_input(
        "出力結果に関する質問（例：「◯◯の意図は？」「◯◯の要点を要約して」）",
        placeholder="例：目標設定の短期目標の根拠を教えてください"
    )

def end_session_box():
    return st.button("🔚 終了", use_container_width=True)

def show_toast(msg, variant="ok"):
    color = {"ok":"ok", "warn":"warn", "error":"error"}.get(variant, "ok")
    st.markdown(f'<div class="{color}">{msg}</div>', unsafe_allow_html=True)

# helpers
def render_bullets(items):
    if not items: return "_該当なし_"
    return "\n".join([f"- {x}" for x in items])

def max_len(plan_table):
    return max(
        len(plan_table.get("problems", [])),
        len(plan_table.get("assessments", [])),
        len(plan_table.get("goals", [])),
        len(plan_table.get("interventions", [])),
        len(plan_table.get("evaluation", [])),
    )

def safe_get(dic, key, idx):
    arr = dic.get(key, [])
    return arr[idx] if idx < len(arr) else ""

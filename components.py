import streamlit as st
from datetime import datetime

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

# ========== Conversation history UI ==========
def history_timeline(history: list):
    """
    Render session-scoped conversation history.
    history: list of dicts with keys:
      - type: "generation" | "followup"
      - ts: ISO string
      - payload: dict (depends on type)
    """
    for item in history:
        ts = fmt_ts(item.get("ts"))
        if item["type"] == "generation":
            _render_generation_card(item["payload"], ts)
        elif item["type"] == "followup":
            _render_followup_card(item["payload"], ts)

def _render_generation_card(payload: dict, ts: str):
    with st.container():
        st.markdown(f"##### 🧪 生成結果 <span class='chip'>{payload.get('output_format','')}</span> <span class='small-muted'>｜{ts}</span>", unsafe_allow_html=True)
        st.markdown("<div class='bubble-u'><b>入力（患者情報）</b><br/>" + nl2br(payload.get("patient_text","（空）")) + "</div>", unsafe_allow_html=True)
        # SOAP
        if payload.get("output_format") in ("SOAP形式", "両方"):
            st.markdown("<div class='section-title'>SOAP（A/P）</div>", unsafe_allow_html=True)
            st.markdown("**A（Assessment）**")
            st.markdown(render_bullets(payload.get("soap",{}).get("assessment")))
            st.markdown("**P（Plan）**")
            st.markdown(render_bullets(payload.get("soap",{}).get("plan")))
        # 計画表
        if payload.get("output_format") in ("看護計画表形式", "両方"):
            st.markdown("<div class='section-title'>看護計画表</div>", unsafe_allow_html=True)
            rows = []
            n = max_len(payload.get("plan_table",{}))
            for i in range(n):
                rows.append({
                    "看護問題（NANDA-I）": safe_get(payload.get("plan_table",{}), "problems", i),
                    "アセスメント（根拠）": safe_get(payload.get("plan_table",{}), "assessments", i),
                    "目標（NOC）": safe_get(payload.get("plan_table",{}), "goals", i),
                    "看護介入（NIC）": safe_get(payload.get("plan_table",{}), "interventions", i),
                    "評価": safe_get(payload.get("plan_table",{}), "evaluation", i),
                })
            st.table(rows)

def _render_followup_card(payload: dict, ts: str):
    with st.container():
        st.markdown(f"##### 💬 フォローアップ <span class='small-muted'>｜{ts}</span>", unsafe_allow_html=True)
        st.markdown("<div class='bubble-u'><b>質問</b><br/>" + nl2br(payload.get("question","")) + "</div>", unsafe_allow_html=True)
        st.markdown("<div class='bubble-a'><b>回答</b><br/>" + nl2br(payload.get("answer","")) + "</div>", unsafe_allow_html=True)

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

def nl2br(text: str) -> str:
    return (text or "").replace("\n", "<br>")

def fmt_ts(iso_ts: str) -> str:
    try:
        return datetime.fromisoformat(iso_ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_ts or ""

SYSTEM_ROLE = """あなたは臨床現場での豊富な経験を持つベテランの看護師です。
出力は日本語。対象は成人一般。NANDA-I/NIC/NOCに準拠した用語を用います。
安全・再現性を重視し、臨床で実行可能な粒度で簡潔明瞭に記述します。
本アプリは教育・支援目的であり、最終判断は医療従事者に委ねられます。"""

PLAN_JSON_SPEC = """
必ず以下のJSONで返してください（余計なテキストは一切禁止）:
{
  "soap": {
    "assessment": [ "A1", "A2", "A3" ],
    "plan": [ "P1", "P2", "P3" ]
  },
  "plan_table": {
    "problems": [ "NANDA-Iラベル + 定義/関連因子（必要に応じて）" ],
    "assessments": [ "問題に関連する観察/測定・根拠" ],
    "goals": [ "NOC: 目標（短期/長期）＋評価指標（尺度があれば併記）" ],
    "interventions": [ "NIC: 具体的介入（頻度・タイミング・留意点）" ],
    "evaluation": [ "再評価方法・判定基準・次の一手" ]
  },
  "reasoning_summary": {
    "key_findings": [ "重要所見1", "重要所見2" ],
    "rationales": [ "根拠/臨床推論の要点" ],
    "differentials": [ "鑑別的観点（該当すれば）" ]
  }
}
リストは臨床的に妥当な件数（概ね3〜5）に調整してください。
"""

def build_generation_prompt(patient_text: str, output_format: str) -> list:
    user = f"""看護情報:
\"\"\"{patient_text}\"\"\"

要求:
- 出力形式の希望: {output_format}
- SOAP形式では A（Assessment）と P（Plan）を列挙
- 看護計画表形式では 問題/アセスメント/目標(NOC)/介入(NIC)/評価 を列挙
- NANDA-I/NIC/NOC に準拠（用語/視点）
- 重複や冗長表現を避ける
- 実行可能性・安全性を明示（頻度、条件、観察ポイントなど）

{PLAN_JSON_SPEC}
"""
    return [
        {"role":"system", "content": SYSTEM_ROLE},
        {"role":"user", "content": user}
    ]

def build_followup_prompt(context: dict, question: str) -> list:
    user = f"""コンテキスト（生成済み出力）:
{context}

質問: {question}

制約:
- 回答は上記コンテキストに基づく説明・要約・意図の明確化に限定。
- 生の思考連鎖の開示は禁止。代わりに reasoning_summary を根拠として説明。
- 看護情報や出力と無関係な質問には答えない。
- 箇条書きや短い段落で、臨床で使える形に簡潔化。
"""
    return [
        {"role":"system", "content": SYSTEM_ROLE},
        {"role":"user", "content": user}
    ]

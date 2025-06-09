import streamlit as st
import json
import sqlite3
from datetime import datetime, timedelta
from litellm import completion
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

class BehaviorChangeResearch:
    def __init__(self):
        self.model = "ollama/hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF"
        self.api_base = "http://localhost:11434"
        self.init_database()
    
    def init_database(self):
        """研究用データベースの初期化"""
        conn = sqlite3.connect('behavior_research.db')
        cursor = conn.cursor()
        
        # 参加者情報
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                age_group TEXT,
                occupation_category TEXT,
                english_motivation_level INTEGER,
                initial_interest_score INTEGER,
                experiment_group TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 行動変容段階（Transtheoretical Model）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                stage TEXT, -- precontemplation, contemplation, preparation, action, maintenance
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trigger_type TEXT,
                confidence_level INTEGER
            )
        ''')
        
        # インタラクション記録
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER,
                interaction_type TEXT,
                content TEXT,
                response_time_ms INTEGER,
                engagement_score INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 実験条件
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experimental_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition_name TEXT,
                description TEXT,
                psychological_principle TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_llm_response(self, messages):
        """LLMからの応答を取得"""
        try:
            response = completion(
                model=self.model,
                messages=messages,
                api_base=self.api_base
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"
    
    def generate_personalized_insight(self, participant_data, condition):
        """実験条件に基づく個人化されたインサイト生成"""
        
        if condition == "loss_aversion":
            prompt = f"""
            回答はすべて日本語で行ってください。
            行動経済学の「損失回避」の原理を使って、以下の参加者に英語学習の動機を与えるメッセージを作成してください。
            学術的で冷静なトーンで、過度な煽りは避けてください。
            
            参加者情報:
            - 年齢層: {participant_data.get('age_group')}
            - 職業カテゴリ: {participant_data.get('occupation_category')}
            - 現在の英語モチベーション: {participant_data.get('motivation_level')}/10
            
            以下の要素を含めてください：
            1. 具体的だが現実的な機会損失
            2. 時間経過による影響
            3. 改善可能性の示唆
            """
        
        elif condition == "social_proof":
            prompt = f"""
            回答はすべて日本語で行ってください。
            社会的証明の原理を使って、以下の参加者に英語学習の動機を与えるメッセージを作成してください。
            研究的な視点で、事実に基づいた内容にしてください。
            
            参加者情報:
            - 年齢層: {participant_data.get('age_group')}
            - 職業カテゴリ: {participant_data.get('occupation_category')}
            - 現在の英語モチベーション: {participant_data.get('motivation_level')}/10
            
            以下の要素を含めてください：
            1. 同じ属性の人々の行動パターン
            2. 統計的事実
            3. 成功事例（控えめに）
            """
        
        elif condition == "implementation_intention":
            prompt = f"""
            回答はすべて日本語で行ってください。
            実装意図の理論を使って、以下の参加者の英語学習計画を作成してください。
            具体的で実行可能な計画に焦点を当ててください。
            
            参加者情報:
            - 年齢層: {participant_data.get('age_group')}
            - 職業カテゴリ: {participant_data.get('occupation_category')}
            - 現在の英語モチベーション: {participant_data.get('motivation_level')}/10
            
            以下の要素を含めてください：
            1. if-then プランニング
            2. 具体的な時間と場所の指定
            3. 障壁への対処法
            """
        
        return self.get_llm_response([{"role": "user", "content": prompt}])

def show_consent_page():
    """研究参加同意書"""
    st.markdown("""
    # 📋 研究参加に関する説明書・同意書
    
    ## 研究題目
    **英語学習に対する行動変容を促すUXの効果に関する研究**
    
    ## 研究の目的
    本研究は、異なる心理学的アプローチが英語学習に対する動機や行動変容に与える影響を調査することを目的としています。
    
    ## 研究方法
    - 参加者は3つの実験グループのいずれかにランダムに割り当てられます
    - 各グループで異なる動機付け手法を体験していただきます
    - 行動変容の段階や興味レベルの変化を測定します
    
    ## 参加者の権利
    - いつでも研究参加を中止できます
    - 個人を特定できる情報は収集しません
    - データは研究目的でのみ使用されます
    
    ## 実験グループ
    1. **損失回避グループ**: 機会損失に焦点を当てたメッセージ
    2. **社会的証明グループ**: 他者の行動に基づいたメッセージ  
    3. **実装意図グループ**: 具体的な行動計画に焦点を当てたメッセージ
    """)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        consent = st.checkbox("上記の内容を理解し、研究に参加することに同意します")
    
    with col2:
        if consent and st.button("研究に参加", type="primary"):
            # ランダムに実験グループを割り当て
            groups = ["loss_aversion", "social_proof", "implementation_intention"]
            st.session_state.experiment_group = random.choice(groups)
            st.session_state.page = "baseline"
            st.rerun()

def show_baseline_assessment():
    """ベースライン測定"""
    st.markdown("""
    # 📊 ベースライン調査
    
    現在の状況について教えてください。これらの情報は研究の基準点として使用されます。
    """)
    
    with st.form("baseline_form"):
        st.subheader("👤 基本属性")
        
        col1, col2 = st.columns(2)
        with col1:
            age_group = st.selectbox("年齢層", ["18-24", "25-34", "35-44", "45-54", "55+"])
        with col2:
            occupation = st.selectbox("職業カテゴリ", [
                "学生", "技術職", "事務職", "営業職", "管理職", "専門職", "その他"
            ])
        
        st.subheader("📈 現在の状況")
        
        motivation_level = st.slider(
            "英語学習に対する現在のモチベーション",
            min_value=1, max_value=10, value=5,
            help="1: 全く興味がない ～ 10: 非常に興味がある"
        )
        
        interest_score = st.slider(
            "英語学習を始める可能性",
            min_value=1, max_value=10, value=5,
            help="1: 絶対に始めない ～ 10: すぐに始める"
        )
        
        current_stage = st.radio(
            "現在の行動段階",
            [
                "英語学習は考えていない（無関心期）",
                "英語学習を考えているが、まだ行動していない（関心期）", 
                "英語学習を始める準備をしている（準備期）",
                "現在英語学習をしている（実行期）",
                "英語学習を継続している（維持期）"
            ]
        )
        
        confidence = st.slider(
            "英語学習を継続できる自信",
            min_value=1, max_value=10, value=5,
            help="1: 全く自信がない ～ 10: 非常に自信がある"
        )
        
        submitted = st.form_submit_button("次へ", type="primary")
        
        if submitted:
            # データを保存
            participant_data = {
                'age_group': age_group,
                'occupation_category': occupation,
                'motivation_level': motivation_level,
                'interest_score': interest_score,
                'current_stage': current_stage,
                'confidence': confidence
            }
            st.session_state.participant_data = participant_data
            st.session_state.page = "intervention"
            st.rerun()

def show_intervention_page():
    """実験介入"""
    participant_data = st.session_state.get('participant_data', {})
    experiment_group = st.session_state.get('experiment_group', 'loss_aversion')
    
    research = BehaviorChangeResearch()
    
    # 実験グループの説明
    group_names = {
        "loss_aversion": "損失回避アプローチ",
        "social_proof": "社会的証明アプローチ", 
        "implementation_intention": "実装意図アプローチ"
    }
    
    st.markdown(f"""
    # 🧪 実験介入: {group_names[experiment_group]}
    
    あなたは「**{group_names[experiment_group]}**」グループに割り当てられました。
    以下のメッセージをお読みください。
    """)
    
    # AIによる個人化されたメッセージ生成
    with st.spinner("あなた専用のメッセージを生成中..."):
        personalized_message = research.generate_personalized_insight(participant_data, experiment_group)
    
    st.markdown(f"""
    ## 📝 あなたへのメッセージ
    
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #007bff;">
    {personalized_message}
    </div>
    """, unsafe_allow_html=True)
    
    # 反応の測定
    st.markdown("---")
    st.subheader("📊 あなたの反応")
    
    col1, col2 = st.columns(2)
    
    with col1:
        post_motivation = st.slider(
            "このメッセージを読んだ後の英語学習に対するモチベーション",
            min_value=1, max_value=10, value=participant_data.get('motivation_level', 5),
            help="1: 全く興味がない ～ 10: 非常に興味がある"
        )
    
    with col2:
        post_interest = st.slider(
            "このメッセージを読んだ後の英語学習を始める可能性",
            min_value=1, max_value=10, value=participant_data.get('interest_score', 5),
            help="1: 絶対に始めない ～ 10: すぐに始める"
        )
    
    message_effectiveness = st.slider(
        "このメッセージの説得力",
        min_value=1, max_value=10, value=5,
        help="1: 全く説得力がない ～ 10: 非常に説得力がある"
    )
    
    behavior_intention = st.radio(
        "今後の行動予定",
        [
            "何も変わらない",
            "英語学習について考えてみる",
            "具体的な学習方法を調べてみる", 
            "今日中に学習を始める",
            "学習計画を立ててすぐに始める"
        ]
    )
    
    if st.button("結果を送信", type="primary"):
        # 変化量を計算
        motivation_change = post_motivation - participant_data.get('motivation_level', 5)
        interest_change = post_interest - participant_data.get('interest_score', 5)
        
        st.session_state.results = {
            'motivation_change': motivation_change,
            'interest_change': interest_change,
            'message_effectiveness': message_effectiveness,
            'behavior_intention': behavior_intention,
            'post_motivation': post_motivation,
            'post_interest': post_interest
        }
        st.session_state.page = "results"
        st.rerun()

def show_results_page():
    """研究結果の表示"""
    participant_data = st.session_state.get('participant_data', {})
    results = st.session_state.get('results', {})
    experiment_group = st.session_state.get('experiment_group', '')
    
    st.markdown("""
    # 📊 あなたの実験結果
    
    実験にご参加いただき、ありがとうございました。以下があなたの結果です。
    """)
    
    # 変化量の可視化
    col1, col2, col3 = st.columns(3)
    
    with col1:
        motivation_change = results.get('motivation_change', 0)
        st.metric(
            "モチベーション変化", 
            f"{motivation_change:+.1f}",
            help="実験前後での変化量"
        )
    
    with col2:
        interest_change = results.get('interest_change', 0)
        st.metric(
            "学習意欲変化", 
            f"{interest_change:+.1f}",
            help="実験前後での変化量"
        )
    
    with col3:
        effectiveness = results.get('message_effectiveness', 0)
        st.metric(
            "メッセージ効果", 
            f"{effectiveness}/10",
            help="メッセージの説得力"
        )
    
    # グラフ表示
    fig = go.Figure()
    
    categories = ['モチベーション', '学習意欲']
    before_values = [
        participant_data.get('motivation_level', 5),
        participant_data.get('interest_score', 5)
    ]
    after_values = [
        results.get('post_motivation', 5),
        results.get('post_interest', 5)
    ]
    
    fig.add_trace(go.Bar(
        name='実験前',
        x=categories,
        y=before_values,
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='実験後',
        x=categories,
        y=after_values,
        marker_color='darkblue'
    ))
    
    fig.update_layout(
        title='実験前後の変化',
        yaxis_title='スコア (1-10)',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 実験グループの情報
    group_info = {
        "loss_aversion": "損失回避：現状維持によるリスクに焦点を当てるアプローチ",
        "social_proof": "社会的証明：他者の行動や成果を参考にするアプローチ",
        "implementation_intention": "実装意図：具体的な行動計画の策定に焦点を当てるアプローチ"
    }
    
    st.markdown(f"""
    ## 🧪 実験条件について
    
    **あなたの実験グループ**: {experiment_group}
    
    **アプローチの説明**: {group_info.get(experiment_group, '不明')}
    
    ## 📈 研究への貢献
    
    あなたのデータは、効果的な英語学習動機付け手法の開発に貴重な情報を提供します。
    この研究により、より多くの人が英語学習を始めるきっかけを作ることができます。
    """)
    
    # フィードバック収集
    st.subheader("💬 研究へのフィードバック")
    feedback = st.text_area(
        "この実験について感想や改善点があれば教えてください（任意）",
        placeholder="実験の感想、改善提案、気づいた点など..."
    )
    
    if st.button("フィードバックを送信"):
        st.success("フィードバックをありがとうございました！")

def main():
    st.set_page_config(
        page_title="英語学習行動変容研究",
        page_icon="🔬",
        layout="wide"
    )
    
    # セッション状態の初期化
    if 'page' not in st.session_state:
        st.session_state.page = "consent"
    
    # ページルーティング
    if st.session_state.page == "consent":
        show_consent_page()
    elif st.session_state.page == "baseline":
        show_baseline_assessment()
    elif st.session_state.page == "intervention":
        show_intervention_page()
    elif st.session_state.page == "results":
        show_results_page()
    
    # 研究者用サイドバー
    with st.sidebar:
        st.markdown("### 🔬 研究管理")
        st.markdown(f"**現在のページ**: {st.session_state.page}")
        if 'experiment_group' in st.session_state:
            st.markdown(f"**実験グループ**: {st.session_state.experiment_group}")
        
        if st.button("🔄 実験をリセット"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main() 
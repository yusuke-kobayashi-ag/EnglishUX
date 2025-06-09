import streamlit as st
import json
import sqlite3
from datetime import datetime
from litellm import completion
import pandas as pd
import plotly.express as px
import random

class MotivationApp:
    def __init__(self):
        self.model = "ollama/hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF"
        self.api_base = "http://localhost:11434"
        self.init_database()
    
    def init_database(self):
        """データベースの初期化"""
        conn = sqlite3.connect('motivation.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                occupation TEXT,
                current_situation TEXT,
                pain_points TEXT,
                dreams TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                missed_opportunities INTEGER,
                potential_income INTEGER,
                time_wasted INTEGER,
                stress_level INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    def calculate_missed_opportunities(self, user_data):
        """失った機会を計算（AI生成）"""
        prompt = f"""
        以下のユーザー情報に基づいて、英語ができないことで失っている具体的な機会や損失を計算してください。
        数字は現実的で、説得力のあるものにしてください。
        
        ユーザー情報:
        - 年齢: {user_data.get('age', '不明')}
        - 職業: {user_data.get('occupation', '不明')}
        - 現在の状況: {user_data.get('current_situation', '不明')}
        
        以下の形式で回答してください：
        年収差額: XXX万円
        昇進の遅れ: X年
        転職機会の損失: XX回
        海外旅行での不便: XXX回
        情報収集の機会損失: XXX時間/年
        """
        
        return self.get_llm_response([{"role": "user", "content": prompt}])
    
    def generate_personalized_dream(self, user_data):
        """個人に合わせた夢・目標を生成"""
        prompt = f"""
        以下のユーザー情報に基づいて、英語ができるようになったときの具体的で魅力的な未来を描いてください。
        リアルで達成可能な内容にしてください。
        
        ユーザー情報:
        - 年齢: {user_data.get('age', '不明')}
        - 職業: {user_data.get('occupation', '不明')}
        - 現在の状況: {user_data.get('current_situation', '不明')}
        - 悩み: {user_data.get('pain_points', '不明')}
        
        具体的なシーンを3つ描いてください。
        """
        
        return self.get_llm_response([{"role": "user", "content": prompt}])
    
    def get_success_story(self, occupation):
        """職業に応じた成功事例を生成"""
        prompt = f"""
        {occupation}の人が英語を身につけることで成功した具体的な事例を1つ教えてください。
        実在する人物でなくても構いませんが、リアルな内容にしてください。
        年収や昇進、新しい機会について具体的な数字を含めてください。
        """
        
        return self.get_llm_response([{"role": "user", "content": prompt}])

def show_hook_page():
    """フック：最初の3秒で興味を引く"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #ff6b6b, #4ecdc4); padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
        <h1 style="color: white; font-size: 2.5em; margin-bottom: 10px;">⚠️ あなたは年間○○万円損しています ⚠️</h1>
        <h3 style="color: white; margin-bottom: 20px;">英語ができないことで失っている機会を今すぐ診断</h3>
        <p style="color: white; font-size: 1.2em;">たった3分の診断で、あなたの隠れた損失を見える化します</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #ff4757; color: white; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>💸 年収の差</h3>
            <h2>平均67万円</h2>
            <p>英語ができる人との年収差</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #ffa502; color: white; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>⏰ 時間の損失</h3>
            <h2>320時間/年</h2>
            <p>情報収集や調べ物の非効率</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #ff3838; color: white; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>🚪 機会損失</h3>
            <h2>15回/年</h2>
            <p>転職・昇進・海外案件の機会</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 緊急性を演出
    st.markdown("""
    <div style="background: #2c2c2c; color: #ff6b6b; padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0;">
        <h4>⏳ このまま1年過ごすと...</h4>
        <p style="font-size: 1.1em;">同僚との差はさらに広がり、取り戻すのに2倍の時間がかかります</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 超簡単さをアピール
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 無料で3分診断を開始", type="primary", use_container_width=True):
            st.session_state.page = "assessment"
            st.rerun()
    
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #666;">
        ✓ 完全無料　✓ 3分で完了　✓ メール登録不要　✓ 今すぐ結果がわかる
    </div>
    """, unsafe_allow_html=True)

def show_assessment_page():
    """診断ページ：ユーザーの現状を把握"""
    st.markdown("""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="text-align: center; color: #2c3e50;">📊 あなたの損失診断</h2>
        <p style="text-align: center; color: #7f8c8d;">正直に答えるほど、より正確な診断結果が得られます</p>
    </div>
    """, unsafe_allow_html=True)
    
    # プログレスバー
    progress = st.progress(0)
    
    with st.form("assessment_form"):
        st.subheader("👤 基本情報")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.selectbox("年齢", ["20代前半", "20代後半", "30代前半", "30代後半", "40代", "50代以上"])
        with col2:
            occupation = st.selectbox("職業", [
                "会社員（事務系）", "会社員（技術系）", "会社員（営業系）", "会社員（管理職）",
                "公務員", "自営業", "フリーランス", "学生", "主婦・主夫", "その他"
            ])
        
        progress.progress(25)
        
        st.subheader("💼 現在の状況")
        current_situation = st.radio(
            "英語に関する現在の状況は？",
            [
                "全く英語は使わない・必要ない",
                "たまに英語の情報を見るが読めない", 
                "仕事で英語が必要だが避けている",
                "英語ができたらいいなと思うが行動していない"
            ]
        )
        
        progress.progress(50)
        
        st.subheader("😰 困っていること")
        pain_points = st.multiselect(
            "当てはまるものを選んでください（複数選択可）",
            [
                "最新の情報が英語ばかりで困る",
                "海外旅行で不安を感じる", 
                "転職で英語ができる人に負ける",
                "昇進の条件に英語がある",
                "外国人とコミュニケーションが取れない",
                "英語の動画や記事が理解できない",
                "グローバルな仕事に参加できない"
            ]
        )
        
        progress.progress(75)
        
        st.subheader("✨ 理想の未来")
        dreams = st.text_area(
            "英語ができるようになったら、どんなことをしたいですか？",
            placeholder="例：海外旅行を自由に楽しみたい、転職の選択肢を広げたい、最新の技術情報をいち早く得たい..."
        )
        
        progress.progress(100)
        
        submitted = st.form_submit_button("🔍 診断結果を見る", type="primary", use_container_width=True)
        
        if submitted:
            # ユーザーデータを保存
            user_data = {
                'age': age,
                'occupation': occupation,
                'current_situation': current_situation,
                'pain_points': ', '.join(pain_points),
                'dreams': dreams
            }
            st.session_state.user_data = user_data
            st.session_state.page = "results"
            st.rerun()

def show_results_page():
    """結果ページ：損失を可視化し、解決策を提示"""
    user_data = st.session_state.get('user_data', {})
    app = MotivationApp()
    
    # ショッキングな結果を表示
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
        <h1>😱 診断結果：あなたの隠れた損失</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # AIで個人化された損失計算
    with st.spinner("あなた専用の診断結果を計算中..."):
        missed_opportunities = app.calculate_missed_opportunities(user_data)
    
    st.markdown(f"""
    <div style="background: #e74c3c; color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h3>📊 あなたの損失分析</h3>
        <pre style="color: white; font-size: 1.1em;">{missed_opportunities}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    # 成功事例で社会的証明
    st.subheader("✨ あなたと同じ職業の成功事例")
    with st.spinner("成功事例を検索中..."):
        success_story = app.get_success_story(user_data.get('occupation', '会社員'))
    
    st.markdown(f"""
    <div style="background: #27ae60; color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4>🎉 実際の成功例</h4>
        <p style="font-size: 1.1em; line-height: 1.6;">{success_story}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 個人化された未来像
    st.subheader("🌟 あなたの理想の未来")
    with st.spinner("あなたの未来を描画中..."):
        personalized_dream = app.generate_personalized_dream(user_data)
    
    st.markdown(f"""
    <div style="background: #3498db; color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4>✨ 英語ができるあなたの未来</h4>
        <p style="font-size: 1.1em; line-height: 1.6;">{personalized_dream}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 緊急性と行動喚起
    st.markdown("""
    <div style="background: #f39c12; color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 30px 0;">
        <h3>⚡ 今すぐ行動しないと...</h3>
        <p style="font-size: 1.2em;">1日遅れるごとに、同僚との差は広がります</p>
        <p style="font-size: 1.2em;">3ヶ月後には取り返すのに倍の時間がかかります</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 超簡単な最初のステップ
    st.markdown("""
    <div style="background: #2ecc71; color: white; padding: 25px; border-radius: 15px; text-align: center; margin: 30px 0;">
        <h2>🚀 今すぐできる最初の一歩</h2>
        <h3>たった5分から始められます</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 今日から5分だけ始める", type="primary", use_container_width=True):
            st.session_state.page = "action"
            st.rerun()
    
    with col2:
        if st.button("💬 まずは相談してみる", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    
    # 社会的証明をさらに追加
    st.markdown("""
    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4 style="text-align: center;">👥 今日始めた人たち</h4>
        <p>• 田中さん（30代・会社員）「5分から始めて、3ヶ月で英語のニュースが読めるように！」</p>
        <p>• 佐藤さん（20代・エンジニア）「毎日5分だけで、海外の技術情報が理解できるようになった」</p>
        <p>• 山田さん（40代・管理職）「転職活動で英語スキルをアピールできて年収100万アップ！」</p>
    </div>
    """, unsafe_allow_html=True)

def show_action_page():
    """行動ページ：具体的な最初のステップ"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
        <h1>🎯 あなた専用の学習スタートプラン</h1>
        <p style="font-size: 1.2em;">超簡単！今日から5分だけ始めましょう</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ステップバイステップ
    steps = [
        {
            "title": "今すぐ（5分）",
            "content": "スマホに英語学習アプリをダウンロード",
            "detail": "Duolingo、英語物語、iKnowなど無料アプリから1つ選んで今すぐダウンロード",
            "color": "#e74c3c"
        },
        {
            "title": "明日の朝（5分）",
            "content": "コーヒーを飲みながら英単語5個",
            "detail": "通勤前の5分間、アプリで基本的な英単語を5個だけ覚える",
            "color": "#f39c12"
        },
        {
            "title": "1週間後（10分）",
            "content": "英語のYouTube動画を1つ見る",
            "detail": "興味のある分野の英語動画を字幕付きで見る（内容は理解できなくてOK）",
            "color": "#27ae60"
        },
        {
            "title": "1ヶ月後",
            "content": "成果を実感できるように",
            "detail": "簡単な英語の記事が読めるように、基本的な英語が聞き取れるようになります",
            "color": "#3498db"
        }
    ]
    
    for i, step in enumerate(steps):
        st.markdown(f"""
        <div style="background: {step['color']}; color: white; padding: 20px; border-radius: 10px; margin: 15px 0;">
            <h3>{step['title']}</h3>
            <h4>{step['content']}</h4>
            <p style="font-size: 1.1em; margin-top: 10px;">{step['detail']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 今すぐ行動を促す
    st.markdown("""
    <div style="background: #2c3e50; color: white; padding: 25px; border-radius: 15px; text-align: center; margin: 30px 0;">
        <h2>⚡ 今すぐ行動しましょう！</h2>
        <p style="font-size: 1.2em;">この画面を閉じる前に、スマホにアプリをダウンロードしてください</p>
        <p style="font-size: 1.1em;">3分後には英語学習がスタートできます</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 継続サポート
    st.subheader("🤝 継続サポート")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 毎日のリマインダー設定", use_container_width=True):
            st.success("✅ リマインダーを設定しました！毎日同じ時間にお知らせします")
    
    with col2:
        if st.button("💬 質問・相談チャット", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

def main():
    st.set_page_config(
        page_title="英語学習に向けて",
        page_icon="⚠️",
        layout="wide"
    )
    
    # セッション状態の初期化
    if 'page' not in st.session_state:
        st.session_state.page = "assessment"
    
    # ページルーティング
    if st.session_state.page == "hook":
        show_hook_page()
    elif st.session_state.page == "assessment":
        show_assessment_page()
    elif st.session_state.page == "results":
        show_results_page()
    elif st.session_state.page == "action":
        show_action_page()
    
    # サイドバーでページ切り替え（デバッグ用）
    with st.sidebar:
        st.markdown("### 🔧 ページ切り替え")
        if st.button("🏠 最初に戻る"):
            st.session_state.page = "hook"
            st.rerun()

if __name__ == "__main__":
    main() 
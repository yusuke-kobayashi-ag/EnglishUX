import streamlit as st
import json
import sqlite3
from datetime import datetime
from litellm import completion
import pandas as pd
import plotly.express as px

class EnglishLearningApp:
    def __init__(self):
        self.model = "ollama/hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF"
        self.api_base = "http://localhost:11434"
        self.init_database()
    
    def init_database(self):
        """データベースの初期化"""
        conn = sqlite3.connect('english_learning.db')
        cursor = conn.cursor()
        
        # ユーザー情報テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                occupation TEXT,
                english_level TEXT,
                goal TEXT,
                interests TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # チャット履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 学習進捗テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity TEXT,
                progress_score INTEGER,
                date DATE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_user_info(self, user_info):
        """ユーザー情報をデータベースに保存"""
        conn = sqlite3.connect('english_learning.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (name, age, occupation, english_level, goal, interests)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_info['name'],
            user_info['age'],
            user_info['occupation'],
            user_info['english_level'],
            user_info['goal'],
            json.dumps(user_info['interests'])
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def save_chat_message(self, user_id, role, content):
        """チャットメッセージをデータベースに保存"""
        conn = sqlite3.connect('english_learning.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_history (user_id, role, content)
            VALUES (?, ?, ?)
        ''', (user_id, role, content))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, user_id):
        """チャット履歴を取得"""
        conn = sqlite3.connect('english_learning.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp ASC
        ''', (user_id,))
        
        history = cursor.fetchall()
        conn.close()
        return history
    
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
    
    def generate_learning_plan(self, user_info):
        """学習計画を生成"""
        prompt = f"""
        以下のユーザー情報に基づいて、詳細な英語学習計画を作成してください。

        ユーザー情報:
        - 名前: {user_info['name']}
        - 年齢: {user_info['age']}
        - 職業: {user_info['occupation']}
        - 英語レベル: {user_info['english_level']}
        - 目標: {user_info['goal']}
        - 興味のある分野: {', '.join(user_info['interests'])}

        以下の内容を含めてください：
        1. 短期目標（1ヶ月以内）
        2. 中期目標（3ヶ月以内）
        3. 長期目標（6ヶ月以内）
        4. 毎日の学習ルーティン
        5. おすすめの学習リソース
        6. モチベーション維持のコツ
        """
        
        return self.get_llm_response([{"role": "user", "content": prompt}])

def main():
    st.set_page_config(
        page_title="English Learning Assistant",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("英語学習アシスタント")
    st.markdown("英語学習を始めよう！")
    
    app = EnglishLearningApp()
    
    # サイドバーでユーザー選択
    st.sidebar.title("ユーザー管理")
    
    # セッション状態の初期化
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    # 新規ユーザー登録 or 既存ユーザー選択
    user_option = st.sidebar.radio("選択してください：", ["新規登録", "既存ユーザー"])
    
    if user_option == "新規登録":
        st.sidebar.subheader("📝 基本情報を入力")
        
        with st.sidebar.form("user_info_form"):
            name = st.text_input("お名前", placeholder="山田太郎")
            age = st.number_input("年齢", min_value=10, max_value=100, value=25)
            occupation = st.text_input("職業", placeholder="エンジニア")
            english_level = st.selectbox("現在の英語レベル", 
                                       ["初心者", "初級", "中級", "上級"])
            goal = st.text_input("目標", placeholder="TOEIC 800点取得")
            interests = st.multiselect("興味のある分野", 
                                     ["ビジネス", "テクノロジー", "旅行", "映画", 
                                      "音楽", "スポーツ", "料理", "文学"])
            
            submitted = st.form_submit_button("登録する")
            
            if submitted and name:
                user_info = {
                    'name': name,
                    'age': age,
                    'occupation': occupation,
                    'english_level': english_level,
                    'goal': goal,
                    'interests': interests
                }
                
                user_id = app.save_user_info(user_info)
                st.session_state.user_id = user_id
                st.session_state.user_info = user_info
                st.sidebar.success(f"ユーザー登録完了！ ID: {user_id}")
    
    # メインコンテンツ
    if st.session_state.user_id:
        tab1, tab2, tab3, tab4 = st.tabs(["💬 チャット", "📋 学習計画", "📊 進捗管理", "🎯 目標設定"])
        
        with tab1:
            st.subheader("💬 AIチャット")
            
            # チャット履歴の表示
            chat_history = app.get_chat_history(st.session_state.user_id)
            
            # チャット表示エリア
            chat_container = st.container()
            with chat_container:
                for role, content, timestamp in chat_history:
                    if role == "user":
                        st.markdown(f"**あなた:** {content}")
                    else:
                        st.markdown(f"{content}")
            
            # 新しいメッセージ入力
            user_input = st.text_input("メッセージを入力してください：", key="chat_input")
            
            if st.button("送信") and user_input:
                # ユーザーメッセージを保存
                app.save_chat_message(st.session_state.user_id, "user", user_input)
                
                # LLMへのメッセージを準備（履歴込み）
                messages = []
                for role, content, _ in chat_history:
                    messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": user_input})
                
                # AI応答を取得
                ai_response = app.get_llm_response(messages)
                
                # AI応答を保存
                app.save_chat_message(st.session_state.user_id, "assistant", ai_response)
                
                # ページをリロード
                st.rerun()
        
        with tab2:
            st.subheader("📋 あなた専用の学習計画")
            
            if st.button("学習計画を生成"):
                with st.spinner("学習計画を作成中..."):
                    learning_plan = app.generate_learning_plan(st.session_state.user_info)
                    st.markdown(learning_plan)
        
        with tab3:
            st.subheader("📊 学習進捗")
            
            # 仮の進捗データ（実際の実装では実際のデータを使用）
            progress_data = {
                "日付": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
                "学習時間（分）": [30, 45, 25, 60, 40],
                "達成度（%）": [70, 85, 60, 90, 75]
            }
            
            df = pd.DataFrame(progress_data)
            
            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.line(df, x="日付", y="学習時間（分）", title="日別学習時間")
                st.plotly_chart(fig1)
            
            with col2:
                fig2 = px.bar(df, x="日付", y="達成度（%）", title="日別達成度")
                st.plotly_chart(fig2)
        
        with tab4:
            st.subheader("🎯 目標設定と管理")
            
            st.markdown("### 現在の目標")
            if 'user_info' in st.session_state:
                st.write(f"**メイン目標:** {st.session_state.user_info['goal']}")
            
            st.markdown("### 新しい目標を追加")
            new_goal = st.text_input("新しい目標を入力してください")
            if st.button("目標を追加"):
                st.success(f"目標「{new_goal}」が追加されました！")

if __name__ == "__main__":
    main() 
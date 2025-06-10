import streamlit as st
import json
from datetime import datetime
from litellm import completion
import litellm
import random
import sqlite3

class MotivationFocusApp:
    def __init__(self):
        # デフォルトのAPIキー設定
        litellm.api_key = "ollama"
        self.model = "ollama/hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF"
        self.api_base = "http://localhost:11434"
        self.init_database()
    
    def init_database(self):
        """データベースの初期化"""
        conn = sqlite3.connect('motivation_analysis.db')
        cursor = conn.cursor()
        
        # 既存のテーブルを削除
        cursor.execute('DROP TABLE IF EXISTS user_analyses')
        
        # 新しいスキーマでテーブルを作成
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            age_group TEXT,
            occupation TEXT,
            english_frequency TEXT,
            past_experience TEXT,
            personality_traits TEXT,
            time_availability TEXT,
            stress_factors TEXT,
            success_preference TEXT,
            interest_level INTEGER,
            concerns TEXT,
            dream TEXT,
            motivation_message TEXT,
            action_plan TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_analysis_to_database(self, user_data, motivation_message=None, action_plan=None):
        """分析結果をデータベースに保存"""
        conn = sqlite3.connect('motivation_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO user_analyses (
            timestamp, age_group, occupation, english_frequency, past_experience,
            personality_traits, time_availability, stress_factors, success_preference,
            interest_level, concerns, dream, motivation_message, action_plan
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            user_data.get('age_group', ''),
            user_data.get('occupation', ''),
            user_data.get('english_frequency', ''),
            user_data.get('past_experience', ''),
            user_data.get('personality_traits', ''),
            user_data.get('time_availability', ''),
            user_data.get('stress_factors', ''),
            user_data.get('success_preference', ''),
            user_data.get('interest_level', 0),
            user_data.get('concerns', ''),
            user_data.get('dream', ''),
            motivation_message or '',
            action_plan or ''
        ))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return analysis_id
    
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
            st.error(f"エラーが発生しました: {str(e)}")
            return None
    
    def generate_personalized_motivation(self, user_data, approach_type):
        print(user_data)
        """個人化されたモチベーション向上メッセージ生成"""
        prompt = f"""
        回答はすべて日本語で行ってください。
        以下のユーザーにゴールから逆算する形で、英語学習に前向きになれるようなメッセージングを心理学の視点に基づいてしてください。
        提供された情報を安直に使わず、ユーザーがどんな思考を持つタイプか、人となりを考えてメッセージングをしてください。
        基本的にユーザーは英語学習に興味がないものだと思ってください。「なぜ」英語学習が必要なのか。「どうして」英語学習を始めるのか。そこを考えてメッセージングをしてください。
        一番重要なことは、この人がメッセージングに触発されて、「英語学習を始めたい」という思いを持ってくれることです。
        学術的で冷静なトーンを保ち、過度な煽りは避けてください。

        また、このメッセージはユーザーに直接表示されるものなので、メタ的な文章は避けてください。
        直接メッセージをください。
        メッセージはできるだけ長くしてください。
        
        ユーザー情報:
        - 年齢層: {user_data.get('age_group')}
        - 職業: {user_data.get('occupation')}
        - 英語使用頻度: {user_data.get('english_frequency')}
        - 過去の学習経験: {user_data.get('past_experience')}
        - 性格傾向: {user_data.get('personality_traits')}
        - 時間的余裕: {user_data.get('time_availability')}
        - ストレス要因: {user_data.get('stress_factors')}
        - 現在の関心度: {user_data.get('interest_level')}/10
        - 悩み: {user_data.get('concerns')}
        - 将来の夢: {user_data.get('dream')}
        """
        
        return self.get_llm_response([{"role": "user", "content": prompt}])
    
    def generate_next_step_guidance(self, user_data):
        """次のステップガイダンス生成"""
        prompt = f"""
        回答はすべて日本語で行ってください。
        以下のユーザーが英語学習を今日から始めるための、超具体的で実行しやすい「最初の一歩」を提案してください。
        また、このメッセージはユーザーに直接表示されるものなので、メタ的な文章は避けてください。
        ユーザー情報:
        - 年齢層: {user_data.get('age_group')}
        - 職業: {user_data.get('occupation')}
        - 英語使用頻度: {user_data.get('english_frequency')}
        - 過去の学習経験: {user_data.get('past_experience')}
        - 性格傾向: {user_data.get('personality_traits')}
        - 時間的余裕: {user_data.get('time_availability')}
        - ストレス要因: {user_data.get('stress_factors')}
        - 現在の関心度: {user_data.get('interest_level')}/10
        - 悩み: {user_data.get('concerns')}
        - 将来の夢: {user_data.get('dream')}
        
        以下の条件を満たしてください：
        1. 今日中に実行できる
        2. この人の時間的余裕に合わせて5-15分以内で完了する
        3. この人の性格や過去の経験を考慮する
        4. 成功体験を感じられる
        5. 継続につながりやすい
        
        具体的なアクションプランを3つ提示してください。
        """
        
        return self.get_llm_response([{"role": "user", "content": prompt}])


def show_assessment_page():
    """詳細分析ページ"""
    st.markdown("""
    # あなたの情報入力
    
    最適なモチベーション手法を判断するため、詳しい情報を入力してください。
    """)


    st.subheader("👤 基本情報")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age_group_select = st.selectbox("年齢層", ["18-24", "25-34", "35-44", "45-54", "55+", "その他"])
        
        if age_group_select == "その他":
            age_group_detail = st.text_area(
                "詳細な年齢を教えてください",
                placeholder="例：17歳、65歳、年齢を言いたくない",
                height=70
            )
            age_group = age_group_detail if age_group_detail else "詳細未入力"
        else:
            age_group = age_group_select
        
    with col2:
        occupation_select = st.selectbox("職業", [
            "学生", "会社員（技術系）", "会社員（事務系）", "会社員（営業系）", 
            "管理職", "専門職", "自営業", "フリーランス", "主婦・主夫", "その他"
        ])
        
        if occupation_select == "その他":
            occupation_detail = st.text_area(
                "詳細な職業を教えてください",
                placeholder="例：研究者、公務員、パートタイマー、無職",
                height=70
            )
            occupation = occupation_detail if occupation_detail else "詳細未入力"
        else:
            occupation = occupation_select
    
    with col3:
        dream_select = st.text_area(
            "将来の夢",
            placeholder="具体的なものでなくても構いません。例：お金持ちになる、エンジニアとして成長する、マネージャーになる。",
            height=70
        )
        dream = dream_select if dream_select else "詳細未入力"
    st.session_state.temp_dream = dream
        
    st.subheader("📚 英語との関わり")
    
    col1, col2 = st.columns(2)
    with col1:
        english_frequency_select = st.selectbox(
            "現在の英語使用頻度",
            ["全く使わない", "月に数回", "週に1-2回", "週に3-5回", "ほぼ毎日", "その他"]
        )
        
        # 「その他」が選択された場合のみテキストエリアを表示
        if english_frequency_select == "その他":
            english_frequency_detail = st.text_area(
                "詳細な使用状況を教えてください",
                placeholder="例：仕事では全く使わないが、YouTubeで英語の動画を週1-2回見る程度",
                height=80
            )
            english_frequency = english_frequency_detail if english_frequency_detail else "詳細未入力"
        else:
            english_frequency = english_frequency_select
    
    with col2:
        past_experience_select = st.selectbox(
            "過去の英語学習経験",
            ["ほとんどない", "学校での授業のみ", "独学で少し", "スクールに通った", "留学経験あり", "その他"]
        )
        
        if past_experience_select == "その他":
            past_experience_detail = st.text_area(
                "詳細な学習経験を教えてください",
                placeholder="例：オンライン学習のみ、海外で仕事経験、TOEIC対策のみ",
                height=80
            )
            past_experience = past_experience_detail if past_experience_detail else "詳細未入力"
        else:
            past_experience = past_experience_select

    # フォーム外の値をセッション状態に保存
    st.session_state.temp_age_group = age_group
    st.session_state.temp_occupation = occupation
    st.session_state.temp_dream = dream
    st.session_state.temp_english_frequency = english_frequency
    st.session_state.temp_past_experience = past_experience
    


        
    st.subheader("💡 性格傾向")
        
    personality_traits = st.multiselect(
        "あなたの性格に当てはまるもの（複数選択可）",
        [
            "計画を立てて着実に進める", "周りの人の意見を参考にする", "完璧主義的",
            "飽きっぽい", "競争心が強い", "慎重派", "チャレンジ精神旺盛",
            "人からの評価を気にする", "マイペース", "効率重視", "その他"
        ]
    )
    
    # 「その他」が選択された場合のみテキストエリアを表示
    if "その他" in personality_traits:
        personality_other_detail = st.text_area(
            "その他の性格傾向を教えてください",
            placeholder="例：楽観的、心配性、協調性がある、独立心が強い、創造的",
            height=80
        )
        # 「その他」を除いた選択肢と詳細入力を結合
        personality_final = [trait for trait in personality_traits if trait != "その他"]
        if personality_other_detail:
            personality_final.append(f"その他: {personality_other_detail}")
        else:
            personality_final.append("その他: 詳細未入力")
    else:
        personality_final = personality_traits
    
    # セッション状態に保存
    st.session_state.temp_personality_traits = personality_final
        
    st.subheader("⏰ 時間とストレス")
        
    col1, col2 = st.columns(2)
    with col1:
        time_availability_select = st.selectbox(
            "学習に使える時間",
            ["1日5分未満", "1日5-15分", "1日15-30分", "1日30分-1時間", "1日1時間以上", "その他"]
        )
        
        if time_availability_select == "その他":
            time_availability_detail = st.text_area(
                "詳細な時間を教えてください",
                placeholder="例：週末のみ3時間、平日なし土日2時間、不定期",
                height=80
            )
            time_availability = time_availability_detail if time_availability_detail else "詳細未入力"
        else:
            time_availability = time_availability_select
        
        # セッション状態に保存
        st.session_state.temp_time_availability = time_availability
    
    with col2:
        stress_factors = st.multiselect(
            "現在のストレス要因（複数選択可）",
            [
                "仕事が忙しい", "家事・育児が大変", "勉強時間が取れない",
                "上達が感じられない", "お金がかかる", "継続できない自分",
                "他の人と比較してしまう", "特になし", "その他"
            ]
        )

        # 「その他」が選択された場合のみテキストエリアを表示
        if "その他" in stress_factors:
            stress_factors_detail = st.text_area(
                "詳細なストレス要因を教えてください",
                placeholder="例：人間関係のストレス、健康面の不安、経済的なプレッシャー",
                height=80
            )
            # 「その他」を除いた選択肢と詳細入力を結合
            stress_factors_final = [factor for factor in stress_factors if factor != "その他"]
            if stress_factors_detail:
                stress_factors_final.append(f"その他: {stress_factors_detail}")
            else:
                stress_factors_final.append("その他: 詳細未入力")
        else:
            stress_factors_final = stress_factors
        
        # セッション状態に保存
        st.session_state.temp_stress_factors = stress_factors_final
    
    st.subheader("🎯 学習スタイル")
    
    col1, col2 = st.columns(2)
    with col1:
        success_preference_select = st.selectbox(
            "成功体験として嬉しいこと",
            [
                "小さくても毎日続けられた", "テストで良い点が取れた", 
                "実際に英語が通じた", "周りから褒められた",
                "目標を達成できた", "新しいことを覚えられた", "その他"
            ]
        )
        
        if success_preference_select == "その他":
            success_preference_detail = st.text_area(
                "詳細な成功体験を教えてください",
                placeholder="例：難しい内容が理解できた、外国人と友達になれた、字幕なしで映画を見れた",
                height=80
            )
            success_preference = success_preference_detail if success_preference_detail else "詳細未入力"
        else:
            success_preference = success_preference_select
        
        # セッション状態に保存
        st.session_state.temp_success_preference = success_preference
    
    with col2:
        interest_level = st.slider(
            "現在の英語学習への関心度",
            min_value=1, max_value=10, value=5,
            help="1: 全く興味がない ～ 10: 非常に興味がある"
        )
        
        # セッション状態に保存
        st.session_state.temp_interest_level = interest_level
    
    concerns = st.multiselect(
        "英語学習に関する具体的な悩み（複数選択可）",
        [
            "時間がない", "何から始めていいかわからない", "継続できるか不安",
            "効果が出るか疑問", "費用がかかりそう", "自分には無理だと思う",
            "必要性を感じない", "過去に挫折した経験がある", "文法が苦手",
            "発音に自信がない", "単語が覚えられない", "リスニングができない"
        ]
    )
    
    # セッション状態に保存
    st.session_state.temp_concerns = concerns
    
    if st.button("🤖 AIに分析してもらう", type="primary"):
        user_data = {
            'age_group': st.session_state.get('temp_age_group', '25-34'),
            'occupation': st.session_state.get('temp_occupation', '会社員（技術系）'),
            'english_frequency': st.session_state.get('temp_english_frequency', '全く使わない'),
            'past_experience': st.session_state.get('temp_past_experience', 'ほとんどない'),
            'personality_traits': ', '.join(st.session_state.get('temp_personality_traits', [])),
            'time_availability': st.session_state.get('temp_time_availability', '1日15-30分'),
            'stress_factors': ', '.join(st.session_state.get('temp_stress_factors', [])),
            'success_preference': st.session_state.get('temp_success_preference', '小さくても毎日続けられた'),
            'interest_level': st.session_state.get('temp_interest_level', 5),
            'concerns': ', '.join(st.session_state.get('temp_concerns', [])),
            'dream': st.session_state.get('temp_dream', '詳細未入力')
        }
        
        # AIでバックグラウンド分析を実行
        app = MotivationFocusApp()
        
        # データベースに分析結果を保存
        analysis_id = app.save_analysis_to_database(user_data)
        user_data['analysis_id'] = analysis_id
        
        st.session_state.user_data = user_data
        st.session_state.page = "motivation"
        st.rerun()


def show_motivation_page():
    """モチベーション向上ページ"""
    user_data = st.session_state.get('user_data', {})
    app = MotivationFocusApp()
    
    st.markdown(f"""
    # 英語学習を始めてみませんか？
    """)
    
    # パーソナライズされたモチベーションメッセージ
    with st.spinner("最適化中..."):
        motivation_message = app.generate_personalized_motivation(user_data, "loss_aversion")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 25px; border-radius: 15px; margin: 20px 0;">
        <h3 style="margin-bottom: 15px;">💡 あなたへのメッセージ</h3>
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; line-height: 1.8;">
            {motivation_message.replace(chr(10), '<br>')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 次のステップ
    st.markdown("---")
    st.subheader("あなた専用の実行プラン")
    
    with st.spinner("あなたの状況に最適化されたアクションプランを作成中..."):
        next_steps = app.generate_next_step_guidance(user_data)
    
    # データベースにモチベーションメッセージとアクションプランを更新保存
    if 'analysis_id' in user_data:
        app.save_analysis_to_database(user_data, motivation_message, next_steps)
    
    st.markdown(f"""
    <div style="background: #2ecc71; color: white; padding: 25px; border-radius: 15px; margin: 20px 0;">
        <h3 style="margin-bottom: 15px;">📋 今日から始められるアクション</h3>
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; line-height: 1.8;">
            {next_steps.replace(chr(10), '<br>')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # リスタート
    st.markdown("---")
    if st.button("🏠最初からやり直す", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    st.set_page_config(
        page_title="AI英語学習",
        page_icon="🤖",
        layout="wide"
    )
    
    # セッション状態の初期化
    if 'page' not in st.session_state:
        st.session_state.page = "assessment"

    if st.session_state.page == "assessment":
        show_assessment_page()
    elif st.session_state.page == "motivation":
        show_motivation_page()
    
    # サイドバー
    with st.sidebar:
        st.markdown("### 分析システム")
        if 'user_data' in st.session_state:
            user_data = st.session_state.user_data
            st.markdown("**📊 分析済み項目**")
            st.markdown(f"• 年齢層: {user_data.get('age_group', '未設定')}")
            st.markdown(f"• 職業: {user_data.get('occupation', '未設定')}")
            st.markdown(f"• 英語頻度: {user_data.get('english_frequency', '未設定')}")
            st.markdown(f"• 学習経験: {user_data.get('past_experience', '未設定')}")
            st.markdown(f"• 時間的余裕: {user_data.get('time_availability', '未設定')}")
            st.markdown(f"• 関心度: {user_data.get('interest_level', '未設定')}/10")
            st.markdown(f"• 将来の夢: {user_data.get('dream', '未設定')}")
            st.markdown(f"• 性格傾向: {user_data.get('personality_traits', '未設定')}")
            st.markdown(f"• ストレス要因: {user_data.get('stress_factors', '未設定')}")
            st.markdown(f"• 成功体験: {user_data.get('success_preference', '未設定')}")
            st.markdown(f"• 悩み: {user_data.get('concerns', '未設定')}")


if __name__ == "__main__":
    main() 
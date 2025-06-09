from litellm import completion
import json

class EnglishLearningUX:
    def __init__(self):
        self.model = "ollama/hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF"
        self.api_base = "http://localhost:11434"
        
    def get_personalized_message(self, user_info):
        prompt = f"""
        以下のユーザー情報に基づいて、英語学習を始めるための励ましのメッセージを生成してください。
        基本的に、英語学習に興味がないユーザーと想定し、「英語を始めたい！！」という風に思わせるようなメッセージを生成してください。
        出力はすべて日本語で行ってください。
        ユーザー情報:
        - 年齢: {user_info['age']}
        - 職業: {user_info['occupation']}
        - 英語レベル: {user_info['english_level']}
        - 目標: {user_info['goal']}
        - 興味のある分野: {user_info['interests']}
        
        以下の要素を含めてください：
        1. 「英語を始めたい！！」という風に思わせるような事実の羅列、英語を学んだことで成功した人、物事の引用
        2. ユーザーの状況に合わせた具体的な目標設定
        3. 最初の一歩としての具体的なアクション
        4. モチベーションを高める励ましの言葉
        5. ゴールを提示する

        また、英語学習に興味がないユーザーと想定し、「英語を始めたい！！」という風に思わせるようなメッセージが一番重要です。ここに力を入れてください。
        """
        
        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            api_base=self.api_base
        )
        return response.choices[0].message.content

    def generate_learning_path(self, user_info):
        prompt = f"""
        以下のユーザー情報に基づいて、英語学習のロードマップを生成してください。
        出力はすべて日本語で行ってください。
        ユーザー情報:
        - 年齢: {user_info['age']}
        - 職業: {user_info['occupation']}
        - 英語レベル: {user_info['english_level']}
        - 目標: {user_info['goal']}
        - 興味のある分野: {user_info['interests']}
        
        以下の要素を含めてください：
        1. 短期目標（1ヶ月）
        2. 中期目標（3ヶ月）
        3. 長期目標（6ヶ月）
        4. 各目標達成のための具体的なアクションプラン
        """
        
        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            api_base=self.api_base
        )
        return response.choices[0].message.content
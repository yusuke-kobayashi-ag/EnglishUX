# ユーザー情報の例
from struction import EnglishLearningUX


user_info = {
    "age": 25,
    "occupation": "エンジニア",
    "english_level": "初級",
    "goal": "エンジニアとして成功する",
    "interests": ["テクノロジー", "プログラミング"]
}

# インスタンス作成
ux = EnglishLearningUX()

# パーソナライズされたメッセージを取得
message = ux.get_personalized_message(user_info)
print("パーソナライズされたメッセージ:")
print(message)

# 学習ロードマップを生成
roadmap = ux.generate_learning_path(user_info)
print("\n学習ロードマップ:")
print(roadmap)
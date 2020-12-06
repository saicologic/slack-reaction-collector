
これは、Slackのスタンプを収集するプログラムです。

# 依存ライブラリ

```
pip install slackclient
pip install sqlalchemy
pip install mysql-connector-python-rf
pip install fire
pip install tabulate
```

# データベースとテーブル作成

```
mysql -uroot < ./schema.sql
```

# コマンド

## セットアップ

```
python ./main.py setup
```

## すべてのリアクションの取得

```
python ./main.py create_reactions 2020-01-01
```

## チャンネル一覧の取得

```
python ./main.py get_channels
```

## 指定したチャンネルのすべてのリアクションを取得

チャンネル一覧の取得に記載されてている`channel_id`を使う

```
python ./main.py create_reactions_by_channel 2020-01-01 CXXXXX
```

# ランキング
リアクションを取得した後に下記のランキングを取得

## ユーザーがスタンプ押したランキング

```
python ./main.py get_user_reaction_ranking --output=yes
```

## 使われたスタンプのランキング

```
python ./main.py get_reaction_ranking
```

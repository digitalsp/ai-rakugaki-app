# ベースイメージとして公式のNode.jsイメージを使用
FROM node:18-alpine

# 作業ディレクトリの作成
WORKDIR /app

# package.jsonとpackage-lock.json（またはyarn.lock）をコピー
COPY package.json package-lock.json* ./

# 依存パッケージのインストール
RUN npm install

# アプリケーションコードをコピー
COPY . /app/

# ビルドの実行
RUN npm run build

# ポートの設定
EXPOSE 3000

# サービスの起動
CMD ["npm", "start"]

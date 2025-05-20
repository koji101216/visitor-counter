# 来場者カウンター

[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Next.js](https://img.shields.io/badge/Next.js-000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

---

## 概要

リアルイベントや展示会などで使える、**来場者数をグループ単位でカウントできるWebアプリ**です。  
スペースキーまたは画面上のスペースキー風ボタンでカウントし、グラフで推移を可視化します。

---

## 特徴

- **スペースキー/クリックで直感的にカウント**
- **グループ判定ロジック**（連続入力でグループ化）
- **リアルタイムグラフ表示**
- **Docker Composeで簡単セットアップ**
- **シンプルな構成：Next.js + FastAPI + Chart.js**

---

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/koji101216/visitor-counter.git
cd visitor-counter
```

### 2. Dockerで起動

```bash
docker compose up --build
```

- フロントエンド: [http://localhost:3000](http://localhost:3000)
- バックエンド: [http://localhost:8000](http://localhost:8000)

### 3. 開発用ホットリロード

フロントエンドのみ開発したい場合：

```bash
cd frontend
npm install
npm run dev
```

バックエンドのみ開発したい場合：

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. バックエンドの更新時

バックエンドのコードを更新した場合、以下のコマンドでバックエンドコンテナのみを再ビルド・再起動できます：

```bash
docker compose up -d --build backend
```

---

## ディレクトリ構成
```
├── backend/ # FastAPI (Python)
├── frontend/ # Next.js (React)
├── data/ # CSVデータ保存用
├── compose.yaml
└── README.md
```

---

## ライセンス

MIT License
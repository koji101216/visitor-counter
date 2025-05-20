from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import csv
import os
import logging

# ログレベルの設定
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket接続を保持するセット
active_connections: set[WebSocket] = set()

# CSVファイルのパス
DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "visitors.csv")

# データディレクトリとCSVファイルの作成
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "group_size"])

def get_visitor_stats():
    try:
        with open(CSV_FILE, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        total_visitors = sum(int(row["group_size"]) for row in rows)
        recent_visitors = [
            {"timestamp": row["timestamp"], "group_size": int(row["group_size"])}
            for row in rows[-10:]  # 最新の10件
        ]
        
        return {
            "total_visitors": total_visitors,
            "recent_visitors": recent_visitors
        }
    except Exception:
        return {
            "total_visitors": 0,
            "recent_visitors": []
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocketエンドポイント"""
    print("新しいWebSocket接続を受け付けました")
    await websocket.accept()
    active_connections.add(websocket)
    print(f"アクティブな接続数: {len(active_connections)}")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                event_data = json.loads(data)
                group_size = event_data.get("group_size", 1)
                
                # 現在時刻を取得
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # CSVにデータを追加
                with open(CSV_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, group_size])
                
                # 全クライアントに統計情報を送信
                stats = get_visitor_stats()
                for connection in active_connections:
                    await connection.send_json(stats)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        print("WebSocket接続が切断されました")
        active_connections.remove(websocket)
        print(f"アクティブな接続数: {len(active_connections)}")
    except Exception as e:
        print(f"WebSocketエラー: {str(e)}")
        if websocket in active_connections:
            active_connections.remove(websocket)
            print(f"アクティブな接続数: {len(active_connections)}")

@app.get("/stats")
async def get_stats():
    """統計情報の取得API"""
    return get_visitor_stats() 
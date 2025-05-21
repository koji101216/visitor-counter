from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from scipy.stats import norm
import numpy as np
import json
import csv
import os
import logging
from zoneinfo import ZoneInfo


# ログレベルの設定
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# カーネル平滑化のバンド幅
bandwidth = 20 # ときどきCVして更新するかも

# 日時を数値で扱うとき用設定
BASE_TIME = datetime(2025, 5, 21, 20, 0, 0)  # 例: 2025年5月24日9時0分0秒を基準
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


def read_csv():
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        data_time = []
        data_num = []
        for row in rows:
            dt = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
            diff = dt - BASE_TIME
            minutes = diff.total_seconds() / 60  # 分数に変換
            if(minutes < 0): continue
            data_time.append(minutes)
            data_num.append(int(row['group_size']))
        data_time = np.array(data_time)
        data_num = np.array(data_num)
    print(f"CSVから読み込んだデータ数: {len(data_time)}")
    return data_time, data_num


def estimate_intensity_function(times, curr_time):

    def intensity_function(t):
        weights = norm.pdf((t - times) / bandwidth)
        correction = norm.cdf((curr_time - t) / bandwidth) - norm.cdf(- t / bandwidth)
        return np.sum(weights) / (bandwidth * correction)
    
    return intensity_function 

def calc_intensity(data_time):

    estimated_intensity = estimate_intensity_function(data_time, data_time[-1])

    dt_st = 0
    dt_ed = data_time[-1] 
    t_values = np.linspace(dt_st, dt_ed, 1000)
    intensity_values = [float(estimated_intensity(t)) for t in t_values]

    t_datetime = [(BASE_TIME + timedelta(minutes=t)).isoformat() for t in t_values]
    
    return t_datetime, intensity_values


def calc_total_num(data_num):
    total_num = np.sum(data_num)
    return int(total_num)    

def get_visitor_stats():
    
    try:
        data_time, data_num = read_csv()
        t_datetime, intensity_values = calc_intensity(data_time)
        total_num = calc_total_num(data_num)
        
        print(f"人数: {total_num}")
        print(f"強度の平均 {np.mean(intensity_values)}")

        return {
            "disp_times": t_datetime,
            "disp_intensity": intensity_values,
            "total_visitors": total_num
        }
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return {
            "disp_times": [],
            "disp_intensity": [],
            "total_visitors": 0
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
                timestamp = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")
                
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
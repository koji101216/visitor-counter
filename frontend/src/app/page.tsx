'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Visitor, VisitorStats } from '@/types/visitor';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const GROUP_THRESHOLD = 0.5;

export default function Home() {
  const [totalVisitors, setTotalVisitors] = useState(0);
  // const [recentVisitors, setRecentVisitors] = useState<Visitor[]>([]);
  const [disp_intensity, setDispIntensity] = useState<number[]>([]);
  const [disp_time, setDispTime] = useState<number[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const lastEventTimeRef = useRef<Date | null>(null);
  const currentGroupSizeRef = useRef<number>(0);
  const groupTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // グループデータを送信する関数
  const sendGroupData = useCallback((groupSize: number) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ group_size: groupSize }));
    }
  }, [ws]);

  // WebSocketの接続状態をチェックする関数
  const isWebSocketReady = useCallback((ws: WebSocket | null): boolean => {
    return ws !== null && ws.readyState === WebSocket.OPEN;
  }, []);

  // グループのタイマーを設定する関数
  const setGroupTimer = useCallback(() => {
    if (groupTimeoutRef.current) {
      clearTimeout(groupTimeoutRef.current);
    }
    groupTimeoutRef.current = setTimeout(() => {
      if (currentGroupSizeRef.current > 0) {
        sendGroupData(currentGroupSizeRef.current);
        lastEventTimeRef.current = null;
        currentGroupSizeRef.current = 0;
      }
    }, GROUP_THRESHOLD * 1000);
  }, [sendGroupData]);

  // 新しいグループを開始する関数
  const startNewGroup = useCallback((currentTime: Date) => {
    lastEventTimeRef.current = currentTime;
    currentGroupSizeRef.current = 1;
    setGroupTimer();
  }, [setGroupTimer]);

  const handleClick = useCallback(() => {
    if (!isWebSocketReady(ws)) return;

    const currentTime = new Date();
    const lastEventTime = lastEventTimeRef.current;

    if (lastEventTime === null) {
      // 初回クリック
      startNewGroup(currentTime);
      console.log('初回クリック');
      return;
    }

    const timeDiff = (currentTime.getTime() - lastEventTime.getTime()) / 1000;
    
    if (timeDiff <= GROUP_THRESHOLD) {
      // 既存のグループに追加
      currentGroupSizeRef.current += 1;
      lastEventTimeRef.current = currentTime;
      console.log('既存のグループに追加');
      console.log('currentGroupSizeRef.current', currentGroupSizeRef.current);
      setGroupTimer();
    } else {
      // 前のグループを確定して送信
      if (currentGroupSizeRef.current > 0) {
        sendGroupData(currentGroupSizeRef.current);
      }
      // 新しいグループを開始
      startNewGroup(currentTime);
    }
  }, [ws, sendGroupData, setGroupTimer, startNewGroup, isWebSocketReady]);

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');
    
    websocket.onopen = () => {
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      try {
        const data: VisitorStats = JSON.parse(event.data);
        setTotalVisitors(data.total_visitors);
        setDispTime(data.disp_times);
        setDispIntensity(data.disp_intensity);
        console.log('データ取得成功');
      } catch {
      }
    };

    websocket.onerror = () => {
    };

    websocket.onclose = () => {
    };

    fetch('http://localhost:8000/stats')
      .then(res => res.json())
      .then((data: VisitorStats) => {
        setTotalVisitors(data.total_visitors);
        // setRecentVisitors(data.recent_visitors);
        setDispTime(data.disp_times);
        setDispIntensity(data.disp_intensity);
        console.log('データ取得成功');
      })
      .catch(() => {
      });

    return () => {
      if (groupTimeoutRef.current) {
        clearTimeout(groupTimeoutRef.current);
      }
      websocket.close();
    };
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        e.preventDefault();
        handleClick();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleClick]);

  const chartData = {
    labels: disp_time.map(t => new Date(t).toLocaleTimeString()),
    datasets: [
      {
        label: '来場者数',
        data: disp_intensity,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-b from-blue-50 to-white px-2">
      <div className="flex flex-col items-center w-full max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold text-blue-800 mt-8 mb-2 text-center">来場者カウンター</h1>
        <p className="text-2xl text-blue-600 mb-4 text-center">総来場者数: {totalVisitors}人</p>
        <p className="text-lg text-gray-600 mb-8 text-center">スペースキーを押すか、下のキーをクリックしてください</p>

        <div
          tabIndex={0}
          onClick={handleClick}
          className="select-none w-[420px] h-16 flex items-center justify-center bg-gradient-to-b from-gray-100 to-gray-300 rounded-xl shadow-[0_4px_16px_rgba(0,0,0,0.15)] border border-gray-300 text-2xl font-bold text-gray-700 transition-all duration-150 hover:shadow-[0_8px_24px_rgba(0,0,0,0.18)] hover:-translate-y-1 active:shadow-[inset_0_2px_8px_rgba(0,0,0,0.18),0_2px_8px_rgba(0,0,0,0.10)] active:translate-y-1 cursor-pointer mb-10 outline-none focus:ring-4 focus:ring-blue-300"
          aria-label='スペースキー'
          style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.10), inset 0 2px 8px rgba(0,0,0,0.10)' }}
        >
          <span className="tracking-widest drop-shadow-sm">Space</span>
        </div>

        <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg p-4 flex-1 min-h-0 mb-8">
          <Line data={chartData} />
        </div>
      </div>
    </div>
  );
}

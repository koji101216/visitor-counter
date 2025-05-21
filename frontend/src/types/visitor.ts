export interface Visitor {
  timestamp: string;
  group_size: number;
}

export interface VisitorStats {
  total_visitors: number;
  disp_times: number[];
  disp_intensity: number[];
} 
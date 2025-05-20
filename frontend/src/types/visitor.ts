export interface Visitor {
  timestamp: string;
  group_size: number;
}

export interface VisitorStats {
  total_visitors: number;
  recent_visitors: Visitor[];
} 
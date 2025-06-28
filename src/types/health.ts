export interface User {
  id: string;
  username: string;
  email: string;
  fitbit_connected: boolean;
  fitbit_user_id?: string;
  created_at: string;
}

export interface FamilyGroup {
  id: string;
  name: string;
  invite_code: string;
  created_at: string;
  member_count: number;
}

export interface HealthData {
  date: string;
  steps: number;
  calories_burned: number;
  resting_heart_rate?: number;
  max_heart_rate?: number;
  hrv?: number;
  active_minutes?: number;
  distance?: number;
  floors?: number;
}

export interface FamilyMember {
  id: string;
  username: string;
  avatar: string;
  status: 'excellent' | 'good' | 'active' | 'warning' | 'inactive';
  todayScore: number;
  isCurrentUser?: boolean;
  fitbit_connected: boolean;
  today_data?: HealthData;
  weekly_data?: HealthData[];
  health_comment?: string;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  isNew: boolean;
  progress?: number;
  completed_at?: string;
}

export interface DashboardStats {
  steps: {
    current: number;
    target: number;
    percentage: number;
  };
  calories: {
    current: number;
    target: number;
    percentage: number;
  };
  heartRate: {
    current: number;
    status: 'normal' | 'elevated' | 'high' | 'low';
  };
  activeMinutes: {
    current: number;
    target: number;
    percentage: number;
  };
}

export interface FamilyStats {
  total_steps: number;
  total_calories: number;
  avg_steps: number;
  avg_calories: number;
  member_count: number;
  active_members: number;
}

export interface MotivationMessage {
  id: string;
  message: string;
  type: 'encouragement' | 'achievement' | 'challenge' | 'reminder';
  priority: 'high' | 'medium' | 'low';
  family_context?: boolean;
}
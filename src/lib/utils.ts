// Utility functions for the Family Health Dashboard

type ClassValue = string | number | boolean | undefined | null | { [key: string]: any } | ClassValue[];

function clsx(...inputs: ClassValue[]): string {
  return inputs
    .flat()
    .filter(Boolean)
    .map(input => {
      if (typeof input === 'string') return input;
      if (typeof input === 'object' && input !== null) {
        return Object.entries(input)
          .filter(([, value]) => Boolean(value))
          .map(([key]) => key)
          .join(' ');
      }
      return '';
    })
    .join(' ');
}

function twMerge(classes: string): string {
  // Simplified version - in production, use the actual tailwind-merge library
  return classes;
}

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// 健康データ関連のユーティリティ関数
export const healthUtils = {
  // 歩数のレベル判定
  getStepsLevel: (steps: number): 'low' | 'moderate' | 'good' | 'excellent' => {
    if (steps < 5000) return 'low';
    if (steps < 8000) return 'moderate';
    if (steps < 10000) return 'good';
    return 'excellent';
  },

  // カロリーのレベル判定
  getCaloriesLevel: (calories: number, target: number = 400): 'low' | 'moderate' | 'good' | 'excellent' => {
    const percentage = (calories / target) * 100;
    if (percentage < 50) return 'low';
    if (percentage < 75) return 'moderate';
    if (percentage < 100) return 'good';
    return 'excellent';
  },

  // 心拍数の状態判定
  getHeartRateStatus: (heartRate: number): 'low' | 'normal' | 'elevated' | 'high' => {
    if (heartRate < 60) return 'low';
    if (heartRate <= 100) return 'normal';
    if (heartRate <= 120) return 'elevated';
    return 'high';
  },

  // 総合的な健康スコア計算 (0-100)
  calculateHealthScore: (data: {
    steps: number;
    calories: number;
    heartRate?: number;
    activeMinutes?: number;
  }): number => {
    let score = 0;
    let factors = 0;

    // 歩数による評価 (40%)
    const stepsScore = Math.min((data.steps / 10000) * 40, 40);
    score += stepsScore;
    factors++;

    // カロリーによる評価 (30%)
    const caloriesScore = Math.min((data.calories / 400) * 30, 30);
    score += caloriesScore;
    factors++;

    // 心拍数による評価 (15%)
    if (data.heartRate) {
      const hrStatus = healthUtils.getHeartRateStatus(data.heartRate);
      const hrScore = hrStatus === 'normal' ? 15 : hrStatus === 'elevated' ? 10 : 5;
      score += hrScore;
      factors++;
    }

    // 活動時間による評価 (15%)
    if (data.activeMinutes) {
      const activeScore = Math.min((data.activeMinutes / 60) * 15, 15);
      score += activeScore;
      factors++;
    }

    return Math.round(score);
  },

  // ステータスに応じた色を取得
  getStatusColor: (status: string): string => {
    switch(status) {
      case 'excellent': return 'bg-green-500';
      case 'good': return 'bg-blue-500';
      case 'active': return 'bg-purple-500';
      case 'moderate': return 'bg-yellow-500';
      case 'warning': return 'bg-orange-500';
      case 'low': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  },

  // 進捗率を色で表現
  getProgressColor: (percentage: number): string => {
    if (percentage >= 100) return 'bg-green-400';
    if (percentage >= 75) return 'bg-blue-400';
    if (percentage >= 50) return 'bg-yellow-400';
    if (percentage >= 25) return 'bg-orange-400';
    return 'bg-red-400';
  }
};

// 日付関連のユーティリティ
export const dateUtils = {
  formatDate: (date: string | Date): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric'
    });
  },

  formatTime: (date: string | Date): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleTimeString('ja-JP', {
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  formatDateTime: (date: string | Date): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  isToday: (date: string | Date): boolean => {
    const d = typeof date === 'string' ? new Date(date) : date;
    const today = new Date();
    return d.toDateString() === today.toDateString();
  },

  getDaysAgo: (days: number): Date => {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return date;
  }
};

// 数値フォーマット関連のユーティリティ
export const formatUtils = {
  number: (num: number): string => {
    return new Intl.NumberFormat('ja-JP').format(num);
  },

  percentage: (num: number, decimals: number = 0): string => {
    return `${num.toFixed(decimals)}%`;
  },

  decimal: (num: number, decimals: number = 1): string => {
    return num.toFixed(decimals);
  }
};

// アニメーション関連のユーティリティ
export const animationUtils = {
  staggerDelay: (index: number, baseDelay: number = 100): number => {
    return index * baseDelay;
  },

  easeInOut: 'transition-all duration-300 ease-in-out',
  fadeIn: 'animate-in fade-in duration-500',
  slideUp: 'animate-in slide-in-from-bottom-4 duration-500',
  slideInFromLeft: 'animate-in slide-in-from-left-4 duration-500',
  slideInFromRight: 'animate-in slide-in-from-right-4 duration-500'
};
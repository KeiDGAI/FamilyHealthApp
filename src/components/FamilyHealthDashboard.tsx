'use client';

import React, { useState, useEffect } from 'react';
import { 
  Heart, 
  Activity, 
  Footprints, 
  Target, 
  TrendingUp, 
  Users, 
  Award,
  Clock,
  Zap,
  ChevronRight,
  Star,
  Calendar,
  Settings,
  RefreshCw
} from 'lucide-react';
import { api } from '@/lib/api';
import { healthUtils, dateUtils, formatUtils } from '@/lib/utils';
import { FamilyMember, DashboardStats, Achievement, FamilyStats, HealthData } from '@/types/health';

interface CircularProgressProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
}

const CircularProgress: React.FC<CircularProgressProps> = ({ 
  percentage, 
  size = 120, 
  strokeWidth = 8, 
  color = 'stroke-blue-500' 
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          className="text-gray-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          className={color}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold text-white">{percentage}%</span>
      </div>
    </div>
  );
};

const FamilyHealthDashboard: React.FC = () => {
  const [selectedMember, setSelectedMember] = useState('me');
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([]);
  const [todayStats, setTodayStats] = useState<DashboardStats | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [familyStats, setFamilyStats] = useState<FamilyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // データを取得する関数
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [members, stats, achievementsData] = await Promise.all([
        api.getFamilyMembers(),
        api.getFamilyStats(),
        api.getAchievements(),
      ]);

      setFamilyMembers(members);
      setFamilyStats(stats);
      setAchievements(achievementsData);

      // 現在のユーザーの今日のデータを取得
      const currentUserData = await api.getDailyHealthData();
      if (currentUserData) {
        const calculatedStats: DashboardStats = {
          steps: {
            current: currentUserData.steps,
            target: 10000,
            percentage: Math.min((currentUserData.steps / 10000) * 100, 100)
          },
          calories: {
            current: currentUserData.calories_burned,
            target: 400,
            percentage: Math.min((currentUserData.calories_burned / 400) * 100, 100)
          },
          heartRate: {
            current: currentUserData.resting_heart_rate || 72,
            status: healthUtils.getHeartRateStatus(currentUserData.resting_heart_rate || 72)
          },
          activeMinutes: {
            current: currentUserData.active_minutes || 45,
            target: 60,
            percentage: Math.min(((currentUserData.active_minutes || 45) / 60) * 100, 100)
          }
        };
        setTodayStats(calculatedStats);
      }

    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('データの取得に失敗しました。再試行してください。');
    } finally {
      setLoading(false);
    }
  };

  // 手動リフレッシュ機能
  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchDashboardData();
    setIsRefreshing(false);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // ステータスに応じた色を取得
  const getStatusColor = (status: string): string => {
    return healthUtils.getStatusColor(status);
  };

  // デフォルトのダッシュボード統計（フォールバック用）
  const defaultStats: DashboardStats = {
    steps: { current: 8542, target: 10000, percentage: 85 },
    calories: { current: 320, target: 400, percentage: 80 },
    heartRate: { current: 72, status: 'normal' },
    activeMinutes: { current: 45, target: 60, percentage: 75 }
  };

  const stats = todayStats || defaultStats;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-400" />
          <p className="text-xl">健康データを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-xl mb-4">{error}</div>
          <button 
            onClick={handleRefresh}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg transition-colors"
          >
            再試行
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4">
      {/* ヘッダー */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">おかえりなさい！</h1>
          <p className="text-slate-300">今日も一緒に健康になりましょう</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={handleRefresh} 
            disabled={isRefreshing}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 text-slate-300 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
          <div className="relative">
            <div className="w-3 h-3 bg-green-400 rounded-full absolute -top-1 -right-1 animate-pulse"></div>
            <Settings className="w-6 h-6 text-slate-300" />
          </div>
        </div>
      </div>

      {/* 家族メンバー選択 */}
      {familyMembers.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-3 flex items-center">
            <Users className="w-5 h-5 mr-2" />
            家族の今日の状況
          </h2>
          <div className="flex space-x-3 overflow-x-auto pb-2">
            {familyMembers.map((member) => (
              <div
                key={member.id}
                onClick={() => setSelectedMember(member.id)}
                className={`flex-shrink-0 p-3 rounded-xl cursor-pointer transition-all duration-300 ${
                  selectedMember === member.id 
                    ? 'bg-blue-600 shadow-lg shadow-blue-600/30' 
                    : 'bg-slate-800 hover:bg-slate-700'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-1">{member.avatar}</div>
                  <div className="text-sm font-medium">{member.username}</div>
                  <div className={`w-2 h-2 rounded-full mx-auto mt-2 ${getStatusColor(member.status)}`}></div>
                  <div className="text-xs text-slate-300 mt-1">{member.todayScore}点</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* メイン統計 */}
      <div className="mb-6">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 mb-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold mb-2">今日の進捗</h3>
              <p className="text-blue-100">目標まであと少し！</p>
            </div>
            <CircularProgress 
              percentage={Math.round(stats.steps.percentage)} 
              size={100} 
              color="stroke-white"
            />
          </div>
        </div>

        {/* 詳細統計グリッド */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <div className="flex items-center justify-between mb-3">
              <Footprints className="w-6 h-6 text-green-400" />
              <span className="text-sm text-slate-300">歩数</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">
              {formatUtils.number(stats.steps.current)}
            </div>
            <div className="text-sm text-slate-400">
              目標: {formatUtils.number(stats.steps.target)}
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 mt-2">
              <div 
                className="bg-green-400 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(stats.steps.percentage, 100)}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <div className="flex items-center justify-between mb-3">
              <Zap className="w-6 h-6 text-red-400" />
              <span className="text-sm text-slate-300">カロリー</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">
              {formatUtils.number(stats.calories.current)}
            </div>
            <div className="text-sm text-slate-400">
              目標: {formatUtils.number(stats.calories.target)}
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 mt-2">
              <div 
                className="bg-red-400 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(stats.calories.percentage, 100)}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <div className="flex items-center justify-between mb-3">
              <Heart className="w-6 h-6 text-pink-400" />
              <span className="text-sm text-slate-300">心拍数</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">
              {stats.heartRate.current}
            </div>
            <div className={`text-sm ${stats.heartRate.status === 'normal' ? 'text-green-400' : 'text-yellow-400'}`}>
              {stats.heartRate.status === 'normal' ? '正常範囲' : '要注意'}
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <div className="flex items-center justify-between mb-3">
              <Activity className="w-6 h-6 text-yellow-400" />
              <span className="text-sm text-slate-300">活動時間</span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">
              {stats.activeMinutes.current}分
            </div>
            <div className="text-sm text-slate-400">
              目標: {stats.activeMinutes.target}分
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 mt-2">
              <div 
                className="bg-yellow-400 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(stats.activeMinutes.percentage, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* 達成度とモチベーション */}
      {achievements.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <Award className="w-5 h-5 mr-2 text-yellow-400" />
            実績 & 挑戦
          </h3>
          <div className="space-y-3">
            {achievements.map((achievement) => (
              <div key={achievement.id} className="bg-slate-800 rounded-xl p-4 border border-slate-700 flex items-center justify-between">
                <div className="flex items-center">
                  <div className="text-2xl mr-3">{achievement.icon}</div>
                  <div>
                    <div className="font-semibold text-white flex items-center">
                      {achievement.title}
                      {achievement.isNew && (
                        <span className="ml-2 bg-green-500 text-xs px-2 py-1 rounded-full">NEW</span>
                      )}
                    </div>
                    <div className="text-sm text-slate-400">{achievement.description}</div>
                    {achievement.progress && (
                      <div className="w-32 bg-slate-700 rounded-full h-2 mt-2">
                        <div 
                          className="bg-blue-400 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${achievement.progress}%` }}
                        ></div>
                      </div>
                    )}
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-slate-400" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* モチベーション向上メッセージ */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl p-4 mb-6">
        <div className="flex items-center">
          <Star className="w-6 h-6 text-yellow-300 mr-3" />
          <div>
            <div className="font-semibold text-white">今日の励まし</div>
            <div className="text-green-100 text-sm">
              あと{formatUtils.number(stats.steps.target - stats.steps.current)}歩で目標達成！{familyStats && `家族みんなで${formatUtils.number(familyStats.total_steps)}歩達成中 👨‍👩‍👧‍👦`}
            </div>
          </div>
        </div>
      </div>

      {/* グループ統計情報 */}
      {familyStats && (
        <div className="mb-6">
          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h5 className="font-semibold text-white mb-3 flex items-center">
              <Users className="w-5 h-5 mr-2 text-blue-400" />
              グループ統計（今日）
            </h5>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-400">{formatUtils.number(familyStats.total_steps)}</div>
                <div className="text-sm text-slate-400">合計歩数</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-400">{formatUtils.number(familyStats.total_calories)}</div>
                <div className="text-sm text-slate-400">合計カロリー</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-400">{familyStats.active_members}</div>
                <div className="text-sm text-slate-400">活動メンバー</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-400">{formatUtils.number(familyStats.avg_steps)}</div>
                <div className="text-sm text-slate-400">平均歩数</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* クイックアクション */}
      <div className="grid grid-cols-2 gap-4">
        <button className="bg-blue-600 hover:bg-blue-700 rounded-xl p-4 flex items-center justify-center space-x-2 transition-colors">
          <TrendingUp className="w-5 h-5" />
          <span>詳細分析</span>
        </button>
        <button className="bg-purple-600 hover:bg-purple-700 rounded-xl p-4 flex items-center justify-center space-x-2 transition-colors">
          <Calendar className="w-5 h-5" />
          <span>チャレンジ</span>
        </button>
      </div>
    </div>
  );
};

export default FamilyHealthDashboard;
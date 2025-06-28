import { User, FamilyGroup, FamilyMember, HealthData, FamilyStats, Achievement } from '@/types/health';

const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000';

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include',
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // 認証関連
  async login(username: string, password: string): Promise<{ success: boolean; user?: User }> {
    return this.request('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async register(userData: { username: string; email: string; password: string; group_action?: string; group_name?: string; invite_code?: string }): Promise<{ success: boolean; user?: User }> {
    return this.request('/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout(): Promise<{ success: boolean }> {
    return this.request('/logout', {
      method: 'POST',
    });
  }

  // ユーザー情報
  async getCurrentUser(): Promise<User | null> {
    try {
      return await this.request('/api/user/current');
    } catch {
      return null;
    }
  }

  async updateProfile(data: Partial<User>): Promise<{ success: boolean; user?: User }> {
    return this.request('/profile', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // 家族グループ
  async getFamilyGroup(): Promise<FamilyGroup | null> {
    try {
      return await this.request('/api/family/group');
    } catch {
      return null;
    }
  }

  async getFamilyMembers(): Promise<FamilyMember[]> {
    try {
      const response = await this.request<{ family_members_data: FamilyMember[]; demo_mode: boolean }>('/api/family/members');
      return response.family_members_data || [];
    } catch {
      return [];
    }
  }

  async getFamilyStats(): Promise<FamilyStats | null> {
    try {
      return await this.request('/api/family/stats');
    } catch {
      return null;
    }
  }

  async joinGroup(inviteCode: string): Promise<{ success: boolean; message?: string }> {
    return this.request('/join_group', {
      method: 'POST',
      body: JSON.stringify({ invite_code: inviteCode }),
    });
  }

  async leaveGroup(): Promise<{ success: boolean; message?: string }> {
    return this.request('/leave_group', {
      method: 'POST',
    });
  }

  // 健康データ
  async getDailyHealthData(userId?: string): Promise<HealthData | null> {
    const endpoint = userId ? `/api/health/daily/${userId}` : '/api/health/daily';
    try {
      return await this.request(endpoint);
    } catch {
      return null;
    }
  }

  async getWeeklyHealthData(userId?: string): Promise<HealthData[]> {
    const endpoint = userId ? `/api/health/weekly/${userId}` : '/api/health/weekly';
    try {
      return await this.request(endpoint);
    } catch {
      return [];
    }
  }

  // Fitbit連携
  async connectFitbit(): Promise<{ auth_url: string }> {
    return this.request('/connect_fitbit');
  }

  async disconnectFitbit(): Promise<{ success: boolean }> {
    return this.request('/disconnect_fitbit', {
      method: 'POST',
    });
  }

  // 実績・目標
  async getAchievements(): Promise<Achievement[]> {
    try {
      return await this.request('/api/achievements');
    } catch {
      return [];
    }
  }

  // AI健康コメント
  async getHealthComment(healthData: HealthData): Promise<{ comment: string }> {
    return this.request('/api/health/comment', {
      method: 'POST',
      body: JSON.stringify({ health_data: healthData }),
    });
  }
}

export const api = new ApiClient();
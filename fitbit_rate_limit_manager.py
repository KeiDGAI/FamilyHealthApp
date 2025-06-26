#!/usr/bin/env python3
"""
Fitbit APIレート制限管理システム
"""

import time
from datetime import datetime, timedelta

class FitbitRateLimitManager:
    def __init__(self):
        self.rate_limit_reset_time = None
        self.is_rate_limited = False
    
    def mark_rate_limited(self):
        """レート制限が発生したことを記録"""
        self.is_rate_limited = True
        # Fitbitのレート制限は通常1時間でリセット
        self.rate_limit_reset_time = datetime.now() + timedelta(hours=1)
        print(f"Rate limit activated until: {self.rate_limit_reset_time}")
    
    def can_make_request(self):
        """APIリクエストが可能かチェック"""
        if not self.is_rate_limited:
            return True
        
        if self.rate_limit_reset_time and datetime.now() > self.rate_limit_reset_time:
            self.is_rate_limited = False
            self.rate_limit_reset_time = None
            print("Rate limit reset - API requests enabled")
            return True
        
        return False
    
    def get_time_until_reset(self):
        """レート制限解除までの時間を取得"""
        if not self.is_rate_limited or not self.rate_limit_reset_time:
            return 0
        
        time_diff = self.rate_limit_reset_time - datetime.now()
        return max(0, int(time_diff.total_seconds() / 60))  # 分単位

# グローバルインスタンス
rate_limit_manager = FitbitRateLimitManager()
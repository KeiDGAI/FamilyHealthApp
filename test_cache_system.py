#!/usr/bin/env python3
"""
Fitbitキャッシュシステムのテスト
"""

import sys
sys.path.append('.')

from app import app, db
from models import User, FitbitData
from datetime import datetime, timedelta

def test_cache_functionality():
    """キャッシュ機能のテスト"""
    with app.app_context():
        # テストユーザーを取得
        user = User.query.filter_by(username='user').first()
        if not user:
            print("テストユーザーが見つかりません")
            return
        
        print("=== Fitbitキャッシュシステムテスト ===")
        
        # 現在のキャッシュデータを確認
        today = datetime.now().date()
        cached_data = FitbitData.query.filter_by(
            user_id=user.id,
            date=today
        ).first()
        
        if cached_data:
            print(f"✓ キャッシュデータ存在: {cached_data.steps}歩, {cached_data.calories_burned}kcal")
            print(f"✓ 取得時刻: {cached_data.fetched_at}")
            print(f"✓ キャッシュ期限切れ: {'はい' if cached_data.is_cache_expired() else 'いいえ'}")
            
            # キャッシュの有効期限をテスト
            minutes_since_fetch = (datetime.utcnow() - cached_data.fetched_at).total_seconds() / 60
            print(f"✓ 取得からの経過時間: {minutes_since_fetch:.1f}分")
            
            if minutes_since_fetch < 30:
                print("✓ キャッシュは有効です（30分以内）")
            else:
                print("⚠ キャッシュは期限切れです（30分経過）")
        else:
            print("✗ キャッシュデータが見つかりません")
        
        # 全キャッシュデータを表示
        all_cache = FitbitData.query.filter_by(user_id=user.id).all()
        print(f"\n総キャッシュレコード数: {len(all_cache)}")
        
        for cache in all_cache:
            print(f"  {cache.date}: {cache.steps}歩, {cache.calories_burned}kcal (取得: {cache.fetched_at})")

if __name__ == '__main__':
    test_cache_functionality()
"""
開発モード用デモデータ
"""
from datetime import datetime, timedelta
import random

def get_demo_data():
    """3人の家族メンバーの10日間のデモデータを生成"""
    
    # 基準日から10日間のデータを生成
    base_date = datetime.now().date()
    dates = [(base_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(9, -1, -1)]
    
    # 家族メンバーのデモデータ
    demo_members = {
        'もえ': {
            'username': 'もえ',
            'fitbit_connected': True,
            'is_current_user': False,
            'daily_data': []
        },
        'すずこ': {
            'username': 'すずこ',
            'fitbit_connected': True,
            'is_current_user': False,
            'daily_data': []
        },
        'なおひさ': {
            'username': 'なおひさ',
            'fitbit_connected': True,
            'is_current_user': False,
            'daily_data': []
        }
    }
    
    # シード値を設定して再現可能なランダムデータを生成
    random.seed(42)
    
    # 各メンバーの10日間のデータを生成
    for member_name, member_data in demo_members.items():
        for date in dates:
            # メンバーごとに特徴的なパターンを作成
            if member_name == 'もえ':
                # もえ：比較的活発
                steps = random.randint(8000, 12000)
                calories = random.randint(2200, 3000)
                heart_rate = random.randint(68, 78)
                hrv = random.randint(48, 58)
            elif member_name == 'すずこ':
                # すずこ：中程度の活動
                steps = random.randint(7000, 10000)
                calories = random.randint(1900, 2500)
                heart_rate = random.randint(65, 75)
                hrv = random.randint(45, 55)
            else:  # なおひさ
                # なおひさ：やや低活動
                steps = random.randint(6500, 9500)
                calories = random.randint(1800, 2300)
                heart_rate = random.randint(70, 80)
                hrv = random.randint(42, 52)
            
            daily_data = {
                'date': date,
                'steps': steps,
                'calories_burned': calories,
                'resting_heart_rate': heart_rate,
                'hrv': hrv,
                'fetched_at': datetime.now()
            }
            
            member_data['daily_data'].append(daily_data)
        
        # 今日のデータを設定（最新の日付）
        member_data['today_data'] = member_data['daily_data'][-1] if member_data['daily_data'] else None
        
        # 健康コメントを生成（簡単な日本語コメント）
        if member_data['today_data']:
            steps = member_data['today_data']['steps']
            if steps >= 10000:
                comment = f"素晴らしい！{steps:,}歩も歩いて健康的な一日を過ごされましたね。この調子で継続していけば、健康寿命の延伸に大きく貢献します。"
            elif steps >= 8000:
                comment = f"{steps:,}歩、よく頑張りました！もう少しで目標の1万歩です。継続的な運動習慣が健康の基盤となります。"
            else:
                comment = f"今日は{steps:,}歩でした。明日はもう少し歩く機会を増やしてみませんか？少しずつでも運動習慣を築いていきましょう。"
        else:
            comment = "健康データを確認中です。日々の記録が健康管理の第一歩です。"
        
        member_data['health_comment'] = comment
    
    return demo_members

def get_demo_family_stats():
    """デモデータの家族統計を計算"""
    demo_data = get_demo_data()
    
    total_steps = 0
    total_calories = 0
    member_count = 0
    
    for member_data in demo_data.values():
        if member_data['today_data']:
            total_steps += member_data['today_data']['steps']
            total_calories += member_data['today_data']['calories_burned']
            member_count += 1
    
    avg_steps = total_steps // member_count if member_count > 0 else 0
    avg_calories = total_calories // member_count if member_count > 0 else 0
    
    return {
        'total_steps': total_steps,
        'total_calories': total_calories,
        'avg_steps': avg_steps,
        'avg_calories': avg_calories,
        'member_count': member_count
    }
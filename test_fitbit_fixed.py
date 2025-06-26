#!/usr/bin/env python3
"""
修正されたFitbit認証をテストする
"""

import os
import sys
sys.path.append('.')

from app import app
import requests
import base64

def test_fixed_auth():
    """修正されたFitbit認証をテスト"""
    with app.app_context():
        print("=== 修正されたFitbit認証のテスト ===")
        
        client_id = os.environ.get('FITBIT_CLIENT_ID')
        client_secret = os.environ.get('FITBIT_CLIENT_SECRET')
        redirect_uri = app.config.get('FITBIT_REDIRECT_URI')
        
        # Basic認証ヘッダーの作成テスト
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        print(f"Basic認証ヘッダー: Basic {auth_b64[:20]}...")
        
        # 修正されたトークン交換のテスト
        token_url = 'https://api.fitbit.com/oauth2/token'
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_b64}'
        }
        
        data = {
            'client_id': client_id,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': 'test_code'  # 模擬コード
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data, timeout=10)
            print(f"修正後のトークン交換: ステータス {response.status_code}")
            
            if response.status_code == 400:
                response_data = response.json()
                if 'invalid_grant' in response.text:
                    print("✓ 認証ヘッダー修正成功: invalid_grantエラー（テストコードが原因、正常）")
                else:
                    print(f"レスポンス: {response.text}")
            elif response.status_code == 401:
                if 'invalid_client' in response.text:
                    print("✗ まだクライアント認証エラーが発生")
                else:
                    print(f"レスポンス: {response.text}")
            else:
                print(f"予期しないステータス: {response.text}")
                
        except Exception as e:
            print(f"テストエラー: {e}")

if __name__ == '__main__':
    test_fixed_auth()
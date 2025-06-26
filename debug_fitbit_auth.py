#!/usr/bin/env python3
"""
Fitbit認証エラーの詳細診断スクリプト
"""

import os
import sys
sys.path.append('.')

from app import app
from models import User
import requests

def test_fitbit_config():
    """Fitbit設定をテスト"""
    with app.app_context():
        print("=== Fitbit OAuth設定の診断 ===")
        
        # 環境変数の確認
        client_id = os.environ.get('FITBIT_CLIENT_ID')
        client_secret = os.environ.get('FITBIT_CLIENT_SECRET')
        redirect_uri = app.config.get('FITBIT_REDIRECT_URI')
        
        print(f"Client ID: {client_id[:8]}..." if client_id else "Client ID: 設定されていません")
        print(f"Client Secret: {'設定済み' if client_secret else '設定されていません'}")
        print(f"Redirect URI: {redirect_uri}")
        
        # Fitbit API接続テスト
        try:
            response = requests.get('https://api.fitbit.com/oauth2/token', timeout=10)
            print(f"Fitbit API接続: OK (ステータス: {response.status_code})")
        except Exception as e:
            print(f"Fitbit API接続: エラー - {e}")
        
        # OAuth URLの構築テスト
        try:
            from requests_oauthlib import OAuth2Session
            
            fitbit = OAuth2Session(
                client_id,
                scope=['activity', 'heartrate', 'profile'],
                redirect_uri=redirect_uri
            )
            
            auth_url, state = fitbit.authorization_url('https://www.fitbit.com/oauth2/authorize')
            print(f"OAuth URL構築: OK")
            print(f"認証URL: {auth_url[:100]}...")
            
        except Exception as e:
            print(f"OAuth URL構築: エラー - {e}")
            import traceback
            traceback.print_exc()

def test_token_exchange():
    """トークン交換のテスト（模擬）"""
    print("\n=== トークン交換テスト ===")
    
    client_id = os.environ.get('FITBIT_CLIENT_ID')
    client_secret = os.environ.get('FITBIT_CLIENT_SECRET')
    redirect_uri = app.config.get('FITBIT_REDIRECT_URI')
    
    # 模擬的なトークン交換リクエスト
    token_url = 'https://api.fitbit.com/oauth2/token'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {client_id}:{client_secret}'
    }
    
    data = {
        'client_id': client_id,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': 'test_code'  # 模擬コード
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data, timeout=10)
        print(f"トークン交換リクエスト: ステータス {response.status_code}")
        
        if response.status_code != 200:
            print(f"レスポンス: {response.text}")
            
            if 'invalid_client' in response.text:
                print("エラー原因: クライアントIDまたはシークレットが無効")
            elif 'invalid_grant' in response.text:
                print("エラー原因: 認証コードが無効（これは正常、テストコードのため）")
            elif 'redirect_uri_mismatch' in response.text:
                print("エラー原因: リダイレクトURIが一致しない")
                
    except Exception as e:
        print(f"トークン交換テスト: エラー - {e}")

if __name__ == '__main__':
    test_fitbit_config()
    test_token_exchange()
#!/usr/bin/env python3
"""
Fitbit OAuth設定のデバッグ用スクリプト
"""
import os

print("=== Fitbit OAuth 設定確認 ===")
print(f"Client ID: {os.environ.get('FITBIT_CLIENT_ID', 'NOT_SET')[:8]}...")
print(f"Client Secret: {'SET' if os.environ.get('FITBIT_CLIENT_SECRET') else 'NOT_SET'}")
print(f"Redirect URI: {os.environ.get('FITBIT_REDIRECT_URI', 'DEFAULT')}")
print(f"Current Domain: {os.environ.get('REPLIT_DOMAINS', 'NOT_AVAILABLE')}")

print("\n=== Fitbit Developer Console 設定確認項目 ===")
print("1. Application Type: Server を選択")
print("2. OAuth 2.0 Application Type: Server")
print("3. Default Access Type: Read & Write")
print(f"4. Redirect URL: https://{os.environ.get('REPLIT_DOMAINS')}/fitbit_callback")
print("\n設定完了後、アプリケーションを保存してから再度テストしてください。")
import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import url_for, request
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        if not self.api_key:
            logger.warning('SENDGRID_API_KEY environment variable not set')
            self.sg = None
        else:
            self.sg = SendGridAPIClient(self.api_key)
    
    def send_family_invitation(self, invitation, inviter_name, base_url=None):
        """家族グループへの招待メールを送信"""
        if not self.sg:
            logger.error('SendGrid not configured - SENDGRID_API_KEY missing')
            return False
        
        try:
            # 招待リンクを生成
            if not base_url:
                base_url = request.url_root.rstrip('/')
            
            invitation_url = f"{base_url}/join-invitation/{invitation.token}"
            
            # メール内容を作成
            subject = f"{inviter_name}さんから家族グループ「{invitation.family_group.name}」への招待"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🏠 家族健康管理アプリ</h1>
                    <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">家族みんなで健康を管理しよう</p>
                </div>
                
                <div style="background: white; padding: 30px; border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-top: 0;">家族グループへの招待</h2>
                    
                    <p style="color: #666; line-height: 1.6;">
                        こんにちは！<br><br>
                        <strong>{inviter_name}</strong>さんから、家族健康管理アプリの家族グループ
                        <strong>「{invitation.family_group.name}」</strong>への招待が届きました。
                    </p>
                    
                    <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="color: #667eea; margin-top: 0; font-size: 18px;">🎯 家族健康管理アプリでできること</h3>
                        <ul style="color: #666; line-height: 1.8; padding-left: 20px;">
                            <li>📊 <strong>健康データの共有</strong> - 歩数、心拍数、消費カロリーなどの健康指標を家族と共有</li>
                            <li>🏆 <strong>目標達成の応援</strong> - 家族みんなで健康目標にチャレンジ</li>
                            <li>🤖 <strong>AI健康アドバイス</strong> - 最新のAI技術による個別健康コメント</li>
                            <li>📱 <strong>Fitbit連携</strong> - お持ちのFitbitデバイスと簡単連携</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{invitation_url}" 
                           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                  color: white; 
                                  padding: 15px 40px; 
                                  text-decoration: none; 
                                  border-radius: 25px; 
                                  font-weight: bold; 
                                  font-size: 16px;
                                  display: inline-block;
                                  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                            🚀 今すぐ参加する
                        </a>
                    </div>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404; font-size: 14px;">
                            ⏰ <strong>招待の有効期限:</strong> {invitation.expires_at.strftime('%Y年%m月%d日 %H:%M')}まで<br>
                            このリンクは一度だけ使用できます。
                        </p>
                    </div>
                    
                    <hr style="border: none; height: 1px; background: #eee; margin: 25px 0;">
                    
                    <p style="color: #999; font-size: 12px; line-height: 1.5;">
                        このメールに心当たりがない場合は、無視してください。<br>
                        リンクをクリックできない場合は、以下のURLをブラウザにコピーしてアクセスしてください：<br>
                        <span style="word-break: break-all;">{invitation_url}</span>
                    </p>
                </div>
                
                <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                    <p>© 2025 家族健康管理アプリ. すべての権利を保有します.</p>
                </div>
            </div>
            """
            
            text_content = f"""
家族グループへの招待

こんにちは！

{inviter_name}さんから、家族健康管理アプリの家族グループ「{invitation.family_group.name}」への招待が届きました。

家族健康管理アプリでは、家族みんなで健康データを共有し、目標達成を応援し合うことができます。

以下のリンクから参加できます：
{invitation_url}

招待の有効期限: {invitation.expires_at.strftime('%Y年%m月%d日 %H:%M')}まで

このリンクは一度だけ使用できます。

このメールに心当たりがない場合は、無視してください。

© 2025 家族健康管理アプリ
            """
            
            # メールを送信
            message = Mail(
                from_email=Email("noreply@health-family-app.com", "家族健康管理アプリ"),
                to_emails=To(invitation.email),
                subject=subject
            )
            
            message.content = Content("text/html", html_content)
            # テキスト版も追加
            message.add_content(Content("text/plain", text_content))
            
            response = self.sg.send(message)
            logger.info(f"Invitation email sent to {invitation.email}, status: {response.status_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send invitation email to {invitation.email}: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email, username, family_group_name=None):
        """新規ユーザーへのウェルカムメールを送信"""
        if not self.sg:
            logger.error('SendGrid not configured - SENDGRID_API_KEY missing')
            return False
        
        try:
            subject = "家族健康管理アプリへようこそ！"
            
            family_section = ""
            if family_group_name:
                family_section = f"""
                <div style="background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">🎉 家族グループに参加しました</h3>
                    <p style="color: #155724; margin-bottom: 0;">
                        <strong>「{family_group_name}」</strong>グループのメンバーになりました！<br>
                        さっそく家族の健康データを確認してみましょう。
                    </p>
                </div>
                """
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🏠 家族健康管理アプリ</h1>
                    <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">ようこそ、{username}さん！</p>
                </div>
                
                <div style="background: white; padding: 30px; border-radius: 10px; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-top: 0;">アカウント作成が完了しました</h2>
                    
                    <p style="color: #666; line-height: 1.6;">
                        家族健康管理アプリにご登録いただき、ありがとうございます！<br>
                        これから家族みんなで健康管理を始めましょう。
                    </p>
                    
                    {family_section}
                    
                    <div style="background: #f8f9ff; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="color: #667eea; margin-top: 0; font-size: 18px;">🚀 次のステップ</h3>
                        <ol style="color: #666; line-height: 1.8; padding-left: 20px;">
                            <li><strong>Fitbitデバイスを連携</strong> - 自動的に健康データを取得</li>
                            <li><strong>健康目標を設定</strong> - 歩数や消費カロリーの目標を決めましょう</li>
                            <li><strong>家族の健康状況を確認</strong> - みんなでモチベーションアップ</li>
                            <li><strong>AIアドバイスを活用</strong> - 個別の健康コメントをチェック</li>
                        </ol>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{request.url_root if request else 'https://your-app-url.com'}" 
                           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                  color: white; 
                                  padding: 15px 40px; 
                                  text-decoration: none; 
                                  border-radius: 25px; 
                                  font-weight: bold; 
                                  font-size: 16px;
                                  display: inline-block;
                                  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                            📱 アプリを開く
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                    <p>© 2025 家族健康管理アプリ. すべての権利を保有します.</p>
                </div>
            </div>
            """
            
            message = Mail(
                from_email=Email("noreply@health-family-app.com", "家族健康管理アプリ"),
                to_emails=To(user_email),
                subject=subject
            )
            
            message.content = Content("text/html", html_content)
            
            response = self.sg.send(message)
            logger.info(f"Welcome email sent to {user_email}, status: {response.status_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
            return False

# シングルトンインスタンス
email_service = EmailService()
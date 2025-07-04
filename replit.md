# Family Health Management App

## Overview

This is a Flask-based family health management web application built with Python. The application provides user authentication, profile management, and is designed to track family members' health information. It uses a simple architecture with SQLAlchemy for database operations and Bootstrap for the frontend styling.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Database**: SQLite (in-memory for development, configured for easy migration to PostgreSQL)
- **Authentication**: Session-based authentication with password hashing using Werkzeug
- **WSGI Server**: Gunicorn for production deployment

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome
- **Responsive Design**: Mobile-first approach using Bootstrap's grid system

### Application Structure
```
├── app.py          # Application factory and configuration
├── main.py         # Entry point for development server
├── models.py       # Database models
├── routes.py       # Route handlers and business logic
├── templates/      # HTML templates
├── static/         # Static assets (CSS, JS, images)
└── .replit         # Replit configuration
```

## Key Components

### Database Models
- **User Model**: Manages family member information including username, display name, email, password hash, age, and gender
- Password hashing implemented using Werkzeug's security functions
- Timestamp tracking for user creation dates

### Authentication System
- Session-based authentication
- Password hashing and verification
- Login/logout functionality
- Registration system with form validation
- Protected routes requiring authentication

### Route Handlers
- **Home Route** (`/`): Dashboard for authenticated users
- **Login Route** (`/login`): User authentication
- **Register Route** (`/register`): New user registration
- Session management and user state tracking

### Frontend Components
- **Base Template**: Common layout with navigation and Bootstrap integration
- **Login/Register Forms**: User authentication interfaces
- **Dashboard**: User profile display and welcome interface
- **Responsive Design**: Mobile-friendly interface using Bootstrap

## Data Flow

1. **User Registration**: New users fill registration form → Server validates data → Password is hashed → User record created in database
2. **User Login**: User submits credentials → Server validates against database → Session is created → User redirected to dashboard
3. **Protected Access**: User requests protected page → Server checks session → If valid, renders page; if invalid, redirects to login
4. **Profile Display**: Authenticated user accesses dashboard → Server retrieves user data from database → Profile information displayed

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Gunicorn**: WSGI HTTP Server
- **email-validator**: Email validation
- **psycopg2-binary**: PostgreSQL adapter (ready for production)

### Frontend Dependencies (CDN)
- **Bootstrap 5**: CSS framework with dark theme
- **Font Awesome**: Icon library

### Development Tools
- **Replit**: Development and deployment platform
- **Nix**: Package management for consistent environment

## Deployment Strategy

### Development Environment
- Uses Flask development server (`flask run`)
- In-memory SQLite database for rapid development
- Hot reload enabled for code changes

### Production Environment
- **Server**: Gunicorn WSGI server
- **Binding**: 0.0.0.0:5000 with autoscale deployment
- **Database**: Configured for easy migration to PostgreSQL
- **Proxy**: ProxyFix middleware for reverse proxy compatibility

### Replit Configuration
- **Deployment Target**: Autoscale
- **Package Management**: UV for Python dependencies
- **System Packages**: OpenSSL and PostgreSQL ready

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- **July 4, 2025**: ナビゲーション視認性改善・全ページ統一完了
  - 現在ページハイライト統一：白文字+青背景+角丸で明確な識別性
  - 全6ページのgetPageClass関数を統一：modern_dashboard.html・family_modern.html・profile_modern.html・components/navigation.html
  - member_achievement.htmlのJSX構文エラー修正：Jinjaテンプレートとの競合解決
  - 色分けメニュー削除：青・緑・紫の個別色からグレー統一表示に変更
  - デスクトップ・モバイル両方で一貫したナビゲーション体験
- **July 3, 2025**: 全ページナビゲーション統一完了
  - 目標設定ページ（/goals）のナビゲーション修正：base.htmlからReact統一ナビゲーションに変更
  - ホーム画面のデスクトップメニューに「目標設定」リンク追加：家族とFitbit連携の間に配置
  - 統一ナビゲーション（components/navigation.html）に「目標設定」メニュー追加
  - 全6ページ（ホーム・家族・目標設定・Fitbit連携・家族管理・プロフィール）で統一メニュー表示
  - React統一ナビゲーション適用：全ページで同一のナビゲーション体験提供
- **July 3, 2025**: ナビゲーション構成を整理・目標設定メニュー追加完了
  - ホーム画面下部の4つのクイックアクション削除：目標設定・詳細分析・家族チャレンジ・実績確認
  - 実績確認ボタンを今日の進捗セクション下に移動：より自然な配置でアクセス向上
  - 上部メニューに目標設定追加：全ページからワンクリックでアクセス可能
  - 家族チャレンジのリンク先を/family/challengesに変更：適切なURLに修正
  - family_modern.html・profile_modern.htmlの統一ナビゲーションに目標設定追加
  - レイアウト簡素化でユーザビリティ向上：不要な機能削除で迷いを軽減
- **July 1, 2025**: 全ページメニュー統一化完了
  - 統一ナビゲーションコンポーネント作成：UnifiedNavigationで全ページ共通メニュー実装
  - 5ページ完全統一：ホーム・家族・Fitbit連携・家族管理・プロフィールで同一メニュー表示
  - モバイル対応完全統一：ハンバーガーメニューボタンと展開メニューが全ページで一致
  - 現在ページハイライト：各ページで適切なメニュー項目が青色でハイライト表示
  - 重複ナビゲーション削除：各ページから個別ナビゲーションを削除して統一コンポーネントのみ使用
- **July 1, 2025**: Fitbit連携・家族管理メニュー項目追加完了
  - ナビゲーションメニュー拡張：Fitbit連携・家族管理の2つの新機能を追加
  - Fitbit連携設定画面：デバイス接続状況、取得可能データ説明、設定手順表示
  - 家族管理画面：グループ作成・参加・招待コード管理・承認システム
  - 統一ナビゲーション：全ページで5つのメニュー項目（ホーム・家族・Fitbit連携・家族管理・プロフィール）
  - 色分けデザイン：各機能に応じた色テーマ（緑：Fitbit、紫：家族管理）
  - 機能別ルート追加：/fitbit-setup・/family-managementエンドポイント実装
- **July 1, 2025**: 残りページ作成・完全ナビゲーション実装完了
  - 家族メンバー目標達成状況ページ：個別メンバーの7日間達成状況、実績バッジ、週間トレンド表示
  - 健康指標詳細ページ：歩数・カロリー・心拍数・活動時間の10日間棒グラフ分析、統計インサイト
  - ナビゲーション完全連携：家族メンバーアイコン→目標達成状況、健康指標アイコン→詳細分析
  - 全ページクリック遷移：ホーム→健康指標詳細、家族→メンバー詳細でシームレス操作
  - React JSXエラー解決：Jinjaテンプレート互換性向上、動的スタイル実装
- **July 1, 2025**: モダンUI全ページ刷新・包括的機能拡張完了
  - 家族ページ刷新：React基盤の統計サマリー、メンバーカード、チャレンジ進捗、実績表示
  - プロフィール拡張：5タブ構成（プロフィール・健康設定・通知・アプリ設定・プライバシー）
  - 詳細分析ページ：長期トレンド分析、カスタムフィルタ、統計インサイト、データエクスポート
  - ナビゲーション統一：全ページでTailwind CSS + React統一デザイン
  - クイックアクション充実：ホームから4つの主要機能への直接アクセス
  - ローカルストレージ活用：ユーザー設定・通知設定・健康目標の永続化
- **June 30, 2025**: 詳細ページ・目標管理・家族チャレンジシステム完全実装
  - メンバー詳細ページ：10日間の健康データを棒グラフで表示、統計サマリー、詳細テーブル
  - 目標設定画面：基本・健康指標・週間チャレンジ設定、プリセット機能、ローカルストレージ保存
  - 目標達成状況画面：7日間の達成状況分析、実績バッジシステム、モチベーションメッセージ
  - 家族チャレンジ画面：アクティブチャレンジ表示、新規作成フォーム、テンプレート機能
  - ダッシュボード連携：家族メンバークリックで詳細遷移、クイックアクションボタン追加
  - Chart.js統合：美しい棒グラフ・円グラフ・プログレスバー表示
- **June 29, 2025**: Modernダッシュボードをホーム画面に変更・ページ構成簡素化完了
  - ホーム画面（/）をModern Dashboardに変更：ログイン後すぐに美しいReactダッシュボード表示
  - 不要ページ削除：React Dashboard、Modern Dashboard、グループページを削除
  - ナビゲーション簡素化：ホーム・家族・プロフィール・ログアウトの4つのみ
  - JavaScriptエラー修正：LucideアイコンをカスタムSVGに置換、Tailwind CSS安定化
  - ページ構成最適化：重複機能削除でユーザビリティ向上
- **June 28, 2025**: デモデータシステム実装完了
  - demo_data.py作成：3人家族（もえ、すずこ、なおひさ）の10日間健康データ生成
  - app.config['USE_DEMO_DATA']フラグでデモ/本番モード切り替え
  - family_demo.htmlテンプレート新規作成（後に不要となり削除）: デモデータ・実データ対応統一表示
  - 各メンバー別に歩数・カロリー・心拍数・HRVの現実的データ範囲生成
  - 5日間のデータテーブル表示とAI健康コメント機能
  - 環境変数USE_DEMO_DATAで本番環境での無効化対応
- **June 26, 2025**: Family Groups functionality implementation
  - Added comprehensive family group system with invite codes for secure family data sharing
  - Enhanced registration process to support creating new groups or joining existing ones
  - Implemented family dashboard showing all members' health data in unified view
  - Added group management features (join, leave, invite code display)
  - Secured data access with group-based permissions ensuring privacy
  - Integrated AI health comments for all family members on shared dashboard
- **June 26, 2025**: Enhanced chart visualization and test user system
  - Implemented dedicated full-screen chart pages with bar charts for better readability
  - Added automatic test user creation (username: user, password: testtest)
  - Integrated statistical analysis (average, max, min, today's values) for each metric
  - Replaced inline charts with navigation to dedicated chart views
  - Improved mobile responsiveness for chart displays
  - Dark theme styling optimized for large chart visualization
- **June 26, 2025**: OpenAI GPT-4o integration for health insights
  - Added AI-powered health commentary generation
  - Integrated with Fitbit daily data (steps, calories, heart rate, HRV)
  - Japanese language health advice using GPT-4o model
  - Displays personalized encouraging comments below health metrics
  - Automated refresh with current-day data on each page load
- **June 26, 2025**: Fitbit OAuth 2.0 integration and database caching system completed
  - Added Fitbit OAuth routes and database fields
  - Implemented complete OAuth flow with proper security
  - Updated UI to show connection status and controls
  - Added requests-oauthlib dependency for OAuth handling
  - Successfully tested OAuth authentication with real Fitbit account
  - Resolved callback URL configuration issues
  - Fixed authentication header encoding for token exchange
  - Implemented FitbitData model for SQLite caching to avoid API rate limits
  - Added 30-minute cache system with automatic data refresh
  - Real Fitbit data retrieval: 11,567 steps, 2,151 calories successfully cached
  - Complete rate limit avoidance with database-backed data persistence
- **June 26, 2025**: Simplified user registration form
  - Removed name, age, and gender fields from registration
  - Username now serves as display name
  - Streamlined to username, email, and password only
- **June 26, 2025**: Initial Flask app setup
  - Session-based authentication system
  - Bootstrap dark theme UI
  - SQLite database with User model
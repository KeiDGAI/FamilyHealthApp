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
  - family_demo.htmlテンプレート新規作成：デモデータ・実データ対応統一表示
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
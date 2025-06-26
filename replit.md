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

- **June 26, 2025**: Fitbit OAuth 2.0 integration completed
  - Added Fitbit OAuth routes and database fields
  - Implemented complete OAuth flow with proper security
  - Updated UI to show connection status and controls
  - Added requests-oauthlib dependency for OAuth handling
  - Successfully tested OAuth authentication with real Fitbit account
  - Resolved callback URL configuration issues
- **June 26, 2025**: Simplified user registration form
  - Removed name, age, and gender fields from registration
  - Username now serves as display name
  - Streamlined to username, email, and password only
- **June 26, 2025**: Initial Flask app setup
  - Session-based authentication system
  - Bootstrap dark theme UI
  - SQLite database with User model
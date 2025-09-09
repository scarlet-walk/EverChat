# EverChat - Social Media Platform

## Overview

EverChat is a social media platform built with Flask that provides Instagram-like functionality including user authentication, photo sharing, messaging, and social interactions. The application features a clean, modern interface with user profiles, post creation with image uploads, likes, comments, and direct messaging capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM for database operations
- **Database**: SQLite for development (configurable to PostgreSQL via DATABASE_URL environment variable)
- **Authentication**: Flask-Login for session management with password hashing using Werkzeug
- **File Handling**: Local file system storage for user-uploaded images with 16MB size limit
- **Security**: ProxyFix middleware for handling reverse proxy headers

### Frontend Architecture
- **Template Engine**: Jinja2 templates with a base template extending pattern
- **Styling**: Bootstrap 5 for responsive design with custom CSS variables
- **Icons**: Font Awesome for consistent iconography
- **JavaScript**: Vanilla JavaScript for interactive features like likes and comments

### Data Model
- **User Model**: Handles authentication, profiles, and relationships to posts/messages
- **Post Model**: Manages user content with image uploads and captions
- **Social Features**: Like and Comment models for user interactions
- **Messaging**: Message model for direct communication between users

### Key Features
- User registration and authentication with secure password hashing
- Image upload and display with file type validation
- Social interactions (likes, comments) with real-time UI updates
- User profiles with post galleries and statistics
- Direct messaging system between users
- Responsive design optimized for mobile and desktop

### File Organization
- **app.py**: Application factory and configuration
- **models.py**: Database models and relationships
- **routes.py**: URL routing and view logic (incomplete in provided code)
- **templates/**: HTML templates with Bootstrap styling
- **static/**: CSS and JavaScript assets
- **uploads/**: Directory for user-uploaded files

## External Dependencies

### Python Packages
- **Flask**: Web framework and core functionality
- **Flask-SQLAlchemy**: Database ORM and management
- **Flask-Login**: User session management
- **Werkzeug**: Security utilities and file handling
- **psycopg2-binary**: PostgreSQL database adapter
- **Gunicorn**: WSGI HTTP server for production deployment
- **OpenAI**: AI integration (referenced in requirements but not implemented)

### Frontend Libraries
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome 6**: Icon library for UI elements

### Infrastructure
- **Database**: SQLite (development) / PostgreSQL (production)
- **File Storage**: Local filesystem with configurable upload directory
- **Session Management**: Flask sessions with configurable secret key

### Environment Configuration
- **SESSION_SECRET**: Security key for session management
- **DATABASE_URL**: Database connection string (defaults to SQLite)
- **Upload Configuration**: File size limits and allowed extensions
#!/bin/zsh
# create_fastapi_project.zsh
# Script to create a FastAPI project structure with appropriate docstrings

# Create base directories
echo "Creating FastAPI project structure..."
mkdir -p fastapi-project/{alembic,src/{auth,gcp,posts},tests/{auth,gcp,posts},templates,requirements}

# Define common docstrings for file types
AUTH_ROUTER_DOCSTRING='"""
Authentication and authorization routes.
Handles user login, registration, password reset, and token management.
"""'

AUTH_SCHEMAS_DOCSTRING='"""
Pydantic models for authentication requests and responses.
Includes schemas for user registration, login, and token validation.
"""'

AUTH_MODELS_DOCSTRING='"""
SQLAlchemy models for authentication-related database tables.
Defines User model and related authentication tables.
"""'

AUTH_DEPENDENCIES_DOCSTRING='"""
Authentication dependency functions for FastAPI.
Provides current_user, optional_user, and admin_user dependencies.
"""'

AUTH_CONFIG_DOCSTRING='"""
Configuration settings specific to authentication.
Includes JWT settings, password policies, and OAuth configurations.
"""'

AUTH_CONSTANTS_DOCSTRING='"""
Constant values used throughout the authentication module.
Defines error messages, token types, and permission levels.
"""'

AUTH_EXCEPTIONS_DOCSTRING='"""
Custom exceptions for authentication-related errors.
Includes AuthenticationError, TokenExpiredError, and PermissionDeniedError.
"""'

AUTH_SERVICE_DOCSTRING='"""
Business logic for authentication processes.
Implements user registration, login, token generation, and password reset flows.
"""'

AUTH_UTILS_DOCSTRING='"""
Utility functions for the authentication module.
Provides password hashing, token encoding/decoding, and verification helpers.
"""'

# GCP docstrings
GCP_CLIENT_DOCSTRING='"""
Google Cloud Platform client implementation.
Provides interfaces for interacting with GCP services like Storage, Pub/Sub, and Cloud Functions.
"""'

GCP_SCHEMAS_DOCSTRING='"""
Pydantic models for GCP service requests and responses.
Defines schemas for Cloud Storage operations, Pub/Sub messages, and service configurations.
"""'

GCP_CONFIG_DOCSTRING='"""
Configuration settings for Google Cloud Platform services.
Includes project IDs, region settings, and service account configurations.
"""'

GCP_CONSTANTS_DOCSTRING='"""
Constants used in GCP service interactions.
Defines bucket names, topic IDs, subscription IDs, and error codes.
"""'

GCP_EXCEPTIONS_DOCSTRING='"""
Custom exceptions for GCP-related errors.
Includes StorageError, PubSubError, and ServiceUnavailableError.
"""'

GCP_UTILS_DOCSTRING='"""
Utility functions for GCP service interactions.
Provides helpers for file uploads, message formatting, and credential management.
"""'

# Posts docstrings
POSTS_ROUTER_DOCSTRING='"""
Routes for post management.
Handles CRUD operations for posts, comments, and related media.
"""'

POSTS_SCHEMAS_DOCSTRING='"""
Pydantic models for post-related requests and responses.
Includes schemas for post creation, updates, comments, and media attachments.
"""'

POSTS_MODELS_DOCSTRING='"""
SQLAlchemy models for post-related database tables.
Defines Post, Comment, and MediaAttachment models.
"""'

POSTS_DEPENDENCIES_DOCSTRING='"""
Dependency functions for post-related routes.
Provides current_post, user_owns_post, and can_comment dependencies.
"""'

POSTS_CONSTANTS_DOCSTRING='"""
Constants used throughout the posts module.
Defines post types, allowed media formats, and visibility settings.
"""'

POSTS_EXCEPTIONS_DOCSTRING='"""
Custom exceptions for post-related errors.
Includes PostNotFoundError, UnauthorizedEditError, and MediaFormatError.
"""'

POSTS_SERVICE_DOCSTRING='"""
Business logic for post management.
Implements post creation, editing, commenting, and media processing flows.
"""'

POSTS_UTILS_DOCSTRING='"""
Utility functions for the posts module.
Provides content sanitization, media processing, and recommendation helpers.
"""'

# Global docstrings
GLOBAL_CONFIG_DOCSTRING='"""
Global application configuration.
Centralizes environment-specific settings and feature flags.
"""'

GLOBAL_MODELS_DOCSTRING='"""
Shared database models used across multiple modules.
Defines BaseModel, TimeStampedModel, and common relationship tables.
"""'

GLOBAL_EXCEPTIONS_DOCSTRING='"""
Global exception handlers and custom exception classes.
Implements exception middleware and standardized error responses.
"""'

PAGINATION_DOCSTRING='"""
Pagination utility for API responses.
Provides consistent pagination behavior across all list endpoints.
"""'

DATABASE_DOCSTRING='"""
Database connection management.
Handles database session creation, migrations, and connection pooling.
"""'

MAIN_DOCSTRING='"""
FastAPI application entry point.
Configures the API, mounts routers, and initializes middleware.
"""'

# Create auth module files
echo "Creating auth module files..."
echo $AUTH_ROUTER_DOCSTRING > fastapi-project/src/auth/router.py
echo $AUTH_SCHEMAS_DOCSTRING > fastapi-project/src/auth/schemas.py
echo $AUTH_MODELS_DOCSTRING > fastapi-project/src/auth/models.py
echo $AUTH_DEPENDENCIES_DOCSTRING > fastapi-project/src/auth/dependencies.py
echo $AUTH_CONFIG_DOCSTRING > fastapi-project/src/auth/config.py
echo $AUTH_CONSTANTS_DOCSTRING > fastapi-project/src/auth/constants.py
echo $AUTH_EXCEPTIONS_DOCSTRING > fastapi-project/src/auth/exceptions.py
echo $AUTH_SERVICE_DOCSTRING > fastapi-project/src/auth/service.py
echo $AUTH_UTILS_DOCSTRING > fastapi-project/src/auth/utils.py

# Create GCP module files
echo "Creating GCP module files..."
echo $GCP_CLIENT_DOCSTRING > fastapi-project/src/gcp/client.py
echo $GCP_SCHEMAS_DOCSTRING > fastapi-project/src/gcp/schemas.py
echo $GCP_CONFIG_DOCSTRING > fastapi-project/src/gcp/config.py
echo $GCP_CONSTANTS_DOCSTRING > fastapi-project/src/gcp/constants.py
echo $GCP_EXCEPTIONS_DOCSTRING > fastapi-project/src/gcp/exceptions.py
echo $GCP_UTILS_DOCSTRING > fastapi-project/src/gcp/utils.py

# Create posts module files
echo "Creating posts module files..."
echo $POSTS_ROUTER_DOCSTRING > fastapi-project/src/posts/router.py
echo $POSTS_SCHEMAS_DOCSTRING > fastapi-project/src/posts/schemas.py
echo $POSTS_MODELS_DOCSTRING > fastapi-project/src/posts/models.py
echo $POSTS_DEPENDENCIES_DOCSTRING > fastapi-project/src/posts/dependencies.py
echo $POSTS_CONSTANTS_DOCSTRING > fastapi-project/src/posts/constants.py
echo $POSTS_EXCEPTIONS_DOCSTRING > fastapi-project/src/posts/exceptions.py
echo $POSTS_SERVICE_DOCSTRING > fastapi-project/src/posts/service.py
echo $POSTS_UTILS_DOCSTRING > fastapi-project/src/posts/utils.py

# Create global files
echo "Creating global files..."
echo $GLOBAL_CONFIG_DOCSTRING > fastapi-project/src/config.py
echo $GLOBAL_MODELS_DOCSTRING > fastapi-project/src/models.py
echo $GLOBAL_EXCEPTIONS_DOCSTRING > fastapi-project/src/exceptions.py
echo $PAGINATION_DOCSTRING > fastapi-project/src/pagination.py
echo $DATABASE_DOCSTRING > fastapi-project/src/database.py
echo $MAIN_DOCSTRING > fastapi-project/src/main.py

# Create other required files
echo "Creating remaining files..."
touch fastapi-project/templates/index.html
echo "# Base requirements for the FastAPI application" > fastapi-project/requirements/base.txt
echo "# Development environment requirements" > fastapi-project/requirements/dev.txt
echo "# Production environment requirements" > fastapi-project/requirements/prod.txt
echo "# Environment variables - DO NOT COMMIT THIS FILE" > fastapi-project/.env
echo "# Git ignore file" > fastapi-project/.gitignore
echo "# Logging configuration" > fastapi-project/logging.ini
echo "# Alembic migration configuration" > fastapi-project/alembic.ini

echo "FastAPI project structure created successfully!"
echo "Run 'chmod +x create_fastapi_project.zsh' to make the script executable"
echo "Then run './create_fastapi_project.zsh' to create the project structure"
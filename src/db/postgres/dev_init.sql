-- Development database initialization script
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create basic schema
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS memory;

-- Create test users table
CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Insert a test user
INSERT INTO auth.users (email, password_hash, first_name, last_name)
VALUES (
    'test@example.com', 
    '$2b$12$1InE4nJwU83EjgP4ftOyOewNcLqHBjQZS3F1Yf7mKs6jh/7WrwVxO', -- password: testpassword
    'Test',
    'User'
);

-- Create basic tables for memory app
CREATE TABLE memory.families (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE TABLE memory.children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    family_id UUID NOT NULL REFERENCES memory.families(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Insert test family and child
INSERT INTO memory.families (id, name, owner_id)
SELECT 
    '11111111-1111-1111-1111-111111111111'::uuid, 
    'Test Family', 
    id 
FROM auth.users WHERE email = 'test@example.com';

INSERT INTO memory.children (name, birth_date, family_id)
VALUES (
    'Test Child',
    '2020-01-01',
    '11111111-1111-1111-1111-111111111111'::uuid
);
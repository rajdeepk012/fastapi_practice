-- chatbot_db Database Schema
-- Created: 2025-11-10
-- Purpose: Store user information and conversation history for FastAPI chatbot

-- Create database
CREATE DATABASE IF NOT EXISTS chatbot_db;
USE chatbot_db;

-- Users table: Stores user account information
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table: Stores chat messages between users and bot
-- Relationship: One user can have many conversations (one-to-many)
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    bot_reply TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Sample data for testing
INSERT INTO users (username, email) VALUES
('ram', 'ram@god.com'),
('alice', 'alice@example.com'),
('bob', 'bob@example.com');

INSERT INTO conversations (user_id, message, bot_reply) VALUES
(1, 'Hello, bot!', 'Hi there! How can I help you?'),
(1, 'What is FastAPI?', 'FastAPI is a modern Python web framework!'),
(2, 'Hey!', 'Hello! Nice to meet you!');

-- Useful queries for reference:

-- Get all conversations with usernames
-- SELECT
--     users.username,
--     conversations.message,
--     conversations.bot_reply,
--     conversations.created_at
-- FROM conversations
-- JOIN users ON conversations.user_id = users.id
-- ORDER BY conversations.created_at DESC;

-- Count conversations per user
-- SELECT
--     users.username,
--     COUNT(conversations.id) as conversation_count
-- FROM users
-- LEFT JOIN conversations ON users.id = conversations.user_id
-- GROUP BY users.id, users.username
-- ORDER BY conversation_count DESC;

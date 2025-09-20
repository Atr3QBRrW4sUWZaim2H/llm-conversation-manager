-- LLM Conversation Manager Database Schema
-- Unified schema for all conversation types

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Main conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    platform TEXT NOT NULL CHECK (platform IN ('chatgpt', 'claude', 'typingmind', 'markdown')),
    create_time TIMESTAMP,
    datemodified TIMESTAMP,
    data JSONB,
    cost FLOAT DEFAULT 0.0,
    model_id TEXT,
    model_name TEXT,
    num_messages INTEGER DEFAULT 0,
    chat_title TEXT,
    preview TEXT,
    synced_at TIMESTAMP,
    file_path TEXT, -- For markdown files
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (title, source, platform)
);

-- Artifacts table (for Claude-specific content and other attachments)
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    artifact_type TEXT NOT NULL, -- 'code', 'markdown', 'image', 'file'
    title TEXT,
    content TEXT,
    file_path TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tags table for conversation categorization
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#007bff',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Many-to-many relationship between conversations and tags
CREATE TABLE conversation_tags (
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (conversation_id, tag_id)
);

-- Indexes for performance
CREATE INDEX idx_conversations_platform ON conversations(platform);
CREATE INDEX idx_conversations_title ON conversations(title);
CREATE INDEX idx_conversations_chat_title ON conversations(chat_title);
CREATE INDEX idx_conversations_create_time ON conversations(create_time);
CREATE INDEX idx_conversations_model_id ON conversations(model_id);
CREATE INDEX idx_conversations_data ON conversations USING GIN(data);
CREATE INDEX idx_conversations_title_trgm ON conversations USING GIN(title gin_trgm_ops);
CREATE INDEX idx_conversations_chat_title_trgm ON conversations USING GIN(chat_title gin_trgm_ops);

CREATE INDEX idx_artifacts_conversation_id ON artifacts(conversation_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX idx_artifacts_metadata ON artifacts USING GIN(metadata);

CREATE INDEX idx_conversation_tags_conversation_id ON conversation_tags(conversation_id);
CREATE INDEX idx_conversation_tags_tag_id ON conversation_tags(tag_id);

-- Full-text search indexes
CREATE INDEX idx_conversations_data_fts ON conversations USING GIN(to_tsvector('english', data::text));
CREATE INDEX idx_conversations_title_fts ON conversations USING GIN(to_tsvector('english', title));
CREATE INDEX idx_conversations_chat_title_fts ON conversations USING GIN(to_tsvector('english', chat_title));

-- Functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_artifacts_updated_at 
    BEFORE UPDATE ON artifacts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for conversation summary with statistics
CREATE VIEW conversation_summary AS
SELECT 
    platform,
    COUNT(*) as total_conversations,
    SUM(num_messages) as total_messages,
    SUM(cost) as total_cost,
    AVG(cost) as avg_cost,
    MIN(create_time) as earliest_conversation,
    MAX(create_time) as latest_conversation,
    COUNT(DISTINCT model_id) as unique_models
FROM conversations 
GROUP BY platform;

-- View for recent conversations
CREATE VIEW recent_conversations AS
SELECT 
    c.*,
    array_agg(t.name) as tags
FROM conversations c
LEFT JOIN conversation_tags ct ON c.id = ct.conversation_id
LEFT JOIN tags t ON ct.tag_id = t.id
WHERE c.create_time >= NOW() - INTERVAL '30 days'
GROUP BY c.id
ORDER BY c.create_time DESC;

-- Function to search conversations
CREATE OR REPLACE FUNCTION search_conversations(
    search_query TEXT DEFAULT '',
    platform_filter TEXT DEFAULT NULL,
    model_filter TEXT DEFAULT NULL,
    limit_count INTEGER DEFAULT 50,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id INTEGER,
    title TEXT,
    platform TEXT,
    model_name TEXT,
    num_messages INTEGER,
    create_time TIMESTAMP,
    preview TEXT,
    similarity REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.title,
        c.platform,
        c.model_name,
        c.num_messages,
        c.create_time,
        c.preview,
        CASE 
            WHEN search_query = '' THEN 1.0
            ELSE ts_rank(
                to_tsvector('english', c.title || ' ' || c.chat_title || ' ' || c.data::text),
                plainto_tsquery('english', search_query)
            )
        END as similarity
    FROM conversations c
    WHERE 
        (search_query = '' OR to_tsvector('english', c.title || ' ' || c.chat_title || ' ' || c.data::text) @@ plainto_tsquery('english', search_query))
        AND (platform_filter IS NULL OR c.platform = platform_filter)
        AND (model_filter IS NULL OR c.model_id = model_filter)
    ORDER BY 
        CASE WHEN search_query = '' THEN c.create_time END DESC,
        CASE WHEN search_query != '' THEN similarity END DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get conversation thread
CREATE OR REPLACE FUNCTION get_conversation_thread(conversation_uuid TEXT)
RETURNS TABLE (
    id INTEGER,
    title TEXT,
    platform TEXT,
    data JSONB,
    artifacts JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.title,
        c.platform,
        c.data,
        COALESCE(
            json_agg(
                json_build_object(
                    'id', a.id,
                    'type', a.artifact_type,
                    'title', a.title,
                    'content', a.content,
                    'metadata', a.metadata
                )
            ) FILTER (WHERE a.id IS NOT NULL),
            '[]'::json
        ) as artifacts
    FROM conversations c
    LEFT JOIN artifacts a ON c.id = a.conversation_id
    WHERE c.source = conversation_uuid
    GROUP BY c.id, c.title, c.platform, c.data;
END;
$$ LANGUAGE plpgsql;

-- Insert some default tags
INSERT INTO tags (name, description, color) VALUES
('Technical', 'Technical discussions and programming', '#007bff'),
('Creative', 'Creative writing and brainstorming', '#28a745'),
('Research', 'Research and analysis', '#ffc107'),
('Personal', 'Personal conversations', '#6f42c1'),
('Work', 'Work-related discussions', '#fd7e14'),
('Learning', 'Educational content', '#20c997'),
('Troubleshooting', 'Problem-solving and debugging', '#dc3545'),
('Planning', 'Project planning and strategy', '#6c757d');

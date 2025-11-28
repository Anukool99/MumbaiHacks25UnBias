-- Create articles table in Supabase
CREATE TABLE IF NOT EXISTS articles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on created_at for faster queries
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);

-- Enable Row Level Security (RLS) - adjust policies as needed
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Policy to allow all operations (adjust based on your security requirements)
-- For development/testing, you might want to allow all operations
CREATE POLICY "Allow all operations on articles" ON articles
    FOR ALL
    USING (true)
    WITH CHECK (true);


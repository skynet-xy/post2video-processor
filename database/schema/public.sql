/**
 * table: job_add_reddit_comment_overlay
 * columns: id, job_code (unique), status, video_name, output_path, comment_ids (json list), comments (json list), error_message, created_at, updated_at
 */
CREATE TABLE job_add_reddit_comment_overlay (
    id SERIAL PRIMARY KEY,
    job_code VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    video_name VARCHAR(255) NOT NULL,
    output_path VARCHAR(255),
    voice_id VARCHAR(255),
    language VARCHAR(255),
    video_length VARCHAR(255),
    ratio VARCHAR(255),
    theme VARCHAR(255),
    post_title VARCHAR(255),
    comments JSONB NOT NULL DEFAULT '[]',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- Add triggers to update the updated_at column
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_job_timestamp
BEFORE UPDATE ON job_add_reddit_comment_overlay
FOR EACH ROW EXECUTE FUNCTION update_timestamp();
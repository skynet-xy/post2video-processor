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
-- Create dev schema
CREATE SCHEMA IF NOT EXISTS atlas_dev;

-- Grant permissions to the app user
GRANT ALL ON SCHEMA atlas_dev TO app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA atlas_dev TO app;
ALTER DEFAULT PRIVILEGES IN SCHEMA atlas_dev GRANT ALL ON TABLES TO app;
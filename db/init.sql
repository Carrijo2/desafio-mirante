CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS modernization_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_code TEXT NOT NULL,
    generated_code TEXT,
    report JSONB NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('sucesso', 'falha', 'parcial')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_modernization_history_status
    ON modernization_history(status);

CREATE INDEX IF NOT EXISTS idx_modernization_history_created_at
    ON modernization_history(created_at);


CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    note TEXT NOT NULL,
    creation_date DATE NOT NULL
);

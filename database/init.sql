CREATE TABLE IF NOT EXISTS items (
    id integer PRIMARY KEY,
    title text NOT NULL,
    done boolean NOT NULL DEFAULT false
);

INSERT INTO items (id, title, done) VALUES
    (1, 'Check service readiness', false),
    (2, 'Review deployment logs', false),
    (3, 'Document the operating procedure', false)
ON CONFLICT (id) DO NOTHING;

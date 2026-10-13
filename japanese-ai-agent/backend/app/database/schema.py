SCHEMA = """
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    reading TEXT NOT NULL,
    romaji TEXT,
    jlpt_level TEXT NOT NULL,
    pos TEXT,
    topic TEXT,
    example_jp TEXT
);

CREATE TABLE IF NOT EXISTS kanji (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character TEXT NOT NULL UNIQUE,
    onyomi TEXT,
    kunyomi TEXT,
    jlpt_level TEXT NOT NULL,
    stroke_count INTEGER,
    example_words TEXT
);

CREATE TABLE IF NOT EXISTS grammar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL UNIQUE,
    jlpt_level TEXT NOT NULL,
    formation TEXT,
    example_jp TEXT,
    example_reading TEXT
);

CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity TEXT NOT NULL CHECK (entity IN ('vocabulary', 'kanji', 'grammar')),
    entity_id INTEGER NOT NULL,
    field TEXT NOT NULL CHECK (field IN ('meaning', 'example')),
    lang TEXT NOT NULL,
    text TEXT NOT NULL,
    UNIQUE (entity, entity_id, field, lang)
);

CREATE INDEX IF NOT EXISTS idx_vocab_level ON vocabulary(jlpt_level);
CREATE INDEX IF NOT EXISTS idx_vocab_topic ON vocabulary(topic);
CREATE INDEX IF NOT EXISTS idx_trans_lookup ON translations(entity, entity_id, lang);
"""
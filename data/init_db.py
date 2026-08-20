import sqlite3

conn = sqlite3.connect("data/company_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS company_funding (
    company_name TEXT PRIMARY KEY,
    founded_year INTEGER,
    headquarters TEXT,
    total_funding_usd_millions REAL,
    valuation_usd_millions REAL,
    last_funding_round TEXT,
    notes TEXT,
    last_updated TEXT
)
""")

companies = [
    ('anthropic', 2021, 'San Francisco, CA, USA', 105000, 965000,
     'Series H (5B, May 2026)', 'Valuation is post-money', '2026-08-19'),
    ('google_deepmind', 2010, 'London, United Kingdom', None, None,
     'Corporate Acquisition (2014)', 'Acquired by Google/Alphabet ~50M in 2014; now internal division', '2026-08-19'),
    ('groq', 2016, 'Mountain View, CA, USA', 1650, 3500,
     'Growth Round (50M, Aug 2026)', 'Valuation reset after Nvidia licensing deal (Dec 2025)', '2026-08-19'),
    ('huggingface', 2016, 'New York, NY, USA', 400, 4500,
     'Series D (35M, Aug 2023)', None, '2026-08-19'),
    ('meta_ai', 2013, 'Menlo Park, CA, USA', None, None,
     'Internal Corporate R&D allocation', 'Internal division of Meta Platforms', '2026-08-19'),
    ('mistral', 2023, 'Paris, France', 3500, 16500,
     'Series C / Infrastructure Raise (€3B, mid-2026)', 'Valuation range €13B-€20B depending on source', '2026-08-19'),
    ('openai', 2015, 'San Francisco, CA, USA', 180000, 852000,
     'Growth Round (22B, March 2026)', 'Valuation is post-money', '2026-08-19'),
]

cursor.executemany("""
INSERT OR REPLACE INTO company_funding VALUES (?,?,?,?,?,?,?,?)
""", companies)

conn.commit()
conn.close()
print("Database created and populated successfully.")

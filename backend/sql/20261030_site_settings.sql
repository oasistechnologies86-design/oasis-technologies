-- Apply once to the production Supabase PostgreSQL database before deploying this release.
-- This table stores editable public contact details and homepage copy.
CREATE TABLE IF NOT EXISTS site_settings (
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    company_name VARCHAR(120) NOT NULL DEFAULT 'Oasis Technologies',
    contact_email VARCHAR(254) NOT NULL DEFAULT 'oasistechnologies86@gmail.com',
    phone_primary VARCHAR(40) NOT NULL DEFAULT '0246470941',
    phone_secondary VARCHAR(40) NOT NULL DEFAULT '0201491597',
    tagline VARCHAR(240) NOT NULL DEFAULT 'Thoughtful technology. Real-world impact.',
    hero_title VARCHAR(120) NOT NULL DEFAULT 'Build what''s next.',
    hero_accent VARCHAR(120) NOT NULL DEFAULT 'Make it matter.',
    hero_description TEXT NOT NULL DEFAULT 'We build useful digital products and deliver dependable IT services that help ambitious businesses move forward.'
);
INSERT INTO site_settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING;

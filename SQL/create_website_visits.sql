CREATE TABLE website_visits (
    id BIGSERIAL PRIMARY KEY,
    site_key VARCHAR(100) NOT NULL,
    visitor_id UUID NOT NULL,
    page_path VARCHAR(2048) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    referer TEXT,
    visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_website_visits_site_time
ON website_visits (site_key, visited_at DESC);

CREATE INDEX idx_website_visits_site_visitor
ON website_visits (site_key, visitor_id);
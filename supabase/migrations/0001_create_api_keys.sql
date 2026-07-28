-- Requires the pgcrypto extension for gen_random_uuid(). Supabase enables
-- this by default; if applied to a bare Postgres instance, run first:
--   create extension if not exists pgcrypto;

create table if not exists api_keys (
    id uuid primary key default gen_random_uuid(),
    owner_label text not null,
    hashed_key text not null,
    created_at timestamptz not null default now(),
    revoked_at timestamptz
);

create unique index if not exists ix_api_keys_hashed_key on api_keys (hashed_key);

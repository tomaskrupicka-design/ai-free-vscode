-- Football Radar V1: aktualni soukroma schema Supabase
-- Nasazeno do projektu jtnreiebhujzyspumxwf, region eu-central-1.
-- Spusteni znovu je idempotentni; uzivatelem spravovane tabulky neodstranuje.
create table if not exists public.matches (
  id bigint generated always as identity primary key,
  source_match_key text not null unique,
  match_date date not null,
  kickoff_at timestamptz,
  home_team text not null,
  away_team text not null,
  home_goals integer check (home_goals is null or home_goals >= 0),
  away_goals integer check (away_goals is null or away_goals >= 0),
  source text not null,
  season text,
  data_available_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists idx_football_matches_date on public.matches(match_date);

create table if not exists public.predictions (
  id bigint generated always as identity primary key,
  match_id bigint not null references public.matches(id) on delete cascade,
  model_version text not null,
  prediction_kind text not null default 'retrospective_backtest',
  predicted_at timestamptz not null default now(),
  home_xg double precision,
  away_xg double precision,
  p_home double precision not null check (p_home between 0 and 1),
  p_draw double precision not null check (p_draw between 0 and 1),
  p_away double precision not null check (p_away between 0 and 1),
  actual_outcome text check (actual_outcome in ('home','draw','away')),
  brier double precision,
  log_loss double precision,
  constraint football_prediction_unique unique (match_id,model_version,prediction_kind),
  constraint football_probability_sum check (p_home+p_draw+p_away between 0.999 and 1.001)
);
create index if not exists idx_football_predictions_match on public.predictions(match_id);

alter table public.matches enable row level security;
alter table public.predictions enable row level security;
-- Zadne anon/authenticated policy: data jsou pouze pro backend.
revoke all on table public.matches from anon, authenticated;
revoke all on table public.predictions from anon, authenticated;
revoke all on sequence public.matches_id_seq from anon, authenticated;
revoke all on sequence public.predictions_id_seq from anon, authenticated;
grant select, insert, update, delete on public.matches to service_role;
grant select, insert, update, delete on public.predictions to service_role;
grant usage, select on sequence public.matches_id_seq to service_role;
grant usage, select on sequence public.predictions_id_seq to service_role;

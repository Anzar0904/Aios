# Supabase Schema Report

## Tables
- **Table:** `users`
  - `id`: uuid
  - `email`: text
  - `created_at`: timestamptz

- **Table:** `orders`
  - `id`: int8
  - `user_id`: uuid
  - `total`: numeric



## Views
active_orders
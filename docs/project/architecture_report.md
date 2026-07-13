# Architecture Report

## Service Map
{
  "web-gateway": [
    "auth-service",
    "data-service"
  ],
  "auth-service": [
    "database-postgres"
  ],
  "data-service": [
    "database-postgres",
    "redis-cache"
  ]
}

## Module Map
{
  "core": [
    "kernel",
    "cli",
    "registry"
  ],
  "services": [
    "supabase",
    "vercel",
    "n8n"
  ]
}
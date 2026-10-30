# Security status and launch checklist

- Keep backend database credentials in Render environment settings.
- VITE_API_BASE_URL is public configuration and must never contain secrets.
- Restrict CORS_ORIGINS to the actual deployed frontend origin.
- Admin enquiries endpoint currently returns HTTP 501 and does not return customer records.
- Before launch, implement tested authentication, server-side role authorization, rate limiting, spam protection, safe file upload handling if added, data retention, backups, and reviewed database migrations.
- Do not collect passwords or unnecessary sensitive information in public forms.
- Review privacy and legal pages before accepting real customer submissions.

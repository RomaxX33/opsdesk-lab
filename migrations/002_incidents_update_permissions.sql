BEGIN;

GRANT UPDATE (title, description, status, priority)
ON TABLE public.incidents
TO opsdesk_runtime;

REVOKE UPDATE (updated_at, resolved_at)
ON TABLE public.incidents
FROM opsdesk_runtime;

COMMIT;

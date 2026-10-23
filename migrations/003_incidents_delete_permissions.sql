BEGIN;

GRANT DELETE
ON TABLE public.incidents
TO opsdesk_runtime;

COMMIT;
CREATE ROLE opsdesk_runtime
    LOGIN
    PASSWORD 'opsdesk-test-runtime-local-only'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;

GRANT CONNECT ON DATABASE opsdesk_test TO opsdesk_runtime;

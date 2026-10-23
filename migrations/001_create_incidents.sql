BEGIN;

CREATE TABLE public.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    title VARCHAR(160) NOT NULL,
    description TEXT NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'open',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,

    CONSTRAINT incidents_title_length
        CHECK (char_length(btrim(title)) BETWEEN 5 AND 160),

    CONSTRAINT incidents_description_length
        CHECK (char_length(btrim(description)) BETWEEN 10 AND 5000),

    CONSTRAINT incidents_status_allowed
        CHECK (status IN (
            'open',
            'in_progress',
            'waiting',
            'resolved',
            'closed'
        )),

    CONSTRAINT incidents_priority_allowed
        CHECK (priority IN (
            'low',
            'medium',
            'high',
            'critical'
        ))
);

CREATE OR REPLACE FUNCTION public.set_incident_timestamps()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at := CURRENT_TIMESTAMP;
        NEW.updated_at := CURRENT_TIMESTAMP;

        IF NEW.status IN ('resolved', 'closed') THEN
            NEW.resolved_at := COALESCE(
                NEW.resolved_at,
                CURRENT_TIMESTAMP
            );
        ELSE
            NEW.resolved_at := NULL;
        END IF;
    ELSE
        NEW.created_at := OLD.created_at;
        NEW.updated_at := CURRENT_TIMESTAMP;

        IF NEW.status IN ('resolved', 'closed') THEN
            IF OLD.status NOT IN ('resolved', 'closed')
               OR NEW.resolved_at IS NULL THEN
                NEW.resolved_at := CURRENT_TIMESTAMP;
            END IF;
        ELSE
            NEW.resolved_at := NULL;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER incidents_set_timestamps
BEFORE INSERT OR UPDATE ON public.incidents
FOR EACH ROW
EXECUTE FUNCTION public.set_incident_timestamps();

REVOKE ALL ON TABLE public.incidents FROM PUBLIC;
GRANT SELECT, INSERT ON TABLE public.incidents TO opsdesk_runtime;

COMMIT;
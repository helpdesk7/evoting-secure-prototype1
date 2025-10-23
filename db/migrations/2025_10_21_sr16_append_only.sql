-- Forbid UPDATE/DELETE on ballot_chain (append-only)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'forbid_ud_ballot_chain') THEN
    CREATE OR REPLACE FUNCTION forbid_ud_ballot_chain()
    RETURNS trigger AS $BODY$
    BEGIN
      RAISE EXCEPTION 'ballot_chain is append-only; % not allowed', TG_OP;
    END;
    $BODY$ LANGUAGE plpgsql;
  END IF;
END$$;

DROP TRIGGER IF EXISTS ballot_chain_no_update ON ballot_chain;
CREATE TRIGGER ballot_chain_no_update
BEFORE UPDATE ON ballot_chain
FOR EACH ROW EXECUTE FUNCTION forbid_ud_ballot_chain();

DROP TRIGGER IF EXISTS ballot_chain_no_delete ON ballot_chain;
CREATE TRIGGER ballot_chain_no_delete
BEFORE DELETE ON ballot_chain
FOR EACH ROW EXECUTE FUNCTION forbid_ud_ballot_chain();
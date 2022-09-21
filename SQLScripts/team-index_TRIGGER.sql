CREATE or replace FUNCTION UPDATE_TIP() RETURNS trigger AS
$$
BEGIN
  UPDATE Business
  SET numTips = numTips+1 
        WHERE business_id = NEW.business_id;
  UPDATE Users
  SET tipCount = tipCount+1 
        WHERE business_id = NEW.business_id;

  RETURN NEW;
END;
$$
LANGUAGE plpgsql;


CREATE TRIGGER UPDATE_NUMTIPS
AFTER INSERT ON Tip
FOR EACH ROW
BEGIN
  EXECUTE PROCEDURE update_business();
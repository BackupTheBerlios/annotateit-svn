ALTER TABLE ObjectDescription ADD COLUMN OwnerID int unsigned default NULL;
ALTER TABLE EvalVectorDesc DROP COLUMN Title;
ALTER TABLE ObjectMap ADD COLUMN OwnerID int unsigned default NULL;


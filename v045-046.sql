CREATE TABLE Rubric (ID bigint unsigned not null primary key, Type varchar(9));
ALTER TABLE Evaluation DROP PRIMARY KEY
ALTER TABLE Evaluation MODIFY COLUMN Weight int not null;
ALTER TABLE Evaluation MODIFY COLUMN Value int not null;
ALTER TABLE Evaluation ADD PRIMARY KEY (ObjectID,EvalVectorID,Value,OwnerID,Weight);
-- Copyright 2003, Buzzmaven Co.
-- This file is part of Annotateit.

-- Annotateit is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.

-- Annotateit is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.

-- You should have received a copy of the GNU General Public License
-- along with Annotateit (see GNU-GPL.txt); if not, write to the Free Software
-- Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.
-- The GNU General Public License may also be found on the Web at:
--   http://www.gnu.org/licenses/gpl.txt

--
---- MySQL dump 8.23
--
-- Host: localhost    Database: annotateit_com
---------------------------------------------------------
-- Server version	3.23.58

--
-- Table structure for table `AnnotationRequest`
--

DROP TABLE IF EXISTS AnnotationRequest;
CREATE TABLE AnnotationRequest (
  ID bigint(20) unsigned NOT NULL auto_increment,
  RemoteAddress varchar(30) default NULL,
  RequestURI varchar(255) default NULL,
  RequestURIDirectory varchar(255) default NULL,
  Timestamp timestamp(14) NOT NULL,
  PRIMARY KEY  (ID)
) TYPE=MyISAM;
ALTER TABLE ObjectMap ADD COLUMN VectorWeight int;
ALTER TABLE Evaluation ADD COLUMN Weight int;
ALTER TABLE ObjectDescription ADD COLUMN OwnerID int unsigned default NULL;
ALTER TABLE EvalVectorDesc DROP COLUMN Title;
ALTER TABLE ObjectMap ADD COLUMN OwnerID int unsigned default NULL;
CREATE TABLE Rubric (ID bigint unsigned not null primary key, Type varchar(9));
ALTER TABLE Evaluation DROP PRIMARY KEY
ALTER TABLE Evaluation MODIFY COLUMN Weight int not null;
ALTER TABLE Evaluation MODIFY COLUMN Value int not null;
ALTER TABLE Evaluation ADD PRIMARY KEY (ObjectID,EvalVectorID,Value,OwnerID,Weight);
ALTER TABLE Assignment ADD COLUMN Weight int;


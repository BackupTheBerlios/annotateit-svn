-- MySQL dump 9.07
--
-- Host: localhost    Database: annie
---------------------------------------------------------
-- Server version	4.0.4-beta

--
-- Table structure for table 'EvalVectorDocumentMap'
--

DROP TABLE IF EXISTS EvalVectorDocumentMap;
CREATE TABLE EvalVectorDocumentMap (
  DocumentID int(10) unsigned NOT NULL default '0',
  EvalVectorID int(10) unsigned NOT NULL default '0',
  EvaluatorID int(10) unsigned NOT NULL default '0',
  Value int(11) default NULL,
  PRIMARY KEY  (DocumentID,EvalVectorID,EvaluatorID)
) TYPE=MyISAM;


-- Add a DjangoCMS tab for an extra survey
DELETE FROM "cms_page" WHERE id = 9;
INSERT INTO "cms_page" VALUES(9,1,NULL,1,'bon','bon',NULL,
       '2011-01-22 15:23:58.389420',NULL,NULL,0,0,NULL,'',0,
       'cms/base_1col.html',1,0,0,1,2,7,0,0);
DELETE FROM "cms_title" WHERE id = 9;
INSERT INTO "cms_title" VALUES(9,1,NULL,1,'en','extra-survey',NULL,
       'extra-survey','extra-survey',0,NULL,NULL,NULL,NULL,NULL,9,
       '2011-01-22 15:23:58.412401');

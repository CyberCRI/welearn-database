-- Show a sample of DOI
SELECT wd.details->> 'doi' AS "VIRTUAL DOI", * FROM document_related.welearn_document wd WHERE wd.details ->> 'doi' IS NOT NULL LIMIT 10

-- Count the quantity of DOI (Very long query)
SELECT COUNT(1) FROM document_related.welearn_document wd WHERE wd.details ->> 'doi' IS NOT NULL


SELECT details ->> 'doi' FROM document_related.welearn_document wd LIMIT 1

SELECT * FROM alembic_version av -- b049924f7067

-- Update only one row
UPDATE
	document_related.welearn_document
SET
	doi = (details ->> 'doi')
WHERE
	id = 'efb2c5d7-4ceb-4022-8fa2-60eac50057b4'
	AND
	EXISTS (
	SELECT
		1
	FROM
		alembic_version
	WHERE
		version_num = 'f1ce0ad2845b')

-- Show this row
SELECT
	*
FROM
	document_related.welearn_document wd
WHERE
	id = 'efb2c5d7-4ceb-4022-8fa2-60eac50057b4'
	
	
-- Update all
UPDATE
	document_related.welearn_document
SET
	doi = (details ->> 'doi')
WHERE
	EXISTS (
	SELECT
		1
	FROM
		alembic_version
	WHERE
		version_num = 'f1ce0ad2845b')
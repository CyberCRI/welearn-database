WITH batch AS (
SELECT
	id
FROM
	document_related.welearn_document
WHERE
	details ->> 'doi' IS NOT NULL
	AND doi IS DISTINCT
FROM
	(details ->> 'doi')
	AND details ->> 'doi' IS DISTINCT
FROM
	''
	AND EXISTS (
	SELECT
		1
	FROM
		alembic_version
	WHERE
		version_num = 'f1ce0ad2845b'
      )
ORDER BY
	id
LIMIT %(batch_size)s
)
UPDATE
	document_related.welearn_document wd
SET
	doi = (details ->> 'doi')
FROM
	batch
WHERE
	wd.id = batch.id
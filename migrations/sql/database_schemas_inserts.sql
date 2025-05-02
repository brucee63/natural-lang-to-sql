INSERT INTO database_schemas 
(database_id, schema_name, description, embedding, include_in_context, extra_metadata, id, created_at, updated_at) 
VALUES
(
    (select id from databases where name = 'student_transcripts_tracking' limit 1),
'public', 'public default schema', NULL, TRUE, NULL, uuid_generate_v4(), NOW(), NULL
);

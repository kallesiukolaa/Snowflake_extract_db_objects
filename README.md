# Snowflake_extract_db_objects

This python-script can be used for extracting objects from Snowflake database DDL to separate sql scripts. You can retrieve database script using Snowflake's get_ddl-command. https://docs.snowflake.com/en/sql-reference/functions/get_ddl.html

Please note that you must set use_fully_qualified_names_for_recreated_objects as true.

Example query

select get_ddl('database', 'mytestdb', true);

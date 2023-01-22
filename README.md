# Snowflake_extract_db_objects

This python-script can be used for extracting objects from Snowflake database DDL to separate sql scripts. You can retrieve database script using Snowflake's get_ddl-command. https://docs.snowflake.com/en/sql-reference/functions/get_ddl.html

Please note that you must set use_fully_qualified_names_for_recreated_objects as true.

Example query

select get_ddl('database', 'mytestdb', true);

You need to build this as wheel package

https://github.com/kallesiukolaa/Snowflake_extract_db_objects.git

cd Snowflake_extract_db_objects

python -m pip install -U pip setuptools wheel build

python -m build --wheel .


Find the Snowflake_ddl_handler-1.0.0-py3-none-any.whl package in the ./dist directory.


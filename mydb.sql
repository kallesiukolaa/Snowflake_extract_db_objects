create or replace database mytestdb;

create or replace schema mytestdb.mySchema;

create or replace table mytestdb.mySchema.collation_demo (
  uncollated_phrase varchar, 
  utf8_phrase varchar collate 'utf8',
  english_phrase varchar collate 'en',
  spanish_phrase varchar collate 'sp'
  );

create or replace table mytestdb.mySchema."collati;on_demo1" (
  uncollated_phrase varchar, 
  utf8_phrase varchar collate 'utf8',
  english_phrase varchar collate 'en',
  "spanish_phr;ase" varchar collate 'sp'
  );

create or replace procedure mytestdb.mySchema.find_invoice_by_id(id varchar)
returns table (id integer, price number(12,2))
language sql
as
'
declare
  res resultset default (select * from invoices where id = :id);
begin
  return table(res);
end;
'
;
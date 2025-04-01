create or replace view fg.my_second_dbt_model
  
  
  as
    -- Use the `ref` function to select from other models

select *
from fg.my_first_dbt_model
where id = 1

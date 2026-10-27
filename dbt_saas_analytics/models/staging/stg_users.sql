with source as (
    select * from {{ source('bronze', 'RAW_USERS') }}
),

parsed as (
    select
        raw_payload:user_id::string as user_id,
        trim(raw_payload:company_name::string) as company_name,
        trim(raw_payload:industry::string) as industry,
        lower(trim(raw_payload:contact_email::string)) as email,
        upper(trim(raw_payload:country::string)) as country,
        raw_payload:created_at::timestamp_ntz as created_at,
        ingested_at
    from source
)

select *
from parsed
qualify row_number() over (partition by user_id order by ingested_at desc) = 1
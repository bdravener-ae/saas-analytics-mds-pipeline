with source as (
    select * from {{ source('bronze', 'RAW_SUBSCRIPTIONS') }}
),

parsed as (
    select
        raw_payload:subscription_id::string as subscription_id,
        raw_payload:user_id::string as user_id,
        trim(raw_payload:plan_tier::string) as plan_name,
        raw_payload:monthly_recurring_revenue::numeric(10,2) as monthly_price,
        lower(trim(raw_payload:status::string)) as status,
        raw_payload:start_date::timestamp_ntz as start_date,
        raw_payload:end_date::timestamp_ntz as end_date,
        ingested_at
    from source
)

select *
from parsed
qualify row_number() over (partition by subscription_id order by ingested_at desc) = 1
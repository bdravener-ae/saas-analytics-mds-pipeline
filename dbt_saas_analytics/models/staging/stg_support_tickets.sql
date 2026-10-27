with source as (
    select * from {{ source('bronze', 'RAW_SUPPORT_TICKETS') }}
),

parsed as (
    select
        raw_payload:ticket_id::string as ticket_id,
        raw_payload:user_id::string as user_id,
        trim(raw_payload:ticket_text::string) as ticket_text,
        lower(trim(raw_payload:priority::string)) as priority,
        lower(trim(raw_payload:resolution_status::string)) as status,
        raw_payload:created_at::timestamp_ntz as created_at,
        ingested_at
    from source
),

deduped as (
    select *
    from parsed
    qualify row_number() over (partition by ticket_id order by ingested_at desc) = 1
)

select
    *,
    status in ('open', 'pending') as is_open,
    ticket_text ilike '%cancel%' as mentions_cancellation
from deduped
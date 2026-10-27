with source as (
    select * from {{ source('bronze', 'RAW_PAYMENTS') }}
),

renamed as (
    select
        raw_payload:payment_id::string as payment_id,
        raw_payload:user_id::string as user_id,
        raw_payload:subscription_id::string as subscription_id,
        raw_payload:amount::numeric(10,2) as amount,
        raw_payload:payment_status::string as payment_status,
        raw_payload:payment_date::timestamp_ntz as payment_date,
        ingested_at
    from source
)

select * from renamed

with tickets as (
    select * from {{ ref('stg_support_tickets') }}
),

users as (
    select * from {{ ref('stg_users') }}
),

with_sla as (
    select
        t.ticket_id,
        t.user_id,
        u.company_name,
        t.priority,
        t.status,
        t.is_open,
        t.mentions_cancellation,
        t.created_at,
        case t.priority
            when 'urgent' then 1
            when 'high'   then 3
            when 'medium' then 5
            when 'low'    then 10
        end as sla_target_days,
        case when t.is_open
            then datediff('day', t.created_at, current_timestamp())
        end as days_open
    from tickets t
    left join users u on t.user_id = u.user_id
)

select
    *,
    coalesce(is_open and days_open > sla_target_days, false) as is_sla_breached
from with_sla
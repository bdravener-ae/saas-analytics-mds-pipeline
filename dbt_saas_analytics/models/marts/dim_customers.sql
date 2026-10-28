with users as (
    select * from {{ ref('stg_users') }}
),

subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

sub_summary as (
    select
        user_id,
        count(*) as total_subscriptions,
        count_if(status = 'active') > 0 as has_active_subscription
    from subscriptions
    group by user_id
)

select
    u.user_id,
    u.company_name,
    u.industry,
    u.country,
    u.created_at as customer_since,
    coalesce(s.total_subscriptions, 0) as total_subscriptions,
    coalesce(s.has_active_subscription, false) as has_active_subscription
from users u
left join sub_summary s on u.user_id = s.user_id
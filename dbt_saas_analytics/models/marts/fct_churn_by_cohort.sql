with subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
)

select
    date_trunc('month', start_date) as cohort_month,
    plan_name,
    count(*) as total_subscriptions,
    count_if(status = 'canceled') as churned_subscriptions,
    round(div0(count_if(status = 'canceled'), count(*)), 3) as churn_rate
from subscriptions
group by 1, 2
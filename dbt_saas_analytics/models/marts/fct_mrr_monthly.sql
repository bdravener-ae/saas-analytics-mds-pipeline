   with subscriptions as (
       select * from {{ ref('stg_subscriptions') }}
   ),

   users as (
       select * from {{ ref('stg_users') }}
   ),

   mrr_calc as (
       select
           s.subscription_id,
           s.user_id,
           s.plan_name,
           u.country,
           s.status,
           case when s.status = 'active' then s.monthly_price else 0 end as mrr_amount,
           date_trunc('month', s.start_date) as mrr_month
       from subscriptions s
       left join users u on s.user_id = u.user_id
   )

   select * from mrr_calc
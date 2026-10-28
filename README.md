# B2B SaaS Analytics Pipeline

Portfolio project built to get hands-on with dbt and Snowflake. Mock B2B SaaS data (users, subscriptions, payments, support tickets) is generated in Python with Faker, loaded into Snowflake, and modeled with dbt using a Bronze / Silver / Gold structure.

## Structure

- **Bronze**: raw JSON loaded into Snowflake, left unchanged.
- **Silver**: dbt staging models that parse the JSON into typed columns, standardize values, dedupe on the primary key, and run tests.
- **Gold**: business-ready marts:
  - `fct_mrr_monthly`: monthly recurring revenue by plan, country, and month. Only active subscriptions are counted.
  - `fct_churn_by_cohort`: cancellation rate by plan and signup month.
  - `fct_support_sla`: open ticket aging against SLA targets by priority, with a flag for tickets that mention canceling.
  - `dim_customers`: one row per customer with company, industry, country, and subscription status. Shared dimension the fact tables join to on `user_id`.

## Testing

16 dbt tests cover unique and not-null keys, relationships back to the users table, and accepted values on status and priority fields.

## Data quality issues found

- Source field names didn't match the original staging models. Remapped in Silver, so the Gold models didn't need to change.
- 5 support tickets reference users that don't exist. Kept them and set the test to warn rather than fail, so the pipeline runs and the issue stays visible.

## Project structure

```
dbt_saas_analytics/
├── macros/
│   └── generate_schema_name.sql   # routes models to exact schemas (SILVER, GOLD)
├── models/
│   ├── staging/                   # Silver
│   │   ├── src_bronze.yml         # Bronze source definitions
│   │   ├── schema.yml             # tests + documentation
│   │   ├── stg_users.sql
│   │   ├── stg_subscriptions.sql
│   │   ├── stg_payments.sql
│   │   └── stg_support_tickets.sql
│   └── marts/                     # Gold
│       ├── dim_customers.sql
│       ├── fct_mrr_monthly.sql
│       ├── fct_churn_by_cohort.sql
│       └── fct_support_sla.sql
└── dbt_project.yml                # staging → views in SILVER, marts → tables in GOLD
```

## Running it

```
cd dbt_saas_analytics
dbt run
dbt test
```

## Next steps

- Add `dim_date` and `dim_plan` as shared dimensions
- Row count and freshness checks
- Replace assumed SLA targets with business-defined ones and add resolution time
- Power BI semantic model on top of Gold

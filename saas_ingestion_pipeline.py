import os
import json
import random
import time
import logging
from datetime import datetime, timedelta
import requests
import pandas as pd
from faker import Faker

# =====================================================================
# 0. SYSTEM & LOGGING CONFIGURATION
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)

fake = Faker()
Faker.seed(42)
random.seed(42)

OUTPUT_DIR = "./raw_landing_zone"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================================================================
# 1. API EXTRACTION LAYER: External Benchmark Telemetry
# =====================================================================
def fetch_finnhub_market_news(api_key: str = "sandbox_c8123456789") -> list:
    """
    Extracts financial news telemetry from the Finnhub Public API.
    Demonstrates: HTTP GET handling, status verification, and API rate-limiting retries (429).
    """
    logging.info("Extracting macroeconomic news telemetry from Finnhub API...")
    url = f"https://finnhub.io/api/v1/news?category=general&token={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Successfully extracted {len(data)} live news records from API.")
            return data[:50]
        
        elif response.status_code == 429:
            logging.warning("API Rate Limit hit (429). Retrying after 5-second backoff...")
            time.sleep(5)
            return fetch_finnhub_market_news(api_key)
        
        else:
            logging.error(f"API extraction failed with status code: {response.status_code}")
            return []
            
    except Exception as e:
        logging.error(f"Connection error during API ingestion: {str(e)}")
        return []


# =====================================================================
# 2. DATA GENERATION LAYER: Messy B2B SaaS Relational Schemas
# =====================================================================
def generate_b2b_saas_data(num_users=250):
    """
    Simulates operational transactional database logs for a B2B SaaS platform.
    Generates Users, Subscriptions, and unstructured Support Tickets for AI enrichment.
    """
    logging.info(f"Simulating B2B SaaS transactional data for {num_users} enterprise tenants...")
    
    plans = ["Starter", "Professional", "Enterprise"]
    plan_costs = {"Starter": 99, "Professional": 499, "Enterprise": 2499}
    statuses = ["active", "active", "active", "past_due", "canceled"]
    
    users = []
    subscriptions = []
    support_tickets = []
    
    # Unstructured support ticket complaints target for downstream AI Sentiment / Churn Analysis
    messy_ticket_texts = [
        "System has been completely down during market open. Unacceptable outage!",
        "Can we upgrade our tier? We are scaling our analyst team next month.",
        "Billing error! We were double-charged for our Enterprise subscription.",
        "The platform speed is sluggish when exporting large reports. Need help.",
        "Great experience so far, just checking on rate limit thresholds for the API.",
        "Threatening to cancel our subscription unless pricing variance is resolved.",
        "Integration with Snowflake keeps throwing connection timeouts."
    ]

    base_date = datetime.now() - timedelta(days=365)

    for i in range(1, num_users + 1):
        user_id = f"USR-{1000 + i}"
        signup_date = base_date + timedelta(days=random.randint(0, 300))
        
        # --- A. Users Log ---
        users.append({
            "user_id": user_id,
            "company_name": fake.company(),
            "industry": random.choice(["Fintech", "Healthcare", "E-commerce", "Energy", "Logistics"]),
            "contact_email": fake.company_email(),
            "country": random.choice(["US", "CA", "UK", "DE", "AU"]),
            "created_at": signup_date.isoformat()
        })
        
        # --- B. Subscriptions Log ---
        plan = random.choice(plans)
        sub_start = signup_date + timedelta(days=random.randint(0, 5))
        sub_status = random.choice(statuses)
        sub_end = (sub_start + timedelta(days=365)).isoformat() if sub_status == "canceled" else None
        
        subscriptions.append({
            "subscription_id": f"SUB-{5000 + i}",
            "user_id": user_id,
            "plan_tier": plan,
            "monthly_recurring_revenue": plan_costs[plan],
            "status": sub_status,
            "start_date": sub_start.isoformat(),
            "end_date": sub_end
        })
        
        # --- C. Support Tickets Log (Target for AI Layer) ---
        num_tickets = random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0]
        for t in range(num_tickets):
            ticket_date = sub_start + timedelta(days=random.randint(5, 60))
            support_tickets.append({
                "ticket_id": f"TCK-{9000 + len(support_tickets)}",
                "user_id": user_id,
                "ticket_text": random.choice(messy_ticket_texts),
                "priority": random.choice(["Low", "Medium", "High", "Urgent"]),
                "created_at": ticket_date.isoformat(),
                "resolution_status": random.choice(["open", "closed", "pending"])
            })

    # --- D. Inject Deliberate Data Quality Edge Cases (Orphan Keys for dbt Tests) ---
    for k in range(5):
        support_tickets.append({
            "ticket_id": f"TCK-ORPHAN-{k}",
            "user_id": f"USR-NONEXISTENT-{k}",
            "ticket_text": "System error. User session unlinked from tenant record.",
            "priority": "High",
            "created_at": datetime.now().isoformat(),
            "resolution_status": "open"
        })

    return users, subscriptions, support_tickets


# =====================================================================
# 3. PIPELINE ORCHESTRATION & EXPORT
# =====================================================================
def run_ingestion_pipeline():
    logging.info("=== STARTING INGESTION & EXTRACTION PIPELINE ===")
    
    market_news = fetch_finnhub_market_news()
    users, subscriptions, support_tickets = generate_b2b_saas_data(num_users=250)
    
    payloads = {
        "raw_users.json": users,
        "raw_subscriptions.json": subscriptions,
        "raw_support_tickets.json": support_tickets,
        "raw_market_news.json": market_news
    }
    
    logging.info(f"Writing raw payloads to directory: {OUTPUT_DIR}")
    for filename, data in payloads.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logging.info(f"Successfully serialized: {filepath} ({len(data)} records)")
        
    logging.info("=== INGESTION PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_ingestion_pipeline()
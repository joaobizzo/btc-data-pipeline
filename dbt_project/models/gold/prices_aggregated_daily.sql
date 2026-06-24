select
    date_trunc('day', price_timestamp) as interval_timestamp,
    round(avg(btc_usd)::numeric, 2) as avg_btc_usd,
    round(max(btc_usd)::numeric, 2) as max_btc_usd,
    round(min(btc_usd)::numeric, 2) as min_btc_usd,
    round(avg(btc_brl)::numeric, 2) as avg_btc_brl,
    round(avg(usd_brl)::numeric, 4) as avg_usd_brl,
    count(*) as records_count
from {{ ref('silver_prices') }}
group by 1
order by 1 desc

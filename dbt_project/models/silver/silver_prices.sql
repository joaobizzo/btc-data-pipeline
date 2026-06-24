with raw_realtime as (
    select
        collected_at,
        -- Trunca para segundos para evitar variações milimétricas em comparações
        date_trunc('second', collected_at) as price_timestamp,
        (payload->'bitcoin'->>'usd')::numeric as btc_usd,
        (payload->'bitcoin'->>'brl')::numeric as btc_brl,
        'coingecko_realtime' as source
    from {{ source('bronze_sources', 'raw_realtime') }}
),

historical_usd as (
    select
        collected_at,
        -- Conversão de unix epoch em milissegundos para timestamp com time zone UTC
        to_timestamp((val->>0)::numeric / 1000.0) at time zone 'UTC' as price_timestamp,
        (val->>1)::numeric as btc_usd
    from {{ source('bronze_sources', 'raw_historical') }},
    lateral jsonb_array_elements(payload->'usd_prices') as val
),

historical_brl as (
    select
        to_timestamp((val->>0)::numeric / 1000.0) at time zone 'UTC' as price_timestamp,
        (val->>1)::numeric as btc_brl
    from {{ source('bronze_sources', 'raw_historical') }},
    lateral jsonb_array_elements(payload->'brl_prices') as val
),

raw_historical as (
    select
        u.collected_at,
        u.price_timestamp,
        u.btc_usd,
        b.btc_brl,
        'coingecko_historical' as source
    from historical_usd u
    -- Join baseado na correspondência do timestamp
    join historical_brl b on u.price_timestamp = b.price_timestamp
),

combined as (
    select * from raw_realtime
    union all
    select * from raw_historical
),

deduplicated as (
    select
        price_timestamp,
        btc_usd,
        btc_brl,
        -- Cálculo da taxa de câmbio implícita BRL/USD a partir do Bitcoin
        case 
            when btc_usd > 0 then round((btc_brl / btc_usd)::numeric, 4)
            else null
        end as usd_brl,
        source,
        collected_at,
        -- Em caso de duplicidade do mesmo timestamp de preço, mantém a coleta mais recente
        row_number() over (partition by price_timestamp order by collected_at desc) as rn
    from combined
    where btc_usd > 0 and btc_brl > 0 and price_timestamp is not null
)

select
    price_timestamp,
    btc_usd,
    btc_brl,
    usd_brl,
    source,
    collected_at
from deduplicated
where rn = 1
order by price_timestamp desc

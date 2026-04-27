import dlt
import requests
import time
from datetime import date
from pyspark.sql import Row
from pyspark.sql.functions import (
    col, to_date, regexp_replace, round,
    avg, lag, row_number
)
from pyspark.sql.window import Window

API_KEY = ""
SYMBOLS = ["AAPL", "GOOGL", "AMZN", "MSFT"]


@dlt.table(
    name="bronze_stock_quotes",
    comment="Raw daily quote data ingested from Alpha Vantage API",
    table_properties={"quality": "bronze"}
)
def bronze_stock_quotes():
    rows = []
    today = str(date.today())

    for symbol in SYMBOLS:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json().get("Global Quote", {})

            if not data:
                print(f"WARNING: No quote data returned for {symbol} — skipping")
                continue

            rows.append(Row(
                symbol=symbol,
                open=data.get("02. open"),
                high=data.get("03. high"),
                low=data.get("04. low"),
                price=data.get("05. price"),
                volume=data.get("06. volume"),
                latest_trading_day=data.get("07. latest trading day"),
                previous_close=data.get("08. previous close"),
                change=data.get("09. change"),
                change_pct=data.get("10. change percent"),
                ingested_date=today
            ))
            print(f"SUCCESS: {symbol} quote fetched")

        except Exception as e:
            print(f"ERROR fetching quote for {symbol}: {e}")

        time.sleep(15)

    if not rows:
        raise Exception("No quote data fetched for any symbol — aborting pipeline")

    today_df = spark.createDataFrame(rows)

    # union with backfill history if it exists
    try:
        backfill_df = spark.table("my_catalog.default.bronze_stock_quotes_backfill")
        print("Backfill table found — unioning with today's data")
        return today_df.unionByName(backfill_df, allowMissingColumns=True)
    except Exception:
        print("No backfill table found — returning today's data only")
        return today_df


@dlt.table(
    name="bronze_company_info",
    comment="Raw company overview data ingested from Alpha Vantage API",
    table_properties={"quality": "bronze"}
)
def bronze_company_info():
    rows = []
    today = str(date.today())

    for symbol in SYMBOLS:
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data or "Symbol" not in data:
                print(f"WARNING: No company data returned for {symbol} — skipping")
                print(f"Response was: {data}")
                continue

            rows.append(Row(
                symbol=symbol,
                name=data.get("Name"),
                exchange=data.get("Exchange"),
                currency=data.get("Currency"),
                country=data.get("Country"),
                sector=data.get("Sector"),
                industry=data.get("Industry"),
                market_cap=data.get("MarketCapitalization"),
                pe_ratio=data.get("PERatio"),
                week_52_high=data.get("52WeekHigh"),
                week_52_low=data.get("52WeekLow"),
                dividend_yield=data.get("DividendYield"),
                ingested_date=today
            ))
            print(f"SUCCESS: {symbol} company info fetched")

        except Exception as e:
            print(f"ERROR fetching company info for {symbol}: {e}")

        time.sleep(15)

    if not rows:
        raise Exception("No company data fetched for any symbol — aborting pipeline")

    return spark.createDataFrame(rows)


@dlt.table(
    name="silver_stock_quotes",
    comment="Cleaned and typed stock quote data, deduplicated by symbol and trade date",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_price", "price IS NOT NULL")
@dlt.expect_or_drop("valid_symbol", "symbol IS NOT NULL")
@dlt.expect_or_drop("valid_volume", "volume IS NOT NULL")
def silver_stock_quotes():
    return (
        dlt.read("bronze_stock_quotes")
        .dropDuplicates(["symbol", "latest_trading_day"])
        .withColumn("open", col("open").cast("double"))
        .withColumn("high", col("high").cast("double"))
        .withColumn("low", col("low").cast("double"))
        .withColumn("price", col("price").cast("double"))
        .withColumn("volume", col("volume").cast("long"))
        .withColumn("previous_close", col("previous_close").cast("double"))
        .withColumn("change", col("change").cast("double"))
        .withColumn("change_pct", regexp_replace(col("change_pct"), "%", "").cast("double"))
        .withColumn("trade_date", to_date(col("latest_trading_day")))
        .withColumn("ingested_date", to_date(col("ingested_date")))
        .drop("latest_trading_day")
    )


@dlt.table(
    name="silver_company_info",
    comment="Cleaned company overview, deduplicated to latest record per symbol",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_symbol", "symbol IS NOT NULL")
@dlt.expect_or_drop("valid_name", "name IS NOT NULL")
def silver_company_info():
    window = Window.partitionBy("symbol").orderBy(col("ingested_date").desc())
    return (
        dlt.read("bronze_company_info")
        .withColumn("market_cap", col("market_cap").cast("long"))
        .withColumn("pe_ratio", col("pe_ratio").cast("double"))
        .withColumn("week_52_high", col("week_52_high").cast("double"))
        .withColumn("week_52_low", col("week_52_low").cast("double"))
        .withColumn("dividend_yield", col("dividend_yield").cast("double"))
        .withColumn("ingested_date", to_date(col("ingested_date")))
        .withColumn("rn", row_number().over(window))
        .filter(col("rn") == 1)
        .drop("rn")
    )


@dlt.table(
    name="gold_price_trends",
    comment="Daily price change and percentage change over 7, 30, 90 day windows",
    table_properties={"quality": "gold"}
)
def gold_price_trends():
    price_window = Window.partitionBy("symbol").orderBy("trade_date")
    return (
        dlt.read("silver_stock_quotes")
        .withColumn("prev_price_7d", lag("price", 7).over(price_window))
        .withColumn("prev_price_30d", lag("price", 30).over(price_window))
        .withColumn("prev_price_90d", lag("price", 90).over(price_window))
        .withColumn("price_change_7d", round(col("price") - col("prev_price_7d"), 2))
        .withColumn("price_change_30d", round(col("price") - col("prev_price_30d"), 2))
        .withColumn("price_change_90d", round(col("price") - col("prev_price_90d"), 2))
        .withColumn("price_change_pct_7d", round(
            (col("price_change_7d") / col("prev_price_7d")) * 100, 2)
        )
        .withColumn("price_change_pct_30d", round(
            (col("price_change_30d") / col("prev_price_30d")) * 100, 2)
        )
        .withColumn("price_change_pct_90d", round(
            (col("price_change_90d") / col("prev_price_90d")) * 100, 2)
        )
        .select(
            "symbol", "trade_date", "price", "open", "high", "low",
            "price_change_7d", "price_change_30d", "price_change_90d",
            "price_change_pct_7d", "price_change_pct_30d", "price_change_pct_90d"
        )
    )


@dlt.table(
    name="gold_volume_trends",
    comment="Daily volume with 7, 30, 90 day rolling average volume",
    table_properties={"quality": "gold"}
)
def gold_volume_trends():
    volume_window = Window.partitionBy("symbol").orderBy("trade_date")
    return (
        dlt.read("silver_stock_quotes")
        .withColumn("avg_volume_7d", round(
            avg("volume").over(volume_window.rowsBetween(-6, 0)), 0)
        )
        .withColumn("avg_volume_30d", round(
            avg("volume").over(volume_window.rowsBetween(-29, 0)), 0)
        )
        .withColumn("avg_volume_90d", round(
            avg("volume").over(volume_window.rowsBetween(-89, 0)), 0)
        )
        .select(
            "symbol", "trade_date", "volume",
            "avg_volume_7d", "avg_volume_30d", "avg_volume_90d"
        )
    )
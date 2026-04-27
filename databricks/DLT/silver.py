import dlt
from pyspark.sql.functions import col, to_date, regexp_replace, to_timestamp


@dlt.table(
    name="silver_stock_quotes",
    comment="Cleaned and typed stock quote data from bronze streaming table",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_price", "price IS NOT NULL")
@dlt.expect_or_drop("valid_symbol", "symbol IS NOT NULL")
@dlt.expect_or_drop("valid_volume", "volume IS NOT NULL")
def silver_stock_quotes():
    return (
        dlt.read_stream("bronze_stock_quotes")
        .withColumn("open", col("open").cast("double"))
        .withColumn("high", col("high").cast("double"))
        .withColumn("low", col("low").cast("double"))
        .withColumn("price", col("price").cast("double"))
        .withColumn("volume", col("volume").cast("long"))
        .withColumn("previous_close", col("previous_close").cast("double"))
        .withColumn("change", col("change").cast("double"))
        .withColumn("change_pct", regexp_replace(col("change_pct"), "%", "").cast("double"))
        .withColumn("trade_date", to_date(col("latest_trading_day")))
        .withColumn("ingested_at", to_timestamp(col("ingested_at")))
        .drop("latest_trading_day")
        .dropDuplicates(["symbol", "trade_date"])
    )


@dlt.table(
    name="silver_company_info",
    comment="Cleaned company overview data from bronze streaming table",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_symbol", "symbol IS NOT NULL")
@dlt.expect_or_drop("valid_name", "name IS NOT NULL")
def silver_company_info():
    return (
        dlt.read_stream("bronze_company_info")
        .withColumn("market_cap", col("market_cap").cast("long"))
        .withColumn("pe_ratio", col("pe_ratio").cast("double"))
        .withColumn("week_52_high", col("week_52_high").cast("double"))
        .withColumn("week_52_low", col("week_52_low").cast("double"))
        .withColumn("dividend_yield", col("dividend_yield").cast("double"))
        .withColumn("ingested_at", to_timestamp(col("ingested_at")))
        .dropDuplicates(["symbol", "ingested_at"])
    )
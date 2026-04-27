import dlt
from pyspark.sql.functions import col

RAW_QUOTE_PATH = "/Volumes/my_catalog/default/raw_stock_quotes"
RAW_COMPANY_PATH = "/Volumes/my_catalog/default/raw_company_info"


@dlt.table(
    name="bronze_stock_quotes",
    comment="Raw stock quote JSON files ingested from Volume using Auto Loader",
    table_properties={"quality": "bronze"}
)
def bronze_stock_quotes():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(RAW_QUOTE_PATH)
        .select(
            col("symbol"),
            col("ingested_at"),
            col("raw_response.`Global Quote`.`02. open`").alias("open"),
            col("raw_response.`Global Quote`.`03. high`").alias("high"),
            col("raw_response.`Global Quote`.`04. low`").alias("low"),
            col("raw_response.`Global Quote`.`05. price`").alias("price"),
            col("raw_response.`Global Quote`.`06. volume`").alias("volume"),
            col("raw_response.`Global Quote`.`07. latest trading day`").alias("latest_trading_day"),
            col("raw_response.`Global Quote`.`08. previous close`").alias("previous_close"),
            col("raw_response.`Global Quote`.`09. change`").alias("change"),
            col("raw_response.`Global Quote`.`10. change percent`").alias("change_pct")
        )
    )


@dlt.table(
    name="bronze_company_info",
    comment="Raw company overview JSON files ingested from Volume using Auto Loader",
    table_properties={"quality": "bronze"}
)
def bronze_company_info():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(RAW_COMPANY_PATH)
        .select(
            col("symbol"),
            col("ingested_at"),
            col("raw_response.Name").alias("name"),
            col("raw_response.Exchange").alias("exchange"),
            col("raw_response.Currency").alias("currency"),
            col("raw_response.Country").alias("country"),
            col("raw_response.Sector").alias("sector"),
            col("raw_response.Industry").alias("industry"),
            col("raw_response.MarketCapitalization").alias("market_cap"),
            col("raw_response.PERatio").alias("pe_ratio"),
            col("raw_response.`52WeekHigh`").alias("week_52_high"),
            col("raw_response.`52WeekLow`").alias("week_52_low"),
            col("raw_response.DividendYield").alias("dividend_yield")
        )
    )
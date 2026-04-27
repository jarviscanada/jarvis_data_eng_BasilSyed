import dlt
from pyspark.sql.functions import col, round, avg, lag
from pyspark.sql.window import Window


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
        .withColumn("price_change_pct_7d", round((col("price_change_7d") / col("prev_price_7d")) * 100, 2))
        .withColumn("price_change_pct_30d", round((col("price_change_30d") / col("prev_price_30d")) * 100, 2))
        .withColumn("price_change_pct_90d", round((col("price_change_90d") / col("prev_price_90d")) * 100, 2))
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
        .withColumn("avg_volume_7d", round(avg("volume").over(volume_window.rowsBetween(-6, 0)), 0))
        .withColumn("avg_volume_30d", round(avg("volume").over(volume_window.rowsBetween(-29, 0)), 0))
        .withColumn("avg_volume_90d", round(avg("volume").over(volume_window.rowsBetween(-89, 0)), 0))
        .select(
            "symbol", "trade_date", "volume",
            "avg_volume_7d", "avg_volume_30d", "avg_volume_90d"
        )
    )
"""
Bitcoin Market Sentiment vs Hyperliquid Trader Performance
============================================================
Run this in Google Colab or Jupyter. Just make sure fear_greed_index.csv
and historical_data.csv are in the same folder (see instructions in chat
for how to download / pull them from Google Drive).

Author: (your name)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# ----------------------------------------------------------------------
# STEP 1: LOAD THE DATA
# ----------------------------------------------------------------------
# Confirmed real columns:
# historical_data.csv -> Account, Coin, Execution Price, Size Tokens, Size USD,
#   Side, Timestamp IST, Start Position, Direction, Closed PnL,
#   Transaction Hash, Order ID, Crossed, Fee, Trade ID
# fear_greed_index.csv -> timestamp, value, classification, date

sentiment = pd.read_csv("fear_greed_index.csv")
trades = pd.read_csv("historical_data.csv")

print("SENTIMENT DATA")
print(sentiment.head())
print(sentiment.shape)
print(sentiment.dtypes)
print("\nTRADER DATA")
print(trades.head())
print(trades.shape)
print(trades.dtypes)

# ----------------------------------------------------------------------
# STEP 2: CLEAN & STANDARDIZE
# ----------------------------------------------------------------------
# Standardize column names: lowercase, spaces -> underscores
sentiment.columns = [c.strip().lower().replace(" ", "_") for c in sentiment.columns]
trades.columns = [c.strip().lower().replace(" ", "_") for c in trades.columns]

print("\nSentiment columns:", sentiment.columns.tolist())
print("Trader columns:", trades.columns.tolist())
# Sentiment  -> timestamp, value, classification, date
# Trader     -> account, coin, execution_price, size_tokens, size_usd, side,
#               timestamp_ist, start_position, direction, closed_pnl,
#               transaction_hash, order_id, crossed, fee, trade_id

# --- Sentiment side ---
# 'date' is already a clean YYYY-MM-DD column here, just parse it properly.
sentiment["date"] = pd.to_datetime(sentiment["date"]).dt.date

# Collapse "Extreme Fear"/"Fear" -> "Fear" and "Extreme Greed"/"Greed" -> "Greed"
# so the buckets are easier to compare. Comment out if you'd rather keep
# the 5 finer-grained categories (Extreme Fear/Fear/Neutral/Greed/Extreme Greed).
def simplify_sentiment(x):
    x = str(x).lower()
    if "fear" in x:
        return "Fear"
    elif "greed" in x:
        return "Greed"
    else:
        return "Neutral"

sentiment["sentiment_simple"] = sentiment["classification"].apply(simplify_sentiment)

# --- Trader side ---
# 'timestamp_ist' looks like "02-12-2024 22:50" i.e. DD-MM-YYYY HH:MM.
# dayfirst=True tells pandas to read it as day-month-year, not month-day-year.
trades["datetime"] = pd.to_datetime(
    trades["timestamp_ist"], dayfirst=True, errors="coerce"
)

# Drop rows that failed to parse
trades = trades.dropna(subset=["datetime"])
trades["date"] = trades["datetime"].dt.date

# Make sure numeric columns are actually numeric (some CSV exports store
# numbers as text, especially if there are stray commas or currency symbols)
for col in ["closed_pnl", "size_tokens", "size_usd", "execution_price",
            "start_position", "fee"]:
    if col in trades.columns:
        trades[col] = pd.to_numeric(trades[col], errors="coerce")

# There's no 'leverage' column in this dataset (checked against the screenshot),
# so any leverage-based analysis below is skipped automatically since the
# script checks "if 'leverage' in merged.columns" before running it.

# ----------------------------------------------------------------------
# STEP 3: MERGE ON DATE
# ----------------------------------------------------------------------
merged = trades.merge(sentiment[["date", "classification", "sentiment_simple"]],
                       on="date", how="left")

print("\nRows before merge:", len(trades))
print("Rows after merge:", len(merged))
print("Rows with no matching sentiment date:", merged["sentiment_simple"].isna().sum())

# Save the merged file so you never have to redo this step
merged.to_csv("merged_trades_sentiment.csv", index=False)

# ----------------------------------------------------------------------
# STEP 4: CORE ANALYSIS
# ----------------------------------------------------------------------

# 4a. Average / total PnL by sentiment
pnl_by_sentiment = merged.groupby("sentiment_simple")["closed_pnl"].agg(
    total_pnl="sum",
    avg_pnl="mean",
    median_pnl="median",
    trade_count="count",
    win_rate=lambda s: (s > 0).mean()
).reset_index()
print("\n=== PnL by Sentiment ===")
print(pnl_by_sentiment)

# 4b. Trading activity (volume) by sentiment -- using Size USD since that's
# directly comparable across different coins
activity = merged.groupby("sentiment_simple")["size_usd"].agg(
    total_size_usd="sum", avg_size_usd="mean"
).reset_index()
print("\n=== Trade Size (USD) by Sentiment ===")
print(activity)

# 4c. Long vs Short behavior by sentiment. This dataset has both 'side'
# (Buy/Sell) and 'direction' (e.g. Open Long/Close Short) -- direction is
# more informative if present.
mix_col = "direction" if "direction" in merged.columns else "side"
side_mix = pd.crosstab(merged["sentiment_simple"], merged[mix_col], normalize="index")
print(f"\n=== {mix_col} mix by Sentiment (row %) ===")
print(side_mix)

# 4d. Per-account performance: does each trader do better in Fear or Greed?
per_account = merged.groupby(["account", "sentiment_simple"])["closed_pnl"].mean().unstack()
print("\n=== Sample per-account avg PnL by sentiment ===")
print(per_account.head())

# 4e. Top and bottom performing accounts overall
account_totals = merged.groupby("account")["closed_pnl"].sum().sort_values(ascending=False)
print("\nTop 5 accounts by total PnL:")
print(account_totals.head())
print("\nBottom 5 accounts by total PnL:")
print(account_totals.tail())

# 4f. Which coins are traded / profitable in Fear vs Greed?
coin_sentiment = merged.groupby(["coin", "sentiment_simple"])["closed_pnl"].agg(
    total_pnl="sum", trade_count="count"
).reset_index()
print("\n=== Sample coin performance by sentiment ===")
print(coin_sentiment.sort_values("total_pnl", ascending=False).head(10))

# ----------------------------------------------------------------------
# STEP 5: STATISTICAL TEST
# Is the PnL difference between Fear and Greed days statistically real,
# or could it just be noise?
# ----------------------------------------------------------------------
from scipy import stats

fear_pnl = merged.loc[merged["sentiment_simple"] == "Fear", "closed_pnl"].dropna()
greed_pnl = merged.loc[merged["sentiment_simple"] == "Greed", "closed_pnl"].dropna()

t_stat, p_value = stats.ttest_ind(fear_pnl, greed_pnl, equal_var=False)
print(f"\nT-test Fear vs Greed PnL: t={t_stat:.3f}, p={p_value:.4f}")
if p_value < 0.05:
    print("=> Statistically significant difference between Fear and Greed PnL")
else:
    print("=> No statistically significant difference detected")

# ----------------------------------------------------------------------
# STEP 6: VISUALIZATIONS
# ----------------------------------------------------------------------

# Chart 1: Average PnL by sentiment
plt.figure(figsize=(6, 4))
sns.barplot(data=pnl_by_sentiment, x="sentiment_simple", y="avg_pnl")
plt.title("Average Closed PnL by Market Sentiment")
plt.ylabel("Avg Closed PnL")
plt.xlabel("Sentiment")
plt.tight_layout()
plt.savefig("chart_avg_pnl_by_sentiment.png", dpi=150)
plt.show()

# Chart 2: Win rate by sentiment
plt.figure(figsize=(6, 4))
sns.barplot(data=pnl_by_sentiment, x="sentiment_simple", y="win_rate")
plt.title("Win Rate by Market Sentiment")
plt.ylabel("Win Rate")
plt.xlabel("Sentiment")
plt.tight_layout()
plt.savefig("chart_win_rate_by_sentiment.png", dpi=150)
plt.show()

# Chart 3: Daily PnL over time colored by sentiment
daily = merged.groupby(["date", "sentiment_simple"])["closed_pnl"].sum().reset_index()
plt.figure(figsize=(12, 5))
sns.scatterplot(data=daily, x="date", y="closed_pnl", hue="sentiment_simple")
plt.title("Daily Total PnL Over Time, Colored by Sentiment")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart_daily_pnl_timeline.png", dpi=150)
plt.show()

# Chart 4: Trade size (USD) distribution by sentiment -- shows whether
# traders bet bigger during Greed (overconfidence) or Fear
plt.figure(figsize=(6, 4))
sns.boxplot(data=merged, x="sentiment_simple", y="size_usd")
plt.yscale("log")  # trade sizes are usually very skewed, log scale helps
plt.title("Trade Size (USD, log scale) by Sentiment")
plt.tight_layout()
plt.savefig("chart_size_by_sentiment.png", dpi=150)
plt.show()

print("\nAll charts saved as PNG files in the working directory.")
print("Merged dataset saved as merged_trades_sentiment.csv")

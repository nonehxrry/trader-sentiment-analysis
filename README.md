# Bitcoin Market Sentiment vs Hyperliquid Trader Performance

This project looks at whether Bitcoin market sentiment (Fear/Greed Index) has any relationship with how traders perform on Hyperliquid.

## Data used

- `fear_greed_index.csv` - daily sentiment classification (Extreme Fear, Fear, Neutral, Greed, Extreme Greed), 2,644 rows
- `historical_data.csv` - individual trade records from Hyperliquid: account, coin, execution price, size, side, direction, closed PnL, fee, timestamp, 211,224 rows
- `merged_trades_sentiment.csv.gz` - the trade data merged with sentiment on date, zipped because the raw file was 60MB and too large to upload directly. Nothing is removed, it's just compressed.

## Approach

1. Cleaned column names and parsed the timestamp columns into proper dates.
2. Grouped sentiment into Fear / Neutral / Greed instead of 5 categories, to keep comparisons simple.
3. Merged every trade with the sentiment for that date. Only 6 out of 211,224 trades didn't have a matching date.
4. Compared average PnL, win rate, trade size, and long/short behavior across the three sentiment groups.
5. Ran a t-test to check if the PnL difference between Fear and Greed was actually meaningful or just noise.
6. Made a few charts to visualize the differences.

Code: [`sentiment_trader_analysis.py`](./sentiment_trader_analysis.py)

## Results

| Sentiment | Trades | Avg PnL/trade | Win rate | Avg trade size (USD) |
|---|---|---|---|---|
| Fear | 83,237 | $49.21 | 40.8% | $7,182 |
| Greed | 90,295 | $53.88 | 42.0% | $4,574 |
| Neutral | 37,686 | $34.31 | 39.7% | $4,783 |

- Greed days have slightly better average PnL and win rate, but the t-test came back with p = 0.32, which means this difference isn't statistically significant. Sentiment by itself doesn't strongly predict how profitable a trade will be.
- Trade sizes are much bigger during Fear, about 57% larger than during Greed, even though Fear trades aren't more profitable. Traders seem to take on more risk when the market is scared, not when it's confident.
- PnL is very concentrated across accounts. The best account made about $2.14M total, the worst lost around $168K. Individual trading skill matters a lot more than sentiment.
- Some coins show clearer patterns: @107 drives most of the Greed-day profit, while HYPE, ETH, SOL and BTC contribute more on Fear days.
- Merge quality was good, only 6 trades out of 211,224 had no matching sentiment date.

## Takeaway

Sentiment doesn't seem to be a reliable signal for predicting whether a trade will be profitable, but it does seem to affect how much risk traders take. A more useful strategy than trying to trade based on sentiment direction might be to reduce position size during Fear periods, since that's when risk-taking goes up without any real improvement in outcomes.

## Files

- `sentiment_trader_analysis.py` - the analysis script
- `merged_trades_sentiment.csv.gz` - merged dataset (zipped)
- `chart_avg_pnl_by_sentiment.png`
- `chart_win_rate_by_sentiment.png`
- `chart_daily_pnl_timeline.png`
- `chart_size_by_sentiment.png`

## Running it yourself

```bash
pip install pandas numpy matplotlib seaborn scipy
python sentiment_trader_analysis.py
```

Needs `fear_greed_index.csv` and `historical_data.csv` in the same folder.

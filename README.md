# Bitcoin Market Sentiment vs Hyperliquid Trader Performance

Exploring the relationship between Bitcoin Fear & Greed sentiment and trader
performance on Hyperliquid, to uncover patterns that could inform smarter
trading strategies.

## Datasets

| File | Description | Rows |
|---|---|---|
| `fear_greed_index.csv` | Daily Bitcoin market sentiment (`Fear` / `Extreme Fear` / `Neutral` / `Greed` / `Extreme Greed`) | 2,644 |
| `historical_data.csv` | Individual Hyperliquid trades: account, coin, execution price, size, side, direction, closed PnL, fee, timestamp | 211,224 |

## Methodology

1. **Cleaning** — standardized column names, parsed `Timestamp IST`
   (`DD-MM-YYYY HH:MM`) into proper datetimes, coerced numeric columns
   (`Closed PnL`, `Size USD`, etc.) to numeric types.
2. **Sentiment simplification** — collapsed the 5-level classification into
   3 buckets (`Fear`, `Neutral`, `Greed`) by merging "Extreme Fear" into
   "Fear" and "Extreme Greed" into "Greed", to make comparisons cleaner.
3. **Merge** — joined every trade to that day's sentiment classification on
   date. 211,218 of 211,224 trades (99.997%) matched successfully.
4. **Analysis** — grouped by sentiment to compare average/total PnL, win
   rate, trade size, long/short direction mix, and per-account and per-coin
   performance. Ran an independent two-sample t-test to check whether the
   Fear vs Greed PnL difference is statistically significant.
5. **Visualization** — 4 charts covering average PnL, win rate, a daily PnL
   timeline, and trade size distribution, all split by sentiment.

Full code: [`sentiment_trader_analysis.py`](./sentiment_trader_analysis.py)

## Key Findings

| Sentiment | Trades | Avg PnL/trade | Win rate | Avg trade size (USD) |
|---|---|---|---|---|
| Fear | 83,237 | $49.21 | 40.8% | $7,182 |
| Greed | 90,295 | $53.88 | 42.0% | $4,574 |
| Neutral | 37,686 | $34.31 | 39.7% | $4,783 |

1. **Sentiment alone is a weak predictor of profitability.** Greed days show
   slightly higher average PnL and win rate than Fear days, but a t-test
   comparing Fear vs Greed PnL gives **p = 0.32** — not statistically
   significant. Traders are not reliably more or less profitable simply
   because the market is fearful or greedy.

2. **Traders take on significantly more risk during Fear.** Average trade
   size is ~57% larger during Fear ($7,182) than during Greed ($4,574),
   despite Fear trades not being more profitable. This suggests risk-taking
   increases with fear rather than with confidence — a pattern worth
   flagging for risk management.

3. **Performance is highly concentrated across accounts**, far more than
   it varies by sentiment. The top account earned ~$2.14M in total closed
   PnL; the worst-performing account lost ~$168K. Individual trading skill
   and positioning dominate any sentiment effect.

4. **Coin-level differences exist**: the `@107` perp dominates Greed-day
   profits (~$2.7M total), while HYPE, ETH, SOL, and BTC drive most of the
   profit generated on Fear days — a possible avenue for coin-specific
   sentiment strategies.

5. **Data quality**: only 6 of 211,224 trades had no matching sentiment
   date, so the merge is essentially complete and reliable.

## Recommendation

Market-wide Fear/Greed sentiment is not a strong standalone signal for
directional profitability, but it is a strong signal for **risk-taking
behavior**. Rather than trying to time direction using sentiment, a more
robust strategy is to **scale position size down during Fear periods**,
when traders empirically take on more risk without a corresponding increase
in edge.

## Files in this repo

- `sentiment_trader_analysis.py` — full analysis pipeline (cleaning,
  merging, statistics, charts)
- `merged_trades_sentiment.csv` — the merged trade + sentiment dataset
  produced by the script
- `chart_avg_pnl_by_sentiment.png`
- `chart_win_rate_by_sentiment.png`
- `chart_daily_pnl_timeline.png`
- `chart_size_by_sentiment.png`

## How to reproduce

```bash
pip install pandas numpy matplotlib seaborn scipy
python sentiment_trader_analysis.py
```

Requires `fear_greed_index.csv` and `historical_data.csv` in the same
directory.

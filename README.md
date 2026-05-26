# 📊 MERVAL Dashboard

Dashboard de señales de trading para el Mercado Argentino (BYMA/MERVAL).

**Acceso:** https://jony96-lab.github.io/merval-dashboard

## 🚀 ¿Qué hace?

Analiza **~130 tickers líquidos** (CEDEARs + locales argentinos) cada hora durante la rueda BYMA y genera señales **COMPRA / VENTA / NEUTRO** basadas en:

- **MACD + RSI** — Estrategia principal (Sharpe 0.94 en backtest)
- **SMA Crossover** — Estrategia secundaria (SMA 10/30)
- **Momentum** — Rendimiento a 5 y 20 días
- **Tendencia** — Precio vs SMA 50/200

## 📈 Sectores monitoreados

| Sector | Descripción | Tickers |
|--------|-------------|---------|
| QQQ | NASDAQ Tecnología | MSFT, NVDA, AAPL, TSLA, META... |
| XLF | Financiero | MELI, GGAL, JPM, PYPL, BMA... |
| XLE | Energía | XOM, YPFD, PAMP, VIST, CVX... |
| XLV | Salud | PFE, LLY, JNJ... |
| XLP | Consumo | KO, PEP, PG, WMT... |
| GDX | Minería/Commodities | VALE, GLD, SLV... |
| ARKK | Innovación/Crypto | IBIT, MSTR, COIN... |
| EEM | Emergentes | BABA, JD, BIDU... |
| SPY | General | UNH, DISN, RACE... |
| LOCAL_ADR | 🇦🇷 Locales con ADR | GGAL, YPFD, PAMP, BMA... |
| LOCAL_PURO | 🇦🇷 Locales BYMA | TXAR, ALUA, BYMA, TRAN... |

## ⏰ Horario de actualización

Durante la rueda BYMA (L-V 11:00 a 17:30 ART), el dashboard se actualiza **cada hora**.

## 🛠️ Stack técnico

- **Frontend:** HTML + Chart.js (GitHub Pages)
- **Backend:** Python + yfinance (GitHub Actions)
- **Indicadores:** SMA, RSI, MACD, Bollinger
- **Deploy:** peaceiris/actions-gh-pages

---

*Generado automáticamente por Hermes Agent.*

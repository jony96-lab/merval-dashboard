#!/usr/bin/env python3
"""
gh_action_dashboard.py — Genera signals.json para GitHub Pages.
Ejecutado cada hora por GitHub Actions.
No requiere Flask, solo genera JSON estático.
"""

import json
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

# ─── News Scoring (opcional) ───
_NEWS_SCORES = None  # cache global de news scores para evitar refetch

def load_news_scores():
    """Obtiene news scores para todos los tickers."""
    global _NEWS_SCORES
    if _NEWS_SCORES is not None:
        return _NEWS_SCORES  # cache: se refresca cada ejecución
    try:
        sys.path.insert(0, os.path.expanduser("~/spikes/001-indicadores-merval"))
        from news_scorer import score_all, fetch_news
        headlines = fetch_news()
        if headlines:
            scores = score_all(headlines)
            _NEWS_SCORES = {k.upper(): v["score"] for k, v in scores.items()}
            print(f"📰 News scoring: {len(_NEWS_SCORES)} tickers sc.")
            return _NEWS_SCORES
    except Exception as e:
        print(f"⚠️ News scoring no disponible: {e}")
    _NEWS_SCORES = {}
    return _NEWS_SCORES

# ───────────────────────────────────────────────────────────────
# TICKERS LÍQUIDOS POR SECTOR (~130 tickers)
# ───────────────────────────────────────────────────────────────
LIQUID_TICKERS_BY_SECTOR = {
    "QQQ": [
        "MSFT.BA", "AAPL.BA", "NVDA.BA", "META.BA", "AMZN.BA", "GOOGL.BA",
        "TSLA.BA", "PLTR.BA", "SNOW.BA", "AMD.BA", "INTC.BA", "QCOM.BA",
        "AVGO.BA", "ARM.BA", "ASML.BA", "ADBE.BA", "TSM.BA", "MU.BA",
        "NFLX.BA", "GLOB.BA", "SHOP.BA", "ZM.BA", "ORCL.BA", "CRM.BA",
        "DOCU.BA", "TEAM.BA", "AI.BA", "PATH.BA", "TWLO.BA", "UBER.BA",
        "PINS.BA", "SNAP.BA", "RBLX.BA", "IBM.BA", "NOW.BA", "SAP.BA",
        "NKE.BA", "ABNB.BA", "ETSY.BA", "INFY.BA", "BKNG.BA", "ACN.BA",
        "MRVL.BA", "SPOT.BA", "CSCO.BA", "PANW.BA", "SWKS.BA", "LRCX.BA",
            "ADI.BA", "EA.BA", "ROKU.BA", "GRMN.BA", "VRSN.BA", "MSI.BA",
            "ASTS.BA", "XROX.BA", "BB.BA",
    ],
    "XLF": [
        "JPM.BA", "V.BA", "BRKB.BA", "PYPL.BA", "MELI.BA", "GGAL.BA",
        "BBAR.BA", "BMA.BA", "SUPV.BA", "C.BA", "BX.BA", "STNE.BA",
        "BBD.BA", "ITUB.BA", "NU.BA", "PAGS.BA", "GS.BA", "MA.BA",
        "AXP.BA", "HSBC.BA", "WFC.BA", "HOOD.BA", "BHIP.BA", "BYMA.BA",
        "CVH.BA",
    ],
    "XLE": [
        "XOM.BA", "CVX.BA", "OXY.BA", "PBR.BA", "VIST.BA", "YPFD.BA",
        "PAMP.BA", "TGSU2.BA", "CEPU.BA", "EDN.BA", "TRAN.BA", "NG.BA",
        "VST.BA", "CEG.BA", "FSLR.BA", "METR.BA", "OEST.BA",
    ],
    "XLV": [
        "PFE.BA", "LLY.BA", "JNJ.BA", "MDT.BA", "MRNA.BA", "ABEV.BA",
    ],
    "XLP": [
        "KO.BA", "PEP.BA", "PG.BA", "WMT.BA", "MCD.BA", "CL.BA",
        "KMB.BA", "HSY.BA", "PM.BA", "MO.BA",
    ],
    "GDX": [
        "VALE.BA", "B.BA", "HMY.BA", "MOS.BA", "GLD.BA", "SLV.BA",
    ],
    "ARKK": [
        "IBIT.BA", "MSTR.BA", "ETHA.BA", "NIO.BA", "COIN.BA", "UPST.BA",
        "SPCE.BA", "HUT.BA", "OKLO.BA",
    ],
    "EEM": [
        "BABA.BA", "JD.BA", "BIDU.BA", "PETR3.BA", "BAK.BA",
        "BBDC3.BA", "BBAS3.BA",
        "JOYY.BA",
    ],
    "SPY": [
        "TECO2.BA", "AAL.BA", "UNH.BA", "DISN.BA", "DOW.BA",
        "RACE.BA", "SONY.BA",
    ],
    "LOCAL_ADR": [
        "GGAL.BA", "YPFD.BA", "PAMP.BA", "BMA.BA", "BBAR.BA", "LOMA.BA",
        "CEPU.BA", "TECO2.BA", "SUPV.BA", "EDN.BA", "IRSA.BA", "CRES.BA",
        "TGSU2.BA", "VIST.BA", "CAAP.BA", "BIOX.BA",
    ],
    "LOCAL_PURO": [
        "TXAR.BA", "ALUA.BA", "TRAN.BA", "MORI.BA", "MIRG.BA", "BYMA.BA",
        "HARG.BA", "CELU.BA", "CVH.BA", "AGRO.BA", "BHIP.BA", "MOLA.BA",
        "MOLI.BA", "LAR.BA", "METR.BA", "OEST.BA", "CECO2.BA", "CAPX.BA",
        "DGCU2.BA", "GRIM.BA", "HAVA.BA", "LEDE.BA", "AUSO.BA", "GARO.BA",
        "GCLA.BA", "GAMI.BA", "INTR.BA", "INVJ.BA", "RICH.BA", "SEMI.BA",
        "CARC.BA", "PATA.BA", "LONG.BA", "ROSE.BA", "CGPA2.BA", "MEST.BA",
        "BOLT.BA", "BPAT.BA", "FERR.BA", "FIPL.BA", "DOME.BA", "CTIO.BA",
        "ECOG.BA", "HSAT.BA", "SAMI.BA",
    ],
}

# ───────────────────────────────────────────────────────────────
# INDICADORES TÉCNICOS
# ───────────────────────────────────────────────────────────────

def add_sma(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df[f"SMA_{window}"] = df["Close"].rolling(window=window).mean()
    return df

def add_ema(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df[f"EMA_{window}"] = df["Close"].ewm(span=window, adjust=False).mean()
    return df

def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = (-delta.clip(upper=0)).rolling(window=window).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def add_macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    exp1 = df["Close"].ewm(span=fast, adjust=False).mean()
    exp2 = df["Close"].ewm(span=slow, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    return df

def add_bollinger(df: pd.DataFrame, window=20, num_std=2) -> pd.DataFrame:
    sma = df["Close"].rolling(window=window).mean()
    std = df["Close"].rolling(window=window).std()
    df["BB_Upper"] = sma + num_std * std
    df["BB_Lower"] = sma - num_std * std
    return df

def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = add_sma(df, 20)
    df = add_sma(df, 50)
    df = add_sma(df, 200)
    df = add_ema(df, 20)
    df = add_rsi(df, 14)
    df = add_macd(df)
    df = add_bollinger(df)
    return df

# ───────────────────────────────────────────────────────────────
# SEÑALES V4 — Optimizadas con backtesting (RSI + MACD)
# ───────────────────────────────────────────────────────────────

RSI_OVERSOLD = 35
RSI_OVERBOUGHT = 65


def get_consolidated_signal(df: pd.DataFrame, news_score: int = 0) -> dict:
    """Señal V4: RSI_35_65 (70%) + MACD (30%) + News Scoring."""
    if df.empty or len(df) < 60:
        return {"señal": "NEUTRO", "score": 0, "confianza": 0,
                "razón": "Datos insuficientes", "news_score": news_score}
    
    # RSI
    rsi_signal, rsi_score = _calc_rsi_signal(df)
    # MACD
    macd_signal, macd_score = _calc_macd_signal(df)
    
    # Score ponderado técnico
    score = rsi_score * 0.7 + macd_score * 0.3
    
    razón = f"RSI({rsi_score}) MACD({macd_score})"
    
    # Aplicar news scoring como boost/penalty (máximo +/-15 puntos)
    if news_score != 0:
        boost = int(news_score * 0.5)  # news_score -30..+30 → boost -15..+15
        score += boost
        razón += f" news({news_score:+d})"
    
    if score >= 50:
        return {"señal": "COMPRA", "score": round(score, 1), "confianza": min(100, int(abs(score))), "razón": razón, "news_score": news_score}
    elif score >= 20:
        return {"señal": "COMPRA_DÉBIL", "score": round(score, 1), "confianza": min(70, int(abs(score))), "razón": razón, "news_score": news_score}
    elif score <= -50:
        return {"señal": "VENTA", "score": round(score, 1), "confianza": min(100, int(abs(score))), "razón": razón, "news_score": news_score}
    elif score <= -20:
        return {"señal": "VENTA_DÉBIL", "score": round(score, 1), "confianza": min(70, int(abs(score))), "razón": razón, "news_score": news_score}
    else:
        return {"señal": "NEUTRO", "score": round(score, 1), "confianza": max(5, 50 - int(abs(score))), "razón": razón, "news_score": news_score}


def _calc_rsi_signal(df):
    """RSI puro: mejor estrategia general (96.4% WR)."""
    if "RSI" not in df.columns:
        return "NEUTRO", 0
    rsi = df["RSI"].iloc[-1]
    if pd.isna(rsi):
        return "NEUTRO", 0
    if rsi < RSI_OVERSOLD:
        return "COMPRA", int((RSI_OVERSOLD - rsi) * 3 + 50)
    elif rsi > RSI_OVERBOUGHT:
        return "VENTA", int((rsi - RSI_OVERBOUGHT) * -3 - 50)
    elif rsi < RSI_OVERSOLD + 5:
        return "COMPRA_DÉBIL", 30
    elif rsi > RSI_OVERBOUGHT - 5:
        return "VENTA_DÉBIL", -30
    return "NEUTRO", 0


def _calc_macd_signal(df, fast=12, slow=26, signal=9):
    """MACD: consistente (59.5% WR, 32 trades/año)."""
    if "MACD" not in df.columns or "MACD_Signal" not in df.columns:
        return "NEUTRO", 0
    curr = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else curr
    score = 0
    if prev["MACD"] <= prev["MACD_Signal"] and curr["MACD"] > curr["MACD_Signal"]:
        score += 60
    elif prev["MACD"] >= prev["MACD_Signal"] and curr["MACD"] < curr["MACD_Signal"]:
        score -= 60
    if curr["MACD"] > curr["MACD_Signal"]:
        score += 20
    elif curr["MACD"] < curr["MACD_Signal"]:
        score -= 20
    if "MACD_Hist" in df.columns and len(df) >= 2:
        if curr["MACD_Hist"] > df["MACD_Hist"].iloc[-2]:
            score += 10
        elif curr["MACD_Hist"] < df["MACD_Hist"].iloc[-2]:
            score -= 10
    if score >= 50:
        return "COMPRA", score
    elif score <= -50:
        return "VENTA", score
    elif score >= 20:
        return "COMPRA_DÉBIL", score
    elif score <= -20:
        return "VENTA_DÉBIL", score
    return "NEUTRO", score


def calculate_market_metrics(df: pd.DataFrame) -> dict:
    """Métricas de mercado para un ticker"""
    if df.empty:
        return {}

    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else last

    change = last["Close"] - prev["Close"]
    change_pct = ((last["Close"] / prev["Close"]) - 1) * 100 if prev["Close"] else 0
    vol = last.get("Volume", 0)
    high_52w = df["High"].rolling(252).max().iloc[-1] if len(df) >= 252 else df["High"].max()
    low_52w = df["Low"].rolling(252).min().iloc[-1] if len(df) >= 252 else df["Low"].min()
    from_52w_high = ((last["Close"] / high_52w) - 1) * 100 if high_52w else 0

    return {
        "precio": round(last["Close"], 2),
        "cambio": round(change, 2),
        "cambio_pct": round(change_pct, 2),
        "volumen": int(vol) if not pd.isna(vol) else 0,
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "from_52w_high": round(from_52w_high, 2),
        "rsi": round(last.get("RSI", 0), 1) if not pd.isna(last.get("RSI", np.nan)) else None,
    }


# ───────────────────────────────────────────────────────────────
# LOG PRINCIPAL
# ───────────────────────────────────────────────────────────────

def analyze_ticker(ticker: str, period: str = "6mo", news_score: int = 0) -> dict:
    """Analiza un ticker y devuelve señal + métricas"""
    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if df.empty or len(df) < 30:
            return {"ticker": ticker, "error": "Sin datos suficientes"}

        # Aplanar MultiIndex si existe
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = add_all_indicators(df)

        metrics = calculate_market_metrics(df)
        signal = get_consolidated_signal(df, news_score=news_score)

        return {
            "ticker": ticker,
            "señal": signal["señal"],
            "score": signal["score"],
            "confianza": signal["confianza"],
            "razón": signal["razón"],
            "precio": metrics.get("precio"),
            "cambio_pct": metrics.get("cambio_pct"),
            "rsi": metrics.get("rsi"),
            "volumen": metrics.get("volumen"),
            "from_52w_high": metrics.get("from_52w_high"),
            "news_score": signal.get("news_score", 0),
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)[:100]}


def run_dashboard():
    """Ejecuta el análisis completo y genera signals.json"""
    print(f"🚀 MERVAL Dashboard — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"📊 Analizando ~130 tickers...")

    # Cargar news scores
    news_scores = load_news_scores()
    if news_scores:
        print(f"📰 {len(news_scores)} tickers con news score")
        for t, s in sorted(news_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"     {t}: {s:+d}")

    all_signals = []
    sector_counts = {}
    total_tickers = 0
    errors = 0

    for sector, tickers in LIQUID_TICKERS_BY_SECTOR.items():
        sector_counts[sector] = {"COMPRA": 0, "COMPRA_DÉBIL": 0, "NEUTRO": 0, "VENTA_DÉBIL": 0, "VENTA": 0, "ERROR": 0}
        for ticker in tickers:
            total_tickers += 1
            # Buscar news_score para este ticker
            ticker_clean = ticker.replace(".BA", "")
            ns = news_scores.get(ticker_clean, news_scores.get(ticker, 0))
            result = analyze_ticker(ticker, news_score=ns)
            result["sector"] = sector
            all_signals.append(result)

            s = result.get("señal", "ERROR")
            if s in sector_counts[sector]:
                sector_counts[sector][s] += 1
            else:
                sector_counts[sector]["ERROR"] += 1
                errors += 1

            ticker_clean = ticker.replace(".BA", "")
            status = "✅" if s in ("COMPRA", "COMPRA_DÉBIL") else "🔴" if s in ("VENTA", "VENTA_DÉBIL") else "⚪"
            score = result.get("score", 0)
            print(f"  {status} {ticker_clean:8s} → {s:15s} (score: {score:>6.1f})")

    print(f"\n{'='*60}")
    print(f"✅ Completado: {total_tickers} tickers, {errors} errores")

    # Resumen por sector
    print(f"\n📊 RESUMEN POR SECTOR:")
    for sector, counts in sorted(sector_counts.items()):
        compras = counts["COMPRA"] + counts["COMPRA_DÉBIL"]
        ventas = counts["VENTA"] + counts["VENTA_DÉBIL"]
        neutros = counts["NEUTRO"]
        total_s = compras + ventas + neutros + counts.get("ERROR", 0)
        print(f"  {sector:12s}: 🟢{compras:3d}  ⚪{neutros:3d}  🔴{ventas:3d}  ({total_s} tickers)")

    # Stats globales
    compras_tot = sum(sector_counts[s]["COMPRA"] + sector_counts[s]["COMPRA_DÉBIL"] for s in sector_counts)
    ventas_tot = sum(sector_counts[s]["VENTA"] + sector_counts[s]["VENTA_DÉBIL"] for s in sector_counts)
    neutros_tot = sum(sector_counts[s]["NEUTRO"] for s in sector_counts)
    print(f"\n📈 TOTAL: 🟢{compras_tot} COMPRAS | ⚪{neutros_tot} NEUTROS | 🔴{ventas_tot} VENTAS")

    # Construir JSON de salida
    output = {
        "generated_at": datetime.now().isoformat(),
        "generated_at_art": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {
            "total": total_tickers,
            "compras": compras_tot,
            "ventas": ventas_tot,
            "neutros": neutros_tot,
            "errores": errors,
            "compras_fuertes": sum(sector_counts[s]["COMPRA"] for s in sector_counts),
            "ventas_fuertes": sum(sector_counts[s]["VENTA"] for s in sector_counts),
        },
        "sector_counts": sector_counts,
        "signals": all_signals,
        "top_compras": sorted(
            [s for s in all_signals if s.get("señal") in ("COMPRA", "COMPRA_DÉBIL")],
            key=lambda x: x.get("score", 0), reverse=True
        )[:10],
        "top_ventas": sorted(
            [s for s in all_signals if s.get("señal") in ("VENTA", "VENTA_DÉBIL")],
            key=lambda x: x.get("score", 0)
        )[:10],
    }

    # Escribir archivo
    output_path = os.environ.get("OUTPUT_PATH", "signals.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Guardado: {output_path} ({os.path.getsize(output_path)} bytes)")

    # También escribir signals.json en /tmp para debug local
    return output


if __name__ == "__main__":
    run_dashboard()

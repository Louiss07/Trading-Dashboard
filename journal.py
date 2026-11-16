from pathlib import Path
import csv
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from datetime import datetime


BASIS = Path(__file__).resolve().parent

DATEI = BASIS / "data" / "beispiel_trades.csv"


PUNKTWERTE = {"MNQ": 2, "MES": 5, "SPY": 1 }



def lade_trades():
    with open(DATEI, newline="", encoding="utf-8") as f:
        zeilen = list(csv.DictReader(f))
    for nummer, z in enumerate(zeilen, start=1):
        z['pnl'] = float(z["pnl"])
        z['id'] = nummer
    return zeilen

def speichere_trade(trade):
    with open(DATEI, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([trade["datum"], trade["ticker"], trade["setup"], trade["richtung"], trade["pnl"]])



def statistik(pnls):
    if not pnls:
        raise ValueError("Keine Trades vorhanden – Statistik nicht möglich")
    pnl = 0
    az_trades = len(pnls)
    winner = 0
    az_verlierer = 0
    g_gewinn = 0
    g_verlust = 999999999999999
    avg_verlust_temp = 0
    avg_gewinn_temp = 0

    for t in pnls:
        pnl += t
        if t > 0:
            winner += 1
            avg_gewinn_temp += t
            if g_gewinn <= t:
                g_gewinn = t
        else: 
            az_verlierer +=1
            avg_verlust_temp += t
            if g_verlust>= t:
                g_verlust = t


    avg_gewinn = avg_gewinn_temp / winner  if winner > 0 else None
    avg_verlust = avg_verlust_temp / az_verlierer  if az_verlierer > 0 else None
    winrate = (winner / az_trades ) * 100  

    profit_faktor = avg_gewinn_temp / abs(avg_verlust_temp)  if avg_verlust_temp > 0 else None


    return {"gesamt": pnl, "anzahl": az_trades, "winrate": winrate, "gewinner": winner, "verlierer": az_verlierer,
             "avg_gewinn": avg_gewinn, "avg_verlust": avg_verlust, "groesster_gewinn":g_gewinn, "groesster_verlust": g_verlust,
             "profit_faktor": profit_faktor}


def punktewert_ticker(ticker):
    wert = PUNKTWERTE.get(ticker)
    if wert is None:
        raise ValueError(f"Unbekannter ticker {ticker}")
    return wert




def berechne_pnl(ticker, richtung, einstieg, ausstieg, groesse):
    punktwert = punktewert_ticker(ticker)

    if richtung =="long":
        punkte = ausstieg - einstieg;
    elif richtung == "short": 
        punkte = einstieg - ausstieg;
    else: 
        raise ValueError("Das ist kein gültige Richtung, nur long oder short!");

    

    pnl = punkte * groesse * punktwert;

    return pnl




def equity_kurve(trades):
    pnl_laufend = 0
    kurve = []
    for z in trades:
        datum = z['datum'] 
        pnl = z['pnl']
        pnl_laufend += pnl
        kurve.append({"datum": datum, "equity": round(pnl_laufend, 2)})
    return kurve


def pruefe_trade(daten):
    try:
        datum = datetime.strptime(daten['datum'], "%Y-%m-%d").strftime("%d.%m.%Y")
        ticker = daten['ticker']
        setup = daten['setup'].strip()
        richtung = daten['richtung']
        einstieg = float(daten['einstieg'])
        ausstieg = float(daten['ausstieg'])
        groesse = int(daten['stueckzahl'])
    except KeyError as e:
        raise ValueError(f"Fehlendes Feld: {e}")
    except ValueError:
        raise ValueError("Datum, Stückzahl, Einstieg und Ausstieg prüfen")

    if groesse < 1:
        raise ValueError("fehler: groesse muss mind 1 sein")
    
    if richtung not in ("long", "short"):
        raise ValueError("Richtung nur long oder short")
    
    if ticker not in PUNKTWERTE:
        raise ValueError("Kein Erlaubter Ticker")

    if setup not in daten['setup']:
        raise ValueError("Kein Erlaubtes Setup")

    pnl = berechne_pnl(ticker, richtung, einstieg, ausstieg, groesse)
    trade = {"datum":datum, "ticker":ticker, "setup": setup, "richtung": richtung,"pnl": pnl}
    return trade

def statistik_pro_setup(trades):
    gruppe = {}
    for t in trades: 
        setup = t['setup']
        
        if setup not in gruppe:
            gruppe[setup] = {"anzahl": 0, "pnl": 0, "gewinner": 0}

        gruppe[setup]["anzahl"] += 1
        gruppe[setup]["pnl"] += t['pnl']
        if  gruppe[setup]["pnl"] >= 0:
            gruppe[setup]["gewinner"] += 1



    ss = []

    for name, werte in gruppe.items():
        winrate = werte["gewinner"] /  werte["anzahl"] * 100
        ss.append({"setup": name, "anzahl": werte["anzahl"], "pnl": werte["pnl"], "winrate": winrate})
        
    
    return sorted(ss, key=lambda k: k["pnl"], reverse=True)

    


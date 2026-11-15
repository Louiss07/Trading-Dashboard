from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import io
from flask import abort
from journal import lade_trades, speichere_trade, statistik, equity_kurve, berechne_pnl, PUNKTWERTE, pruefe_trade, statistik_pro_setup


app = Flask(__name__)


def trades_mit_filter():
    trades = lade_trades()
    ticker = request.args.get("ticker")
    if ticker is None:
        return trades
    if ticker not in PUNKTWERTE:
        raise ValueError(f"Unbekannter Ticker: {ticker}")
    return [t for t in trades if t["ticker"] == ticker]


@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/trade/<int:nummer>")
def trade_detail(nummer):
    trades = lade_trades()
    if nummer < 1 or nummer > len(trades):
        abort(404) 

    return render_template("trade.html", trade=trades[nummer - 1], titel="Trade")



@app.errorhandler(404)
def nicht_gefunden(fehler):
    return render_template("404.html",  title="ERROR"), 404



@app.route("/api/stats")
def api_stats():
    try: 
        pnls = [s['pnl'] for s in trades_mit_filter()]
        stats = statistik(pnls)

        pnl = stats["gesamt"]
        az_trades = stats["anzahl"]
        winrate = stats["winrate"]
        winner = stats["gewinner"]
        az_verlierer = stats["verlierer"]
        avg_gewinn = stats["avg_gewinn"]
        avg_verlust = stats["avg_verlust"]
        g_gewinn = stats["groesster_gewinn"]
        g_verlust = stats["groesster_verlust"]
        profit_faktor = stats["profit_faktor"]
    except ValueError:
        return {"fehler": "Statistik nicht gefunden "}, 404
    return {"gesamt": pnl, "anzahl": az_trades, "winrate": winrate, "gewinner": winner, "verlierer": az_verlierer,
             "avg_gewinn": avg_gewinn, "avg_verlust": avg_verlust, "groesster_gewinn":g_gewinn, "groesster_verlust": g_verlust,
             "profit_faktor": profit_faktor}


@app.route("/api/trades")
def api_trades():
    try:
        trades = trades_mit_filter()
        ticker = request.args.get("ticker")
    except ValueError as e:
        return {"fehler": str(e)}, 400

    if ticker is None:
        return trades

    if ticker not in PUNKTWERTE:
        return {"fehler": "Ticker nicht gefunden "}, 400

    treffer = [t for t in trades if t["ticker"] == ticker]
    return treffer



@app.route("/api/setups")
def api_trades_setup():
    try:
        trades = trades_mit_filter()
    except ValueError as e:
        return {"fehler": str(e)}, 400
    return jsonify(statistik_pro_setup(trades))


@app.route("/api/trade/<int:nummer>")
def api_trade_detail(nummer):
    trades = lade_trades()
    if nummer < 1 or nummer > len(trades):
        return {"fehler":"Unglültige nummer"}, 404

    return trades[nummer - 1]





@app.route("/api/trades", methods=["POST"])
def api_trade_neu():
    try: 
        trade = pruefe_trade(request.get_json())
    except ValueError as e:
        return {"fehler": str(e)}, 400
    speichere_trade(trade)
    return trade, 201



@app.route("/api/equity")
def api_equity():
    try: 
        trades = trades_mit_filter()
    except ValueError as e:
        return {"fehler": str(e)}, 400
    return jsonify(equity_kurve(trades))


if __name__ == "__main__":
    app.run(debug=True)


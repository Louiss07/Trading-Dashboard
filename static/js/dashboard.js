async function ladeTrades(ticker) {
    const antwort = await fetch(mitFilter("/api/trades", ticker));
    if (!antwort.ok) {
        throw new Error('Server meldet ${antwort.status}');
    }
    const trades = await antwort.json();
    return trades;

}

async function ladeStatistik(ticker) {
    const antwort = await fetch(mitFilter("/api/stats", ticker));
    if (!antwort.ok) {
        throw new Error(`Server meldet ${antwort.status}`);
    }
    const stats = await antwort.json();
    return stats;

}


async function ladeSetups(ticker) {
    const antwort = await fetch(mitFilter("/api/setups", ticker));
    if (!antwort.ok) {
        throw new Error(`Server meldet ${antwort.status}`);
    }
    const setups = await antwort.json();
    return setups;

}


async function ladeEquity(ticker) {
    const antwort = await fetch(mitFilter("/api/equity", ticker));
    if (!antwort.ok) {
        const info = await antwort.json();
        throw new Error(info.fehler);
    }
    const punkte = await antwort.json();
    return punkte
}


function zelleBauen(text) {
    const eintrag = document.createElement("td");

    eintrag.textContent = text;
    return eintrag
}


function tabelleZeichnen(trades) {
    const list = document.querySelector("#trade-liste");
    list.replaceChildren();
    for (const t of trades) {

        const link = document.createElement("a");
        link.href = `/trade/${t.id}`;
        link.textContent = t.datum;


        const zeile = document.createElement("tr");

        const datumZelle = document.createElement("td");
        datumZelle.append(link);


        zeile.append(datumZelle);
        zeile.append(zelleBauen(t.ticker));
        zeile.append(zelleBauen(t.setup));
        zeile.append(zelleBauen(t.richtung));
        const pnlZelle = zelleBauen(`${t.pnl.toFixed(2)} $`);

        pnlZelle.classList.remove("gewinn", "verlust")

        if (t.pnl > 0) {
            pnlZelle.classList.add("gewinn");
        }
        else {
            pnlZelle.classList.add("verlust");

        }
        zeile.append(pnlZelle);
        list.append(zeile);

        zeile.addEventListener("click", function (event) {
            zeile.classList.toggle("markiert");



        });


    }



}

function statsKarte(stats) {
    const AnzGesamtPnl = document.querySelector("#gesamt-pnl");
    const tabelleGesamtPnl = document.querySelector("#summe");
    const AnzWinrate = document.querySelector("#winrate");
    const AnzTrades = document.querySelector("#gesamt-trades");
    const gewinner = document.querySelector("#winner");
    const verlierer = document.querySelector("#verlierer");
    const avgGewinn = document.querySelector("#avg-w");
    const avgVerlust = document.querySelector("#avg-l");
    const GroessterW = document.querySelector("#gg");
    const GroessterL = document.querySelector("#gl");
    const profitFaktor = document.querySelector("#pf");
    const versteckKnopf = document.querySelector("#verstecken");
    const karte = document.querySelector("#inhaltKarte2")



    AnzGesamtPnl.textContent = `${stats.gesamt.toFixed(2)} $`;
    AnzWinrate.textContent = `${stats.winrate.toFixed(2)} %`;
    AnzTrades.textContent = `${stats.anzahl} `;
    gewinner.textContent = ` ${stats.gewinner}`;
    verlierer.textContent = `${stats.verlierer} `;
    avgGewinn.textContent = ` ${stats.avg_gewinn} $`;
    avgVerlust.textContent = `${stats.avg_verlust} $`;
    GroessterL.textContent = `${stats.groesster_verlust.toFixed(2)} $`;
    GroessterW.textContent = `${stats.groesster_gewinn.toFixed(2)} $`;
    profitFaktor.textContent = `x ${stats.profit_faktor.toFixed(2)} `;


    tabelleGesamtPnl.textContent = `${stats.gesamt.toFixed(2)} $`;

    tabelleGesamtPnl.classList.remove("gewinn", "verlust");
    if (stats.gesamt > 0) {
        tabelleGesamtPnl.classList.add("gewinn");
    }
    else {
        tabelleGesamtPnl.classList.add("verlust");

    }



    versteckKnopf.addEventListener("click", function () {

        const anzeigeK = karte.classList.toggle("versteckt");


        if (anzeigeK === true) {

            versteckKnopf.textContent = `Statistik Anzeigen`;
        } else {

            versteckKnopf.textContent = `Statistik Verstecken`;
        }

    });

}





async function start(ticker) {
    try {
        const trades = await ladeTrades(ticker);
        const stats = await ladeStatistik(ticker);
        const equity = await ladeEquity(ticker);
        const setups = await ladeSetups(ticker);
        tabelleZeichnen(trades);
        statsKarte(stats);
        diagrammZeichnen(equity);
        statTabelle(setups);
    } catch (fehler) {
        const fehlerFeld = document.querySelector("#fehler");
        fehlerFeld.textContent = "Trades konnten nicht geladen werden.";
        fehlerFeld.classList.remove("versteckt");
        console.error(fehler);
    }
}

start();



const formular = document.querySelector("#trade-form")



formular.addEventListener("submit", async function (event) {
    event.preventDefault();

    const neuerTrade = {
        datum: document.querySelector("#datum").value,
        ticker: document.querySelector("#ticker").value,
        setup: document.querySelector("#setup").value,
        richtung: document.querySelector('input[name="richtung"]:checked').value,
        einstieg: Number(document.querySelector("#einstieg").value),
        ausstieg: Number(document.querySelector("#ausstieg").value),
        stueckzahl: Number(document.querySelector("#stueckzahl").value),
    }

    try {
        await speichereTrades(neuerTrade);
        await start(filter.value);
        formular.reset();
    }
    catch (fehler) {
        const fehlerFeld = document.querySelector("#fehler");
        fehlerFeld.textContent = fehler.message;
        fehlerFeld.classList.remove("versteckt");
        console.error(fehler);
    }






})

async function speichereTrades(neuerTrade) {


    const antwort = await fetch("/api/trades", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(neuerTrade),




    });
    if (!antwort.ok) {
        const info = await antwort.json();
        throw new Error(info.fehler);

    }

}


let diagramm = null;




function diagrammZeichnen(punkte) {

    const canvas = document.querySelector("#equity-chart");

    if (diagramm) {
        diagramm.destroy();
    }

    diagramm = new Chart(canvas, {
        type: "line",
        data: {
            labels: punkte.map((p) => p.datum),
            datasets: [{
                label: "Equity",
                data: punkte.map((p) => p.equity),
                borderColor: "#FD91CC",
                backgroundColor: "rgba(214, 9, 122, 0.2)",
                fill: true,
                tension: 0.1,
            }],
        },
        options: {
            scales: {
                x: { ticks: { color: "white" } },
                y: { ticks: { color: "white" } },
            },
            plugins: { legend: { labels: { color: "white" } } },
        },
    });
}



function statTabelle(setups) {
    const list = document.querySelector("#setup-liste");
    list.replaceChildren();
    for (const t of setups) {


        const zeile = document.createElement("tr");




        zeile.append(zelleBauen(t.setup));
        zeile.append(zelleBauen(t.anzahl));
        const pnlZelle = zelleBauen(`${t.pnl.toFixed(2)} $`);



        pnlZelle.classList.remove("gewinn", "verlust")

        if (t.pnl > 0) {
            pnlZelle.classList.add("gewinn");
        }
        else {
            pnlZelle.classList.add("verlust");

        }
        zeile.append(pnlZelle);
        zeile.append(zelleBauen(t.winrate));
        list.append(zeile);

        zeile.addEventListener("click", function (event) {
            zeile.classList.toggle("markiert");

        });
    }
}

function mitFilter(pfad, ticker) {
    if (!ticker) {
        return pfad
    }
    return `${pfad}?ticker=${ticker}`;


}


const filter = document.querySelector("#ticker-filter");
filter.addEventListener("change", function () {
    start(filter.value);
});


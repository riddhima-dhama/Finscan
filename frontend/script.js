const API = "http://127.0.0.1:5000";

let transactions = [];
let transactionChart;
let fraudChart;


// ------------------------------------
// Load transactions
// ------------------------------------

async function loadTransactions() {

    try {

        const response = await fetch(
            `${API}/api/transactions`
        );

        transactions = await response.json();

        displayTransactions();

        loadStats();

        createCharts();

    } catch (error) {

        console.error(error);

        alert(
            "Cannot connect to FinScan backend. Make sure Flask is running."
        );
    }
}


// ------------------------------------
// Display transaction table
// ------------------------------------

function displayTransactions() {

    const table =
        document.getElementById("transactionTable");

    table.innerHTML = "";

    transactions.forEach(transaction => {

        const isFraud =
            transaction.symbol.includes("HF");

        const row =
            document.createElement("tr");

        row.innerHTML = `

            <td>${transaction.id}</td>

            <td>₹${transaction.amount.toLocaleString()}</td>

            <td>${transaction.type}</td>

            <td>${transaction.location}</td>

            <td>${transaction.timestamp}</td>

            <td>
                <span class="symbol">
                    ${transaction.symbol}
                </span>
            </td>

            <td class="${
                isFraud
                    ? "fraud-status"
                    : "normal-status"
            }">

                ${
                    isFraud
                        ? "FRAUD"
                        : "NORMAL"
                }

            </td>
        `;

        table.appendChild(row);

    });
}


// ------------------------------------
// Load statistics
// ------------------------------------

async function loadStats() {

    try {

        const response =
            await fetch(`${API}/api/stats`);

        const stats =
            await response.json();

        document.getElementById(
            "totalTransactions"
        ).textContent = stats.total;

        document.getElementById(
            "normalTransactions"
        ).textContent = stats.normal;

        document.getElementById(
            "fraudTransactions"
        ).textContent = stats.fraud;

    } catch (error) {

        console.error(error);

    }
}


// ------------------------------------
// Run fraud detection
// ------------------------------------

async function runDetection() {

    try {

        const response = await fetch(
            `${API}/api/detect`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    transactions: transactions
                })
            }
        );

        const result =
            await response.json();

        console.log(result);


        if (result.fraud) {

            document
                .getElementById("alertBox")
                .classList.remove("hidden");

            document.getElementById(
                "fraudRule"
            ).textContent = result.rule;

            document.getElementById(
                "symbolSequence"
            ).textContent =
                result.symbols.join(" → ");

        } else {

            document
                .getElementById("alertBox")
                .classList.add("hidden");

            alert("No fraud detected.");

        }

    } catch (error) {

        console.error(error);

        alert("Detection failed.");
    }
}


// ------------------------------------
// Charts
// ------------------------------------

function createCharts() {

    const normal =
        transactions.filter(
            t => !t.symbol.includes("HF")
        ).length;

    const fraud =
        transactions.filter(
            t => t.symbol.includes("HF")
        ).length;


    // Destroy old charts
    if (transactionChart) {
        transactionChart.destroy();
    }

    if (fraudChart) {
        fraudChart.destroy();
    }


    // Transaction chart

    const transactionCtx =
        document
            .getElementById("transactionChart")
            .getContext("2d");

    transactionChart =
        new Chart(transactionCtx, {

            type: "bar",

            data: {

                labels: [
                    "Normal",
                    "Fraud"
                ],

                datasets: [

                    {
                        label: "Transactions",

                        data: [
                            normal,
                            fraud
                        ]
                    }

                ]

            },

            options: {

                responsive: true,

                plugins: {
                    legend: {
                        display: false
                    }
                }

            }

        });


    // Fraud chart

    const fraudCtx =
        document
            .getElementById("fraudChart")
            .getContext("2d");

    fraudChart =
        new Chart(fraudCtx, {

            type: "doughnut",

            data: {

                labels: [
                    "Normal",
                    "Fraud"
                ],

                datasets: [

                    {
                        data: [
                            normal,
                            fraud
                        ]
                    }

                ]

            },

            options: {
                responsive: true
            }

        });

}


// ------------------------------------
// Start application
// ------------------------------------

loadTransactions();
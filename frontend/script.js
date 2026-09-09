const API_BASE = "http://127.0.0.1:5001/api";

let txChartInstance = null;
let fraudChartInstance = null;
let currentTransactions = [];

function renderCharts(normalCount, fraudCount, transactions) {
    if (typeof Chart === "undefined") return;

    const canvasFraud = document.getElementById("fraudChart");
    if (canvasFraud) {
        if (fraudChartInstance) fraudChartInstance.destroy();
        fraudChartInstance = new Chart(canvasFraud, {
            type: "doughnut",
            data: {
                labels: ["Normal", "Fraud"],
                datasets: [{
                    data: [normalCount, fraudCount],
                    backgroundColor: ["#10b981", "#ef4444"],
                    borderColor: "#1e293b",
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: false,
                plugins: { legend: { labels: { color: "#e2e8f0" } } }
            }
        });
    }

    const canvasTx = document.getElementById("transactionChart");
    if (canvasTx) {
        if (txChartInstance) txChartInstance.destroy();
        const labels = transactions.map((t, idx) => `ID ${t.id || idx + 1}`);
        const amounts = transactions.map(t => Number(t.amount || 0));
        
        txChartInstance = new Chart(canvasTx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Amount (₹)",
                    data: amounts,
                    backgroundColor: "#38bdf8",
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: false,
                scales: {
                    x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
                    y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } }
                },
                plugins: { legend: { labels: { color: "#e2e8f0" } } }
            }
        });
    }
}

async function loadAutomataDiagram() {
    try {
        const res = await fetch(`${API_BASE}/automata-diagram`);
        const data = await res.json();
        
        const viz = document.getElementById("state-diagram-viz");
        if (viz && data.transitions) {
            let traceStr = `DFA Formal Model: M = (Q, Σ, δ, q0, F)\nStates: { q0 (Start), q1, q2* (Fraud Trap Accept) }\n\nState Transitions δ:\n`;
            data.transitions.forEach(tr => {
                traceStr += `  δ(${tr.from}, '${tr.symbol}') ➔ ${tr.to}\n`;
            });
            viz.innerText = traceStr;
        }

        const rulesList = document.getElementById("automata-rules-list");
        if (rulesList && data.rules) {
            rulesList.innerHTML = "<strong>Active Automata Regex Rules:</strong> " + 
                data.rules.map(r => `<span style="background:#334155;padding:2px 6px;border-radius:4px;margin-right:6px;">${r.pattern}</span>`).join(" ");
        }
    } catch (e) {
        console.error("Failed to load diagram", e);
    }
}

function updateSequenceTracer(list) {
    const tracer = document.getElementById("sequence-tracer");
    if (!tracer) return;

    let traceText = "=== AUTOMATA EXECUTION TRACE ===\n";
    let state = "q0";
    
    list.forEach((item, index) => {
        const sym = Array.isArray(item.symbols) ? item.symbols.join("") : (item.symbols || "L");
        let nextState = "q0";
        if (sym.includes("H")) {
            nextState = (sym.includes("F") || sym.includes("O") || sym.includes("R")) ? "q2 (TRAP/ACCEPT)" : "q1";
        } else if (state === "q1" && (sym.includes("F") || sym.includes("O") || sym.includes("R"))) {
            nextState = "q2 (TRAP/ACCEPT)";
        }
        
        const status = item.fraud ? "[REJECT/FRAUD]" : "[ACCEPT/NORMAL]";
        traceText += `Step ${index + 1}: Symbol='${sym}' | State Transition: ${state} ➔ ${nextState} | ${status}\n`;
        state = nextState.includes("q2") ? "q0" : nextState;
    });

    tracer.innerText = traceText;
}

function renderRows(items) {
    const tableBody = document.getElementById("transactionTable") || document.querySelector("tbody");
    if (!tableBody) return;
    tableBody.innerHTML = "";

    items.forEach(item => {
        const t = item.transaction || item;
        const isFraud = Boolean(item.fraud);
        const sym = Array.isArray(item.symbols) ? item.symbols.join(", ") : (item.symbols || "-");
        
        let ruleText = "-";
        if (item.matched_rules && item.matched_rules.length > 0) {
            ruleText = item.matched_rules.map(r => (typeof r === "object" ? r.rule : r)).join(", ");
        } else if (isFraud) {
            ruleText = "Automata Pattern Triggered";
        }

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${t.id || "-"}</td>
            <td>₹${Number(t.amount || 0).toLocaleString()}</td>
            <td>${t.type || "purchase"}</td>
            <td>${t.country || t.location || "INDIA"}</td>
            <td>${t.timestamp ? t.timestamp.split(" ")[1] : "-"}</td>
            <td>${sym}</td>
            <td>
                <span class="badge ${isFraud ? 'badge-danger' : 'badge-success'}" style="background:${isFraud ? '#ef4444' : '#10b981'};color:#fff;padding:4px 8px;border-radius:4px;font-weight:bold;">
                    ${isFraud ? 'FRAUD' : 'NORMAL'}
                </span>
            </td>
            <td style="color:${isFraud ? '#f87171' : '#94a3b8'};font-size:0.9em;">${ruleText}</td>
        `;
        tableBody.appendChild(row);
    });
}

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const data = await res.json();
        
        const elTotal = document.getElementById("total-transactions");
        const elNormal = document.getElementById("normal-transactions");
        const elFraud = document.getElementById("fraud-transactions");
        
        const total = data.total ?? 0;
        const normal = data.normal ?? 0;
        const fraud = data.fraud ?? 0;

        if (elTotal) elTotal.innerText = total;
        if (elNormal) elNormal.innerText = normal;
        if (elFraud) elFraud.innerText = fraud;

        return { normal, fraud };
    } catch (err) {
        return { normal: 0, fraud: 0 };
    }
}

async function fetchTransactions() {
    try {
        const res = await fetch(`${API_BASE}/transactions`);
        currentTransactions = await res.json();
        renderRows(currentTransactions.map(t => ({ transaction: t, fraud: false, symbols: t.symbol || "L", matched_rules: [] })));
        
        const stats = await fetchStats();
        renderCharts(stats.normal, stats.fraud, currentTransactions);
    } catch (err) {
        console.error("Failed to load initial transactions", err);
    }
}

async function runDetection(txList = null) {
    const btn = document.querySelector("button[onclick='runDetection()']");
    try {
        if (btn) btn.innerText = "Analyzing...";
        const txs = txList || currentTransactions;
        
        const detectRes = await fetch(`${API_BASE}/detect`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ transactions: txs })
        });
        const resultData = await detectRes.json();
        const list = resultData.transactions || [];
        
        renderRows(list);
        updateSequenceTracer(list);
        
        const stats = await fetchStats();
        const rawTxs = list.map(item => item.transaction || item);
        renderCharts(stats.normal, stats.fraud, rawTxs);
    } catch (err) {
        console.error("Detection error:", err);
    } finally {
        if (btn) btn.innerText = "Run Fraud Detection";
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async function(e) {
        try {
            const data = JSON.parse(e.target.result);
            currentTransactions = Array.isArray(data) ? data : (data.transactions || []);
            renderRows(currentTransactions.map(t => ({ transaction: t, fraud: false, symbols: t.symbol || "-", matched_rules: [] })));
            runDetection(currentTransactions);
        } catch (err) {
            alert("Invalid JSON format");
        }
    };
    reader.readAsText(file);
}

document.addEventListener("DOMContentLoaded", () => {
    fetchTransactions();
    loadAutomataDiagram();
});

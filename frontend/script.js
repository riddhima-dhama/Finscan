// =========================================================
// FinScan - Frontend JavaScript
// =========================================================

const API_BASE = "http://127.0.0.1:5001/api";

let txChartInstance = null;
let fraudChartInstance = null;
let currentTransactions = [];


// =========================================================
// HTML ESCAPE
// =========================================================

function escapeHtml(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// =========================================================
// GRAPHVIZ ESCAPE
// =========================================================

function escapeDot(value) {

    return String(value ?? "")
        .replace(/\\/g, "\\\\")
        .replace(/"/g, '\\"')
        .replace(/\r?\n/g, "\\n");
}


// =========================================================
// GRAPH MESSAGE
// =========================================================

function setGraphMessage(containerId, message) {

    const container =
        document.getElementById(containerId);

    if (!container) return;

    container.innerHTML = `
        <div class="graph-placeholder">
            ${escapeHtml(message)}
        </div>
    `;
}


// =========================================================
// GENERATE AUTOMATA
// =========================================================

async function generateAutomata() {

    const input =
        document.getElementById("regex-input");

    const button =
        document.getElementById(
            "generate-automata-btn"
        );

    if (!input || !button) {

        console.error(
            "Regex input or Generate button not found."
        );

        return;
    }


    const regex =
        input.value.trim();


    if (!regex) {

        alert(
            "Please enter a regular expression."
        );

        return;
    }


    button.disabled = true;
    button.innerText = "Generating...";


    setGraphMessage(
        "nfa-graph",
        "Building NFA..."
    );

    setGraphMessage(
        "dfa-graph",
        "Building DFA..."
    );

    setGraphMessage(
        "min-dfa-graph",
        "Building Minimized DFA..."
    );


    try {

        const response =
            await fetch(
                `${API_BASE}/automata/visualize`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        regex: regex
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Automata generation failed."
            );
        }


        console.log(
            "Automata generated:",
            data
        );


        // =================================================
        // STATE COUNTS
        // =================================================

        const nfaCount =
            document.getElementById(
                "nfa-count"
            );

        const dfaCount =
            document.getElementById(
                "dfa-count"
            );

        const minDfaCount =
            document.getElementById(
                "min-dfa-count"
            );


        if (nfaCount) {

            nfaCount.innerText =
                data.statistics.nfa_states;
        }


        if (dfaCount) {

            dfaCount.innerText =
                data.statistics.dfa_states;
        }


        if (minDfaCount) {

            minDfaCount.innerText =
                data.statistics.min_dfa_states;
        }


        // =================================================
        // RENDER NFA
        // =================================================

        await renderAutomataGraph(
            "nfa-graph",
            data.nfa,
            "NFA"
        );


        // =================================================
        // RENDER DFA
        // =================================================

        await renderAutomataGraph(
            "dfa-graph",
            data.dfa,
            "DFA"
        );


        // =================================================
        // RENDER MIN DFA
        // =================================================

        await renderAutomataGraph(
            "min-dfa-graph",
            data.min_dfa,
            "Minimized DFA"
        );


    } catch (error) {

        console.error(
            "Automata generation error:",
            error
        );


        setGraphMessage(
            "nfa-graph",
            "Error: " + error.message
        );

        setGraphMessage(
            "dfa-graph",
            "Error: " + error.message
        );

        setGraphMessage(
            "min-dfa-graph",
            "Error: " + error.message
        );


    } finally {

        button.disabled = false;

        button.innerText =
            "Generate Automata";
    }
}


// =========================================================
// AUTOMATA GRAPH RENDERER
// =========================================================

async function renderAutomataGraph(
    containerId,
    graph,
    title
) {

    const container =
        document.getElementById(
            containerId
        );


    if (!container) {

        console.error(
            `Container ${containerId} not found.`
        );

        return;
    }


    if (typeof Viz === "undefined") {

        container.innerHTML = `
            <div class="graph-error">
                Viz.js failed to load.
            </div>
        `;

        return;
    }


    if (
        !graph ||
        !Array.isArray(graph.nodes) ||
        !Array.isArray(graph.edges)
    ) {

        container.innerHTML = `
            <div class="graph-error">
                ${escapeHtml(title)}
                data unavailable.
            </div>
        `;

        return;
    }


    try {

        // =================================================
        // GRAPHVIZ DOT
        // =================================================

        let dot = `
            digraph FinScan {

                graph [

                    rankdir=LR,

                    bgcolor="transparent",

                    margin="0.1",

                    pad="0.2",

                    nodesep="0.65",

                    ranksep="0.9",

                    splines=true,

                    overlap=false,

                    outputorder=edgesfirst

                ];


                node [

                    shape=circle,

                    style="filled",

                    fillcolor="white",

                    color="#172033",

                    fontcolor="#172033",

                    fontname="Arial",

                    fontsize=19,

                    penwidth=2.5,

                    margin="0.12,0.08"

                ];


                edge [

                    color="#172033",

                    fontcolor="#172033",

                    fontname="Arial",

                    fontsize=17,

                    penwidth=2,

                    arrowsize=0.8

                ];
        `;


        // =================================================
        // START ARROW
        // =================================================

        const startNode =
            graph.nodes.find(
                node => node.is_start
            );


        if (startNode) {

            dot += `

                start [

                    shape=point,

                    width=0.12,

                    height=0.12,

                    label="",

                    color="#172033",

                    fillcolor="#172033"

                ];


                start -> "${escapeDot(
                    startNode.id
                )}";

            `;
        }


        // =================================================
        // STATES
        // =================================================

        graph.nodes.forEach(node => {

            let label =
                node.label ||
                node.id;


            /*
             * Convert escaped newline
             * into Graphviz newline.
             */

            label = String(label)
                .replace(/\\\\n/g, "\\n");


            const shape =
                node.is_final
                    ? "doublecircle"
                    : "circle";


            dot += `

                "${escapeDot(
                    node.id
                )}" [

                    label="${escapeDot(
                        label
                    )}",

                    shape=${shape},

                    width=1.0,

                    height=1.0

                ];

            `;
        });


        // =================================================
        // TRANSITIONS
        // =================================================

        graph.edges.forEach(edge => {

            const from =
                escapeDot(edge.from);

            const to =
                escapeDot(edge.to);

            const label =
                escapeDot(
                    edge.label || ""
                );


            dot += `

                "${from}" -> "${to}" [

                    label="${label}"

                ];

            `;
        });


        dot += `

            }

        `;


        console.log(
            `${title} DOT:`,
            dot
        );


        // =================================================
        // RENDER SVG
        // =================================================

        const viz =
            new Viz();


        const svg =
            await viz.renderSVGElement(
                dot
            );


        // =================================================
        // SVG SIZE
        // =================================================

        svg.removeAttribute("width");

        svg.removeAttribute("height");


        svg.setAttribute(
            "width",
            "100%"
        );

        svg.setAttribute(
            "height",
            "100%"
        );

        svg.setAttribute(
            "preserveAspectRatio",
            "xMidYMid meet"
        );


        // =================================================
        // DISPLAY
        // =================================================

        container.innerHTML = "";

        container.appendChild(svg);


    } catch (error) {

        console.error(
            `${title} rendering error:`,
            error
        );


        container.innerHTML = `

            <div class="graph-error">

                <strong>
                    ${escapeHtml(title)}
                    rendering failed
                </strong>

                <br><br>

                <small>
                    ${escapeHtml(
                        error.message
                    )}
                </small>

            </div>

        `;
    }
}


// =========================================================
// FETCH TRANSACTIONS
// =========================================================

async function fetchTransactions() {

    try {

        const response =
            await fetch(
                `${API_BASE}/transactions`
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load transactions."
            );
        }


        currentTransactions =
            await response.json();


        renderRows(
            currentTransactions.map(
                transaction => ({

                    transaction:
                        transaction,

                    fraud: false,

                    symbols:
                        transaction.symbol ||
                        "-",

                    matched_rules: [],

                    execution_trace: []

                })
            )
        );


        await fetchStats();


    } catch (error) {

        console.error(
            "Transaction loading error:",
            error
        );
    }
}


// =========================================================
// FETCH STATISTICS
// =========================================================

async function fetchStats() {

    try {

        const response =
            await fetch(
                `${API_BASE}/stats`
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load statistics."
            );
        }


        const data =
            await response.json();


        const total =
            data.total || 0;

        const normal =
            data.normal || 0;

        const fraud =
            data.fraud || 0;


        const totalElement =
            document.getElementById(
                "total-transactions"
            );

        const normalElement =
            document.getElementById(
                "normal-transactions"
            );

        const fraudElement =
            document.getElementById(
                "fraud-transactions"
            );


        if (totalElement) {

            totalElement.innerText =
                total;
        }


        if (normalElement) {

            normalElement.innerText =
                normal;
        }


        if (fraudElement) {

            fraudElement.innerText =
                fraud;
        }


        renderCharts(
            normal,
            fraud,
            currentTransactions
        );


        return {
            total,
            normal,
            fraud
        };


    } catch (error) {

        console.error(
            "Stats error:",
            error
        );


        return {
            total: 0,
            normal: 0,
            fraud: 0
        };
    }
}


// =========================================================
// FRAUD DETECTION
// =========================================================

async function runDetection(
    txList = null
) {

    const button =
        document.querySelector(
            ".primary-button"
        );


    try {

        if (button) {

            button.disabled = true;

            button.innerText =
                "Analyzing...";
        }


        const transactions =
            txList ||
            currentTransactions;


        const response =
            await fetch(
                `${API_BASE}/detect`,
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        transactions:
                            transactions

                    })

                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.error ||
                "Detection failed."
            );
        }


        renderRows(
            result.transactions || []
        );


        updateSequenceTracer(
            result.transactions || []
        );


        // =================================================
        // RESULT BOX
        // =================================================

        const resultBox =
            document.getElementById(
                "detection-result"
            );


        const status =
            document.getElementById(
                "detection-status"
            );


        const rule =
            document.getElementById(
                "detection-rule"
            );


        if (resultBox) {

            resultBox.classList.remove(
                "hidden"
            );
        }


        if (status) {

            status.innerText =
                result.fraud
                    ? "FRAUD DETECTED"
                    : "NO FRAUD";


            status.className =
                result.fraud
                    ? "danger-text"
                    : "success-text";
        }


        if (rule) {

            rule.innerText =
                result.rule ||
                "No matching rule";
        }


        await fetchStats();


    } catch (error) {

        console.error(
            "Detection error:",
            error
        );


        alert(
            "Detection failed: " +
            error.message
        );


    } finally {

        if (button) {

            button.disabled = false;

            button.innerText =
                "Run Fraud Detection";
        }
    }
}


// =========================================================
// RENDER TRANSACTION TABLE
// =========================================================

function renderRows(items) {

    const tableBody =
        document.getElementById(
            "transactionTable"
        );


    if (!tableBody) return;


    tableBody.innerHTML = "";


    items.forEach(item => {

        const transaction =
            item.transaction ||
            item;


        const isFraud =
            Boolean(item.fraud);


        let symbols = "-";


        if (
            Array.isArray(item.symbols)
        ) {

            symbols =
                item.symbols.join("");

        } else if (
            item.symbols
        ) {

            symbols =
                item.symbols;

        } else if (
            transaction.symbol
        ) {

            symbols =
                transaction.symbol;
        }


        let ruleText = "—";


        if (
            item.matched_rules &&
            item.matched_rules.length > 0
        ) {

            ruleText =
                item.matched_rules
                    .map(rule => {

                        if (
                            typeof rule ===
                            "object"
                        ) {

                            return (
                                rule.rule ||
                                rule.name ||
                                "Matched Rule"
                            );
                        }

                        return rule;

                    })
                    .join(", ");
        }


        const amount =
            Number(
                transaction.amount ||
                0
            );


        let time = "-";


        if (
            transaction.timestamp
        ) {

            const parts =
                String(
                    transaction.timestamp
                ).split(" ");


            time =
                parts.length > 1
                    ? parts[1]
                    : parts[0];

        } else if (
            transaction.time
        ) {

            time =
                transaction.time;
        }


        const row =
            document.createElement(
                "tr"
            );


        row.innerHTML = `

            <td>
                ${escapeHtml(
                    transaction.id || "-"
                )}
            </td>


            <td>
                ₹${amount.toLocaleString()}
            </td>


            <td>
                ${escapeHtml(
                    transaction.type ||
                    transaction.transaction_type ||
                    "Purchase"
                )}
            </td>


            <td>
                ${escapeHtml(
                    transaction.country ||
                    transaction.location ||
                    "India"
                )}
            </td>


            <td>
                ${escapeHtml(time)}
            </td>


            <td>
                <span class="symbol-badge">
                    ${escapeHtml(symbols)}
                </span>
            </td>


            <td>

                <span class="
                    status-badge
                    ${
                        isFraud
                            ? "fraud-badge"
                            : "normal-badge"
                    }
                ">

                    ${
                        isFraud
                            ? "FRAUD"
                            : "NORMAL"
                    }

                </span>

            </td>


            <td class="
                rule-cell
                ${
                    isFraud
                        ? "fraud-rule"
                        : ""
                }
            ">

                ${escapeHtml(ruleText)}

            </td>

        `;


        tableBody.appendChild(
            row
        );

    });
}


// =========================================================
// EXECUTION TRACE
// =========================================================

function updateSequenceTracer(list) {

    const tracer =
        document.getElementById(
            "sequence-tracer"
        );


    if (!tracer) return;


    let output =
        "AUTOMATA EXECUTION TRACE\n";

    output +=
        "=========================\n\n";


    list.forEach((item, index) => {

        const transaction =
            item.transaction || {};


        const symbols =
            Array.isArray(item.symbols)
                ? item.symbols.join("")
                : (
                    item.symbols ||
                    transaction.symbol ||
                    "-"
                );


        const fraud =
            Boolean(item.fraud);


        output +=
            `Transaction ${
                transaction.id ||
                index + 1
            }\n`;


        output +=
            `  Input Symbol : ${symbols}\n`;


        output +=
            `  Start State  : D0\n`;


        // =================================================
        // FRAUD
        // =================================================

        if (
            fraud &&
            Array.isArray(
                item.execution_trace
            ) &&
            item.execution_trace.length > 0
        ) {

            item.execution_trace.forEach(
                traceItem => {

                    output += "\n";


                    output +=
                        `  Rule         : ${
                            traceItem.rule ||
                            "Matched Rule"
                        }\n`;


                    output +=
                        `  Pattern      : ${
                            traceItem.pattern ||
                            "-"
                        }\n`;


                    output +=
                        `  Path         : ${
                            traceItem.path ||
                            "D0"
                        }\n`;


                    output +=
                        `  Final State  : ${
                            traceItem.final_state ||
                            "D0"
                        }\n`;


                    output +=
                        `  Result       : FRAUD / ACCEPT\n`;
                }
            );


        } else {

            // =================================================
            // NORMAL
            // =================================================

            output +=
                `  Result       : NORMAL / REJECT\n`;
        }


        output += "\n";

    });


    tracer.innerText =
        output;
}


// =========================================================
// JSON FILE UPLOAD
// =========================================================

function handleFileUpload(event) {

    const file =
        event.target.files[0];


    if (!file) return;


    const reader =
        new FileReader();


    reader.onload =
        function(event) {

            try {

                const data =
                    JSON.parse(
                        event.target.result
                    );


                if (
                    Array.isArray(data)
                ) {

                    currentTransactions =
                        data;

                } else {

                    currentTransactions =
                        data.transactions ||
                        [];
                }


                renderRows(
                    currentTransactions.map(
                        transaction => ({

                            transaction:
                                transaction,

                            fraud: false,

                            symbols:
                                transaction.symbol ||
                                "-",

                            matched_rules: [],

                            execution_trace: []

                        })
                    )
                );


                runDetection(
                    currentTransactions
                );


            } catch (error) {

                console.error(
                    error
                );


                alert(
                    "Invalid JSON file."
                );
            }
        };


    reader.readAsText(file);
}


// =========================================================
// CHARTS
// =========================================================

function renderCharts(
    normalCount,
    fraudCount,
    transactions
) {

    if (
        typeof Chart ===
        "undefined"
    ) {

        return;
    }


    // =====================================================
    // FRAUD CHART
    // =====================================================

    const fraudCanvas =
        document.getElementById(
            "fraudChart"
        );


    if (fraudCanvas) {

        if (
            fraudChartInstance
        ) {

            fraudChartInstance.destroy();
        }


        fraudChartInstance =
            new Chart(
                fraudCanvas,
                {

                    type: "doughnut",

                    data: {

                        labels: [
                            "Normal",
                            "Fraud"
                        ],

                        datasets: [{

                            data: [
                                normalCount,
                                fraudCount
                            ],

                            backgroundColor: [
                                "#10b981",
                                "#ef4444"
                            ],

                            borderColor:
                                "#0f172a",

                            borderWidth: 3

                        }]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        plugins: {

                            legend: {

                                labels: {

                                    color:
                                        "#cbd5e1"
                                }
                            }
                        }
                    }
                }
            );
    }


    // =====================================================
    // TRANSACTION AMOUNT CHART
    // =====================================================

    const transactionCanvas =
        document.getElementById(
            "transactionChart"
        );


    if (transactionCanvas) {

        if (
            txChartInstance
        ) {

            txChartInstance.destroy();
        }


        const labels =
            transactions.map(
                (transaction, index) => {

                    return `ID ${
                        transaction.id ||
                        index + 1
                    }`;
                }
            );


        const amounts =
            transactions.map(
                transaction => {

                    return Number(
                        transaction.amount ||
                        0
                    );
                }
            );


        txChartInstance =
            new Chart(
                transactionCanvas,
                {

                    type: "bar",

                    data: {

                        labels:
                            labels,

                        datasets: [{

                            label:
                                "Amount (₹)",

                            data:
                                amounts,

                            backgroundColor:
                                "#38bdf8",

                            borderRadius:
                                5

                        }]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        scales: {

                            x: {

                                ticks: {

                                    color:
                                        "#94a3b8"
                                },

                                grid: {

                                    color:
                                        "#1e293b"
                                }
                            },

                            y: {

                                ticks: {

                                    color:
                                        "#94a3b8"
                                },

                                grid: {

                                    color:
                                        "#1e293b"
                                }
                            }
                        },

                        plugins: {

                            legend: {

                                labels: {

                                    color:
                                        "#cbd5e1"
                                }
                            }
                        }
                    }
                }
            );
    }
}


// =========================================================
// REGEX ENTER KEY
// =========================================================

document.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key !== "Enter"
        ) {

            return;
        }


        const active =
            document.activeElement;


        if (
            active &&
            active.id ===
            "regex-input"
        ) {

            generateAutomata();
        }
    }
);


// =========================================================
// PAGE LOAD
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    async function() {

        console.log(
            "FinScan frontend loaded."
        );


        // =================================================
        // LOAD TRANSACTIONS
        // =================================================

        await fetchTransactions();


        // =================================================
        // DEFAULT REGEX
        // =================================================

        const input =
            document.getElementById(
                "regex-input"
            );


        if (
            input &&
            !input.value.trim()
        ) {

            input.value = "01";
        }


        // =================================================
        // GENERATE AUTOMATA
        // =================================================

        await generateAutomata();

    }
);
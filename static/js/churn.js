document.addEventListener("DOMContentLoaded", function () {
    // Probability slider logic for filtering table
    const slider = document.getElementById("probability-slider");
    const valueSpan = document.getElementById("probability-value");
    const resultsBody = document.getElementById("results-body");
    const totalBox = document.getElementById("total-customers");
    const predictedChurnBox = document.getElementById("predicted-churn");

    // Always show total number of customers in the database (not filtered by slider)
    fetch("/api/customers")
        .then(response => response.json())
        .then(data => {
            totalBox.textContent = Array.isArray(data) ? data.length : (data.error ? 'Error' : '0');
        })
        .catch(error => {
            totalBox.textContent = "Error";
        });

    function loadCustomers(threshold) {
        fetch(`/api/customers/predicted?threshold=${threshold}`)
            .then(response => response.json())
            .then(data => {
                // Filter for customers who are likely to leave (prediction == 1) for the table and metric box
                const filtered = Array.isArray(data) ? data.filter(c => c.prediction === 1) : [];
                // Update predicted-churn metric box to show only those with prediction == 1 and Churn_Probability >= threshold
                predictedChurnBox.textContent = filtered.length;

                resultsBody.innerHTML = "";
                if (filtered.length === 0) {
                    resultsBody.innerHTML = `<tr><td colspan=\"23\" style=\"text-align:center; color: #666;\">No customers found above this probability.</td></tr>`;
                    return;
                }
                for (const customer of filtered) {
                    const prob = customer.Churn_Probability !== null
                        ? (parseFloat(customer.Churn_Probability) * 100).toFixed(2) + "%"
                        : "N/A";
                    const predictionLabel = `<span class=\"text-red-600\">Customer will leave</span>`;
                    const row = `
                        <tr class=\"border-b hover:bg-gray-50\">\n                            <td class=\"p-3\">${customer.Customer_ID}</td>\n                            <td class=\"p-3\">${customer.Age}</td>\n                            <td class=\"p-3\">${customer.Gender}</td>\n                            <td class=\"p-3\">${customer.District}</td>\n                            <td class=\"p-3\">${customer.Region}</td>\n                            <td class=\"p-3\">${customer['Location_Type']}</td>\n                            <td class=\"p-3\">${customer['Customer_Type']}</td>\n                            <td class=\"p-3\">${customer['Employment_Status']}</td>\n                            <td class=\"p-3\">${customer['Income_Level']}</td>\n                            <td class=\"p-3\">${customer['Education_Level']}</td>\n                            <td class=\"p-3\">${customer.Tenure}</td>\n                            <td class=\"p-3\">${customer.Balance}</td>\n                            <td class=\"p-3\">${customer['Credit_Score']}</td>\n                            <td class=\"p-3\">${customer['Outstanding_Loans']}</td>\n                            <td class=\"p-3\">${customer['Num_Of_Products']}</td>\n                            <td class=\"p-3\">${customer['Mobile_Banking_Usage']}</td>\n                            <td class=\"p-3\">${customer['Number_of_Transactions_per_Month']}</td>\n                            <td class=\"p-3\">${customer['Num_Of_Complaints']}</td>\n                            <td class=\"p-3\">${customer['Proximity_to_NearestBranch_or_ATM_km']}</td>\n                            <td class=\"p-3\">${customer['Mobile_Network_Quality']}</td>\n                            <td class=\"p-3\">${customer['Owns_Mobile_Phone']}</td>\n                            <td class=\"p-3\">${predictionLabel}</td>\n                            <td class=\"p-3\">${prob}</td>\n                        </tr>\n                    `;
                    resultsBody.insertAdjacentHTML("beforeend", row);
                }
            })
            .catch(error => {
                predictedChurnBox.textContent = "Error";
                resultsBody.innerHTML = `<tr><td colspan=\"23\" class=\"text-red-600 p-3\">Error loading data.</td></tr>`;
            });
    }
    // Initial load
    loadCustomers(slider.value);
    slider.addEventListener("input", () => {
        valueSpan.textContent = slider.value + "%";
        loadCustomers(slider.value);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    fetch('/api/customers/churn_summary')
        .then(response => response.json())
        .then(data => {
            buildChurnCharts(data);
        })
        .catch(error => {
            console.error("Error loading churn summary:", error);
            document.getElementById("churn-summary-charts").textContent = "Failed to load summary.";
        });
});

function buildChurnCharts(summary) {
    const container = document.getElementById("churn-summary-charts");
    container.innerHTML = "";

    for (const [attr, rows] of Object.entries(summary)) {
        const canvas = document.createElement("canvas");
        canvas.style.marginBottom = "30px";

        const h4 = document.createElement("h4");
        h4.textContent = attr.replace(/_/g, " ");

        container.appendChild(h4);
        container.appendChild(canvas);

        const labels = rows.map(r => String(r.value));
        const values = rows.map(r => parseFloat(r.percentage.toFixed(2)));

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "% of churners",
                    data: values,
                    backgroundColor: "rgba(255, 99, 132, 0.6)"
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => context.parsed.y + "%"
                        }
                    },
                    title: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: { display: true, text: "% churn" }
                    }
                }
            }
        });
    }
}

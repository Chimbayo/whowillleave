document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/customers")
        .then(response => response.json())
        .then(data => {
            renderCustomerTable(data.customers);
        })
        .catch(err => {
            console.error(err);
            document.getElementById("results-body").innerHTML = `
                <tr><td colspan="24">Failed to load customer data.</td></tr>
            `;
        });
});

function renderCustomerTable(customers) {
    const tbody = document.getElementById("results-body");
    tbody.innerHTML = "";

    customers.forEach(customer => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td class="p-3">${customer.Customer_ID}</td>
            <td class="p-3">${customer.Age}</td>
            <td class="p-3">${customer.Gender}</td>
            <td class="p-3">${customer.District}</td>
            <td class="p-3">${customer.Region}</td>
            <td class="p-3">${customer["Location_Type"]}</td>
            <td class="p-3">${customer["Customer_Type"]}</td>
            <td class="p-3">${customer["Employment_Status"]}</td>
            <td class="p-3">${customer["Income_Level"]}</td>
            <td class="p-3">${customer["Education_Level"]}</td>
            <td class="p-3">${customer.Tenure}</td>
            <td class="p-3">${customer.Balance}</td>
            <td class="p-3">${customer["Credit_Score"]}</td>
            <td class="p-3">${customer["Outstanding_Loans"]}</td>
            <td class="p-3">${customer["Num_Of_Products"]}</td>
            <td class="p-3">${customer["Mobile_Banking_Usage"]}</td>
            <td class="p-3">${customer["Number_of_Transactions_per_Month"]}</td>
            <td class="p-3">${customer["Num_Of_Complaints"]}</td>
            <td class="p-3">${customer["Proximity_to_NearestBranch_or_ATM_km"]}</td>
            <td class="p-3">${customer["Mobile_Network_Quality"]}</td>
            <td class="p-3">${customer["Owns_Mobile_Phone"]}</td>
            <td class="p-3">${customer.prediction}</td>
            <td class="p-3">${(customer.Churn_Probability * 100).toFixed(2)}%</td>
        `;
        tbody.appendChild(row);
    });
}

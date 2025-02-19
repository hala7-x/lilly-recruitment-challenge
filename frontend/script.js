document.addEventListener('DOMContentLoaded', function () {
    fetchMedicines();  // Load medicines on page load

    // Objective 1: Fetch medicines and display in the table
    function fetchMedicines() {
        fetch('http://127.0.0.1:8000/medicines')
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector('#medicineTable tbody');
                tableBody.innerHTML = '';  // Clear existing rows

                if (!data.medicines || !Array.isArray(data.medicines)) {
                    console.error('Invalid data format:', data);
                    tableBody.innerHTML = '<tr><td colspan="2">Error loading medicines.</td></tr>';
                    return;
                }

                data.medicines.forEach(medicine => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${medicine.name ? medicine.name : 'No Medicine Name'}</td>
                        <td>${medicine.price ? `$${parseFloat(medicine.price).toFixed(2)}` : 'Price Unavailable'}</td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error fetching medicines:', error);
                document.querySelector('#medicineTable tbody').innerHTML = '<tr><td colspan="2">Failed to load medicines.</td></tr>';
            });
    }

    // Objective 3: Handle form submission to create new medicine
    document.getElementById('medicineForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const nameInput = document.getElementById('nameInput').value.trim();
        const priceInput = document.getElementById('priceInput').value.trim();

        // Validate inputs
        if (!nameInput || !priceInput || isNaN(priceInput) || parseFloat(priceInput) <= 0) {
            alert('Please enter a valid medicine name and price.');
            return;
        }

        // Send data to backend
        fetch('http://127.0.0.1:8000/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                name: nameInput,
                price: priceInput,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showPopup(data.message);
                fetchMedicines();  // Refresh table
            } else {
                alert('Failed to add medicine.');
            }
        })
        .catch(error => {
            console.error('Error adding medicine:', error);
            alert('Failed to add medicine.');
        });
    });

    // Get Average Price button
    document.getElementById("getAvgPriceBtn").addEventListener("click", fetchAveragePrice);
});

// Fetch and display the average price when the button is clicked
function fetchAveragePrice() {
    fetch('http://127.0.0.1:8000/average_price')
        .then(response => response.json())
        .then(data => {
            const avgPriceElement = document.getElementById("averagePrice");
            
            if (data.average_price && !isNaN(data.average_price)) {
                avgPriceElement.textContent = `Average Price: $${parseFloat(data.average_price).toFixed(2)}`;
            } else {
                avgPriceElement.textContent = "No valid prices available";
            }
        })
        .catch(error => {
            console.error('Error fetching average price:', error);
            document.getElementById("averagePrice").textContent = "Error fetching average price.";
        });
}

// Show popup message
function showPopup(message) {
    document.getElementById('popupMessage').textContent = message;
    document.getElementById('popup').style.display = 'block';
}

// Close popup
function closePopup() {
    document.getElementById('popup').style.display = 'none';
}

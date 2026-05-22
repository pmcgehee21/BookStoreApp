
// -------------------------------------------------
// INK AND LEATHER BOOKSTORE APP
// Vendor Order Management System
// -------------------------------------------------

const vendorOrderForm = document.getElementById('vendorOrderForm');
const ordersTableBody = document.getElementById('ordersTableBody');

// Load existing orders from local storage
let vendorOrders = JSON.parse(localStorage.getItem('vendorOrders')) || [];

// -------------------------------------------------
// DISPLAY ORDERS
// -------------------------------------------------

function displayOrders() {

    ordersTableBody.innerHTML = '';

    vendorOrders.forEach((order) => {

        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${order.id}</td>
            <td>${order.vendorName}</td>
            <td>${order.bookTitle}</td>
            <td>${order.quantity}</td>
            <td>${order.status}</td>

            <td>
                <select onchange="updateStatus(${order.id}, this.value)">
                    <option value="Pending" ${order.status === 'Pending' ? 'selected' : ''}>Pending</option>
                    <option value="Processing" ${order.status === 'Processing' ? 'selected' : ''}>Processing</option>
                    <option value="Shipped" ${order.status === 'Shipped' ? 'selected' : ''}>Shipped</option>
                    <option value="Delivered" ${order.status === 'Delivered' ? 'selected' : ''}>Delivered</option>
                    <option value="Cancelled" ${order.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
                </select>
            </td>

            <td>
                <button onclick="deleteOrder(${order.id})">
                    Delete
                </button>
            </td>
        `;

        ordersTableBody.appendChild(row);

    });
}

// -------------------------------------------------
// ADD NEW ORDER
// -------------------------------------------------

vendorOrderForm.addEventListener('submit', function(event) {

    event.preventDefault();

    const vendorName = document.getElementById('vendorName').value;
    const bookTitle = document.getElementById('bookTitle').value;
    const quantity = document.getElementById('quantity').value;

    const newOrder = {
        id: Date.now(),
        vendorName,
        bookTitle,
        quantity,
        status: 'Pending'
    };

    vendorOrders.push(newOrder);

    saveOrders();
    displayOrders();

    vendorOrderForm.reset();
});

// -------------------------------------------------
// UPDATE ORDER STATUS
// -------------------------------------------------

function updateStatus(orderId, newStatus) {

    vendorOrders = vendorOrders.map((order) => {

        if (order.id === orderId) {
            order.status = newStatus;
        }

        return order;
    });

    saveOrders();
    displayOrders();
}

// -------------------------------------------------
// DELETE ORDER
// -------------------------------------------------

function deleteOrder(orderId) {

    vendorOrders = vendorOrders.filter(
        order => order.id !== orderId
    );

    saveOrders();
    displayOrders();
}

// -------------------------------------------------
// SAVE ORDERS
// -------------------------------------------------

function saveOrders() {

    localStorage.setItem(
        'vendorOrders',
        JSON.stringify(vendorOrders)
    );
}

// -------------------------------------------------
// INITIAL DISPLAY
// -------------------------------------------------

displayOrders();

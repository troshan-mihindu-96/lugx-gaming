const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware to parse JSON bodies
app.use(express.json());

// Serve static files from the current directory (for index.html, CSS, etc.)
app.use(express.static('.'));

// API endpoint for games
app.get('/api/games', (req, res) => {
    // You'll need to replace this with a real database query later
    const games = [
        { id: 1, name: 'Adventure Game', category: 'Adventure', price: 19.99, release_date: '2023-01-15' },
        { id: 2, name: 'Racing Simulator', category: 'Racing', price: 29.99, release_date: '2022-05-20' }
    ];
    res.json(games);
});

// API endpoint for recent orders
app.get('/api/orders', (req, res) => {
    const orders = [
        { id: 101, customer_name: 'John Doe', total_price: 49.98, order_date: '2025-08-01' },
        { id: 102, customer_name: 'Jane Smith', total_price: 29.99, order_date: '2025-08-05' }
    ];
    res.json(orders);
});

// API endpoint for analytics tracking
app.post('/api/analytics/track', (req, res) => {
    const { event_type, page, timestamp } = req.body;
    console.log(`Analytics Event: ${event_type} on ${page} at ${timestamp}`);
    res.status(200).send({ message: "Event tracked successfully" });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
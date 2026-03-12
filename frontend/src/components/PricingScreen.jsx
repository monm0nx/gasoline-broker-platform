import React, { useEffect, useState } from 'react';

const PricingScreen = () => {
    const [marketData, setMarketData] = useState([]);
    const [time, setTime] = useState(new Date().toISOString());

    useEffect(() => {
        const fetchData = async () => {
            // Here, replace with your logic to fetch data
            const data = await fetchMarketData();
            setMarketData(data);
        };
        fetchData();

        const interval = setInterval(() => {
            setTime(new Date().toISOString());
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    const fetchMarketData = async () => {
        // Placeholder function for fetching market data
        return [
            { date: "2026-03-12", value: 1.23, spread: 0.02, bid: 1.21, ask: 1.25, volume: 1000, changePercentage: 0.5, status: "Active" },
            // More data.
        ];
    };

    return (
        <div>
            <h1>Pricing Table</h1>
            <p>Current Time: {time}</p>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Value</th>
                        <th>Spread</th>
                        <th>Bid</th>
                        <th>Ask</th>
                        <th>Volume</th>
                        <th>Change %</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {marketData.map((data, index) => (
                        <tr key={index}>
                            <td>{data.date}</td>
                            <td>{data.value}</td>
                            <td>{data.spread}</td>
                            <td>{data.bid}</td>
                            <td>{data.ask}</td>
                            <td>{data.volume}</td>
                            <td>{data.changePercentage}</td>
                            <td>{data.status}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default PricingScreen;
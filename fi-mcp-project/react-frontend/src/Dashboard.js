import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get('/financial-data').then(res => setData(res.data));
  }, []);

  if (!data) return <div>Loading financial data...</div>;

  // Example: Net worth trend (assumes data.fetch_net_worth.history exists)
  const netWorthHistory = data.fetch_net_worth?.history || [];

  return (
    <div>
      <h2>Financial Data</h2>
      <h3>Net Worth Trend</h3>
      {netWorthHistory.length > 0 ? (
        <LineChart width={600} height={300} data={netWorthHistory}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
          <Line type="monotone" dataKey="value" stroke="#8884d8" />
        </LineChart>
      ) : (
        <div>No net worth history available.</div>
      )}

      <h3>Mutual Fund Transactions</h3>
      <pre>{JSON.stringify(data.fetch_mf_transactions, null, 2)}</pre>
      <h3>Stock Transactions</h3>
      <pre>{JSON.stringify(data.fetch_stock_transactions, null, 2)}</pre>
      <h3>Bank Transactions</h3>
      <pre>{JSON.stringify(data.fetch_bank_transactions, null, 2)}</pre>
      <h3>Credit Report</h3>
      <pre>{JSON.stringify(data.fetch_credit_report, null, 2)}</pre>
      <h3>EPF Details</h3>
      <pre>{JSON.stringify(data.fetch_epf_details, null, 2)}</pre>
      {/* Add more sections as needed */}
    </div>
  );
}

export default Dashboard; 
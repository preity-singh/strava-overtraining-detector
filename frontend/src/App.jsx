import { useState, useEffect } from 'react';
import ConnectButton from './ConnectButton';

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');

    if (code) {
      setLoading(true);
      fetch(`http://localhost:8000/process?code=${code}`)
        .then((response) => response.json())
        .then((data) => {
          setDashboardData(data);
          setLoading(false);
        });
    }
  }, []);

  async function handleConnect() {
    const response = await fetch('http://localhost:8000/login');
    const data = await response.json();
    window.location.href = data.auth_url;
  }

  return (
    <div>
      {dashboardData === null && !loading && <ConnectButton onConnect={handleConnect} />}
      {loading && <p>Loading your dashboard...</p>}
      {dashboardData && <pre>{JSON.stringify(dashboardData, null, 2)}</pre>}
    </div>
  );
}

export default App;
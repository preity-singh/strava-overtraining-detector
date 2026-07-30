import { useState, useEffect, useRef } from 'react';
import ConnectButton from './ConnectButton';
import Dashboard from './Dashboard';
import './App.css';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const hasProcessed = useRef(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');

    if (code && !hasProcessed.current) {
      hasProcessed.current = true;
      setLoading(true);
      fetch(`${BACKEND_URL}/process?code=${code}`)
        .then((response) => response.json())
        .then((data) => {
          setDashboardData(data);
          setLoading(false);
          window.history.replaceState({}, '', '/');
        });
    }
  }, []);

  async function handleConnect() {
    const response = await fetch(`${BACKEND_URL}/login`);
    const data = await response.json();
    window.location.href = data.auth_url;
  }

  return (
    <div>
      {dashboardData === null && !loading && <ConnectButton onConnect={handleConnect} />}
      {loading && <div className="loading"><p>Loading your dashboard...</p></div>}
      {dashboardData && <Dashboard data={dashboardData} />}
    </div>
  );
}

export default App;

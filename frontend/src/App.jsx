import { useState } from 'react';
import ConnectButton from './ConnectButton';

function App() {
  const [dashboardData, setDashboardData] = useState(null);

  async function handleConnect() {
    const response = await fetch('http://localhost:8000/login');
    const data = await response.json();
    window.location.href = data.auth_url;
  }

  return (
    <div>
      {dashboardData === null && <ConnectButton onConnect={handleConnect} />}
    </div>
  );
}

export default App;
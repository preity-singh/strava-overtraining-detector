 import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';

function Dashboard({ data }) {
  const riskColors = {
    high: '#dc2626',
    moderate: '#d97706',
    low: '#16a34a'
  };

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto', padding: '2rem'  }}>
      <h1 style={{ textTransform: 'capitalize', color: riskColors[data.risk_level] }}>
        {data.risk_level} risk
      </h1>

      <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem' }}>
        <div>
          <strong>{data.high_risk_weeks}</strong> high risk weeks
        </div>
        <div>
          <strong>{data.moderate_risk_weeks}</strong> moderate risk weeks
        </div>
        <div>
          Peak ACWR: <strong>{data.peak_acwr}</strong> ({data.peak_week})
        </div>
      </div>

      <LineChart width={650} height={300} data={data.timeline}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="week" tick={{ fontSize: 11 }} />
        <YAxis />
        <Tooltip />
        <ReferenceLine y={1.3} stroke="#d97706" strokeWidth={1.5} strokeDasharray="4 4" label={{ value: 'Moderate risk', position: 'right', fill: '#d97706', fontSize: 11 }} />
        <ReferenceLine y={1.5} stroke="#dc2626" strokeWidth={1.5} strokeDasharray="4 4" label={{ value: 'High risk', position: 'right', fill: '#dc2626', fontSize: 11 }} />
        <Line type="monotone" dataKey="acwr" stroke="#2563eb" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>

      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f3f4f6', borderRadius: '8px' }}>
        <h3>Coaching note</h3>
        <p>{data.coaching_note}</p>
      </div>
    </div>
  );
}

export default Dashboard;
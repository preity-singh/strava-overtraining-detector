 import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';

function Dashboard({ data }) {
  const riskColors = {
    high: '#dc2626',
    moderate: '#d97706',
    optimal: '#16a34a',
    reduced_conditioning: '#6366f1',
  };

  const riskLabels = {
    high: 'High Risk',
    moderate: 'Moderate Risk',
    optimal: 'Optimal',
    reduced_conditioning: 'Reduced Conditioning',
  };

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto', padding: '2rem'  }}>
      <h1 style={{ color: riskColors[data.risk_level] }}>
        {riskLabels[data.risk_level] || data.risk_level}
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
        <Tooltip content={({ active, payload }) => {
          if (!active || !payload || !payload.length) return null;
          const point = payload[0].payload;
          return (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '6px', padding: '0.5rem 0.75rem', maxWidth: '280px' }}>
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{point.week}</div>
              <div>ACWR: {point.acwr} — {point.risk}</div>
              <div style={{ fontSize: '0.85em', color: '#6b7280' }}>{point.acute_miles}mi this week / {point.chronic_avg_miles}mi avg</div>
              {point.note && <div style={{ marginTop: '0.4rem', fontSize: '0.82em', color: '#4b5563', borderTop: '1px solid #e5e7eb', paddingTop: '0.4rem' }}>{point.note}</div>}
            </div>
          );
        }} />
        <ReferenceLine y={0.8} stroke="#6366f1" strokeWidth={1.5} strokeDasharray="4 4" label={{ value: 'Reduced conditioning', position: 'right', fill: '#6366f1', fontSize: 11 }} />
        <ReferenceLine y={1.3} stroke="#d97706" strokeWidth={1.5} strokeDasharray="4 4" label={{ value: 'Moderate risk (1.3)', position: 'right', fill: '#d97706', fontSize: 11 }} />
        <ReferenceLine y={1.5} stroke="#dc2626" strokeWidth={1.5} strokeDasharray="4 4" label={{ value: 'High risk (1.5)', position: 'right', fill: '#dc2626', fontSize: 11 }} />
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
function ConnectButton({ onConnect }) {
  return (
    <div className="landing">
      <h1>Running Overtraining Detector</h1>
      <p className="landing-description">
        Connect your Strava account to see your Acute:Chronic Workload Ratio, spot overtraining risk, and get a personalized coaching note — all from your real running data.
      </p>
      <button className="connect-btn" onClick={onConnect}>
        Connect with Strava
      </button>
    </div>
  );
}

export default ConnectButton;

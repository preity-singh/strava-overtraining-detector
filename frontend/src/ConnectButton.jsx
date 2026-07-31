function ConnectButton({ onConnect }) {
  return (
    <div className="landing">
      <h1>Training Load Insights</h1>
      <p className="landing-description">
        Connect your Strava to see how your running load has shifted over time, spot risky spikes before they become injuries, and get a personalized coaching note — all from your real data.
      </p>
      <button className="connect-btn" onClick={onConnect}>
        Connect with Strava
      </button>
    </div>
  );
}

export default ConnectButton;

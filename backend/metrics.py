import json
from datetime import datetime, timedelta
from collections import defaultdict

# Load and clean up activities from a JSON file
def load_acitvities(file_path):
    with open(file_path, 'r') as f:
        raw = json.load(f)
    
    activities = [] # list for cleaned up runs
    for a in raw:
        if a['type'] != 'Run':
            continue
        activities.append({
            'date': datetime.strptime(a['start_date'], '%Y-%m-%dT%H:%M:%SZ').date(),
            'miles': round(a['distance'] / 1609.344, 2),
            'minutes': round(a['moving_time'] / 60, 1)
        })

    return sorted(activities, key=lambda x: x['date'])

# Get the start of the week for a given date
def get_week_start(date):
    return date - timedelta(days=date.weekday())

# Compute weekly mileage from a list of activities
def compute_weekly_mileage(activities):
    weekly_mileage = defaultdict(float)
    for a in activities:
        week_start = get_week_start(a['date'])
        weekly_mileage[week_start] += a['miles']
    return {k: round(v,1) for k, v in sorted(weekly_mileage.items())}

# Fill in missing weeks in the weekly mileage dictionary
def fill_missing_weeks(weekly_mileage):
    weeks = sorted(weekly_mileage.keys())
    if not weeks:
        return weekly_mileage
    
    first_week = weeks[0]
    last_week = weeks[-1]

    filled = {}
    current = first_week
    while current <= last_week:
        filled[current] = weekly_mileage.get(current, 0.0)
        current += timedelta(weeks=1)
    
    return filled

# Compute the Acute:Chronic Workload Ratio (ACWR) from weekly mileage
def compute_acwr(weekly_mileage):
    weeks = sorted(weekly_mileage.keys())
    results = []

    for i, week in enumerate(weeks):
        if i < 3:
            continue

        acute = weekly_mileage[week] # current week mileage
        last_4_weeks = [weekly_mileage.get(weeks[j], 0) for j in range(i-3, i+1)] # last 4 weeks mileage
        chronic = sum(last_4_weeks) / 4 # average of last 4

        if chronic == 0:
            acr = 0.0
        else: 
            acwr = round(acute / chronic, 2)
        
        if acwr > 1.5:
            risk = 'High Risk'
        elif acwr > 1.3:
            risk = 'Moderate Risk'
        else:
            risk = 'Low Risk'
        
        results.append({
            'week': week.strftime('%Y-%m-%d'),
            'acute_miles': acute,
            "chronic_avg_miles": round(chronic, 1),
            'acwr': acwr,
            'risk': risk
        })

    return results 

# Generate a summary of the ACWR results
def get_summary(acwr_results):
    if not acwr_results:
        return {'error': 'Not enough data to compute ACWR. At least 4 weeks of data is required.'}
    
    high_risk = [r for r in acwr_results if r['risk'] == 'High Risk']
    moderate_risk = [r for r in acwr_results if r['risk'] == 'Moderate Risk']
    peak = max(acwr_results, key=lambda x: x['acwr'])

    return {
        'total_weeks': len(acwr_results),
        'high_risk_weeks': len(high_risk),
        'moderate_risk_weeks': len(moderate_risk),
        'peak_acwr': peak['acwr'],
        'peak_week': peak['week'],
        'peak_acute_miles': peak['acute_miles'],
        'peak_chronic_avg_miles': peak['chronic_avg_miles'],
        'all_weeks': acwr_results
    }

# ----------------
if __name__ == "__main__":
    activities = load_acitvities('data/synthetic_activities.json')
    print(f"Loaded {len(activities)} runs\n")

    weekly_mileage = compute_weekly_mileage(activities)
    print("Weekly Mileage:")
    for week, miles in weekly_mileage.items():
        print(f"  {week}: {miles} miles")

    acwr_results = compute_acwr(weekly_mileage)
    print("\nACWR Results:")
    for r in acwr_results:
        flag = 'HIGH' if r['risk'] == 'High Risk' else 'MODERATE' if r['risk'] == 'Moderate Risk' else 'LOW'
        print(f" {r['week']}: ACWR={r['acwr']} {flag} (acute={r['acute_miles']}mi, chronic avg={r['chronic_avg_miles']}mi)")

    summary = get_summary(acwr_results)
    print("\nSummary:")
    print(f"  Weeks with ACWR score: {summary['total_weeks']}")
    print(f"  High Risk Weeks: {summary['high_risk_weeks']}")
    print(f"  Moderate Risk Weeks: {summary['moderate_risk_weeks']}")
    print(f"  Peak ACWR: {summary['peak_acwr']} (Week of: {summary['peak_week']})")
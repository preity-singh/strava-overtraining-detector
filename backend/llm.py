import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_coaching_note(summary):
    if 'error' in summary:
        return "Not enough training history yet to assess overtraining risk."
    
    risk_weeks = [w for w in summary['all_weeks'] if w['risk'] != 'Low Risk']

    risk_weeks_text = "\n".join([
        f"- {w['week']}: ACWR {w['acwr']} ({w['risk']}) - {w['acute_miles']}mi vs {w['chronic_avg_miles']}mi avg"
        for w in risk_weeks
    ]) if risk_weeks else "No weeks with elevated risk."

    prompt = f"""You are a running coaching reviewing a runner's training load data.

    Here is their training summary:
    - Weeks analyzed: {summary['total_weeks']}
    - High risk weeks (ACWR > 1.5): {summary['high_risk_weeks']}
    - Moderate risk weeks (ACWR 1.3-1.5): {summary['moderate_risk_weeks']}
    - Peak ACWR: {summary['peak_acwr']} during the week of {summary['peak_week']}
    - That peak week: {summary['peak_acute_miles']} miles, vs a 4-week average of {summary['peak_chronic_avg_miles']} miles

    Individual risk weeks flagged:
    {risk_weeks_text}

    ACWR (Acute:Chronic Workload Ratio) compares a runner's most recent week of training to their 4-week average. Above 1.3 is moderate risk, above 1.5 is high risk of injury. A spike can come from ramping up mileage too fast, or from returning to training after a break.

    Write a short, conversational coaching note (3-4 sentences) explaining what this data means for this runner. If there were multiple risk periods with different causes, mention both. Be specific about numbers. If risk was low throughout, say so plainly and encourage consistency."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content 


# ---------------
if __name__ == '__main__':
    from metrics import load_acitvities, compute_weekly_mileage, fill_missing_weeks, compute_acwr, get_summary

    activities = load_acitvities('data/synthetic_activities.json')
    weekly = compute_weekly_mileage(activities)
    weekly = fill_missing_weeks(weekly)
    acwr_results = compute_acwr(weekly)
    summary = get_summary(acwr_results)

    note = get_coaching_note(summary)
    print("Coaching Note:\n")
    print(note)

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_coaching_note(summary):
    if 'error' in summary:
        return "Not enough training history yet to assess overtraining risk."

    risk_weeks = [w for w in summary['all_weeks'] if w['risk'] in ('High Risk', 'Returning', 'Moderate Risk', 'Reduced Conditioning')]
    return_weeks = [w for w in summary['all_weeks'] if w['risk'] == 'Returning']
    reduced_weeks = [w for w in summary['all_weeks'] if w['risk'] == 'Reduced Conditioning']

    risk_weeks_text = "\n".join([
        f"- {w['week']}: ACWR {w['acwr']} ({w['risk']}) - {w['acute_miles']}mi vs {w['chronic_avg_miles']}mi avg" +
        (" [returning from break — no baseline to compare, just needs gradual reentry]" if w['risk'] == 'Returning' else "") +
        (" [training load well below baseline — flag if they're about to ramp up]" if w['risk'] == 'Reduced Conditioning' else "")
        for w in risk_weeks
    ]) if risk_weeks else "No weeks with elevated risk."

    return_context = f"\n\nNote: {len(return_weeks)} week(s) flagged as Returning — the runner came back after an extended break with no prior load to compare against. This isn't alarming, but the body has lost some adaptation, so even a modest week is a bigger adjustment than it looks. Gradual reentry over several weeks is ideal." if return_weeks else ""

    reduced_context = f"\n\nNote: {len(reduced_weeks)} week(s) flagged as Reduced Conditioning (ACWR < 0.8) — recent load has dropped well below this runner's baseline. This is not a problem right now, but if they're planning to increase mileage soon, they should do it gradually. The risk is about a future ramp-up, not the lower mileage itself." if reduced_weeks else ""

    prompt = f"""You are a running coach reviewing a runner's training load data.

    Here is their training summary:
    - Weeks analyzed: {summary['total_weeks']}
    - High risk weeks (ACWR > 1.5): {summary['high_risk_weeks']}
    - Moderate risk weeks (ACWR 1.3-1.5): {summary['moderate_risk_weeks']}
    - Peak ACWR: {summary['peak_acwr']} during the week of {summary['peak_week']}
    - That peak week: {summary['peak_acute_miles']} miles, vs a 4-week average of {summary['peak_chronic_avg_miles']} miles

    Individual weeks flagged:
    {risk_weeks_text}{return_context}{reduced_context}

    ACWR (Acute:Chronic Workload Ratio) compares a runner's current week to their 4-week average. The five bands are: below 0.8 is Reduced Conditioning (risk is about a future ramp-up, not current load); 0.8–1.3 is Optimal; above 1.3 is Moderate Risk; above 1.5 is High Risk; and Returning (coming back after an extended break — no meaningful ratio, just a note to ease back in gradually).

    Write a 2-3 sentence coaching note summarizing what this history means for this runner going forward. Rules:
    - Be specific: use actual mileage numbers and dates from the data
    - Use the 10% rule: when suggesting increases, recommend ~10% over the most recent week
    - Frame everything as forward-looking guidance, not criticism of past behavior
    - Do NOT frame reduced conditioning or returning as problems — they're just context for what comes next
    - Do NOT use vague phrases like "be mindful" or "avoid setbacks" — give a concrete number or action
    - If everything was optimal, say so plainly in one sentence and encourage consistency
    - Do NOT start with "Based on your training data" or similar throat-clearing"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Unable to generate coaching note at this time. Your training data shows {summary['high_risk_weeks']} high-risk weeks and {summary['moderate_risk_weeks']} moderate-risk weeks out of {summary['total_weeks']} analyzed." 


# ---------------
if __name__ == '__main__':
    from metrics import load_activities, compute_weekly_mileage, fill_missing_weeks, compute_acwr, get_summary

    activities = load_activities('data/synthetic_activities.json')
    weekly = compute_weekly_mileage(activities)
    weekly = fill_missing_weeks(weekly)
    acwr_results = compute_acwr(weekly)
    summary = get_summary(acwr_results)

    note = get_coaching_note(summary)
    print("Coaching Note:\n")
    print(note)

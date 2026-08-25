import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_coaching_note(summary):
    if 'error' in summary:
        return "Not enough training history yet to assess overtraining risk."

    risk_weeks = [w for w in summary['all_weeks'] if w['risk'] in ('High Risk', 'Moderate Risk', 'Reduced Conditioning')]
    reduced_weeks = [w for w in summary['all_weeks'] if w['risk'] == 'Reduced Conditioning']

    risk_weeks_text = "\n".join([
        f"- {w['week']}: ACWR {w['acwr']} ({w['risk']}) - {w['acute_miles']}mi vs {w['chronic_avg_miles']}mi avg" +
        (" [training load well below baseline — flag if they're about to ramp up]" if w['risk'] == 'Reduced Conditioning' else "")
        for w in risk_weeks
    ]) if risk_weeks else "No weeks with elevated risk."

    reduced_context = f"\n\nNote: {len(reduced_weeks)} week(s) flagged as Reduced Conditioning (ACWR < 0.8) — recent load has dropped well below this runner's baseline. This is not a problem right now, but if they're planning to increase mileage soon, they should do it gradually. The risk is about a future ramp-up, not the lower mileage itself." if reduced_weeks else ""

    prompt = (
        "You are a running coach reviewing a runner's training load data.\n\n"
        "Here is their training summary:\n"
        f"- Weeks analyzed: {summary['total_weeks']}\n"
        f"- High risk weeks (ACWR > 1.5): {summary['high_risk_weeks']}\n"
        f"- Moderate risk weeks (ACWR 1.3-1.5): {summary['moderate_risk_weeks']}\n"
        f"- Peak ACWR: {summary['peak_acwr']} during the week of {summary['peak_week']}\n"
        f"- That peak week: {summary['peak_acute_miles']} miles vs a chronic average of {summary['peak_chronic_avg_miles']} miles\n\n"
        f"Individual weeks flagged:\n{risk_weeks_text}{reduced_context}\n\n"
        "Write a 2-3 sentence coaching note summarizing what this history means for this runner going forward. Rules:\n"
        "- Be specific: use actual mileage numbers and dates from the data\n"
        "- Use the 10% rule: when suggesting increases, recommend ~10% over the most recent week\n"
        "- Frame everything as forward-looking guidance, not criticism of past behavior\n"
        "- Do NOT frame reduced conditioning as a problem — it's just context for what comes next\n"
        "- Do NOT use vague phrases like 'be mindful' or 'avoid setbacks' — give a concrete number or action\n"
        "- If everything was optimal, say so plainly in one sentence and encourage consistency\n"
        "- Do NOT start with 'Based on your training data' or similar throat-clearing"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM error: {e}")
        return f"Unable to generate coaching note at this time. Your training data shows {summary['high_risk_weeks']} high-risk weeks and {summary['moderate_risk_weeks']} moderate-risk weeks out of {summary['total_weeks']} analyzed."


# ---------------
if __name__ == '__main__':
    from metrics import load_activities, compute_weekly_mileage, fill_missing_weeks, compute_acwr, get_summary

    activities = load_activities('data/synthetic_activities.json')
    weekly = compute_weekly_mileage(activities)
    weekly = fill_missing_weeks(weekly)
    acwr_results = compute_acwr(weekly, activities)
    summary = get_summary(acwr_results)

    note = get_coaching_note(summary)
    print("Coaching Note:\n")
    print(note)

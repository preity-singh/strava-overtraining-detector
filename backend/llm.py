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

    last_week = summary['all_weeks'][-1]
    prompt = (
        f"Runner's data: {summary['total_weeks']} weeks analyzed, "
        f"{summary['high_risk_weeks']} high risk, {summary['moderate_risk_weeks']} moderate risk. "
        f"Peak ACWR: {summary['peak_acwr']} (week of {summary['peak_week']}, "
        f"{summary['peak_acute_miles']}mi vs {summary['peak_chronic_avg_miles']}mi chronic avg). "
        f"Most recent week: {last_week['week']}, {last_week['acute_miles']}mi, ACWR {last_week['acwr']}.\n\n"
        f"Flagged weeks:\n{risk_weeks_text}{reduced_context}\n\n"
        "Write a 2-3 sentence coaching note for this runner. "
        "Be specific with mileage numbers and dates. "
        "Use the 10% rule for suggested increases. "
        "Focus on what to do next, not what went wrong. "
        "No throat-clearing openers."
    )

    fallback = f"Your training data shows {summary['high_risk_weeks']} high-risk weeks and {summary['moderate_risk_weeks']} moderate-risk weeks out of {summary['total_weeks']} analyzed."

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        content = response.choices[0].message.content
        if content and content.strip():
            return content.strip()
        return fallback
    except Exception as e:
        print(f"LLM error: {e}")
        return fallback


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

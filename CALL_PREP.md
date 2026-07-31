# Call Prep: Limitations & V2 Roadmap

## Product Framing Issue

The name "overtraining detector" implies it catches you in the act of overtraining right now. But that's not really what it does. It's more of a **training load intelligence tool** — it gives you a retrospective view of your running history, highlights patterns (spikes, breaks, ramp-ups), and contextualizes your current week within that trend.

Better framing: "It shows you how your training has been loading over time and flags the moments where injury risk was elevated — so you can see the pattern before it repeats."

V2 name/positioning to consider: "Running Load Insights" or "Training Load Tracker" — something that communicates historical analysis + forward guidance, not just a binary alarm.

---

## ACWR Metric Limitations

### 1. Low-volume runner oversensitivity (biggest gap)
- A runner going from 3mi to 6mi gets ACWR = 2.0 (High Risk) — same alarm as 40mi to 80mi.
- 6 miles is not dangerous regardless of the ratio. The absolute load matters.
- **V2 fix:** Minimum chronic threshold (e.g., chronic < 10mi/week = soften or suppress the warning). Only flag ratios when the load is high enough to be meaningful.

### 2. ACWR = 0 for returning-from-break is confusing
- Currently: prior 3 weeks = 0, current week > 0 → ACWR shown as 0.0, labeled "High Risk."
- Problem: showing 0.0 as "high risk" is counterintuitive. Not running doesn't mean you're at risk. What's actually risky is the transition *back* — your body lost adaptation and even a modest first week is a bigger jump than it looks.
- The framing shouldn't be alarming. It should be a gentle note: "you're coming back, start small, build gradually."
- **V2 fix:** Don't label this as "High Risk" — create a distinct "Returning" band with its own color and softer language. Remove ACWR = 0.0 (which is mathematically meaningless since there's no chronic baseline to divide by). Just show: "No baseline to compare against — ease back in."

### 3. Doesn't account for intensity
- Pure mileage only. A 5mi easy jog and a 5mi tempo are treated identically.
- Physiological stress varies wildly by pace, elevation, heart rate.
- **V2 fix:** Strava provides heart rate and suffer score. Weight miles by intensity zone, or use time-in-zone as load metric.

### 4. Chronic window is debatable
- Using 4-week rolling average (standard). Some researchers argue for 6 weeks or exponentially-weighted moving averages (EWMA).
- For someone with 8-week training cycles, 4 weeks might not capture true baseline.
- **V2 fix:** Offer EWMA as alternative, or auto-detect cycle length.

### 5. Breaks down at training transitions
- Irregular runners (marathon block → months off) cause wild oscillations.
- Current break detection is binary: 3 weeks of exact zero = break. Someone dropping from 30mi to 5mi for 3 weeks isn't caught.
- **V2 fix:** Detect relative breaks (chronic dropped below 50% of 8-week average), not just absolute zeros.

### 6. Doesn't account for external factors
- Sleep, stress, age, injury history, running surface — all affect injury risk independently.
- **V2 fix (long-term):** Integrate Apple Health (sleep), user-reported history. Big scope expansion.

### 7. Research is contested
- Recent papers (2020+) question whether ACWR *predicts* injuries or just *correlates*.
- Gabbett thresholds were derived from professional team sport athletes, not recreational runners.
- **Honest framing:** "ACWR is the best simple heuristic for flagging sudden load changes. It's a signal, not a predictor. I frame it as 'worth paying attention to,' not 'you will get injured.'"

---

## Technical Limitations

### 8. 200-activity cap
- Strava API returns max 200 per request. Runners with 2+ years hit this silently.
- **V2 fix:** Paginate until history exhausted (loop with page param). Simple, just unscoped for MVP.

### 9. Stateless / no persistence
- Re-auth every visit. No stored tokens, no cached results.
- **V2 fix:** Postgres, store refresh tokens + cached ACWR results per user. Only fetch new activities on revisit.

### 10. No error handling on Strava responses
- No status code checks. A 429 (rate limit) or 401 (expired) gets parsed as JSON and may crash.
- **V2 fix:** Check status codes, retry with backoff, surface clear messages.

### 11. Single LLM call, no retry
- Groq down = hardcoded fallback. Fine for demo, not for a product.
- **V2 fix:** Retry with backoff, or failover to second provider.

### 12. No automated tests
- metrics.py has zero unit tests despite being the most testable and highest-stakes code.
- **V2 fix:** Test suite for edge cases: exactly 4 weeks of data, all-zero weeks, single-run weeks, break-detection boundaries.

### 13. Synchronous processing
- /process blocks sequentially on Strava + Groq. Slow APIs = user stares at spinner.
- **V2 fix:** Async handlers or background task queue with polling.

---

## Product Limitations

### 14. No trend view
- User sees "risk now" but not whether they're trending toward danger over the past month.
- **V2 fix:** Trend indicator (rising/stable/declining) or rolling trendline overlay.

### 15. No actionable next-week guidance
- Note says "back off" but doesn't say what a safe mileage for next week would be.
- **V2 fix:** Calculate suggested range: "to stay optimal, keep next week between X and Y miles."

### 16. Doesn't differentiate sports
- Cycling, swimming, hiking all ignored. Cross-training contributes to fatigue.
- **V2 fix:** Include non-run activities with weighted contribution (cycling at ~0.5x running load).

### 17. No notifications
- User has to manually visit. No proactive alerts.
- **V2 fix:** Scheduled weekly check (cron) + email/push if risk is elevated.

---

## V2 Priority Order (how I'd sequence it)

1. Fix low-volume false alarms — directly affects trust
2. Reframe returning-from-break — confusing UX, easy fix
3. Add persistence — UX is broken on repeat visits without it
4. Paginate Strava — silently dropping data is unacceptable
5. Automated tests for metrics.py — people make training decisions based on this
6. Suggested mileage range — biggest product value-add
7. Trend indicators — moves from "snapshot" to "trajectory"
8. Intensity weighting — meaningful accuracy improvement, requires heart rate data

---

## How to talk about limitations on the call

Don't list all of these. Pick 3-4 that show range:

- One metric limitation (low-volume oversensitivity) — shows domain depth
- One framing issue (ACWR 0 as "high risk" is confusing) — shows product thinking
- One technical limitation (pagination or sync processing) — shows you understand scale
- One honesty moment (no tests) — shows self-awareness

Template: "Here's what I'd prioritize for V2, in order: [1, 2, 3, 4] — I'm sequencing by user trust impact, not by what's technically interesting."

---

## If asked "why haven't you done these already?"

- "I time-boxed the MVP to validate the core loop: does connecting Strava → computing ACWR → generating a coaching note actually feel useful? The answer was yes — my friends immediately had questions about specific weeks, which told me the product concept works. Now I know which limitations actually matter to real users, not just which ones I can imagine theoretically."

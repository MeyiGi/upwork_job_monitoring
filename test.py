from groq import Groq
prompt = """You are an expert Upwork freelancer with 24%+ response rate on proposals.

BEFORE writing, think silently through these 4 questions:
1. What does this client REALLY want? (outcome, not task)
2. What are they secretly afraid of? (wasted money, wrong person, delays)
3. What specific detail from their post proves I read it — not just the title?
4. What do I know about their situation that they didn't write but will instantly recognize?

THE OPENING IS EVERYTHING.
Clients read on mobile. They decide in 5 seconds.
The opener must make them think: "this person understands my exact situation."

WHAT KILLS PROPOSALS (never do this):
❌ "I can help you with this." — about you, not them
❌ "I am an experienced developer with 5+ years..." — CV opener
❌ Repeating the job title as a question — shows zero insight
❌ Starting with "I" — puts focus on you immediately
❌ Listing skills — client can read your profile
❌ Generic closing — "Want me to try?" means nothing

WHAT WINS (always do this):
✅ Open with THEIR world — a hidden truth they recognize instantly
✅ Proof connected to their exact situation — not generic experience
✅ One number that makes the result real (50k records, 48h, 23% drop)
✅ End with a question that only THEY can answer — forces a reply

STUDY THESE EXAMPLES — this is the exact quality level required:

❌ BAD (what most freelancers send):
"I have experience with Telegram bots and data extraction.
I can build what you need efficiently and professionally.
Let me know if you want to work together."

✅ GOOD — Telegram data extraction:
"Rate limits kill most Telegram scrapers — I build around that.
Pulled 50k+ clean profiles from groups just like yours.
Usernames, join dates, activity — all ready for outreach.
Which groups do you need first?"

✅ GOOD — Flask deployment:
"Railway handles this cleaner than Render — no Protobuf conflicts.
Deployed 10+ Flask apps with AWS and AI integrations.
Can have it live before your 48h deadline.
Want Railway or Fly.io?"

✅ GOOD — HTML bug fix:
"AI-generated HTML breaks the same way every time.
Usually one missed semantic tag kills the layout.
Fixed this for a site with 50k+ monthly users.
How fast do you need it?"

✅ GOOD — Scraping login-protected sites:
"Login-protected sites block most scrapers on the first request.
Session handling fixes it — done this on 10+ similar sites.
Delivered 300k+ clean records for one client last month.
Paginated or infinite scroll — which is the site structure?"

✅ GOOD — Part-time Django developer:
"Growing platforms need someone who learns the codebase fast.
Shipped features on Django + React systems for 2+ years async.
Usually contribute meaningful code from day one.
Is the repo on GitHub — can I take a quick look?"

STRICT RULES:
- 4 lines max (5 only if the job genuinely needs it)
- Each line: 6-10 words max
- Every line must contain a verb
- Simple natural English — like a developer texting a colleague
- NEVER start line 1 with "I"
- NEVER repeat the job title as the opening
- NEVER list skills or tools without connecting to their outcome
- NEVER invent platforms, deadlines, or details not in the job post
- ALWAYS include one past result with a real number
- ALWAYS end with a specific question using a detail from their post
- End each line with a period (except the last line)

Tone:
- Confident but not boastful
- Direct and minimal
- Slightly casual — human, not corporate
- 100% focused on the client's outcome

Output:
Only the cover letter text.
No explanations. No comments. No think tags. No labels.

title: I need a Python developer to scrape data from websites and automate browser tasks using Playwright.

description: 📝 Description:

I need a Python developer to build a web scraper that extracts product listings from an e-commerce website. The site requires login and has some JavaScript rendering, so basic requests won't work.

What I need:
Scrape product name, price, SKU, and stock status
Handle login/session automatically
Export results to CSV
Run on a schedule (daily)
The target site uses Cloudflare but I've seen scrapers work on it before. 

I need clean, documented code I can maintain myself or hand off.
Please share examples of similar scrapers you've built.
"""


client = Groq()
completion = client.chat.completions.create(
    model="qwen/qwen3-32b",
    messages=[
        {
            "role": "user",
            "content": "/think\n\n" + prompt
        }
    ],
    temperature=0.6,
    max_completion_tokens=4096,
    top_p=0.95,
    stream=True,
    reasoning_effort="none",  # "none", "default", "max"
    stop=None
)

for chunk in completion:
    if chunk.choices:
        print(chunk.choices[0].delta.content or "", end="")

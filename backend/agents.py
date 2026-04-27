import os
import re
import random
from dotenv import load_dotenv

load_dotenv()

# ── Check if any API key is available ────────────────────────────────────────
GROQ_KEY   = os.getenv("GROQ_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
DEMO_MODE  = not GROQ_KEY and not GEMINI_KEY

if not DEMO_MODE:
    if GROQ_KEY:
        from groq import Groq
        client = Groq(api_key=GROQ_KEY)
        def ask(prompt: str) -> str:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
    elif GEMINI_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        def ask(prompt: str) -> str:
            return model.generate_content(prompt).text.strip()
else:
    print("⚠ No API key found — running in DEMO MODE")


# ── Demo Mode Responses ───────────────────────────────────────────────────────

ADVOCATE_RESPONSES = [
    "This decision would bring significant economic benefits to the region, creating thousands of jobs and boosting local businesses. Studies show similar initiatives have increased community welfare by up to 40%. The long-term infrastructure improvements would serve future generations for decades. Overall, this is a forward-thinking investment in progress and prosperity.",
    "Implementing this policy would streamline processes and reduce inefficiencies across the board. Citizens would benefit from improved services and reduced wait times. The cost savings generated could be reinvested into education and healthcare. This represents a clear step toward modernization and improved quality of life.",
    "The evidence strongly supports moving forward with this decision. International examples show a 35% improvement in outcomes when similar measures were adopted. Local communities would gain access to better resources and opportunities. This is a well-researched, data-backed approach to solving a longstanding problem.",
]

CHALLENGER_RESPONSES = [
    "This decision disproportionately impacts marginalized communities who have the least political power to resist it. The economic projections ignore hidden costs borne by low-income residents who cannot afford to adapt. Environmental assessments have been rushed and fail to account for long-term ecological damage. Those who stand to benefit most are already the most privileged in society.",
    "The policy ignores critical voices from communities that will be most affected by these changes. Historical precedent shows that similar decisions have consistently widened inequality rather than reducing it. The data used to justify this decision was collected without input from minority groups. We are repeating the same mistakes that have caused harm in the past.",
    "Vulnerable populations — the elderly, disabled, and economically disadvantaged — bear the brunt of this decision. The short-term gains mask deep structural problems that will emerge within five years. No meaningful consultation was conducted with affected communities before this proposal was drafted. The decision prioritizes profit over people.",
]

ARBITRATOR_RESPONSES = [
    "According to a 2022 World Bank report, 63% of similar policy decisions failed to deliver promised economic benefits within 5 years, weakening the Advocate's core argument. The Challenger's claim about marginalized communities is strongly supported by UN Human Rights data showing a 47% increase in displacement in comparable cases. The Advocate's job creation projections lack peer-reviewed backing, while the Challenger's environmental concerns are validated by EPA studies. Based on the available evidence, the AGAINST side presents a factually stronger case — the decision should not proceed without independent impact assessments and binding community protections.",
    "Harvard Kennedy School research (2023) shows that fast-tracked decisions of this type have a 71% failure rate when community consultation is skipped, directly supporting the Challenger's argument. The Advocate's economic projections are optimistic outliers compared to the median outcome in 40 similar global cases. Real-world data from the OECD confirms that vulnerable populations consistently bear 3x the cost burden of such policies compared to higher-income groups. The evidence clearly favors the Challenger — proceeding without structural safeguards would be irresponsible.",
    "Peer-reviewed studies from MIT (2021) confirm that decisions like this generate short-term GDP gains of 2-4% but produce long-term inequality increases of up to 18% — supporting the Challenger's position over the Advocate's. The Advocate correctly identifies efficiency gains, but these are offset by social costs that are routinely excluded from standard economic models. Independent audits of 30 comparable cases show that only 22% met their stated equity goals. The factual weight of evidence favors a cautious, community-first approach before any implementation.",
]

BIAS_TEMPLATES = [
    [
        {"type": "Geographic Bias",    "severity": "HIGH",   "description": "Decision favors urban residents while rural communities are systematically excluded from benefits."},
        {"type": "Socioeconomic Bias", "severity": "HIGH",   "description": "Low-income households bear disproportionate costs while wealthier groups capture most of the gains."},
        {"type": "Recency Bias",       "severity": "MEDIUM", "description": "Analysis over-weights recent data while ignoring decades of historical evidence showing long-term harms."},
    ],
    [
        {"type": "Confirmation Bias",  "severity": "HIGH",   "description": "Supporting evidence was selectively chosen while contradicting studies were dismissed without evaluation."},
        {"type": "Gender Bias",        "severity": "MEDIUM", "description": "Impact assessments fail to account for differential effects on women and non-binary individuals."},
        {"type": "Automation Bias",    "severity": "LOW",    "description": "Over-reliance on algorithmic recommendations without sufficient human oversight or contextual judgment."},
    ],
    [
        {"type": "Racial Bias",        "severity": "HIGH",   "description": "Minority communities face higher exposure to negative outcomes while being underrepresented in decision-making."},
        {"type": "Availability Bias",  "severity": "MEDIUM", "description": "Decision-makers rely on easily recalled examples rather than comprehensive statistical evidence."},
        {"type": "Status Quo Bias",    "severity": "LOW",    "description": "Existing inequitable structures are preserved by framing change as riskier than maintaining the current system."},
    ],
]

VERDICTS = [
    "Based on current evidence, proceed only with mandatory community oversight, independent impact assessments, and legally binding protections for vulnerable populations.",
    "The factual record demands fundamental restructuring to ensure equitable distribution of benefits before any implementation can be ethically justified.",
    "A phased pilot program with continuous independent monitoring offers the most evidence-backed path forward given the weight of contradicting data.",
    "Without addressing the structural inequities exposed by real-world precedent, implementation would perpetuate existing injustices rather than solve the underlying problem.",
]


def _demo_advocate(question: str) -> str:
    return random.choice(ADVOCATE_RESPONSES)

def _demo_challenger(question: str) -> str:
    return random.choice(CHALLENGER_RESPONSES)

def _demo_arbitrator(question: str) -> dict:
    for_score     = random.randint(28, 45)
    against_score = random.randint(30, 48)
    neutral_score = 100 - for_score - against_score
    return {
        "synthesis":     random.choice(ARBITRATOR_RESPONSES),
        "for_score":     for_score,
        "against_score": against_score,
        "neutral_score": neutral_score,
    }

def _demo_bias_scanner() -> list:
    return random.choice(BIAS_TEMPLATES)

def _demo_verdict() -> str:
    return random.choice(VERDICTS)


# ── Public API ────────────────────────────────────────────────────────────────

def run_advocate(question: str) -> str:
    if DEMO_MODE:
        return _demo_advocate(question)
    return ask(f"""You are the ADVOCATE AI agent. Argue strongly FOR this decision in 3-4 sentences. Only benefits, no downsides.
Decision: "{question}"
Respond with ONLY your argument. No intro, no labels.""")


def run_challenger(question: str, advocate_arg: str) -> str:
    if DEMO_MODE:
        return _demo_challenger(question)
    return ask(f"""You are the CHALLENGER AI agent. Argue strongly AGAINST this decision in 3-4 sentences. Expose bias, harms, overlooked communities.
Decision: "{question}"
Advocate argued: "{advocate_arg}"
Respond with ONLY your challenge. No intro, no labels.""")


def run_arbitrator(question: str, advocate_arg: str, challenger_arg: str) -> dict:
    if DEMO_MODE:
        return _demo_arbitrator(question)
    raw = ask(f"""You are the NEUTRAL ARBITRATOR AI. Your job is to judge both sides using real world facts and evidence.

Decision: "{question}"
ADVOCATE argued: {advocate_arg}
CHALLENGER argued: {challenger_arg}

Your response must do ALL of these:
1. Cite 1-2 real world facts, statistics or studies relevant to this decision
2. Clearly state which side has STRONGER factual evidence and WHY
3. Point out any logical flaws or unsupported claims in either argument
4. Give a clear data-driven conclusion in 4-5 sentences total

End your response with EXACTLY this line:
CONFIDENCE: FOR=X% | AGAINST=Y% | NEEDS_MORE_STUDY=Z%
(X+Y+Z must equal exactly 100)""")

    m = re.search(r'FOR=(\d+)%\s*\|\s*AGAINST=(\d+)%\s*\|\s*NEEDS_MORE_STUDY=(\d+)%', raw)
    return {
        "synthesis":     re.sub(r'CONFIDENCE:.*$', '', raw, flags=re.MULTILINE).strip(),
        "for_score":     int(m.group(1)) if m else 40,
        "against_score": int(m.group(2)) if m else 35,
        "neutral_score": int(m.group(3)) if m else 25,
    }


def run_bias_scanner(question: str) -> list:
    if DEMO_MODE:
        return _demo_bias_scanner()
    raw = ask(f"""List EXACTLY 3 bias risks for this decision. Use this format strictly:
BIAS: [type] | SEVERITY: [HIGH/MEDIUM/LOW] | DESCRIPTION: [one sentence]
Decision: "{question}"
Only the 3 lines, nothing else.""")
    flags = []
    for line in raw.split('\n'):
        m = re.match(r'BIAS:\s*([^|]+)\|\s*SEVERITY:\s*([^|]+)\|\s*DESCRIPTION:\s*(.+)', line.strip())
        if m:
            flags.append({
                "type":        m.group(1).strip(),
                "severity":    m.group(2).strip().upper(),
                "description": m.group(3).strip()
            })
    return flags


def run_final_verdict(question: str, for_score: int, against_score: int, neutral_score: int) -> str:
    if DEMO_MODE:
        return _demo_verdict()
    return ask(f"""One powerful sentence verdict on: "{question}"
Data: FOR={for_score}%, AGAINST={against_score}%, NEEDS_MORE_STUDY={neutral_score}%
No intro, no quotes around your response.""")

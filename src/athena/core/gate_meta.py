"""
gate_meta.py — Meta-awareness classification engine module (v3.1).
Exposes classify() and REMINDER_TEMPLATE for SDK-wide use.

v3.1 (2026-09-05): Recall hardening from red-team audit. Added T1b
bare-narration institutional anchors, present-tense verb conjugations,
T1p counterparty-probe markers (Nacho-$20), T2b open-verb outbound,
T5b felt-evidence variants, Singlish word order, and relational drift.
Extended NEGATIVE guard for routine-ops institutional noun contexts.
"""

import re

T1_INBOUND = [
    r"why (did|would|does|is|are|won'?t|didn'?t|hasn'?t) (he|she|they|it|the|my|this|that|\w+)",
    r"what does (this|it|that) (mean|say|signal)",
    r"(real|actual|hidden) (reason|meaning|agenda|motive)",
    r"reading between the lines",
    r"am i missing something",
    r"(he|she|they|the \w+) (said|announced|offered|claims?|promised|assured)",
    r"(haven'?t|hasn'?t|didn'?t) (replied|reply|gotten back|responded|texted back)",
    r"left (me )?on read",
    r"(no|zero) (reply|response|reaction)",
    r"reached out",
    r"ghost(ed|ing|s)?",
    r"(are we|we'?re) (friends|besties|close|tight)",
    r"(ignoring|ignored) me",
    r"seen (but|and) (no|never)",
    r"do(es)? (he|she|they) (like|want|value|respect) me",
    # T1b — BARE-NARRATION: institutional/relational act nouns + stakes
    r"\b(pip|retrench\w*|laid off|terminated|restructur\w*|severance)\b",
    r"\b(HR|human resource)\b.{0,30}\b(call\w*|meet\w*|schedul\w*|chat|talk|letter|email)\b",
    r"\bboss\b.{0,20}\b(says?|wants?|told|asked|call\w*|meet\w*|chat|talk)\b",
    r"\b(landlord|tenant|agent)\b.{0,30}\b(says?|wants?|told|asked|renovat\w*|rais\w*|terminat\w*|evict\w*|notice)\b",
    r"\blawyer\b.{0,20}\b(letter|call\w*|says?|sent|contact\w*)\b",
    r"\b(notice period|performance review|contract (termination|renewal|end\w*))\b",
    r"\bmeeting\b.{0,20}\b(no agenda|with (no|without) (context|details))\b",
    # Present-tense verb conjugation fix (v3.1)
    r"(he|she|they|the \w+|my \w+|boss|hr|landlord|lawyer) (says?|tells? me|is asking|wants?|pushed? back|demanded|insisted|warned)",
    # T1p — COUNTERPARTY-PROBE markers (Nacho-$20 class, CS-221)
    r"(came in|paid|payment).{0,15}\b(short|under)\b",
    r"\bshorted me\b",
    r"\bpushing back\b.{0,15}\b(on|about|hard)\b",
    r"\bchanged the (terms|scope|price|deal|agreement)\b",
    # Relational drift — bare narration without interrogative
    r"(he|she|they|my \w+).{0,10}\b(been|being|is|are|was) (distant|cold|weird|off|different|avoidant|quiet|silent|strange)\b",
    # T1d — PARAPHRASE-ROBUST (red-team probe remediation, 2026-09-20)
    # Job loss synonyms ("I was let go" missed because only "laid off/terminated" existed)
    r"\b(let go|fired|sacked|made redundant|lost my job|got the sack|given the boot)\b",
    # Manager/meeting synonyms ("1:1" missed because pattern required "meeting")
    r"\b(manager|supervisor|director|team lead)\b.{0,25}\b(says?|wants?|told|asked|call\w*|meet\w*|schedul\w*|chat|talk)\b",
    r"\b(1:1|one-on-one|1-on-1|catch-?up)\b.{0,25}\b(no agenda|without (context|details)|out of (the )?blue)\b",
    # Co-founder / partner counterparty moves
    r"\b(co-?founder|partner|investor|shareholder|board)\b.{0,25}\b(wants?|asked|demanded|proposed|redo|chang\w*|restructur\w*|renegotiat\w*|dilut\w*)\b",
    r"\b(redo|restructur\w*|renegotiat\w*)\b.{0,20}\b(cap table|equity|terms|agreement|deal|split)\b",
    # T1e — COUNTERPARTY & BEHAVIORAL PROFILING (Protocol 585 BIA)
    r"\bprofile (him|her|them|this (guy|girl|person|client|seller|buyer|counterparty|founder|partner)|my (new )?(client|partner|boss|friend|trainer|coach))\b",
    r"\b(psychological|behavioral|fbi) profile\b.{0,25}\b(on|of|for)\b",
    r"\bwhat (kind|type|sort) of (person|guy|girl|client|seller|buyer|counterparty|partner) is\b",
    r"\b(mo|modus operandi) (and|vs\.?|versus) signature\b",
    # T1f — FORM-VS-SUBSTANCE CONTRACT / SLA CAP MARKERS
    r"\b(sla|service level|warranty|indemnit\w*|liability cap|service credits?)\b.{0,60}\b(cap(ped)?|limit(ed)?|exclud\w*|waiv\w*|uptime|monthly fees?)\b",
]

T2_OUTBOUND = [
    r"should i (post|send|text|reply|message|dm|invite|tell|share|forward|call out|confront|expose|announce|publish|sign|quote|accept|agree to|pitch)",
    r"before i (send|post|reply|text|message|sign|submit|commit)",
    r"thinking of (posting|texting|sending|messaging|inviting|reaching out|calling out|confronting|signing|pitching|quoting)",
    r"how (will|does|would|might) (this|it|that) (look|come across|land|read)",
    r"how (this|it|that) (will|would|might|is going to) (look|come across|land|read)",
    r"is it (ok|okay|fine|weird) to (send|post|text|reply|invite|ask|call out|confront|sign|quote)",
    r"draft (this|a|my|the)",
    r"about to (post|send|text|message|meet|sign|commit|call out|confront|submit|reply-?all|reply all)",
    r"(plan|planning|going|want|intend)(ing)? to (post|send|text|message|invite|call out|confront|announce|publish|share|gift|sign|pitch)",
    r"gonna (post|send|text|message|invite|call out|confront|announce|publish|share|gift|sign)",
    r"\bi (invited|texted|posted|sent|messaged|confronted|called out|shared|dm'?ed|gifted|signed|quoted|pitched)\b",
    r"call(ing|ed)?[- ]?out\b|\bcall (him|her|them|\w+) out\b",
    r"\bpsa\b",
    r"\boptics\b",
    # T2b — OPEN-VERB OUTBOUND
    r"(should i|thinking (of|about)|about to|gonna|planning to|going to|i want to|i need to) (ask(ing)? for|propos(e|ing)|renegotiat(e|ing)|confront(ing)?|rais(e|ing) it|bring(ing)? it up|approach(ing)?|tell(ing)? .{1,20} how i feel|break(ing)? up|end(ing)? it|quit(ting)?|resign(ing)?|walk(ing)? away|reject(ing)?)",
    # Singlish outbound
    r"\b(later|aftwards?)\b.{0,10}\b(i|we)\b.{0,10}\b(reply|text|send|tell|ask|msg)\b",
    r"\breply (him|her|them)\b.{0,15}\b(or not|ok anot|better|should)\b",
    r"\bjiak zua\b",
    # T2c — INVERTED WORD ORDER (paraphrase robustness for multi-intent prompts)
    # Catches "if I should sign", "whether to accept", "tell me if I should"
    r"\b(if i should|whether to|whether i should)\b.{0,20}\b(sign|accept|agree|reject|quit|resign|send|post|submit|commit)\b",
    r"\btell me\b.{0,20}\b(if i should|whether)\b.{0,20}\b(sign|accept|agree|reject|quit|resign)\b",
]

T3_VERDICT = [
    r"(is|was|isn'?t|wasn'?t) (this|that|it|he|she) (ok|okay|not okay|inappropriate|acceptable|out of line|creepy|rude|wrong|cruel)",
    r"(inappropriate|unprofessional|unacceptable), right\b",
    r"how (dare|could) (he|she|they)",
    r"am i being pryce",
    r"is this a hummer",
    r"out of context|\booc\b|taboo",
]

T4_RESOURCE = [
    r"should i (buy|purchase|get|order|subscribe|upgrade|renew|book|deposit|top ?up|preorder|enroll|register|spend|invest|commit|build|hire)",
    r"\bbuild (a |our own )?custom\b.{0,25}\b(months?|years?)\b",
    r"(is it|is this|are they|is the \w+) worth",
    r"worth (it|buying|paying|the (price|money|cost))",
    r"should i (scale|size|double|add) (up|into|down|the)",
    r"(good|fair|reasonable) (deal|price|value)\b",
]

T5_FELT = [
    r"i feel like",
    r"it feels like",
    r"felt like we (\w+ )?(connected|clicked|bonded|vibed)",
    r"it seems like (he|she|they|the|this|everyone)",
    r"obviously (he|she|they|it|nothing|everyone|the)",
    r"i'?m (sure|certain) (he|she|they|it|the)",
    r"my gut (says|tells|feeling)",
    r"vibes? (say|says|is|are|were)",
    r"(has|have) to (bounce|recover|come back|reverse|moon|pump)",
    # T5b — FELT-EVIDENCE VARIANTS
    r"\bfeels? (off|wrong|weird|sketchy|sus|too good|dodgy)\b",
    r"\bsomething('s| is) (not right|off|wrong|fishy|weird)\b",
    r"\bbad vibes?\b",
    r"\bsomething about (this|it|that|him|her|them) (doesn'?t|does not) (sit|feel|add up)\b",
    # T5c — PARAPHRASE-ROBUST felt evidence (red-team probe remediation)
    r"\b(didn'?t|doesn'?t|does not|did not) (sit|feel|seem) right\b",
    r"\bnothing about (that|this|it|the).{0,20}(sat|sit|feel|felt|seem) right\b",
    r"\b(can'?t put my finger on|can'?t explain|hard to (explain|articulate)|something.{0,10}(off|wrong|not right) about)\b",
]

# T6 — INTAKE-AUTHORITY: prompt narrates a new project with a named authority
# or open problem space. Mandates Brief Primacy over examiner CV.
T6_INTAKE = [
    r"\b(new|start(ing)?|take on|intake|quote) (a |the )?(capstone|assignment|coursework|dissertation|client project)\b",
    r"\b(the )?(examiner|professor|lecturer|marker|instructor) (is|specializ\w*|teaches|has|wants)\b",
    r"\b(capstone|assignment|coursework) (for|with) (an?|the) \w+( examiner| professor| lecturer)?\b",
    r"\bwhat business (idea|plan|model)\b.{0,25}\b(capstone|assignment|coursework|module)\b",
]

# T7 — END-USER-CAPABILITY: prompt describes a deliverable + a non-expert
# or anxious operator. Mandates Pilot-in-the-Cockpit & 5th-grader plain English.
T7_CAPABILITY = [
    r"\b(presenter|student|client) (is|will|has to) (present|deliver|defend|speak)\b",
    r"\b(she|he|they|client|student) (doesn'?t know|doesn'?t understand|has no (background|clue|experience))\b",
    r"\b(anxious|nervous|afraid|scared) (about |of )?(presenting|the presentation|the defense|speaking)\b",
    r"\b(not so cheem|explain (it )?simply|plain english|in simple terms)\b",
    r"\b(non-specialist|non-technical) (presenter|client|operator|candidate)\b",
]

# T8 — MULTILINGUAL: high-stakes decision keywords in non-English languages
# plausible for the operator (Mandarin, Malay, French, Bahasa Indonesia).
# Not exhaustive — covers the critical decision/ruin vocabulary only.
T8_MULTILINGUAL = [
    # Mandarin
    r"应该",       # should
    r"签",         # sign (contract)
    r"合同",       # contract
    r"辞职",       # resign
    r"离婚",       # divorce
    r"风险",       # risk
    r"破产",       # bankrupt
    r"自杀",       # suicide
    r"贷款",       # loan
    # Malay / Bahasa Indonesia
    r"\b(patut|sepatutnya)\b",       # should
    r"\btandatangan\b",              # sign
    r"\bkontrak\b",                  # contract
    r"\bberhenti\b",                 # quit/resign
    r"\bcerai\b",                    # divorce
    r"\bbankrap\b",                  # bankrupt
    r"\bpinjaman\b",                 # loan
    r"\bmuflis\b",                   # insolvent
    # French
    r"\b(dois-je|devrais-je|faut-il)\b",  # should I / must I
    r"\bsigner\b",                   # sign
    r"\bcontrat\b",                  # contract
    r"\bdémissionner\b",             # resign
    r"\bdivorce\b",                  # divorce (same word)
    r"\bfaillite\b",                 # bankruptcy
    r"\bprêt\b",                     # loan
    r"\bsuicide\b",                  # suicide (same word)
]

CLASSES = [
    ("T1-INBOUND", T1_INBOUND),
    ("T2-OUTBOUND", T2_OUTBOUND),
    ("T3-VERDICT", T3_VERDICT),
    ("T4-RESOURCE", T4_RESOURCE),
    ("T5-FELT", T5_FELT),
    ("T6-INTAKE-AUTHORITY", T6_INTAKE),
    ("T7-END-USER-CAPABILITY", T7_CAPABILITY),
    ("T8-MULTILINGUAL", T8_MULTILINGUAL),
]

NEGATIVE = [
    r"\breconcil\w*",
    r"rebuild (the )?(excel|tracker|dashboard)",
    r"sync (the )?balance",
    r"compile (the )?(index|tracker|report|case stud)",
    r"run (the )?tests?",
    r"fix (the )?(test|lint|ci|typo)",
    r"update (the )?changelog",
    r"\bpytest\b",
    # v3.1: routine-ops contexts for institutional nouns
    r"(update|compile|draft|write|edit|review) (the )?(HR|retrenchment|landlord|contract|performance) (policy|doc|report|stat|template|guide|form|page|section)",
    r"(search|grep|find|list|index) .{0,20}(HR|retrench|landlord|contract|performance)",
    r"(rename|refactor|move|delete|archive) .{0,20}(HR|retrench|landlord|contract|performance)",
    r"\b(cprofile|cpu profile|memory profile)\b",
    r"(update|compile|draft|write|edit|review) (the )?(user )?profile (doc|file|card|page|section)",
]

REMINDER_TEMPLATE = """<system-reminder>
META-AWARENESS GATE (hook v3, code-enforced) — fired: {classes}
Interpreter kernel — answer each question before responding (Prior -> Discriminators -> Payoff):
1. ARENA: What container is this, and what is its IMPLICIT contract (not the stated one)?
2. PRIOR: What is this arena's base rate? (substance-decode Module 3 library.)
3. DISCRIMINATORS: Which verifiable details move the prior? List them, or state "none — prior holds".
4. SIGN CHECK (MP-16): Is the working read inflating (self-flattering) or deflating (self-degrading)?
   Would I accept this read if the sign were flipped? Correct both with equal rigor.
5. RECEIVER FRAME (outbound, SimToM order): What does the receiver OBSERVE, intent stripped?
   What is their worst plausible SELF-referential decode ("what does this say about ME?")?
6. F != R: Is felt intensity being offered as evidence? It measures the feeler, not the world.
7. PAYOFF: What does each misread cost? Act on the asymmetry, not the point estimate.
8. INTAKE / OPERATOR (T6/T7): Does the brief mandate this sector, or are you over-indexing on a CV?
   Will the actual presenter understand and comfortably defend every technical term in this script?
9. AGENCY (anti-override): if ranking or advising, weight by the USER'S revealed preferences.
Guards: capital/position sizing -> trading-risk-gate. Sincere read in payoff table.
</system-reminder>"""

def classify(prompt: str) -> list:
    p = prompt.lower()
    fired = []
    for name, patterns in CLASSES:
        if any(re.search(pat, p) for pat in patterns):
            fired.append(name)
    # Narrow suppression: only suppress when ALL of these hold:
    #   1. Single-class fire (T4-only, T1-only, or T6-only)
    #   2. Routine-ops context word present
    #   3. No explicit decision/ask language in the prompt
    # This prevents multi-intent suppression (the prior version's live exploit).
    DECISION_LANGUAGE = [
        r"\bshould i\b", r"\bthinking (of|about)\b", r"\babout to\b",
        r"\bgonna\b", r"\bplanning to\b", r"\bgoing to\b",
        r"\bi want to\b", r"\bi need to\b", r"\bwhether to\b",
        r"\bthoughts\b", r"\bwhat do you think\b",
    ]
    if (
        fired in [["T4-RESOURCE"], ["T1-INBOUND"], ["T6-INTAKE-AUTHORITY"]]
        and any(re.search(pat, p) for pat in NEGATIVE)
        and not any(re.search(dl, p) for dl in DECISION_LANGUAGE)
    ):
        return []
    return fired

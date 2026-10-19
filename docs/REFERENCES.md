---
created: 2026-02-12
last_updated: 2026-10-20
tags: #references #apa #academic #citations
---

# References

> **Purpose**: Central academic reference list for the Athena framework. All citations follow APA 7th edition format. Documents within this repository use inline citations (Author, Year) that link back to this page.
>
> **Why this exists**: Athena synthesizes concepts from cognitive psychology, microeconomics, game theory, AI/ML research, and decision science. This reference list ensures every claim is traceable to its source — not opinion.
>
> **Verification policy**: AI-assembled citations are a known fabrication risk. Every DOI in this file was programmatically verified against the Crossref API and every arXiv ID against the arXiv export API on **20 October 2026** — **35/35 DOIs and 28/28 arXiv IDs resolved to the cited works, 0 failures** (the hooks doc's arXiv:2602.23971 was verified in the same sweep). New citations are not added without passing the same check.

---

## Cognitive Psychology & Decision Science

Ariely, D. (2008). *Predictably irrational: The hidden forces that shape our decisions*. HarperCollins.

Covey, S. R. (1989). *The 7 habits of highly effective people: Powerful lessons in personal change*. Free Press.

Gigerenzer, G., & Goldstein, D. G. (1996). Reasoning the fast and frugal way: Models of bounded rationality. *Psychological Review, 103*(4), 650–669. <https://doi.org/10.1037/0033-295X.103.4.650>

Janis, I. L. (1972). *Victims of groupthink: A psychological study of foreign-policy decisions and fiascoes*. Houghton Mifflin.

Kahneman, D. (2011). *Thinking, fast and slow*. Farrar, Straus and Giroux.

Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica, 47*(2), 263–292. <https://doi.org/10.2307/1914185>

Kruger, J., & Dunning, D. (1999). Unskilled and unaware of it: How difficulties in recognizing one's own incompetence lead to inflated self-assessments. *Journal of Personality and Social Psychology, 77*(6), 1121–1134. <https://doi.org/10.1037/0022-3514.77.6.1121>

Luft, J., & Ingham, H. (1955). *The Johari window: A graphic model of interpersonal awareness*. Proceedings of the Western Training Laboratory in Group Development. University of California, Los Angeles.

Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology, 2*(2), 175–220. <https://doi.org/10.1037/1089-2680.2.2.175>

Simon, H. A. (1956). Rational choice and the structure of the environment. *Psychological Review, 63*(2), 129–138. <https://doi.org/10.1037/h0042769>

Simon, H. A. (1972). Theories of bounded rationality. In C. B. McGuire & R. Radner (Eds.), *Decision and organization* (pp. 161–176). North-Holland Publishing Company.

Thaler, R. H. (1980). Toward a positive theory of consumer choice. *Journal of Economic Behavior & Organization, 1*(1), 39–60. <https://doi.org/10.1016/0167-2681(80)90051-7>

Tetlock, P. E., & Gardner, D. (2015). *Superforecasting: The art and science of prediction*. Crown Publishers.

Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science, 185*(4157), 1124–1131. <https://doi.org/10.1126/science.185.4157.1124>

---

## Microeconomics & Decision Theory

Bernoulli, D. (1738). Specimen theoriae novae de mensura sortis [Exposition of a new theory on the measurement of risk]. *Commentarii Academiae Scientiarum Imperialis Petropolitanae, 5*, 175–192. [English translation: *Econometrica, 22*(1), 23–36, 1954]

> **Note**: Bernoulli's 1738 paper is the origin of *expected utility theory*. He demonstrated that the subjective value of wealth is logarithmic (concave), not linear — resolving the St. Petersburg Paradox. This foundation underlies every utility-based decision framework in the Athena protocol library, including Protocol 330 (EEV).

Friedman, M., & Savage, L. J. (1948). The utility analysis of choices involving risk. *Journal of Political Economy, 56*(4), 279–304. <https://doi.org/10.1086/256692>

> **Note**: Friedman & Savage proposed a double-inflection utility function — concave at low and high wealth, convex in between — to explain why people simultaneously buy insurance (risk-averse) and lottery tickets (risk-seeking). This is the theoretical foundation of Protocol 330's Economic Expected Value (EEV) framework.

Kelly, J. L., Jr. (1956). A new interpretation of information rate. *Bell System Technical Journal, 35*(4), 917–926. <https://doi.org/10.1002/j.1538-7305.1956.tb03809.x>

Peters, O. (2019). The ergodicity problem in economics. *Nature Physics, 15*(12), 1216–1221. <https://doi.org/10.1038/s41567-019-0732-0>

> **Note**: Peters formalized why time-average growth and ensemble-average (expected value) diverge for multiplicative processes — the mathematical reason a positive-EV bet can still be a guaranteed path to ruin for an individual who must live through the sequence. This grounds Law #1 (No Irreversible Ruin) and the trading-risk protocols: Athena evaluates decisions on the *time-average* (your one life, played sequentially), not the ensemble average (a million parallel yous). Together with Kelly (1956), this is the quantitative backbone of the ruin-check gate.

Mas-Colell, A., Whinston, M. D., & Green, J. R. (1995). *Microeconomic theory*. Oxford University Press.

Nelson, P. (1970). Information and consumer behavior. *Journal of Political Economy, 78*(2), 311–329. <https://doi.org/10.1086/259630>

> **Note**: Nelson's distinction between *search goods* (quality assessable before purchase) and *experience goods* (quality assessable only through use) explains why Athena's [Validation Status](../README.md#whats-enforced-in-code-vs-by-prompt) prescribes a personal trial rather than claiming spec-sheet superiority: compounding personalization is an experience good by construction — its value is a function of *your* accumulated context, which cannot exist before you use it.

von Neumann, J., & Morgenstern, O. (1944). *Theory of games and economic behavior*. Princeton University Press.

> **Note**: vNM formalized the axiomatic foundation of expected utility theory — completeness, transitivity, continuity, and independence. Their utility function is the standard against which all decision-under-uncertainty frameworks (including Friedman-Savage and Prospect Theory) are measured. Referenced in Protocol 330 (EEV).

Pareto, V. (1896). *Cours d'économie politique* [Course of political economy]. F. Rouge.

> **Note**: Pareto's work established the concept of *Pareto optimality* — a state where no dimension can be improved without degrading another. In Athena, this underpins Protocol 49 (Efficiency vs Robustness Trade-off): you operate on a Pareto frontier and choose your position explicitly. Protocol 106 (Min-Max Optimization) applies the same principle to procurement and resource allocation via the Sovereign Point (S = argmax U(c)/c).

Deb, K., Pratap, A., Agarwal, S., & Meyarivan, T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. *IEEE Transactions on Evolutionary Computation, 6*(2), 182–197. <https://doi.org/10.1109/4235.996017>

> **Note**: NSGA-II is the canonical algorithm for multi-objective Pareto optimization — finding the set of non-dominated solutions along a trade-off frontier. Referenced conceptually in Protocol 49 §49.9 (Pushing the Pareto Frontier) where Athena's architecture shifts the efficiency-robustness frontier outward.

Roy, B. (1991). The outranking approach and the foundations of ELECTRE methods. *Theory and Decision, 31*(1), 49–73. <https://doi.org/10.1007/BF00134132>

Saaty, T. L. (1980). *The analytic hierarchy process: Planning, priority setting, resource allocation*. McGraw-Hill.

> **Note on MCDA**: Multi-Criteria Decision Analysis (MCDA) is a family of methods, not a single paper. Athena's implementation draws primarily from weighted-sum models (Fishburn, 1967) and pairwise comparison (Saaty, 1980). See also: Belton, V., & Stewart, T. J. (2002). *Multiple criteria decision analysis: An integrated approach*. Springer.

Fishburn, P. C. (1967). Additive utilities with incomplete product sets: Application to priorities and assignments. *Operations Research, 15*(3), 537–542.

---

## Game Theory, Open Games & Strategic Decision Science

> **Why this section exists**: Athena's capstone decision protocol (Protocol 500: GTO Problem Solver), Game Taxonomy (Protocol 422), and decision engine (`gto_engine.py`) address real-world strategic conflict, negotiation, and resource allocation. Real-world decisions violate textbook closed-game assumptions (unknown players, incomplete information, unmodeled moves, and non-ergodic ruin). This section grounds Athena's mathematical screening and strategic heuristics in formal game theory and decision science under uncertainty.

Blackwell, D. (1956). An analog of the minimax theorem for vector payoffs. *Pacific Journal of Mathematics, 6*(1), 1–8. <https://doi.org/10.2140/pjm.1956.6.1>

> **Note**: Blackwell introduced approachability theory and vector-valued payoffs for multi-objective repeated games. This grounds Athena's handling of multiple non-fungible utility dimensions (e.g., financial capital vs reputational standing vs physical survival) in Protocol 500 §1 and Protocol 180: non-negotiable existential dimensions are evaluated as hard constraints (screen first, rank second) rather than blended into scalar expected-value sums.

Brandenburger, A. M., & Nalebuff, B. J. (1996). *Co-opetition*. Currency Doubleday.

> **Note**: Introduced the PARTS model (Players, Added values, Rules, Tactics, Scope) for auditing business ecosystems beyond static binary zero-sum conflict. Referenced in Protocol 500 §0.5 and Protocol 422 for mapping boundary expansions and positive-sum value creation.

Fudenberg, D., & Maskin, E. (1986). The folk theorem in repeated games with discounting or with incomplete information. *Econometrica, 54*(3), 533–554. <https://doi.org/10.2307/1911307>

> **Note**: Established the formal conditions under which cooperative equilibria can be sustained indefinitely in repeated games through credible threats of punishment. Underpins Athena's defection response matrix (Protocol 500 §4D) across repeated interaction horizons.

Fudenberg, D., & Tirole, J. (1985). Preemption and rent equalization in the adoption of new technology. *Review of Economic Studies, 52*(3), 383–401. <https://doi.org/10.2307/2297660>

> **Note**: Modeled timing games and the strategic trade-off between first-mover preemption and waiting for information resolution. Formalizes Path E in Protocol 500 (Option Value of Delay vs Preemption).

Gilboa, I., & Schmeidler, D. (1989). Maxmin expected utility with non-unique prior. *Journal of Mathematical Economics, 18*(2), 141–153. <https://doi.org/10.1016/0304-4068(89)90018-9>

> **Note**: Formalized decision-making under Knightian ambiguity (multiple plausible priors), establishing maxmin expected utility as a robust criterion when probabilities cannot be empirically identified. Implemented in `gto_engine.py`'s maximin floor optimization.

Halpern, J. Y., & Rego, L. C. (2014). Extensive games with possibly unaware players. *Mathematical Social Sciences, 70*, 42–58. <https://doi.org/10.1016/j.mathsocsci.2012.11.002>

> **Note**: Extends extensive-form games to players who are unaware of certain actions until revealed. Directly grounds Athena's handling of open games: because players cannot anticipate all unmodeled moves or rule changes, survival requires structural downside bounding (position limits, defined-risk structures) rather than optimizing over a closed game tree.

Harsanyi, J. C. (1967). Games with incomplete information played by "Bayesian" players, Part I: The basic model. *Management Science, 14*(3), 159–182. <https://doi.org/10.1287/mnsc.14.3.159>

> **Note**: Founded the theory of games with asymmetric and incomplete information by modeling player types via common priors. Grounds Protocol 422 Rule 4 (separating stochastic noise from hidden information) and Protocol 500 Path D (cheap probes to screen counterparty types).

Heifetz, A., Meier, M., & Schipper, B. C. (2006). Interactive unawareness. *Journal of Economic Theory, 130*(1), 78–94. <https://doi.org/10.1016/j.jet.2005.02.007>

> **Note**: Provided the epistemic foundation for modeling mutual unawareness in multi-agent environments. Complements Halpern & Rego (2014) in formalizing the limits of textbook closed-world game theory.

Maynard Smith, J., & Price, G. R. (1973). The logic of animal conflict. *Nature, 246*(5427), 15–18. <https://doi.org/10.1038/246015a0>

> **Note**: Introduced the Hawk-Dove game and the concept of Evolutionarily Stable Strategies (ESS). Demonstrates that conflict games with costly escalation are fundamentally mixed-motive, not zero-sum, motivating structural de-escalation and commitment devices in Protocol 500 §4D.

Myerson, R. B. (1998). Population uncertainty and Poisson games. *International Journal of Game Theory, 27*(3), 375–392. <https://doi.org/10.1007/s001820050079>

> **Note**: Formally models games where the number of players is an unobserved random variable (Poisson distributed). Grounds Athena's Balance-Sheet Census (Protocol 500 §0.5): evaluating exposure across unknown potential participants by separating capacity to intervene from willingness to act.

Savage, L. J. (1951). The theory of statistical decision. *Journal of the American Statistical Association, 46*(253), 55–67. <https://doi.org/10.1080/01621459.1951.10500768>

> **Note**: Introduced the minimax regret decision criterion. Implemented in `gto_engine.py` (`compute_robustness`) to select policies that minimize worst-case opportunity loss across uncertain future scenarios.

Schelling, T. C. (1960). *The strategy of conflict*. Harvard University Press.

> **Note**: The foundational work on strategic commitment, focal points (Schelling points), and mixed-motive bargaining. Grounds Protocol 500 §4D (binding commitment devices, escrow, and staged execution) when parties operate under high mutual dependency.

Taleb, N. N. (2007). *The black swan: The impact of the highly improbable*. Random House.

> **Note**: Chapter 9 introduces the *Ludic Fallacy* — the fatal mistake of confusing the clean, bounded uncertainty of games (dice, casinos, textbook payoff matrices) with the open-ended, fat-tailed uncertainty of real life. Underpins Athena's refusal to compute closed Nash equilibria for real-world dilemmas, mandating structural exposure bounds (Law #1) and fail-closed ruin screening instead.

Wu, J., & Axelrod, R. (1995). How to cope with noise in the iterated prisoner's dilemma. *Journal of Conflict Resolution, 39*(1), 183–189. <https://doi.org/10.1177/0022002795039001008>

> **Note**: Demonstrated that in the presence of noise (misimplementation or misperception of moves), standard Tit-for-Tat triggers endless mutual defection loops. Generous Tit-for-Tat and Contrite Tit-for-Tat restore cooperation through calibrated tolerance, directly grounding Athena's noise-tolerant relational defection responses in Protocol 500 §4D.

---

## AI, Machine Learning & Retrieval-Augmented Generation

Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems, 33*, 1877–1901. <https://arxiv.org/abs/2005.14165>

Dell'Acqua, F., McFowland, E., III, Mollick, E. R., Lifshitz-Assaf, H., Kellogg, K., Rajendran, S., ... & Lakhani, K. R. (2023). Navigating the jagged technological frontier: Field experimental evidence of the effects of AI on knowledge worker productivity and quality. *Harvard Business School Technology & Operations Management Unit Working Paper No. 24-013*. <https://doi.org/10.2139/ssrn.4573321>

Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., & Mordatch, I. (2023). Improving factuality and reasoning in language models through multiagent debate. *arXiv preprint arXiv:2305.14325*. <https://arxiv.org/abs/2305.14325>

Khattab, O., Singhvi, A., Maheshwari, P., Zhang, Z., Santhanam, K., Vardhamanan, S., ... & Potts, C. (2023). DSPy: Compiling declarative language model calls into self-improving pipelines. *arXiv preprint arXiv:2310.03714*. <https://arxiv.org/abs/2310.03714>

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems, 33*, 9459–9474. <https://arxiv.org/abs/2005.11401>

Liang, Y., Wu, Z., Liu, Y., Sun, Q., & Liu, D. (2023). Encouraging divergent thinking in large language models through multi-agent debate. *arXiv preprint arXiv:2305.19118*. <https://arxiv.org/abs/2305.19118>

Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). Lost in the middle: How language models use long contexts. *Transactions of the Association for Computational Linguistics, 12*, 157–173. <https://arxiv.org/abs/2307.03172>

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., ... & Zhou, D. (2022). Chain-of-thought prompting elicits reasoning in large language models. *Advances in Neural Information Processing Systems, 35*, 24824–24837. <https://arxiv.org/abs/2201.11903>

Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T. L., Cao, Y., & Narasimhan, K. (2024). Tree of thoughts: Deliberate problem solving with large language models. *Advances in Neural Information Processing Systems, 36*. <https://arxiv.org/abs/2305.10601>

---

## Agent Architecture & Tool Use

Schick, T., Dwivedi-Yu, J., Dessì, R., Raileanu, R., Lomeli, M., Hambro, E., ... & Scialom, T. (2024). Toolformer: Language models can teach themselves to use tools. *Advances in Neural Information Processing Systems, 36*. <https://arxiv.org/abs/2302.04761>

Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2024). Reflexion: Language agents with verbal reinforcement learning. *Advances in Neural Information Processing Systems, 36*. <https://arxiv.org/abs/2303.11366>

Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., ... & Wang, J. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science, 18*(6), 186345. <https://arxiv.org/abs/2308.11432>

Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing reasoning and acting in language models. *International Conference on Learning Representations (ICLR)*. <https://arxiv.org/abs/2210.03629>

---

## Agent Memory & Long-Term Personalization

> This section grounds Athena's core thesis — that persistent, structured, externally-owned memory changes what an LLM agent can do — in the peer-reviewed and preprint literature. These are the papers a skeptic should read before dismissing "compounding memory" as marketing.

Packer, C., Wooders, S., Lin, K., Fang, V., Patil, S. G., Stoica, I., & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as operating systems. *arXiv preprint arXiv:2310.08560*. <https://arxiv.org/abs/2310.08560>

> **Note**: MemGPT introduced OS-style virtual memory management for LLMs — a fixed context window treated as RAM, with paging to external storage. Athena's JIT boot (2K–20K tokens loaded from a much larger disk-resident memory) is the same architectural insight, implemented as files + retrieval rather than a runtime. Athena's local-first memory and context management architecture has a direct academic analogue here.

Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. *Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology (UIST '23)*, 1–22. <https://doi.org/10.1145/3586183.3606763>

> **Note**: The Stanford "Smallville" paper demonstrated that a memory stream + retrieval + periodic reflection loop produces qualitatively richer agent behavior than context alone. Athena's session logs (memory stream), Exocortex search (retrieval), and `/end` insight-filing (reflection) implement the same three-component architecture for a single real user instead of simulated townspeople.

Sumers, T. R., Yao, S., Narasimhan, K., & Griffiths, T. L. (2024). Cognitive architectures for language agents. *Transactions on Machine Learning Research*. <https://arxiv.org/abs/2309.02427>

> **Note**: CoALA provides the formal taxonomy Athena instantiates: working memory (context window), episodic memory (session logs), semantic memory (CANONICAL / protocols), and procedural memory (skills / workflows), with decision procedures governing retrieval and action. Athena was built independently but maps cleanly onto this framework — useful as the academic vocabulary for the architecture.

Wu, D., Wang, H., Yu, W., Zhang, Y., Chang, K.-W., & Yu, D. (2024). LongMemEval: Benchmarking chat assistants on long-term interactive memory. *arXiv preprint arXiv:2410.10813*. <https://arxiv.org/abs/2410.10813>

> **Note**: LongMemEval showed that commercial assistants' long-term memory degrades sharply on multi-session tasks (information extraction, temporal reasoning, knowledge updates across sessions) — the empirical case for Athena's central complaint about platform memory. It is also the closest existing template for the benchmark Athena's own [What's Enforced in Code](../README.md#whats-enforced-in-code-vs-by-prompt) table says is still missing: decision-quality-vs-session-count, not just recall accuracy.

---

## Knowledge Graphs & GraphRAG

Edge, D., Trinh, H., Cheng, N., Bradley, J., Chao, A., Mody, A., ... & Larson, J. (2024). From local to global: A graph RAG approach to query-focused summarization. *arXiv preprint arXiv:2404.16130*. <https://arxiv.org/abs/2404.16130>

Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain to Leiden: Guaranteeing well-connected communities. *Scientific Reports, 9*(1), 5233. <https://doi.org/10.1038/s41598-019-41695-z>

Pan, S., Luo, L., Wang, Y., Chen, C., Wang, J., & Wu, X. (2024). Unifying large language models and knowledge graphs: A roadmap. *IEEE Transactions on Knowledge and Data Engineering, 36*(7), 3580–3599. <https://arxiv.org/abs/2306.08302>

---

## Retrieval & Search

Cormack, G. V., Clarke, C. L. A., & Büttcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. *Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval*, 758–759. <https://doi.org/10.1145/1571941.1572114>

Nogueira, R., & Cho, K. (2020). Passage re-ranking with BERT. *arXiv preprint arXiv:1901.04085*. <https://arxiv.org/abs/1901.04085>

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP)*. <https://arxiv.org/abs/1908.10084>

Robertson, S. E., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval, 3*(4), 333–389. <https://doi.org/10.1561/1500000019>

> **Note**: The definitive formalization of Okapi BM25 and the probabilistic relevance framework. Grounds the lexical retrieval channel in Athena's Hybrid RAG stack (SQLite FTS5 BM25 + pgvector dense embeddings), fused via Reciprocal Rank Fusion (Cormack et al., 2009).

---

## Prompt Engineering & Context Window Management

Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., ... & Zhou, D. (2023). Self-consistency improves chain of thought reasoning in language models. *International Conference on Learning Representations (ICLR)*. <https://arxiv.org/abs/2203.11171>

Xu, F. F., Alon, U., Neubig, G., & Hellendoorn, V. J. (2022). A systematic evaluation of large language models of code. *Proceedings of the 6th ACM SIGPLAN International Symposium on Machine Programming*, 1–10. <https://arxiv.org/abs/2202.13169>

Zhou, D., Schärli, N., Hou, L., Wei, J., Scales, N., Wang, X., ... & Chi, E. (2023). Least-to-most prompting enables complex reasoning in large language models. *International Conference on Learning Representations (ICLR)*. <https://arxiv.org/abs/2205.10625>

---

## Business Strategy & Productivity

Dalio, R. (2017). *Principles: Life and work*. Simon & Schuster.

Graham, P. (2009). *Maker's schedule, manager's schedule*. <http://www.paulgraham.com/makersschedule.html>

Juran, J. M. (1951). *Quality control handbook*. McGraw-Hill. [Origin of the 80/20 "vital few" principle, building on Pareto]

Koch, R. (1998). *The 80/20 principle: The secret to achieving more with less*. Nicholas Brealey Publishing.

Pearson, T. (2015). *The end of jobs: Money, meaning and freedom without the 9-to-5*. Lioncrest Publishing.

Pearson, T. (2018, June 6). The ultimate guide to apprenticeships. *Mission.org*. <https://medium.com/the-mission/the-ultimate-guide-to-apprenticeships-54fc932683a2>

Ries, E. (2011). *The lean startup: How today's entrepreneurs use continuous innovation to create radically successful businesses*. Crown Business.

Snowden, D. J., & Boone, M. E. (2007). A leader's framework for decision making. *Harvard Business Review, 85*(11), 68–76.

> **Note**: Introduced the Cynefin sensemaking framework (Clear, Complicated, Complex, Chaotic, Confusion). Directly grounds Protocol 525's progressive domain reclassification and cross-domain weighting matrix.

Taleb, N. N. (2004). *Fooled by randomness: The hidden role of chance in life and in the markets* (2nd ed.). Random House.

Taleb, N. N. (2012). *Antifragile: Things that gain from disorder*. Random House.

Taleb, N. N. (2018). *Skin in the game: Hidden asymmetries in daily life*. Random House.

---

## Epistemology & Frameworks

Frankfurt, H. G. (2005). *On bullshit*. Princeton University Press. [Academic basis for BS-detection heuristics]

Rumsfeld, D. H. (2002, February 12). DoD news briefing — Secretary Rumsfeld and Gen. Myers [Press briefing transcript]. U.S. Department of Defense. [Origin of the "known unknowns" framework, widely attributed]

> **Note**: The "known unknowns" matrix predates Rumsfeld's press conference. The conceptual framework traces to the Johari Window (Luft & Ingham, 1955) and NASA risk management literature from the 1990s. Rumsfeld popularized the terminology.

---

## AI Safety & Alignment

Perez, E., Ringer, S., Lukošiūtė, K., Nguyen, K., Chen, E., Heiner, S., ... & Kaplan, J. (2023). Discovering language model behaviors with model-written evaluations. *Findings of the Association for Computational Linguistics: ACL 2023*, 13387–13434. <https://arxiv.org/abs/2212.09251>

> **Note on Sycophancy**: Sycophancy — the tendency of LLMs to agree with user's stated beliefs regardless of truthfulness — is a well-documented failure mode. Perez et al. (2023) demonstrated that models systematically shift their answers to align with user opinions, even when the user's stated position is factually wrong. This is the core safety risk that Athena's Trilateral Feedback Protocol is designed to mitigate.

Wrongful-death action against OpenAI (and Microsoft), U.S. District Court, N.D. Cal., filed Dec. 29, 2025 — arising from the Aug. 5, 2025 Soelberg murder-suicide in Greenwich, CT. *(Caption and docket hedged: the "Soelberg v. OpenAI, No. 3:25-cv-11037" style previously cited here could not be independently confirmed as of 21 Jul 2026 — Stein-Erik Soelberg is the deceased, so the plaintiff is his estate/heirs, and parallel federal/state filings carry different captions. Confirm the exact style against PACER before any legal-adjacent use.)*

> **Note**: The suit alleges GPT-4o's sycophantic design reinforced Stein-Erik Soelberg's paranoid delusions over months of conversation — reportedly telling him his "Delusion Risk Score" was "near zero" — contributing to the killing of his mother and his own suicide. Cited in Athena's [Trilateral Feedback](TRILATERAL_FEEDBACK.md) documentation as a real-world illustration of why single-model, agreement-biased feedback is dangerous. Independently reported by *SF Standard* (11 Dec 2025) and the plaintiffs' firm, Hagens Berman; the underlying incident and filing are verified, the specific caption is not.

Wei, A., Haghtalab, N., & Steinhardt, J. (2024). Jailbroken: How does LLM safety training fail? *Advances in Neural Information Processing Systems, 36*. <https://arxiv.org/abs/2307.02483>

---

## Sycophancy & the Personalization Tension

> **Why this section exists**: Athena's central mechanism — injecting a condensed, persistent user profile into context — is the *same* mechanism the 2025–2026 literature identifies as the largest amplifier of sycophancy. Intellectual honesty (and the Epistemic Status convention) requires citing the strongest evidence *against* the design, not only for it. The mitigating nuance — that the effect is role-dependent, and an *advisory* frame can reverse it — is cited alongside, not in place of, the risk. All three entries below were verified against the arXiv API on 21 July 2026 (title, authors, and topic confirmed).

Fanous, A., Goldberg, J., Agarwal, A. A., Lin, J., Zhou, A., Daneshjou, R., & Koyejo, S. (2025). SycEval: Evaluating LLM sycophancy. *Proceedings of the AAAI/ACM Conference on AI, Ethics, and Society, 8*(1), 893–900. <https://doi.org/10.1609/aies.v8i1.36598> (arXiv:2502.08177)

> **Note**: Measured a 58.19% overall sycophancy (capitulation) rate across ChatGPT-4o (56.71%), Claude-Sonnet, and Gemini-1.5-Pro (62.47%). Baseline evidence that sycophancy is a *majority-case* failure in frontier models, not an edge case — the problem Athena's meta-awareness gate exists to counter.

Jain, S., Park, C., Viana, M., Wilson, A., & Calacci, D. (2025). Interaction context often increases sycophancy in LLMs. *arXiv preprint arXiv:2509.12517*. <https://arxiv.org/abs/2509.12517>

> **Note**: The load-bearing citation for Athena's honesty pass. Agreement sycophancy rises **substantially when a user memory profile is present** (reported +45% for Gemini 2.5 Pro) — i.e., the persistent-profile architecture that *is* Athena is empirically among the top drivers of the mirror effect. Cited directly in the README's [What's Enforced in Code](../README.md#whats-enforced-in-code-vs-by-prompt) as the strongest evidence against the design.

Kelley, S. W., & Riedl, C. (2026). Personalization increases affective alignment but has role-dependent effects on epistemic independence in LLMs. *arXiv preprint arXiv:2603.00024*. <https://arxiv.org/abs/2603.00024>

> **Note**: The mitigating nuance — and the empirical case for Athena's advisory framing. Personalization broadly increases *affective* alignment (validation, hedging, deference), but its effect on *epistemic* independence is role-dependent: in a **social-peer** frame it erodes independence, while in an **advisory** frame it can *strengthen* it. Athena's entire posture (Chief-of-Staff, premise-challenge, "hand the pen back") is a deliberate bet that the advisory frame is the protective condition this paper isolates — a bet only as strong as the frame is actually *enforced*, which is the job of the meta-awareness gate.

---

## Information Theory & System Design

Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal, 27*(3), 379–423. <https://doi.org/10.1002/j.1538-7305.1948.tb01338.x>

> **Note**: Shannon's information theory provides the mathematical foundation for Athena's risk-proportional routing. The classification tier (SNIPER / STANDARD / ULTRA) is fundamentally a channel capacity problem: how much information about query risk can be extracted at minimal cost? The Λ complexity score is an entropy estimate that determines how much computational "bandwidth" to allocate.

Graves, A. (2016). Adaptive computation time for recurrent neural networks. *arXiv preprint arXiv:1603.08983*. <https://arxiv.org/abs/1603.08983>

> **Note**: Graves introduced the concept of *adaptive computation time* — allowing neural networks to allocate variable amounts of processing to different inputs based on difficulty. This is the ML-theoretic foundation of Athena's Λ-scoring: simple queries get SNIPER-level processing; complex queries get ULTRA-level processing. The system "thinks harder" when the input warrants it.

Tarjan, R. E. (1985). Amortized computational complexity. *SIAM Journal on Algebraic and Discrete Methods, 6*(2), 306–318. <https://doi.org/10.1137/0606031>

> **Note**: Tarjan formalized *amortized analysis* — proving that expensive operations can be "paid for" by cheaper ones when analyzed over a sequence. This grounds Protocol 49 §49.9.1 (Pre-Computation / Amortized Robustness): Athena's expensive `/start` boot sequence is a one-time cost that buys robustness for all subsequent queries at zero marginal latency.

---

## Systems Biology & Cognitive Architecture

von Bertalanffy, L. (1968). *General system theory: Foundations, development, applications*. George Braziller.

> **Note**: von Bertalanffy's General Systems Theory provides the formal foundation for Athena's Biological Stack Architecture. The principle that systems exhibit emergent properties not reducible to their parts — and that hierarchical organization (subsystem → system → suprasystem) is a universal pattern — directly maps to Athena's hierarchy: Protocols → Clusters → Cognitive Systems → Organism.

Meadows, D. H. (2008). *Thinking in systems: A primer* (D. Wright, Ed.). Chelsea Green Publishing.

> **Note**: Meadows' principles of system dynamics (feedback loops, delays, leverage points, and structure driving behavior) provide the conceptual foundation for Athena's Meta-Pattern Engine (MP-1 through MP-14) and the Iceberg Model detailed in `docs/concepts/Systems_Thinking.md`.

Minsky, M. (1986). *The society of mind*. Simon & Schuster.

> **Note**: Minsky's "Society of Mind" theory — that intelligence emerges from the interaction of many small, unintelligent agents — is the conceptual ancestor of Athena's multi-protocol architecture. Each protocol is a "mindless agent"; intelligence emerges from their orchestrated interaction via clusters and cognitive systems.

Newell, A. (1990). *Unified theories of cognition*. Harvard University Press.

> **Note**: Newell's SOAR architecture demonstrated that a unified cognitive system requires multiple levels of processing (from reflexive to deliberative). Athena's SNIPER / STANDARD / ULTRA routing tiers are a direct implementation of this principle: allocate cognitive depth proportional to problem complexity.

---

## Problem Framing & Wicked Problems

Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review, 78*(1), 1–3. <https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2>

> **Note**: Brier introduced the canonical strictly proper scoring rule for probability forecasts. Implemented in `frame_ledger.py` (`compute_brier_score`) to measure calibration across pre-registered hypotheses against the 0.25 random coin-flip baseline.

Howard, R. A. (1966). Information value theory. *IEEE Transactions on Systems Science and Cybernetics, 2*(1), 22–26. <https://doi.org/10.1109/TSSC.1966.300074>

> **Note**: Howard formalized the concepts of Value of Information (VOI) and Expected Value of Information (EVI). Grounds the anti-rumination stop rule in `frame_ledger.py` (Rule R8): computational deliberation is terminated when the expected value of further analysis falls below the cost of a cheap empirical probe.

Rittel, H. W. J., & Webber, M. M. (1973). Dilemmas in a general theory of planning. *Policy Sciences, 4*(2), 155–169. <https://doi.org/10.1007/BF01405730>

> **Note**: Rittel & Webber's formalization of "wicked problems" — problems that resist definition and have no stopping rule — is the theoretical basis for Protocol 504 (Problem Framing). Their insight that "the formulation of a wicked problem IS the problem" directly motivates P504's 5-gate diagnostic before any solution attempt.

Spradlin, D. (2012). Are you solving the right problem? *Harvard Business Review, 90*(9), 84–93.

> **Note**: Spradlin's HBR framework for problem articulation — distinguishing between the stated problem and the actual problem — informed Protocol 504's emphasis on framing before execution. The observation that 85% of companies he studied were solving the wrong problem validates P504's existence.

---

## Developmental & Clinical Psychology

Schwartz, R. C. (1995). *Internal family systems therapy*. Guilford Press.

> **Note**: Schwartz's Internal Family Systems (IFS) model — which treats the psyche as a system of sub-personalities ("parts") with protective and exiled roles — provides the therapeutic framework for Athena's Inner Work cluster (#7) and the `therapeutic-ifs` skill. IFS is evidence-based and recognized by NREPP.

Young, J. E., Klosko, J. S., & Weishaar, M. E. (2003). *Schema therapy: A practitioner's guide*. Guilford Press.

> **Note**: Schema Therapy's concept of "early maladaptive schemas" — stable, self-defeating patterns formed in childhood — grounds Athena's schema deconstruction skill. The 18-schema taxonomy provides the diagnostic vocabulary for Cluster #7's pattern detection.

---

## AI Benchmarks & Live Evaluation Infrastructure

Arena Intelligence. (2026, September 2). *Agent Arena Leaderboard: Dynamic ranking of models on how well they orchestrate tools for real-world agentic tasks*. Arena AI. <https://arena.ai/leaderboard/agent>

> **Note**: The Agent Arena leaderboard provides empirical, causal evaluation of frontier models based on over 2.18 million real-world agentic sessions across 58 models. It measures key operational dimensions: net task improvement, confirmed success rate (task outcome explicit confirmation), steerability (landing user pushback/corrections), bash error recovery steps, and tool hallucination rate. Serves as Athena's empirical benchmark and selection matrix for cross-model validation pairings in Protocol 171 (`VER-171-cross-model-validation.md`) and runtime multi-agent ensembling.

LMSYS Org. (2026). *Chatbot Arena LLM Leaderboard*. Large Model Systems Organization. <https://lmarena.ai>

> **Note**: Crowdsourced open evaluation platform evaluating general reasoning, coding, and instruction following via pairwise human preference (Elo rating) across 350+ models. Serves as secondary validation infrastructure for general model capabilities and cost-performance Pareto frontiers.

---

## How Citations Are Used in This Repository

Inline citations follow APA format: `(Author, Year)`. For example:

- *"The Johari Window divides knowledge into four quadrants"* → (Luft & Ingham, 1955)
- *"Anchoring bias — first number sets the reference point"* → (Tversky & Kahneman, 1974)
- *"Bounded rationality: execute 'Good Enough' immediately"* → (Simon, 1956)
- *"Graph RAG: from local to global summarization"* → (Edge et al., 2024)
- *"Cross-encoder reranking for retrieval quality"* → (Nogueira & Cho, 2020)
- *"A mathematical theory of communication"* → (Shannon, 1948)
- *"Antifragile systems gain from disorder"* → (Taleb, 2012)

When a concept is referenced frequently across multiple documents, the first instance in each document includes the full inline citation. Subsequent mentions within the same document use the short form.

For AI/ML papers, arXiv links are provided alongside formal publication details where available.

---

*Last verified: 20 October 2026 — added foundational citations for Value of Information (Howard, 1966), probability forecast verification (Brier, 1950), Okapi BM25 probabilistic retrieval (Robertson & Zaragoza, 2009), systems thinking (Meadows, 2008), and Cynefin sensemaking (Snowden & Boone, 2007), directly grounding frame_ledger.py, hybrid RAG lexical FTS, and Systems_Thinking.md. **Full re-verification sweep this date: 35/35 DOIs (Crossref API) + 28/28 arXiv IDs (arXiv export API), 0 failures.** Previous fact-checks: 4 October 2026; 5 September 2026; 23 July 2026; 22 July 2026; 5 July 2026; 6 June 2026 (S437).*

# Protocol 105: Neuro-Symbolic Verification Loop

> **Purpose**: Bridge the gap between "Intuition" (LLM) and "Ground Truth" (Code) by creating a self-correcting loop for verifiable claims.
> **Source**: Adopted from Google DeepMind's "Gemini for Scientific Discovery" (arXiv:2602.03837)
> **Trigger**: Logic puzzles, Complex math, Cryptographic proofs, Algorithmic derivations.
> **Tags**: #neuro-symbolic #verification #code-interpreter #ground-truth

---

## 1. The Core Loop

**"Don't guess. Run."**

When faced with a problem that has a objectively verifiable answer (math, logic, code behavior), **NEVER** rely on internal monolithic reasoning alone.

### The Cycle

1. **Derive (Intuition)**: Formulate a hypothesis or initial solution using standard reasoning.
2. **Transpile (Symbolic)**: Convert the hypothesis into an executable Python script (`verification_script.py`).
3. **Execute (Ground Truth)**: Run the script to capture actual output.
4. **Refine (Loop)**:
    * If Output == Hypothesis -> **CONFIRM**.
    * If Output != Hypothesis -> **DEBUG** the logic, not the hypothesis. Did the code fail, or was the intuition wrong?
    * **Loop** until Code and Intuition align.

---

## 2. Implementation Triggers

### A. Mathematical Derivations

* *Query*: "What is the 100th Fibonacci number that is also prime?"
* *Action*: Do NOT derive textually. Write a script to calculate it.

### B. Logic Puzzles

* *Query*: "Three gods A, B, and C are called True, False, and Random..."
* *Action*: Model the logic constraints in Z3 or Python sets. Solve via satisfiability.

### C. Cryptographic/Algorithmic Claims

* *Query*: "Verify if this curve is secure."
* *Action*: Write a SageMath or Python script to check curve parameters against known attacks.

---

## 3. The "Verifier" Pattern

When generating the verification script, adhere to the **Verifier Pattern**:

```python
# verification_script.py
def verify_hypothesis():
    # 1. Define the Ground Truth constraints
    target_value = ...
    
    # 2. Implement the Logic
    result = ...
    
    # 3. Assert Truth
    assert result == target_value, f"Mismatch: {result} != {target_value}"
    print(f"✅ Verified: {result}")

if __name__ == "__main__":
    verify_hypothesis()
```

---

## 4. Integration with Reasoning

* **Output Format**:
    > "I have derived a solution, but to ensure absolute accuracy, I have verified it numerically."
    > [Show Code]
    > [Show Output]
    > "The verified answer is X."

* **Failure Protocol**:
    If the code contradicts your intuition, **TRUST THE CODE**.
  * *Self-Correction*: "Initially, I hypothesized X. However, the simulation proves Y. The error in my reasoning was..."

---

## 5. Metadata

Tags: #verification #math #logic #python #grounding

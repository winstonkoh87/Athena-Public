import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate import Evaluate
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configure DSPy to use Gemini (via Vertex AI or Google AI Studio)
# NOTE: DSPy supports Google models. You need to ensure credentials are set.
# If using the 'dspy.Google' provider, it needs api_key.

try:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  Warning: GEMINI_API_KEY not found. Optimization will likely fail.")

    # Initialize the Language Model using the new dspy.LM interface (LiteLLM backend)
    # Prefix with 'gemini/' for LiteLLM
    lm = dspy.LM("gemini/gemini-1.5-flash", api_key=api_key)
    dspy.configure(lm=lm)
except Exception as e:
    print(f"Error configuring DSPy LM: {e}")


# 1. Define the Signature (Input/Output Interface)
class StrategicReasoning(dspy.Signature):
    """
    Synthesize a "Category of One" strategy by connecting unrelated domains or using deep reframing.
    Output should be actionable, concise, and high-status.
    """

    input_text = dspy.InputField(desc="The user's query or problem.")
    strategy = dspy.OutputField(desc="The synthesized strategic advice.")


# 2. Define the Module (The Chain of Thought)
class LateralStrategist(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(StrategicReasoning)

    def forward(self, input_text):
        return self.prog(input_text=input_text)


# 3. Load the Golden Dataset
def load_dataset():
    with open(".agent/datasets/golden_reasoning.json", "r") as f:
        data = json.load(f)

    # Convert to DSPy Examples
    examples = [
        dspy.Example(input_text=d["input"], strategy=d["output"]).with_inputs(
            "input_text"
        )
        for d in data
    ]
    return examples


# 4. Define the Metric (How do we judge quality?)
# For now, we use a simple "Similarity" metric or LLM-based judge.
# Here we define a simple metric function.
def validate_strategy(example, pred, trace=None):
    # Check if the response is non-empty and reasonably long
    return len(pred.strategy) > 50


# 5. The Optimizer Loop
def optimize():
    print("🧬 Starting DSPy Optimization Loop...")

    trainset = load_dataset()

    # Define the Teleprompter (The Optimizer)
    # BootstrapFewShot extracts the best examples and rationales to put in the prompt.
    teleprompter = BootstrapFewShot(
        metric=validate_strategy, max_bootstrapped_demos=3, max_labeled_demos=3
    )

    # Compile the program
    print("   Compiling (Optimizing)... This acts as 'Training'...")
    optimized_program = teleprompter.compile(LateralStrategist(), trainset=trainset)

    # Save the optimized prompt
    save_path = ".agent/prompts/optimized/strategic_analysis.json"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    optimized_program.save(save_path)

    print(f"✅ Optimization Complete. Compiled prompt saved to {save_path}")

    # Verify
    print("\n--- Test Run (Optimized) ---")
    question = "How do I make a boring accounting firm go viral?"
    pred = optimized_program(input_text=question)
    print(f"Q: {question}")
    print(f"A: {pred.strategy}")


if __name__ == "__main__":
    optimize()

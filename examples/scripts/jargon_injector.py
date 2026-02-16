#!/usr/bin/env python3
"""
athena.core.kinetic.jargon_injector
===================================
Kinetic Information Engine (Protocol 053) - The Jargon Injector

Uses TF-IDF (Term Frequency-Inverse Document Frequency) to extract "High-Status Vocabulary"
from specific Wikipedia categories. It identifies words that are common *locally* (in the target niche)
but rare *globally* (in general English), signaling deep expertise.

Dependencies:
    pip install scikit-learn numpy

Usage:
    python3 jargon_injector.py "Dermatology"
"""

import sys
import math
from collections import Counter
import re

# Mock the sklearn import to allow the script to run without the package installed
# In production, remove this mock and use: from sklearn.feature_extraction.text import TfidfVectorizer
try:
    from sklearn.feature_extraction.text import TfidfVectorizer

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print(
        "⚠️  Scikit-learn not installed. Using native Python TF-IDF implementation for demonstration."
    )

# --- MOCK DATA LOADER ---


def load_category_documents(category: str):
    """
    Simulates loading documents from the local Wikipedia dump for a specific category.
    """
    print(f"📚 [DISK] Loading documents for Category: '{category}'...")

    if category.lower() == "dermatology":
        return [
            "Dermatology involves the study of skin, hair, and nails. Conditions include acne, eczema, and psoriasis.",
            "Botulinum toxin (Botox) is used to treat wrinkles by paralyzing facial muscles.",
            "Hyaluronic acid is a glycosaminoglycan distributed widely throughout connective, epithelial, and neural tissues.",
            "The Fitzpatrick scale is a numerical classification schema for human skin color.",
            "Tretinoin is the carboxylic acid form of vitamin A and is used to treat acne vulgaris and keratosis pilaris.",
            "Neocollagenesis is the formation of new collagen, often stimulated by laser therapy or microneedling.",
            "Melasma is a common skin problem. It causes brown to gray-brown patches, usually on the face.",
            "Cryotherapy is the use of extreme cold in surgery or other medical treatment.",
            "Mohs surgery is a precise surgical technique used to treat skin cancer.",
            "Photodynamic therapy involves light-sensitive medicine and a light source to destroy abnormal cells.",
        ]
    elif category.lower() == "military_strategy":
        return [
            "Attrition warfare is a military strategy consisting of belligerent attempts to win a war by wearing down the enemy.",
            "The OODA loop (Observe, Orient, Decide, Act) is the cycle of decision-making.",
            "Center of gravity is the hub of all power and movement, on which everything depends.",
            "Flanking maneuver involves attacking the enemy from the side/rear rather than the front.",
            "Logistics is the management of the flow of things between the point of origin and the point of consumption.",
            "Asymmetric warfare is war between belligerents whose relative military power differs significantly.",
            "Blitzkrieg is an attacking force, encapsulated by a dense concentration of armoured and motorised or mechanised infantry formations.",
            "Encirclement is a military term for the situation when a force or target is isolated and surrounded by enemy forces.",
            "Scorched earth is a military strategy that aims to destroy anything that might be useful to the enemy.",
            "Total war includes any and all civilian-associated resources and infrastructure as legitimate military targets.",
        ]
    else:
        # Default generic text
        return [
            f"This is a generic article about {category}.",
            f"Here is some more information regarding the topic of {category}.",
            "It is very interesting and has many applications.",
        ]


def load_general_corpus():
    """
    Simulates a small 'General English' corpus to calculate Inverse Document Frequency (IDF).
    """
    return [
        "The quick brown fox jumps over the lazy dog.",
        "To be or not to be, that is the question.",
        "I love eating pizza and drinking soda.",
        "The weather is nice today, sunny and bright.",
        "Cars drive on the road and stop at traffic lights.",
        "Computers are useful for calculation and processing information.",
        "Music is the art of arranging sounds in time.",
        "Sports are physical activities that involve skill and competition.",
        "Reading books is a good way to learn new things.",
        "Writing code is a skill that requires logic and practice.",
    ]


# --- NATIVE TF-IDF IMPLEMENTATION (For Demo) ---


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def compute_tf(text):
    tokens = tokenize(text)
    tf_map = Counter(tokens)
    total_tokens = len(tokens)
    return {k: v / total_tokens for k, v in tf_map.items()}


def compute_idf(corpus):
    idf_map = {}
    N = len(corpus)
    all_tokens = set([t for doc in corpus for t in tokenize(doc)])

    for t in all_tokens:
        count = sum([1 for doc in corpus if t in tokenize(doc)])
        idf_map[t] = math.log(N / (count + 1))  # +1 smoothing
    return idf_map


def run_native_tfidf(target_docs, reference_docs):
    # Combine corpora to get global IDF
    doc_corpus = target_docs + reference_docs
    idf_map = compute_idf(doc_corpus)

    # Calculate scores for words in TARGET docs
    word_scores = {}

    for doc in target_docs:
        tf_map = compute_tf(doc)
        for word, tf in tf_map.items():
            tfidf = tf * idf_map.get(word, 0)
            if word not in word_scores:
                word_scores[word] = 0
            word_scores[word] += tfidf  # Sum scores across target docs

    # Filter common stop words (very basic list)
    stop_words = {
        "the",
        "is",
        "of",
        "and",
        "a",
        "to",
        "in",
        "for",
        "with",
        "on",
        "that",
        "this",
        "it",
        "are",
        "by",
        "or",
        "an",
        "be",
    }

    # Sort
    sorted_words = sorted(
        [(k, v) for k, v in word_scores.items() if k not in stop_words and len(k) > 3],
        key=lambda x: x[1],
        reverse=True,
    )

    return sorted_words


# --- MAIN EXECUTION ---


def inject_jargon(category: str):
    print(f"\n💉 JARGON INJECTOR initializing for Niche: '{category.upper()}'\n")

    # 1. Load Data
    target_docs = load_category_documents(category)
    reference_docs = load_general_corpus()

    # 2. Extract Terms
    print("⚙️  Calculating TF-IDF scores (Local Freq vs Global Freq)...")

    top_terms = run_native_tfidf(target_docs, reference_docs)

    # 3. Output "Gold List"
    print("\n🏆 THE GOLD VOCABULARY LIST (Top 15 High-Status Terms):")
    print("-" * 50)

    for i, (term, score) in enumerate(top_terms[:15]):
        print(f"   {i + 1}. {term.ljust(20)} (Signaling Score: {score:.4f})")

    print("-" * 50)
    print("\n💡 CONSULTANT TIP: Instruct your Copywriting Agent to use these words.")
    print(
        f"   Instead of saying 'skin doctor', say 'specialist in {top_terms[0][0]} and {top_terms[1][0]}'."
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        category = sys.argv[1]
        inject_jargon(category)
    else:
        # Default Demo
        inject_jargon("Dermatology")

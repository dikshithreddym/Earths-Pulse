"""
Quick evaluation script for the SentimentAnalyzer.
Runs a small labeled dataset through the analyzer and prints simple metrics
so you can get an idea of accuracy on basic examples.

Run from backend folder, e.g.:
    python scripts/evaluate_sentiment.py

This is intended as a sanity check, not a full benchmark.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so imports from services/ work when running this script
sys.path.append(str(Path(__file__).parent.parent))

from services.sentiment_analyzer import SentimentAnalyzer

def normalize_expected(label: str) -> str:
    l = label.lower()
    if l in ("positive", "joyful", "happy", "pos"):
        return "joyful"
    if l in ("negative", "anxious", "sad", "neg"):
        return "anxious"
    return "neutral"

def normalize_pred(pred_label: str) -> str:
    l = pred_label.lower()
    if "positive" in l or "label_2" in l or "joy" in l:
        return "joyful"
    if "negative" in l or "label_0" in l or "sad" in l or "anxious" in l:
        return "anxious"
    return "neutral"

def run_evaluation():
    analyzer = SentimentAnalyzer()

    # Small labeled test set (text, expected_label)
    labeled = [
        ("I am so happy and excited about the results!", "positive"),
        ("This is the worst day ever, I hate this.", "negative"),
        ("The event was okay, nothing special.", "neutral"),
        ("Feeling anxious about the meeting tomorrow.", "negative"),
        ("What a wonderful surprise, I'm thrilled!", "positive"),
        ("I don't care either way.", "neutral"),
        ("I love this community, everyone is so helpful.", "positive"),
        ("So frustrated with the delays and bad service.", "negative"),
        ("Meh, it's fine.", "neutral"),
    ]

    correct = 0
    total = len(labeled)
    details = []

    for text, expected in labeled:
        res = analyzer.analyze(text)
        pred_norm = normalize_pred(res.get("label", "neutral"))
        exp_norm = normalize_expected(expected)
        ok = pred_norm == exp_norm
        if ok:
            correct += 1
        details.append((text, expected, res.get("label"), res.get("score"), ok))

    print("\nSentiment analyzer quick evaluation")
    print("----------------------------------")
    for t, e, p, s, ok in details:
        print(f"Expected: {e:<8} | Predicted: {p:<12} | score: {s:>6} | OK: {ok} | text: {t}")

    accuracy = correct / total if total else 0
    print(f"\nAccuracy on small test set: {accuracy:.2%} ({correct}/{total})")

if __name__ == '__main__':
    run_evaluation()

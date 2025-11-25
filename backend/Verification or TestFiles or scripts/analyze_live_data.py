"""Analyze current mood data for real vs fallback content.

Usage:
    python scripts/analyze_live_data.py --limit 200 --hours 6

Distinguishes fallback (synthetic/seeded) vs real fetched posts using `is_fallback`
and heuristics for older rows without the flag (seeded suffix or matching mock text).
Outputs JSON summary and a markdown table for the accuracy report.
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime
from collections import Counter
import json

sys.path.append(str(Path(__file__).parent.parent))

from services.database import DatabaseService
from models.mood import MoodPoint
from services.social_fetcher import SocialMediaFetcher

MOCK_TEXTS = set(SocialMediaFetcher()._mock_texts())

def infer_fallback(m: MoodPoint) -> bool:
    if getattr(m, "is_fallback", None) is True:
        return True
    if getattr(m, "is_fallback", None) is False:
        return False
    txt = (m.text or "").strip()
    if not txt:
        return True
    if txt in MOCK_TEXTS:
        return True
    if " — seeded for " in txt:
        return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--hours", type=int, default=24)
    args = parser.parse_args()

    db = DatabaseService()
    async def run():
        await db.connect()
        moods = await db.get_moods(limit=args.limit, hours=args.hours)
        await db.disconnect()

        total = len(moods)
        if total == 0:
            print("No data found.")
            return

        fallback_flags = [infer_fallback(m) for m in moods]
        fallback_count = sum(fallback_flags)
        real_count = total - fallback_count
        by_label = Counter(m.label for m in moods)
        by_source = Counter(m.source for m in moods)

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "total": total,
            "real": real_count,
            "fallback": fallback_count,
            "real_ratio": round(real_count / total, 3),
            "fallback_ratio": round(fallback_count / total, 3),
            "by_label": by_label,
            "by_source": by_source,
        }

        print(json.dumps(summary, indent=2, default=str))
        print("\nMarkdown table:\n")
        print("| Metric | Value |")
        print("|--------|-------|")
        print(f"| Total points | {total} |")
        print(f"| Real posts | {real_count} |")
        print(f"| Fallback posts | {fallback_count} |")
        print(f"| Real ratio | {summary['real_ratio']*100:.1f}% |")
        print(f"| Fallback ratio | {summary['fallback_ratio']*100:.1f}% |")
        print("\nBy label:")
        for label, c in by_label.items():
            print(f"  - {label}: {c}")
        print("\nBy source:")
        for src, c in by_source.items():
            print(f"  - {src}: {c}")

    import asyncio
    asyncio.run(run())

if __name__ == "__main__":
    main()
from datetime import datetime
from collections import deque

# ===== CONSTANTS =====
MAX_HISTORY = 10


class StatsTracker:
    """
    Single Responsibility: track and expose classification statistics.
    Open/Closed: add new stats methods without changing existing ones.
    """

    def __init__(self, max_history: int = MAX_HISTORY):
        self._counts  = {"organic": 0, "inorganic": 0}
        self._history = deque(maxlen=max_history)
        self._latest  = None

    def record(self, result: str, confidence: str) -> None:
        """Record a new classification result."""
        self._counts[result] += 1
        entry = {
            "result":     result,
            "confidence": confidence,
            "time":       datetime.now().strftime("%H:%M:%S"),
        }
        self._history.append(entry)
        self._latest = entry

    def to_dict(self) -> dict:
        """Return full stats as a serializable dict."""
        total = sum(self._counts.values())
        return {
            "total":     total,
            "organic":   self._counts["organic"],
            "inorganic": self._counts["inorganic"],
            "history":   list(self._history),
            "latest":    self._latest,
        }


# Module-level singleton — one tracker shared across all routes (DRY)
tracker = StatsTracker()

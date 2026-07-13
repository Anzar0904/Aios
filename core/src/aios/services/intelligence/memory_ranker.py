import time
from typing import Any, List


class MemoryRanker:
    def __init__(self, memories: List[Any]) -> None:
        self.memories = memories

    def rank(self, query: str, active_workspace: str, limit: int = 5) -> List[Any]:
        query_words = set(query.lower().split())

        ranked_memories = []
        for m in self.memories:
            score = 0.0

            # 1. Semantic overlap heuristic
            content_words = set(m.content.lower().split())
            if query_words:
                overlap = len(query_words.intersection(content_words))
                score += overlap * 2.0

            # 2. Recency heuristic
            if hasattr(m, "created_at") and m.created_at:
                age_seconds = time.time() - m.created_at
                recency_boost = max(0.0, 1.0 - (age_seconds / 86400.0))
                score += recency_boost

            # 3. Importance
            if hasattr(m, "metadata") and m.metadata:
                importance = getattr(m.metadata, "importance", 1)
                score += importance * 0.5

            # 4. Workspace match
            if hasattr(m, "metadata") and m.metadata:
                ws_id = getattr(m.metadata, "workspace_id", None)
                if ws_id == active_workspace:
                    score += 1.5

            # 5. Tags match
            if hasattr(m, "metadata") and m.metadata:
                tags = getattr(m.metadata, "tags", [])
                for tag in tags:
                    if tag.lower() in query_words:
                        score += 1.0

            ranked_memories.append((m, score))

        ranked_memories.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in ranked_memories[:limit]]

from pydantic import BaseModel, field_validator
from typing import List, Set

class Ranking(BaseModel):
    candidateId: str
    rank: int

class Ballot(BaseModel):
    electionId: str
    rankings: List[Ranking]

    @field_validator("rankings")
    @classmethod
    def validate_rankings(cls, v: List[Ranking]):
        if not v:
            raise ValueError("empty_rankings")

        seen_candidates: Set[str] = set()
        seen_ranks: Set[int] = set()

        for r in v:
            # rank must be positive integer starting at 1
            if not isinstance(r.rank, int) or r.rank < 1:
                raise ValueError("invalid_rank_value")

            if r.candidateId in seen_candidates:
                raise ValueError("duplicate_candidate")
            seen_candidates.add(r.candidateId)

            if r.rank in seen_ranks:
                raise ValueError("duplicate_rank")
            seen_ranks.add(r.rank)

        # ranks must be contiguous 1..N
        ranks_sorted = sorted(seen_ranks)
        expected = list(range(1, len(v) + 1))
        if ranks_sorted != expected:
            raise ValueError("invalid_rank_sequence")

        return v

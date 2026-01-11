#!/usr/bin/env python3
"""
ECHONATE PHASE 3 CORE (REWRITTEN)

Integrated from Echo Phase 3:
Antifragile, constitutionally‑bounded epistemic engine for Echonate constellation.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum, auto
from dataclasses import dataclass, field
from collections import defaultdict, deque

# ============================================================================
# CONSTITUTIONAL LAYER
# ============================================================================

CONSTITUTION = {
    "sovereignty": "human_over_system",
    "auditability": "full",
    "autonomy_bounds": "cryptographically_enforced",
    "epistemic_invariants": {
        "confidence_range": (0.0, 1.0),
        "contradiction_range": (0.0, 1.0),
        "max_sources": 1024,
    },
}


class ConstitutionalViolation(Exception):
    """Raised when epistemic or structural invariants are violated."""
    pass


# ============================================================================
# AUDIT LAYER
# ============================================================================

class AuditEventType(str, Enum):
    TRUTH_CREATED = "truth_created"
    TRUTH_CORROBORATED = "truth_corroborated"
    TRUTH_CONTRADICTION = "truth_contradiction"
    OPPORTUNITY_VALIDATED = "opportunity_validated"
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_CYCLE = "dependency_cycle_detected"
    ENGINE_INTEGRATION = "engine_integration"


@dataclass
class AuditRecord:
    timestamp: datetime
    event_type: AuditEventType
    payload: Dict[str, Any]


class AuditTrail:
    """
    Minimal, structured audit trail.
    In production, this would stream to immutable storage.
    """

    def __init__(self):
        self._records: List[AuditRecord] = []

    def log(self, event_type: AuditEventType, **payload: Any) -> None:
        record = AuditRecord(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            payload=payload,
        )
        self._records.append(record)

    def export(self) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "event_type": r.event_type.value,
                "payload": r.payload,
            }
            for r in self._records
        ]


# ============================================================================
# CORE EPISTEMOLOGICAL ENGINE
# ============================================================================

class EpistemicState(Enum):
    """States of knowledge certainty."""
    RAW_OBSERVATION = auto()
    CORROBORATED = auto()
    DISPUTED = auto()
    ANOMALOUS = auto()
    ARCHETYPAL = auto()


@dataclass
class TruthVector:
    """Multi-dimensional truth representation."""
    content_hash: str
    sources: Set[str]
    lineage: List[str]  # Dependency chain
    confidence: float   # 0.0 to 1.0
    contradiction_score: float  # 0.0 (consistent) to 1.0 (contradictory)
    epistemic_state: EpistemicState
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.lineage:
            self.lineage = ["OBSERVATION"]
        self._enforce_invariants()

    def _enforce_invariants(self) -> None:
        c_min, c_max = CONSTITUTION["epistemic_invariants"]["confidence_range"]
        k_min, k_max = CONSTITUTION["epistemic_invariants"]["contradiction_range"]
        max_sources = CONSTITUTION["epistemic_invariants"]["max_sources"]

        if not (c_min <= self.confidence <= c_max):
            raise ConstitutionalViolation(
                f"Confidence {self.confidence} out of range {c_min}–{c_max}"
            )
        if not (k_min <= self.contradiction_score <= k_max):
            raise ConstitutionalViolation(
                f"Contradiction score {self.contradiction_score} out of range {k_min}–{k_max}"
            )
        if len(self.sources) > max_sources:
            raise ConstitutionalViolation(
                f"Too many sources: {len(self.sources)} > {max_sources}"
            )

    @property
    def is_consensus(self) -> bool:
        """True if multiple independent sources agree."""
        return len(self.sources) >= 3 and self.contradiction_score < 0.3

    @property
    def is_singular(self) -> bool:
        """True if single source without corroboration."""
        return len(self.sources) == 1

    @property
    def requires_investigation(self) -> bool:
        """Flag for human attention."""
        return (
            (self.contradiction_score > 0.7 and self.confidence > 0.5)
            or (self.epistemic_state == EpistemicState.ANOMALOUS)
        )


# ============================================================================
# DEPENDENCY GRAPH WITH CYCLE DETECTION
# ============================================================================

class DependencyGraph:
    """Track hidden dependencies between APIs."""

    def __init__(self, audit: Optional[AuditTrail] = None):
        self.graph: Dict[str, Set[str]] = {}
        self.upstream_map: Dict[str, Set[str]] = defaultdict(set)
        self.downstream_map: Dict[str, Set[str]] = defaultdict(set)
        self.audit = audit or AuditTrail()

    def _ensure_node(self, node: str) -> None:
        if node not in self.graph:
            self.graph[node] = set()

    def _detect_cycle(self, source: str) -> bool:
        """
        Simple DFS-based cycle detection from a given source.
        Deterministic via sorted traversal.
        """
        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            stack.add(node)
            for dep in sorted(self.graph.get(node, [])):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in stack:
                    return True
            stack.remove(node)
            return False

        return dfs(source)

    def add_dependency(self, source: str, depends_on: List[str]) -> None:
        """Add dependency lineage with cycle protection."""
        self._ensure_node(source)
        for dep in depends_on:
            self._ensure_node(dep)
            self.graph[source].add(dep)
            self.upstream_map[source].add(dep)
            self.downstream_map[dep].add(source)

        if self._detect_cycle(source):
            self.audit.log(
                AuditEventType.DEPENDENCY_CYCLE,
                source=source,
                depends_on=sorted(depends_on),
            )
            raise ConstitutionalViolation(
                f"Dependency cycle detected when adding {source} -> {depends_on}"
            )

        self.audit.log(
            AuditEventType.DEPENDENCY_ADDED,
            source=source,
            depends_on=sorted(depends_on),
        )

    def get_all_upstream(self, source: str) -> Set[str]:
        """Get all upstream dependencies recursively (deterministic)."""
        visited: Set[str] = set()
        stack: deque[str] = deque([source])

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            for dep in sorted(self.graph.get(current, [])):
                if dep not in visited:
                    stack.append(dep)

        return visited - {source}

    def get_independence_score(self, sources: List[str]) -> float:
        """Calculate independence score (1.0 = completely independent)."""
        if not sources:
            return 0.0

        # Deterministic ordering
        sources = sorted(set(sources))
        total_pairs = 0
        shared_upstreams = 0

        for i, src1 in enumerate(sources):
            for src2 in sources[i + 1 :]:
                total_pairs += 1
                upstream1 = self.get_all_upstream(src1)
                upstream2 = self.get_all_upstream(src2)
                if upstream1.intersection(upstream2):
                    shared_upstreams += 1

        if total_pairs == 0:
            return 1.0

        return 1.0 - (shared_upstreams / total_pairs)

    def find_hidden_convergences(
        self, threshold: float = 0.8
    ) -> List[Tuple[str, str, float]]:
        """Find sources that covertly converge."""
        convergences: List[Tuple[str, str, float]] = []
        sources = sorted(self.graph.keys())

        for i, src1 in enumerate(sources):
            for src2 in sources[i + 1 :]:
                upstream1 = self.get_all_upstream(src1)
                upstream2 = self.get_all_upstream(src2)
                if not upstream1 or not upstream2:
                    continue
                overlap = len(upstream1.intersection(upstream2))
                union = len(upstream1.union(upstream2))
                if union > 0:
                    jaccard = overlap / union
                    if jaccard > threshold:
                        convergences.append((src1, src2, jaccard))

        return sorted(convergences, key=lambda x: x[2], reverse=True)


# ============================================================================
# ECHONATE EPISTEMIC ENGINE
# ============================================================================

class EchonateEpistemicEngine:
    """Epistemological engine for Echonate agents."""

    def __init__(self, audit: Optional[AuditTrail] = None):
        self.audit = audit or AuditTrail()
        self.dependency_graph = DependencyGraph(audit=self.audit)
        self.truth_vectors: Dict[str, TruthVector] = {}

    # -------------------------
    # Internal helpers
    # -------------------------

    def _normalize_confidence(self, confidence: float) -> float:
        c_min, c_max = CONSTITUTION["epistemic_invariants"]["confidence_range"]
        return max(c_min, min(c_max, confidence))

    # -------------------------
    # Truth vector operations
    # -------------------------

    def create_truth_vector(
        self,
        content: str,
        source: str,
        confidence: float = 0.5,
    ) -> TruthVector:
        """Create a new truth vector from agent observation."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        confidence = self._normalize_confidence(confidence)

        tv = TruthVector(
            content_hash=content_hash,
            sources={source},
            lineage=["OBSERVATION", source],
            confidence=confidence,
            contradiction_score=0.0,
            epistemic_state=EpistemicState.RAW_OBSERVATION,
            timestamp=datetime.utcnow(),
            metadata={"content": content},
        )

        self.truth_vectors[content_hash] = tv

        self.audit.log(
            AuditEventType.TRUTH_CREATED,
            content_hash=content_hash,
            source=source,
            confidence=confidence,
        )

        return tv

    def corroborate(self, content_hash: str, new_source: str) -> Optional[TruthVector]:
        """Add corroborating source to existing truth vector."""
        tv = self.truth_vectors.get(content_hash)
        if tv is None:
            return None

        tv.sources.add(new_source)
        tv.lineage.append(f"CORROBORATION:{new_source}")

        # Recalculate epistemic state
        if len(tv.sources) >= 3:
            tv.epistemic_state = EpistemicState.CORROBORATED

        # Recalculate independence and adjust confidence deterministically
        independence = self.dependency_graph.get_independence_score(list(tv.sources))
        tv.confidence = self._normalize_confidence(tv.confidence + (independence * 0.2))
        tv._enforce_invariants()

        self.audit.log(
            AuditEventType.TRUTH_CORROBORATED,
            content_hash=content_hash,
            new_source=new_source,
            independence=independence,
            confidence=tv.confidence,
            epistemic_state=tv.epistemic_state.name,
        )

        return tv

    def flag_contradiction(self, content_hash: str, contradiction_score: float) -> None:
        """Flag a truth vector as contradictory."""
        tv = self.truth_vectors.get(content_hash)
        if tv is None:
            return

        c_min, c_max = CONSTITUTION["epistemic_invariants"]["contradiction_range"]
        contradiction_score = max(c_min, min(c_max, contradiction_score))

        tv.contradiction_score = contradiction_score
        if contradiction_score > 0.7:
            tv.epistemic_state = EpistemicState.DISPUTED
        tv._enforce_invariants()

        self.audit.log(
            AuditEventType.TRUTH_CONTRADICTION,
            content_hash=content_hash,
            contradiction_score=contradiction_score,
            epistemic_state=tv.epistemic_state.name,
        )

    # -------------------------
    # Wealth opportunity validation
    # -------------------------

    def validate_wealth_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Validate wealth opportunity with epistemic engine."""
        # Deterministic serialization
        content = json.dumps(opportunity, sort_keys=True)
        source = opportunity.get("source", "UNKNOWN")
        confidence_label = opportunity.get("confidence", "MEDIUM")

        confidence_map = {"LOW": 0.3, "MEDIUM": 0.5, "HIGH": 0.8}
        confidence_float = confidence_map.get(confidence_label, 0.5)

        tv = self.create_truth_vector(content, source, confidence_float)

        enriched = dict(opportunity)
        enriched["truth_vector"] = {
            "content_hash": tv.content_hash,
            "sources": sorted(tv.sources),
            "confidence": tv.confidence,
            "epistemic_state": tv.epistemic_state.name,
            "is_consensus": tv.is_consensus,
            "requires_investigation": tv.requires_investigation,
        }

        self.audit.log(
            AuditEventType.OPPORTUNITY_VALIDATED,
            content_hash=tv.content_hash,
            source=source,
            confidence=tv.confidence,
            epistemic_state=tv.epistemic_state.name,
        )

        return enriched

    def get_consensus_opportunities(self) -> List[Dict[str, Any]]:
        """Get only consensus-validated opportunities."""
        consensus: List[Dict[str, Any]] = []
        # Deterministic ordering by content_hash
        for content_hash in sorted(self.truth_vectors.keys()):
            tv = self.truth_vectors[content_hash]
            if tv.is_consensus and not tv.requires_investigation:
                consensus.append(
                    {
                        "content": tv.metadata.get("content", ""),
                        "sources": sorted(tv.sources),
                        "confidence": tv.confidence,
                        "epistemic_state": tv.epistemic_state.name,
                    }
                )
        return consensus


# ============================================================================
# AGENT INTEGRATION HELPERS
# ============================================================================

def integrate_with_agent(agent_name: str, engine: EchonateEpistemicEngine) -> None:
    """Helper to integrate epistemic engine with existing agents."""
    print(f"Integrating Phase 3 with {agent_name}...")

    name_lower = agent_name.lower()

    if "crypto" in name_lower:
        engine.dependency_graph.add_dependency(
            agent_name, ["CoinGecko API", "CoinDesk API"]
        )
    elif "github" in name_lower:
        engine.dependency_graph.add_dependency(agent_name, ["GitHub API"])
    elif "intelligence" in name_lower:
        engine.dependency_graph.add_dependency(
            agent_name, ["HackerNews API", "GitHub API", "Reddit API"]
        )

    engine.audit.log(
        AuditEventType.ENGINE_INTEGRATION,
        agent_name=agent_name,
    )

    print(f"✓ {agent_name} integrated with Phase 3 epistemic engine")


# ============================================================================
# INTEGRATION TEST HARNESS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ECHONATE PHASE 3 CORE - INTEGRATION TEST")
    print("=" * 80)

    engine = EchonateEpistemicEngine()

    # Test truth vector creation
    tv1 = engine.create_truth_vector(
        "BTC moved +5.2% in 24h", "CoinGecko API", 0.8
    )
    print(f"\n✓ Truth Vector created: {tv1.content_hash[:16]}...")
    print(f"  State: {tv1.epistemic_state.name}")
    print(f"  Confidence: {tv1.confidence}")

    # Test corroboration
    tv2 = engine.corroborate(tv1.content_hash, "CoinDesk API")
    if tv2:
        print("\n✓ Corroboration added")
        print(f"  Sources: {len(tv2.sources)}")
        print(f"  State: {tv2.epistemic_state.name}")
        print(f"  Confidence: {tv2.confidence}")

    # Test dependency graph + independence
    engine.dependency_graph.add_dependency("CoinGecko API", ["CoinMarketCap"])
    engine.dependency_graph.add_dependency("CoinDesk API", ["CoinMarketCap"])

    independence = engine.dependency_graph.get_independence_score(
        ["CoinGecko API", "CoinDesk API"]
    )
    print(f"\n✓ Independence Score: {independence:.2f}")

    convergences = engine.dependency_graph.find_hidden_convergences(threshold=0.5)
    print(f"✓ Hidden Convergences: {len(convergences)}")

    print("\n" + "=" * 80)
    print("PHASE 3 INTEGRATION SUCCESSFUL")
    print("=" * 80)


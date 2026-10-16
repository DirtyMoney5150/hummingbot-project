"""Open-ended store: any kind of thing (team, date, product, IP...) with free-form data,
tags and typed relations, plus queries to discover related information."""
import json
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Entity:
    kind: str
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.name}"


class Store:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: Set[Tuple[str, str, str]] = set()  # (src key, label, dst key)

    def add(self, kind: str, name: str, tags=(), **data) -> Entity:
        """Add or update an entity; data/tags merge into any existing one."""
        key = f"{kind}:{name}"
        ent = self.entities.setdefault(key, Entity(kind, name))
        ent.data.update(data)
        ent.tags.update(tags)
        return ent

    def get(self, kind: str, name: str) -> Optional[Entity]:
        return self.entities.get(f"{kind}:{name}")

    def relate(self, a: Entity, label: str, b: Entity) -> None:
        for e in (a, b):
            if e.key not in self.entities:
                raise KeyError(f"unknown entity {e.key}")
        self.relations.add((a.key, label, b.key))

    def find(self, kind: Optional[str] = None, tag: Optional[str] = None,
             text: Optional[str] = None, **data) -> List[Entity]:
        """Filter by kind, tag, case-insensitive text search, and exact data values."""
        out = []
        for e in self.entities.values():
            if kind and e.kind != kind:
                continue
            if tag and tag not in e.tags:
                continue
            if any(e.data.get(k) != v for k, v in data.items()):
                continue
            if text and text.lower() not in json.dumps([e.name, e.data], default=str).lower():
                continue
            out.append(e)
        return out

    def related(self, e: Entity) -> List[Tuple[str, Entity]]:
        """Direct neighbours as (label, entity); incoming labels are prefixed with '<-'."""
        out = []
        for a, label, b in sorted(self.relations):
            if a == e.key:
                out.append((label, self.entities[b]))
            elif b == e.key:
                out.append(("<-" + label, self.entities[a]))
        return out

    def connected(self, e: Entity, depth: int = 2) -> List[Entity]:
        """Everything reachable within `depth` hops (breadth first), excluding e."""
        seen, queue, out = {e.key}, deque([(e, 0)]), []
        while queue:
            cur, d = queue.popleft()
            if d == depth:
                continue
            for _, n in self.related(cur):
                if n.key not in seen:
                    seen.add(n.key)
                    out.append(n)
                    queue.append((n, d + 1))
        return out

    def save(self, path: str) -> None:
        payload = {
            "entities": [{"kind": e.kind, "name": e.name, "data": e.data, "tags": sorted(e.tags)}
                         for e in self.entities.values()],
            "relations": sorted(self.relations),
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2, default=str)

    @classmethod
    def load(cls, path: str) -> "Store":
        with open(path) as f:
            payload = json.load(f)
        s = cls()
        for e in payload["entities"]:
            s.add(e["kind"], e["name"], tags=e["tags"], **e["data"])
        s.relations = {tuple(r) for r in payload["relations"]}
        return s

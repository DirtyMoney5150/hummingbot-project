from openbird import Store


def build():
    s = Store()
    team = s.add("team", "Lakers", tags=["sports"], sport="basketball")
    date = s.add("date", "2026-10-21", note="season opener")
    prod = s.add("product", "Jersey", price=120)
    s.relate(team, "plays_on", date)
    s.relate(prod, "merch_for", team)
    return s, team, date, prod


def test_find():
    s, *_ = build()
    assert [e.name for e in s.find(kind="team")] == ["Lakers"]
    assert [e.name for e in s.find(tag="sports")] == ["Lakers"]
    assert [e.name for e in s.find(text="OPENER")] == ["2026-10-21"]
    assert [e.name for e in s.find(price=120)] == ["Jersey"]


def test_relations_and_connected():
    s, team, date, prod = build()
    assert {l for l, _ in s.related(team)} == {"plays_on", "<-merch_for"}
    assert {e.key for e in s.connected(prod)} == {team.key, date.key}
    assert [e.key for e in s.connected(prod, depth=1)] == [team.key]


def test_save_load(tmp_path):
    s, team, *_ = build()
    p = str(tmp_path / "s.json")
    s.save(p)
    t = Store.load(p)
    assert t.get("team", "Lakers").data == {"sport": "basketball"}
    assert t.relations == s.relations

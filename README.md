# hummingbot-project
new project we're working on for hummingbot and different things that we can do with it.

## openbird
An open-ended, dependency-free store for anything you want to track and connect: sports teams,
dates, products, intellectual property, datasets. Each entity has a `kind`, `name`, free-form
data and tags; entities are linked with labelled relations so you can discover related info.

```python
from openbird import Store
s = Store()
team = s.add("team", "Lakers", tags=["sports"], sport="basketball")
date = s.add("date", "2026-10-21", note="season opener")
s.relate(team, "plays_on", date)
s.find(tag="sports"); s.connected(team); s.save("data.json")
```
Run tests with `python -m pytest`.

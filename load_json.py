"""Load mobility.json -> capabilities table."""
import json
from pathlib import Path

import database as db

BASE = Path(__file__).parent


def load_mobility(path=BASE / "mobility.json", db_path=db.DB_PATH):
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    return [db.add_capability(i["application_name"], i["capability_name"],
                              i["interface_type"], i.get("instructions"),
                              i.get("evidence"), i.get("confidence", 0.5),
                              db_path=db_path) for i in items]


if __name__ == "__main__":
    db.init_db()
    print("Mobility loaded:", len(load_mobility()))
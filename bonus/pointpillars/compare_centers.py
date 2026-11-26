"""Count one-to-one, same-class matches with 3D center distance <= 0.5 m."""
import argparse
import csv
import json
import math
from pathlib import Path


def count_matches(online, offline, tolerance=0.5):
    edges = []
    for box in online:
        candidates = []
        for j, other in enumerate(offline):
            if box["label"] != other["label"]:
                continue
            distance = math.sqrt(sum((box[k] - other[k]) ** 2 for k in ("x", "y", "z")))
            if distance <= tolerance:
                candidates.append((distance, j))
        edges.append([j for _, j in sorted(candidates)])
    owners = {}

    def assign(i, visited):
        for j in edges[i]:
            if j in visited:
                continue
            visited.add(j)
            if j not in owners or assign(owners[j], visited):
                owners[j] = i
                return True
        return False

    for i in range(len(online)):
        assign(i, set())
    return len(owners)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", type=Path, required=True)
    parser.add_argument("--offline", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    online = json.loads(args.online.read_text(encoding="utf-8-sig"))["frames"]
    offline = json.loads(args.offline.read_text(encoding="utf-8-sig"))["frames"]
    assert set(online) == set(offline), "Frame sets differ"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in sorted(online):
        rows.append(dict(frame=name, boxes_cvat=len(online[name]), boxes_offline=len(offline[name]),
                         matched_center_0_5m=count_matches(online[name], offline[name])))
    with args.out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(*rows, sep="\n")
    print("TOTAL", {k: sum(row[k] for row in rows) for k in rows[0] if k != "frame"})


if __name__ == "__main__":
    main()

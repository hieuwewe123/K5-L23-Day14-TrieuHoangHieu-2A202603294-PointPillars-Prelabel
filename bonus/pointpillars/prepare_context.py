"""Stage dependencies and weights into ignored out/; keep third-party files out of Git."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "out" / "pointpillars-function"
DEST.mkdir(parents=True, exist_ok=True)
for name in ("main.py", "function.yaml"):
    shutil.copy2(Path(__file__).with_name(name), DEST / name)
shutil.copy2(ROOT / "d14_2A202603294" / "best_config.json", DEST / "best_config.json")
shutil.copytree(ROOT / "vf_pp", DEST / "vf_pp", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
upstream = ROOT / "third_party" / "PointPillars"
for name in ("pointpillars", "pretrained"):
    shutil.copytree(upstream / name, DEST / "third_party" / "PointPillars" / name,
                    dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.so"))
for name in ("LICENSE", "LICENSE.txt"):
    if (upstream / name).exists():
        shutil.copy2(upstream / name, DEST / "third_party" / "PointPillars" / name)
print(DEST)

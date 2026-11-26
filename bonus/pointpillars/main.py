"""Nuclio entry point for CVAT 3D. No access to annotation reference files."""
import base64
import io
import json
import math
from pathlib import Path

import numpy as np


def parse_pcd(raw):
    """Read the lab's uncompressed binary PCD; undo its log-grayscale intensity."""
    stream = io.BytesIO(raw)
    header = {}
    for _ in range(100):
        line = stream.readline()
        if not line:
            raise ValueError("PCD DATA header missing")
        text = line.decode("ascii").strip()
        if not text or text.startswith("#"):
            continue
        key, *values = text.split()
        header[key.upper()] = values
        if key.upper() == "DATA":
            break
    else:
        raise ValueError("PCD header too long")
    if header.get("DATA") != ["binary"]:
        raise ValueError("Only uncompressed binary PCD is supported")
    fields = header["FIELDS"]
    sizes = list(map(int, header["SIZE"]))
    types = header["TYPE"]
    counts = list(map(int, header.get("COUNT", ["1"] * len(fields))))
    if not (len(fields) == len(sizes) == len(types) == len(counts)) or any(n != 1 for n in counts):
        raise ValueError("Unsupported PCD field layout")
    dtypes = {("F", 4): "<f4", ("F", 8): "<f8", ("U", 4): "<u4", ("U", 1): "u1", ("I", 4): "<i4"}
    dtype = np.dtype([(name, dtypes[(typ, size)]) for name, typ, size in zip(fields, types, sizes)])
    count = int(header["POINTS"][0])
    body = stream.read()
    if len(body) != count * dtype.itemsize:
        raise ValueError("PCD payload length does not match POINTS")
    array = np.frombuffer(body, dtype=dtype, count=count)
    xyz = np.column_stack([array[k] for k in ("x", "y", "z")]).astype(np.float32)
    if "intensity" in fields:
        intensity = array["intensity"].astype(np.float32)
    else:
        rgb = array["rgb"]
        packed = rgb.view("<u4") if rgb.dtype.kind == "f" else rgb.astype(np.uint32)
        gray = (packed & 255).astype(np.float32)
        # gray==40 also represents zero: retain exact zeros rather than midpoint noise.
        fraction = np.clip((gray + 0.5 - 40.0) / 215.0, 0, 1)
        intensity = np.expm1(fraction * math.log1p(50.0)).astype(np.float32)
        intensity[gray <= 40] = 0
    result = np.column_stack([xyz, intensity]).astype(np.float32)
    return result[np.isfinite(result).all(axis=1)]


def init_context(context):
    import torch
    from vf_pp.core import Config, Detector

    torch.set_num_threads(4)
    config_path = Path(__file__).with_name("best_config.json")
    config = Config(**json.loads(config_path.read_text()))
    context.user_data.detector = Detector(config)
    context.logger.info("PointPillars ready: CPU; four rotations; binary PCD intensity inversion")


def handler(context, event):
    from vf_pp.core import VF_NAMES

    try:
        body = event.body if isinstance(event.body, dict) else json.loads(event.body)
        points = parse_pcd(base64.b64decode(body["image"], validate=True))
        boxes = context.user_data.detector.detect(points)
        threshold = float(body.get("threshold", 0.5))
        results = []
        for box in boxes:
            if box["score"] < threshold:
                continue
            results.append({
                "type": "cuboid", "label": VF_NAMES[box["label"]],
                "confidence": str(float(box["score"])),
                "points": [float(box[k]) for k in ("x", "y", "z")] + [0, 0, float(box["yaw"])]
                + [float(box[k]) for k in ("length", "width", "height")] + [0] * 7,
            })
        context.logger.info(f"Detected {len(results)} cuboids from {len(points)} points")
        return context.Response(body=json.dumps(results), headers={}, content_type="application/json", status_code=200)
    except (ValueError, KeyError) as error:
        context.logger.error(str(error))
        return context.Response(body=json.dumps({"error": str(error)}), headers={}, content_type="application/json", status_code=400)

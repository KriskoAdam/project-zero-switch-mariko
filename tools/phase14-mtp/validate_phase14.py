#!/usr/bin/env python3
"""Validate Phase 14 probe JSONL and build a compact session matrix."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Iterable

MAX_LINE_BYTES = 256 * 1024
MAX_RECORDS = 20_000
MAX_DEVICE_LIST = 256
MAX_STORAGE_LIST = 32
SAFE_OPS = {"0x1001", "0x1002", "0x1003", "0x1004", "0x1005", "0x1006"}
HEX16 = re.compile(r"^0x[0-9a-fA-F]{4}$")


def parse_jsonl(text: str) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    diagnostics: list[str] = []
    total = 0
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        if len(raw.encode("utf-8")) > MAX_LINE_BYTES:
            raise ValueError(f"line {lineno}: exceeds {MAX_LINE_BYTES} bytes")
        if not raw.lstrip().startswith("{"):
            diagnostics.append(raw[:1000])
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {lineno}: invalid JSON: {exc.msg}") from exc
        if not isinstance(obj, dict) or not isinstance(obj.get("kind"), str):
            raise ValueError(f"line {lineno}: expected record object with kind")
        total += 1
        if total > MAX_RECORDS:
            raise ValueError(f"record count exceeds {MAX_RECORDS}")
        records.append(obj)
    return records, diagnostics


def _timestamp(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label}: timestamp is not a string")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label}: invalid ISO timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError(f"{label}: timestamp has no timezone")
    return dt


def validate_records(records: Iterable[dict]) -> list[dict]:
    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for index, r in enumerate(records, 1):
        kind = r.get("kind")
        if kind not in {"usb_identity", "session_open", "session_close", "operation",
                        "device_info", "storage_ids", "storage_info", "object_count"}:
            raise ValueError(f"record {index}: unknown kind {kind!r}")
        if kind == "usb_identity":
            if r.get("vid") != "0x057e" or r.get("pid") != "0x201d":
                raise ValueError(f"record {index}: unexpected target VID/PID")
            continue
        state, trial = r.get("state"), r.get("trial")
        if not isinstance(state, str) or not state or not isinstance(trial, int) or trial < 1:
            raise ValueError(f"record {index}: invalid state/trial")
        if kind in {"session_open", "session_close", "operation"}:
            start = _timestamp(r.get("started_at"), f"record {index}")
            end = _timestamp(r.get("finished_at"), f"record {index}")
            if end < start:
                raise ValueError(f"record {index}: end precedes start")
        if kind == "operation":
            op = r.get("operation_code")
            if op not in SAFE_OPS:
                raise ValueError(f"record {index}: operation not on approved safe list: {op}")
            if r.get("performed") and not r.get("declared_supported"):
                raise ValueError(f"record {index}: performed operation was not declared supported")
            if r.get("performed"):
                response = r.get("response_code")
                if not isinstance(response, str) or not HEX16.fullmatch(response):
                    raise ValueError(f"record {index}: missing/invalid response code")
        if kind == "object_count":
            if r.get("operation_code", "0x1006") not in {"0x1006", None}:
                raise ValueError(f"record {index}: count record has wrong opcode")
            if r.get("association_handle") != "0xffffffff" or r.get("format_code") != "0x0000":
                raise ValueError(f"record {index}: count query was not root/all formats")
            if r.get("response_code") == "0x2001" and not isinstance(r.get("count"), int):
                raise ValueError(f"record {index}: successful count has no integer result")
        groups[(state, trial)].append(r)

    matrix = []
    for (state, trial), rows in sorted(groups.items()):
        kinds = [x["kind"] for x in rows]
        if "session_open" not in kinds or "session_close" not in kinds:
            raise ValueError(f"{state}/{trial}: missing session open/close")
        performed = [x for x in rows if x["kind"] == "operation" and x.get("performed")]
        by_code = {x["operation_code"]: x for x in performed}
        for required in ("0x1001", "0x1004", "0x1005", "0x1006"):
            if required not in by_code:
                raise ValueError(f"{state}/{trial}: missing operation {required}")
        infos = [x for x in rows if x["kind"] == "device_info"]
        stores = [x for x in rows if x["kind"] == "storage_ids"]
        storage_info = [x for x in rows if x["kind"] == "storage_info"]
        counts = [x for x in rows if x["kind"] == "object_count"]
        if len(infos) != 1 or len(stores) != 1 or not storage_info or not counts:
            raise ValueError(f"{state}/{trial}: incomplete datasets")
        if (len(infos[0].get("operations_supported", [])) > MAX_DEVICE_LIST or
            len(infos[0].get("events_supported", [])) > MAX_DEVICE_LIST or
            len(infos[0].get("device_properties_supported", [])) > MAX_DEVICE_LIST or
            len(stores[0].get("ids", [])) > MAX_STORAGE_LIST or
            len(storage_info) > MAX_STORAGE_LIST or len(counts) > MAX_STORAGE_LIST):
            raise ValueError(f"{state}/{trial}: dataset exceeds parser safety limits")
        advertised_ops = {x.get("code") for x in infos[0].get("operations_supported", [])}
        for op in performed:
            if op["operation_code"] not in advertised_ops:
                raise ValueError(f"{state}/{trial}: performed operation absent from DeviceInfo")
        matrix.append({
            "state": state, "trial": trial,
            "open": next(x for x in rows if x["kind"] == "session_open"),
            "close": next(x for x in rows if x["kind"] == "session_close"),
            "device_info": infos[0], "storage_ids": stores[0]["ids"],
            "storage_info": storage_info, "object_counts": counts,
            "responses": {op: by_code[op]["response_code"] for op in sorted(by_code)},
            "operation_durations_ms": [
                (_timestamp(x["finished_at"], "finish") -
                 _timestamp(x["started_at"], "start")).total_seconds() * 1000
                for x in performed
            ],
        })
    return matrix


def build_differential(matrix: list[dict]) -> dict:
    states: dict[str, list[dict]] = defaultdict(list)
    for row in matrix:
        states[row["state"]].append(row)
    summary = {}
    for state, trials in sorted(states.items()):
        devinfos = [t["device_info"] for t in trials]
        canonical = [{k: v for k, v in d.items() if k not in {"state", "trial"}} for d in devinfos]
        op_sets = [[x["code"] for x in d["operations_supported"]] for d in devinfos]
        event_sets = [d["events_supported"] for d in devinfos]
        storage_sets = [t["storage_ids"] for t in trials]
        counts = [c["count"] for t in trials for c in t["object_counts"]]
        response_sets = [t["responses"] for t in trials]
        summary[state] = {
            "trial_count": len(trials),
            "all_device_info_equal": all(d == canonical[0] for d in canonical),
            "operation_capabilities_stable": all(x == op_sets[0] for x in op_sets),
            "event_capabilities_stable": all(x == event_sets[0] for x in event_sets),
            "storage_id_values": storage_sets,
            "count_values": counts,
            "all_requested_responses_ok": all(set(x.values()) == {"0x2001"} for x in response_sets),
            "max_operation_duration_ms": max((d for t in trials for d in t["operation_durations_ms"]), default=0),
        }
    return {"states": summary, "cross_state_comparison": {
        "states_compared": sorted(states),
        "storage_id_is_session_or_mode_dependent": len({tuple(t["storage_ids"]) for t in matrix}) > 1,
        "object_counts_stable": len({c["count"] for t in matrix for c in t["object_counts"]}) <= 1,
    }}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", action="append", required=True, help="state JSONL files")
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--differential", required=True)
    args = ap.parse_args()
    matrix, diagnostics = [], []
    for file in args.input:
        recs, diag = parse_jsonl(Path(file).read_text())
        matrix.extend(validate_records(recs))
        diagnostics.extend({"file": file, "line": d} for d in diag)
    diff = build_differential(matrix)
    Path(args.matrix).write_text(json.dumps({"sessions": matrix, "diagnostics": diagnostics}, indent=2) + "\n")
    Path(args.differential).write_text(json.dumps(diff, indent=2) + "\n")
    print(f"Validated {len(matrix)} sessions; {len(diagnostics)} non-JSON diagnostic lines.")


if __name__ == "__main__":
    main()

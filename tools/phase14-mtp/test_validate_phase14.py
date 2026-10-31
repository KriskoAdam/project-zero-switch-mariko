import unittest

from validate_phase14 import parse_jsonl, validate_records


def session_records():
    t0 = "2026-10-31T00:00:00.000+0100"
    t1 = "2026-10-31T00:00:00.001+0100"
    ops = [{"code": f"0x{code:04x}", "name": name} for code, name in (
        (0x1001, "GetDeviceInfo"), (0x1002, "OpenSession"),
        (0x1003, "CloseSession"), (0x1004, "GetStorageIDs"),
        (0x1005, "GetStorageInfo"), (0x1006, "GetNumObjects"),
    )]
    out = [
        {"state":"A","trial":1,"kind":"session_open","started_at":t0,"finished_at":t1},
        {"state":"A","trial":1,"kind":"device_info","operations_supported":ops,
         "events_supported":[],"device_properties_supported":[]},
        {"state":"A","trial":1,"kind":"storage_ids","ids":["0x00040001"]},
        {"state":"A","trial":1,"kind":"storage_info","storage_id":"0x00040001"},
        {"state":"A","trial":1,"kind":"object_count","storage_id":"0x00040001",
         "format_code":"0x0000","association_handle":"0xffffffff","response_code":"0x2001","count":3},
    ]
    for code, name in ((0x1001,"GetDeviceInfo"),(0x1004,"GetStorageIDs"),
                       (0x1005,"GetStorageInfo"),(0x1006,"GetNumObjects")):
        out.append({"state":"A","trial":1,"kind":"operation","operation":name,
                    "operation_code":f"0x{code:04x}","declared_supported":True,"performed":True,
                    "started_at":t0,"finished_at":t1,"response_code":"0x2001"})
    out.append({"state":"A","trial":1,"kind":"session_close","started_at":t1,"finished_at":t1})
    return out


class ValidatorTests(unittest.TestCase):
    def test_valid_session_and_diagnostic_line(self):
        import json
        lines = ["Device 0 (VID=057e and PID=201d) is a Nintendo Switch."]
        lines += [json.dumps(x) for x in session_records()]
        rows, diagnostics = parse_jsonl("\n".join(lines))
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(len(validate_records(rows)), 1)

    def test_rejects_malformed_json(self):
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            parse_jsonl('{"kind":\n')

    def test_rejects_unadvertised_performed_operation(self):
        rows = session_records()
        rows[5]["declared_supported"] = False
        with self.assertRaisesRegex(ValueError, "not declared supported"):
            validate_records(rows)

    def test_rejects_non_root_count_parameters(self):
        rows = session_records()
        next(x for x in rows if x["kind"] == "object_count")["association_handle"] = "0x00000000"
        with self.assertRaisesRegex(ValueError, "not root/all formats"):
            validate_records(rows)

    def test_rejects_unsafe_getobjecthandles_request(self):
        rows = session_records()
        op = next(x for x in rows if x["kind"] == "operation" and x["operation_code"] == "0x1006")
        op["operation_code"] = "0x1007"
        with self.assertRaisesRegex(ValueError, "not on approved safe list"):
            validate_records(rows)

    def test_rejects_oversized_capability_array(self):
        rows = session_records()
        di = next(x for x in rows if x["kind"] == "device_info")
        di["operations_supported"] = [{}] * 257
        with self.assertRaisesRegex(ValueError, "exceeds parser safety limits"):
            validate_records(rows)


if __name__ == "__main__":
    unittest.main()

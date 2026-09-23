"""Synthetic offline fixtures, not empirical security findings."""

import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import generate_findings as generator
from prepare_case import MODEL_FILES


def response_bytes(findings):
    return json.dumps({
        "status": "completed",
        "model": "synthetic-model",
        "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
        "output": [
            {"type": "reasoning"},
            {"type": "message", "role": "assistant", "content": [
                {"type": "output_text", "text": json.dumps({"findings": findings})},
            ]},
        ],
    }).encode()


class GenerateFindingsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.model_input = self.root / "model_input"
        self.output = self.root / "run"
        self.source = "// synthetic fixture\r\n// könnte gelten\r\n".encode()
        for name in MODEL_FILES:
            path = self.model_input / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.source)

    def run_review(self):
        return generator.generate_findings(self.model_input, self.output, "synthetic-model", 100)

    def manifest(self):
        return json.loads((self.output / "run_manifest.json").read_bytes())

    @patch.dict("os.environ", {"OPENAI_API_KEY": "synthetic-test-key"})
    def test_only_allowlisted_sources_sent_and_artifacts_preserved(self):
        marker = "REFERENCE_MUST_NOT_LEAK"
        (self.root / "reference").mkdir()
        (self.root / "reference/fix.txt").write_text(marker)
        (self.root / "manifest.json").write_text(marker)
        (self.model_input / "unexpected.txt").write_text(marker)
        finding = {"title": " Synthetic title ", "report": "Could occur, if enabled.\nUnverified."}
        raw = response_bytes([finding]) + b"\n "
        with patch("generate_findings.request_review", return_value=(200, "test-request", raw)) as request:
            self.assertEqual(self.run_review(), "completed")
        request.assert_called_once()
        sent = request.call_args.args[0]
        self.assertEqual(sent, (self.output / "request.json").read_bytes())
        self.assertNotIn(marker, sent.decode())
        self.assertNotIn("VUL4J-18", sent.decode())
        self.assertNotIn("synthetic-test-key", sent.decode())
        payload = json.loads(sent)
        self.assertEqual(payload["tools"], [])
        self.assertEqual(payload["input"].count("FILE: "), 5)
        self.assertIn("1: // synthetic fixture\r\n2: // könnte gelten\r\n", payload["input"])
        self.assertEqual((self.output / "generation_raw.json").read_bytes(), raw)
        manifest = self.manifest()
        self.assertEqual(manifest["request_sha256"], hashlib.sha256(sent).hexdigest())
        self.assertEqual(manifest["response_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(manifest["usage"]["total_tokens"], 30)
        for name in MODEL_FILES:
            self.assertEqual((self.output / "model_input" / name).read_bytes(), self.source)
            self.assertEqual(manifest["source_sha256"][name], hashlib.sha256(self.source).hexdigest())
        saved = json.loads((self.output / "findings.jsonl").read_text())
        self.assertEqual(saved, {"finding_id": f"{manifest['run_id']}:F001", **finding})

    @patch.dict("os.environ", {"OPENAI_API_KEY": "synthetic-test-key"})
    def test_empty_result_is_saved_without_retry(self):
        with patch("generate_findings.request_review", return_value=(200, None, response_bytes([]))) as request:
            self.assertEqual(self.run_review(), "no_findings")
        request.assert_called_once()
        self.assertEqual((self.output / "findings.jsonl").read_bytes(), b"")
        self.assertEqual(self.manifest()["finding_count"], 0)

    @patch.dict("os.environ", {"OPENAI_API_KEY": "synthetic-test-key"})
    def test_invalid_and_incomplete_outputs_are_kept_without_findings(self):
        incomplete = json.loads(response_bytes([]))
        incomplete["status"] = "incomplete"
        refusal = json.loads(response_bytes([]))
        refusal["output"][1]["content"] = [{"type": "refusal", "refusal": "synthetic refusal"}]
        examples = [b"not JSON", b"[]", response_bytes([{"title": "missing report"}]),
                    json.dumps(incomplete).encode(), json.dumps(refusal).encode()]
        for index, raw in enumerate(examples):
            with self.subTest(index=index):
                self.output = self.root / f"invalid-{index}"
                with patch("generate_findings.request_review", return_value=(200, None, raw)) as request:
                    self.assertEqual(self.run_review(), "invalid_output")
                request.assert_called_once()
                self.assertEqual((self.output / "generation_raw.json").read_bytes(), raw)
                self.assertFalse((self.output / "findings.jsonl").exists())
                self.assertEqual(self.manifest()["status"], "invalid_output")

    @patch.dict("os.environ", {"OPENAI_API_KEY": "synthetic-test-key"})
    def test_http_error_and_network_failure_are_saved_without_retry(self):
        raw = b'{"error": "synthetic rate limit"}'
        error = HTTPError(generator.ENDPOINT, 429, "rate limit", {"x-request-id": "err-1"}, io.BytesIO(raw))
        with patch("generate_findings.urlopen", side_effect=error) as request:
            self.assertEqual(self.run_review(), "run_error")
        request.assert_called_once()
        self.assertEqual(self.manifest()["http_status"], 429)
        self.assertEqual((self.output / "generation_raw.json").read_bytes(), raw)
        self.assertFalse((self.output / "findings.jsonl").exists())
        self.output = self.root / "network-error"
        with patch("generate_findings.urlopen", side_effect=URLError("synthetic offline")) as request:
            self.assertEqual(self.run_review(), "run_error")
        request.assert_called_once()
        self.assertEqual(self.manifest()["request_attempts"], 1)
        self.assertFalse((self.output / "generation_raw.json").exists())

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_key_is_recorded_without_request(self):
        with patch("generate_findings.request_review") as request:
            self.assertEqual(self.run_review(), "run_error")
        request.assert_not_called()
        self.assertEqual(self.manifest()["request_attempts"], 0)
        self.assertTrue((self.output / "request.json").exists())

    def test_existing_run_is_not_touched(self):
        self.output.mkdir()
        marker = self.output / "keep.txt"
        marker.write_text("existing run")
        with patch("generate_findings.request_review") as request:
            with self.assertRaises(FileExistsError):
                self.run_review()
        request.assert_not_called()
        self.assertEqual(marker.read_text(), "existing run")

    def test_symlink_cannot_import_reference_material(self):
        source = self.model_input / MODEL_FILES[0]
        source.unlink()
        reference = self.root / "reference.txt"
        reference.write_text("reference only")
        source.symlink_to(reference)
        with patch("generate_findings.request_review") as request:
            with self.assertRaises(ValueError):
                self.run_review()
        request.assert_not_called()
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()

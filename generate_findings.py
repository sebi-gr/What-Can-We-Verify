"""Save one tool-free OpenAI review of the five prepared VUL4J-18 files."""

import argparse
from datetime import datetime, timezone
import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from prepare_case import CASE_ID, MODEL_FILES, json_bytes


ENDPOINT = "https://api.openai.com/v1/responses"
PROMPT = Path(__file__).with_name("review_prompt_v1.txt")
TIMEOUT_SECONDS = 180


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def load_sources(model_input: Path) -> dict:
    """Read only the allowlist; reject symlinks that could expose references."""
    if model_input.is_symlink():
        raise ValueError(f"Model input must not be a symlink: {model_input}")
    files = {}
    for name in MODEL_FILES:
        source = model_input
        for part in Path(name).parts:
            source = source / part
            if source.is_symlink():
                raise ValueError(f"Symlinks are not allowed in model input: {source}")
        files[name] = source.read_bytes()
    return files


def request_review(body: bytes, api_key: str) -> tuple:
    """One HTTP request, with no automatic retries or agent tools."""
    request = Request(ENDPOINT, data=body, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, response.headers.get("x-request-id"), response.read()
    except HTTPError as error:
        return error.code, error.headers.get("x-request-id"), error.read()


def parse_findings(response: dict) -> list:
    """Check the report envelope, without repairing or verifying its claims."""
    if response.get("status") != "completed":
        raise ValueError(f"Provider response is not completed: {response.get('status')}")
    chunks = []
    for item in response["output"]:
        if item["type"] == "reasoning":
            continue
        if item["type"] != "message" or item.get("role") != "assistant":
            raise ValueError("Unexpected provider output item.")
        for content in item["content"]:
            if content["type"] != "output_text":
                raise ValueError("Refusal or non-text output; not an empty finding list.")
            chunks.append(content["text"])
    report = json.loads("".join(chunks))
    if not isinstance(report, dict) or set(report) != {"findings"}:
        raise ValueError("Expected exactly one findings field.")
    findings = report["findings"]
    if not isinstance(findings, list):
        raise ValueError("findings must be a list.")
    for finding in findings:
        if not isinstance(finding, dict) or set(finding) != {"title", "report"}:
            raise ValueError("Each finding must contain exactly title and report.")
        if any(not isinstance(value, str) or not value.strip() for value in finding.values()):
            raise ValueError("Finding title and report must be nonempty strings.")
    return findings


def generate_findings(model_input: Path, output: Path, model: str,
                      max_output_tokens: int) -> str:
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Output already exists: {output}. Choose a new --output path.")
    if not model.strip() or max_output_tokens < 1:
        raise ValueError("A model and a positive max-output-tokens value are required.")

    files = load_sources(model_input)
    prompt = PROMPT.read_bytes()
    sections = []
    for name, content in files.items():
        lines = content.decode("utf-8").splitlines(keepends=True)
        numbered = "".join(f"{number}: {line}" for number, line in enumerate(lines, 1))
        sections.append(f"FILE: {name}\n{numbered}\nEND FILE\n")
    payload = {
        "model": model,
        "instructions": prompt.decode("utf-8"),
        "input": "\n".join(sections),
        "max_output_tokens": max_output_tokens,
        "tools": [],
        "store": False,
        "truncation": "disabled",
        "text": {"format": {"type": "json_object"}},
    }
    body = json_bytes(payload)
    run_id = str(uuid4())
    manifest = {
        "case_id": CASE_ID,
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "provider": "openai",
        "endpoint": ENDPOINT,
        "model_requested": model,
        "parameters": {key: value for key, value in payload.items()
                       if key not in ("input", "instructions")},
        "prompt_version": PROMPT.name,
        "prompt_sha256": sha256(prompt),
        "request_sha256": sha256(body),
        "source_sha256": {name: sha256(content) for name, content in files.items()},
        "generator_sha256": sha256(Path(__file__).read_bytes()),
        "timeout_seconds": TIMEOUT_SECONDS,
        "request_attempts": 0,
        "status": "running",
        "usage": None,
        "cost_usd": None,
    }

    # Reserve a new directory. Preserve every started run, including failures.
    output.mkdir(parents=True)
    for name, content in files.items():
        target = output / "model_input" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    (output / PROMPT.name).write_bytes(prompt)
    (output / "request.json").write_bytes(body)
    (output / "run_manifest.json").write_bytes(json_bytes(manifest))

    started = time.monotonic()
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set; no request was sent.")
        manifest["request_attempts"] = 1
        (output / "run_manifest.json").write_bytes(json_bytes(manifest))
        status, request_id, raw = request_review(body, api_key)
        (output / "generation_raw.json").write_bytes(raw)
        manifest.update(http_status=status, provider_request_id=request_id,
                        response_sha256=sha256(raw))
        if status != 200:
            raise ValueError(f"Provider HTTP status {status}; see generation_raw.json.")
    except (OSError, URLError, HTTPException, ValueError) as error:
        manifest.update(status="run_error", error=f"{type(error).__name__}: {error}")
    else:
        try:
            response = json.loads(raw)
            manifest.update(model_returned=response.get("model"),
                            usage=response.get("usage"),
                            provider_status=response.get("status"))
            findings = parse_findings(response)
            rows = [json.dumps({"finding_id": f"{run_id}:F{index:03d}", **finding},
                               ensure_ascii=False) + "\n"
                    for index, finding in enumerate(findings, 1)]
            findings_file = output / "findings.jsonl.tmp"
            findings_file.write_bytes("".join(rows).encode("utf-8"))
            findings_file.rename(output / "findings.jsonl")
            manifest.update(status="completed" if findings else "no_findings",
                            finding_count=len(findings))
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            manifest.update(status="invalid_output", error=f"{type(error).__name__}: {error}")
        except OSError as error:
            manifest.update(status="run_error", error=f"{type(error).__name__}: {error}")
    finally:
        if manifest["status"] == "running":
            manifest.update(status="run_error", error="Review interrupted before completion.")
        manifest["duration_seconds"] = round(time.monotonic() - started, 3)
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        (output / "run_manifest.json").write_bytes(json_bytes(manifest))
    return manifest["status"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-input", type=Path, default=Path("data") / CASE_ID / "model_input")
    parser.add_argument("--output", type=Path, required=True, help="New run directory under data/.")
    parser.add_argument("--model", required=True, help="Explicit model ID; prefer a pinned snapshot.")
    parser.add_argument("--max-output-tokens", type=int, required=True,
                        help="Output limit including reasoning; not a monetary budget.")
    args = parser.parse_args()
    try:
        status = generate_findings(args.model_input, args.output, args.model, args.max_output_tokens)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Could not start review: {error}\n")
    print(f"Review status: {status}; saved at {args.output.resolve()}")
    if status not in ("completed", "no_findings"):
        parser.exit(1, "Review did not complete; see run_manifest.json. No automatic retry.\n")


if __name__ == "__main__":
    main()

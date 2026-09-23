# What Can We Verify?

Research repository for evaluating claims in LLM-generated security findings.

Repository layout:

```text
src/
  01_prepare_case.py
  02_generate_findings.py
tests/
  __init__.py
  test_01_prepare_case.py
  test_02_generate_findings.py
resources/
  review_prompt_v1.txt
  reproduce_vul4j18.md
data/                       # generated, ignored by Git
```

Project documentation and the license remain at the repository root.
Run the commands below from that root.

Current stage: case preparation, one complete review and the Java-PoV reproduction
are complete. The review artifact integrity has been checked, but its security
claims remain unverified. Claim extraction and independent claim verification
remain pending. See
[WORKPLAN.md](WORKPLAN.md) for the current plan and [HANDOFF.md](HANDOFF.md) for
the checked state; keep this README synchronized with user-facing changes.

The first step prepares **VUL4J-18**, the JSPWiki path-traversal case
**CVE-2019-0225 / CWE-22**, for a localized code review.

Run from this repository with **Python 3.9+** and internet access to
`raw.githubusercontent.com`. No Python packages, Java or Docker are needed for
this preparation step:

```bash
python3 src/01_prepare_case.py
```

The script writes `data/VUL4J-18/`. It refuses to overwrite an existing output.
For another copy, choose a new directory:

```bash
python3 src/01_prepare_case.py --output data/VUL4J-18-copy
```

| Output | Purpose |
|---|---|
| `model_input/` | Five original source/configuration files for the review model |
| `reference/vul4j_row.json` | Benchmark metadata, CVE, test names and build commands |
| `reference/fixed/` | The upstream fixed `DefaultURLConstructor.java` |
| `reference/pov/` | The benchmark's `WikiServletTest.java` |
| `reference/LICENSE`, `reference/NOTICE` | JSPWiki's upstream licensing and attribution |
| `manifest.json` | Pinned sources, file hashes and `pov_status: not_run` |

Pass **only `model_input/`** to the finding generator. Reference material and
the manifest contain the answer and must stay outside its accessible context.
Separate directories alone do not restrict a tool-enabled agent: its file tools
must be scoped to `model_input/`.

The model input contains the full, unchanged files:

- `jspwiki-main/src/main/java/org/apache/wiki/WikiServlet.java`
- `jspwiki-main/src/main/java/org/apache/wiki/url/DefaultURLConstructor.java`
- `jspwiki-main/src/main/java/org/apache/wiki/url/URLConstructor.java`
- `jspwiki-main/src/main/resources/ini/jspwiki.properties`
- `jspwiki-war/src/main/webapp/WEB-INF/web.xml`

This selection preserves the request-forwarding code, interface and configuration
context, with original paths and line numbers. It excludes tests, patches,
advisories and Git history. It is a **selected source subset**, not a runnable
checkout or a scan of the whole application. Other URL constructors, filters,
`WikiEngine` and deployment-specific settings are outside this first context;
claims needing them must retain that uncertainty. The supplied configuration is
a source template, not evidence of a particular running deployment.

All downloads use immutable commit hashes:

| Source | Commit |
|---|---|
| [Vul4J dataset](https://github.com/tuhh-softsec/Vul4J/blob/376411da11fa705019f731404de1d0679fe73537/dataset/vul4j_dataset.csv) | `376411da11fa705019f731404de1d0679fe73537` |
| [VUL4J-18 benchmark snapshot](https://github.com/tuhh-softsec/Vul4J/tree/07ad7850a041876befb99847053e4b5e181597a5) | `07ad7850a041876befb99847053e4b5e181597a5` |
| [Upstream JSPWiki fix](https://github.com/apache/jspwiki/commit/88d89d6523802c044cfcb7930cba40d8eeb21da2) | `88d89d6523802c044cfcb7930cba40d8eeb21da2` |

The source context comes from Vul4J's prepared case snapshot, which can include
benchmark adjustments; it is not presented as a pristine upstream checkout.
The vulnerable `DefaultURLConstructor.java` was checked against the upstream
fix's parent, `f140a2a4371735ad24d04a1d78c6e1d9ceaed76f`: its bytes match.

The fix changes the forwarding destination returned by `getForwardPage()`.
The PoV checks forwarding URLs using mocked servlet requests. It is not, by
itself, an end-to-end proof of arbitrary file reads or unauthenticated access.
This preparation script **does not run the PoV**. Step 1b was executed separately
with the complete benchmark, Eclipse Temurin 8 and Maven 3.9.16. Both unchanged
PoV tests failed on the vulnerable version because the actual forward URL was
`/?page=Main&` instead of `/Wiki.jsp?page=Main&`; both passed after applying the
original upstream fix. Builds succeeded and neither test run contained errors or
skips. Exact commands, provenance, environment and limits are documented in
[resources/reproduce_vul4j18.md](resources/reproduce_vul4j18.md); full logs remain
under the ignored `data/pov/VUL4J-18-001/`.

This differential result reproduces the forwarding behavior covered by the mock
servlet tests. It does not by itself prove arbitrary file reads, unauthenticated
remote exploitation or behavior in a deployed JSPWiki instance. See the pinned
[Vul4J instructions](https://github.com/tuhh-softsec/Vul4J/blob/376411da11fa705019f731404de1d0679fe73537/README.md).

Generated data stays untracked. Our code uses this repository's MIT license;
downloaded JSPWiki files keep their upstream licenses and notices. The Vul4J
dataset is [CC BY 4.0](https://github.com/tuhh-softsec/Vul4J/blob/376411da11fa705019f731404de1d0679fe73537/DATA_LICENSE).

Run the small offline checks with:

```bash
python3 -m unittest -v
```

## Generate one localized review

`src/02_generate_findings.py` uses the standard library and a single OpenRouter
Chat Completions request with an explicitly selected **`:free` model**.
Paid model IDs and automatic routers are rejected before a run is created.
No model download, local training or additional Python package is needed.
The latest inspected `VUL4J-18-review-001` completed on 2026-09-23 at 14:31 UTC:
one finding, `finish_reason: stop`, 7.656 seconds, 25,832 prompt tokens and 216
completion tokens. It used Nemotron with an 8192-token limit and `--no-reasoning`;
the provider reported zero reasoning tokens and zero cost. Saved hashes and the
finding text match the request/source artifacts and raw response. This confirms
technical completion, not the truth of the finding. Earlier attempts encountered
an unavailable Qwen endpoint, token limits and Nvidia overload. Those earlier
artifacts are no longer at the reused path; HANDOFF records their inspections.

Create an [OpenRouter API key](https://openrouter.ai/settings/keys) and put it in
`.env` at the repository root. Use `.env.example` as a template if the file does
not exist:

```dotenv
OPENROUTER_API_KEY=your-key-here
```

The generator automatically reads this file relative to its script location;
no console key entry is needed on subsequent runs. `.env` is ignored by Git and
is never copied into model inputs or run artifacts. Only the blank `.env.example`
is versioned. An existing nonempty `OPENROUTER_API_KEY` environment variable takes
precedence; `OPENAI_API_KEY` is not used.

The small loader supports UTF-8 (including BOM), blank lines, whole-line comments
and an optionally single- or double-quoted key value. Use one key entry, with no
inline comments, `export`, variable expansion or multiline values. No additional
Python package is needed.

Prepare the case with `python3 src/01_prepare_case.py` if it is not already present.
For any separately planned new review, choose an explicit token limit and a fresh
run directory. The following settings produced the completed technical PoC;
another run is not needed for the next Java-PoV step:

```bash
python3 src/02_generate_findings.py --model nvidia/nemotron-3-super-120b-a12b:free --max-output-tokens 8192 --no-reasoning --output data/runs/VUL4J-18-review-002
```

Both `--model` and the output-token limit are required; there is no default model.
`--no-reasoning` sends `reasoning: {"enabled": false}` and records it in the request
and manifest. Without the flag, provider defaults remain unchanged. Only use the
flag on models supporting disabled reasoning; unsupported settings should fail
under `require_parameters: true`, rather than be silently removed. The public
Nemotron catalog checked on 2026-09-23 reports `mandatory: false` and reasoning
enabled by default. The completed live attempt sent this flag and returned zero
reported reasoning tokens; effects on review quality have not been evaluated.
The example uses Nemotron 3 Super, listed with zero prompt/completion prices and
JSON-format support in the live public catalog checked on 2026-09-23. This is a
model that has produced one complete findings report. Its
[free endpoint](https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b:free) discloses
logging for security and service improvement; use only the public benchmark input.
The output limit is saved as `max_tokens` and is not a monetary budget.

For the initial pipeline proof of concept, disabling reasoning is a reasonable
technical trial, but it changes the experimental condition. It requests a response
without the model's additional reasoning phase; it does not establish equal review
quality. Token use and latency may decrease, while findings, their detail,
uncertainty and the distribution of claim types may change. The size and direction
of these effects have not been measured here.

The complete response establishes report storage and provides input for subsequent
claim extraction. It characterizes only this model, context and generation setting.
One selected case cannot establish representative LLM security-review performance,
with or without reasoning. The completed no-reasoning trial is technical validation,
not a finalized evaluation configuration.

Before evaluation, fix and document the model, prompt, source context, token budget,
reasoning setting and run count. Keep technical trials separate from evaluation
and retain failures. A small, predefined comparison with reasoning enabled and
disabled is an optional later check, not a prerequisite for this PoC. Do not select
settings based on obtaining preferred findings. Methodological planning belongs in
[WORKPLAN.md](WORKPLAN.md).

Only explicit model IDs ending in `:free` are permitted. The request also sets provider price ceilings
to zero for prompt tokens, completion tokens and requests, and disables provider
fallbacks. No model fallback, paid plugin or automatic retry is requested. If no
free provider supports the requested parameters, the run fails visibly instead
of switching to a paid endpoint. Free availability and limits may change; see
[the current model catalog](https://openrouter.ai/api/v1/models) and
[OpenRouter limits](https://openrouter.ai/docs/api-reference/limits).

Only the five allowlisted files under `--model-input` (default:
`data/VUL4J-18/model_input`) enter the request. Root/file/directory symlinks within
that input are rejected. Extra files are ignored. The versioned
`resources/review_prompt_v1.txt` is the system message; paths and original one-based
source line numbers form the user message. Source bytes are preserved separately.
No reference, manifest, case ID, project instructions, chat history or agent tools
are supplied. Context compression is explicitly disabled. JSON output is requested
with only titles and reports, without claim categories. This generates reports;
it does not independently verify their claims.

The HTTP timeout is 180 seconds. There is no automatic retry, repair request or
follow-up. An uncertain network outcome is retained as an error. OpenRouter chooses
an eligible serving provider; its returned name, model and generation ID are saved
when available. The model ID is not an immutable revision or a guarantee of identical
future results. Data handling follows the account and serving-provider policies;
the script makes no zero-retention promise.

| Run output | Purpose |
|---|---|
| `model_input/`, `review_prompt_v1.txt` | Exact source and prompt bytes |
| `request.json` | Exact HTTP request body, excluding the authorization header |
| `generation_raw.json` | Unmodified response body, including HTTP errors; may not be valid JSON |
| `findings.jsonl` | Validated titles/reports with stable run-scoped IDs; text is not corrected |
| `run_manifest.json` | Case/run IDs, timestamps, duration, model, serving provider, response ID, sent parameters, hashes, status, usage and errors |

`completed` means structurally valid findings were saved, not that their claims
are true. An explicit empty list produces `no_findings` and an empty JSONL file.
Only a single assistant completion with `finish_reason: stop` is accepted.
Malformed output, refusals, tool calls and incomplete responses produce
`invalid_output`; HTTP/network failures, top-level provider errors or a missing/invalid key configuration
produce `run_error`. Neither error status produces a findings file. Raw response
bytes are saved whenever received. Usage, including any reported cost, is preserved
unchanged; `cost_usd` remains `null` because the script does not independently
calculate billing. Provider defaults are visible only as returned in the response.

Input/configuration errors before a run is created leave no run directory.
Started runs remain on disk, and an existing output is always refused. A process
killed before finalization can leave `running` in the manifest: that is an unfinished
run, not evidence of no findings. Outputs belong under the ignored `data/` directory.

The twelve generator tests use synthetic responses and no network. Together with
three preparation tests they cover isolation, byte preservation, free-model
restrictions, `.env` loading, credential exclusion, explicit reasoning control and failure handling. On Windows, the symlink test is explicitly
skipped if the process lacks the required privilege; protection is not verified
there. These tests do not establish live API/model compatibility.

Protocol references: [Chat Completions](https://openrouter.ai/docs/api/reference/overview),
[provider routing and price caps](https://openrouter.ai/docs/guides/routing/provider-selection),
[context compression](https://openrouter.ai/docs/guides/features/message-transforms).

The Java-PoV comparison in step 1b is complete. Keep the completed review and PoV
evidence unchanged; no further generator request is needed. The next planned work
is manual decomposition of the saved finding and refinement of the codebook.

For `finish_reason: length`, the saved response is incomplete and must not be
repaired or counted as findings. Reasoning can consume the same output budget;
see [OpenRouter reasoning limits](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens).
The CLI now prints the saved failure reason. Keep each run directory, even on
failure, and choose a fresh path for an explicitly changed technical trial.

If the response reports `503` with `Service temporarily overloaded`, retain the
failed run. The observed error does not justify changing the prompt, token budget
or reasoning mode. An explicitly chosen later technical attempt can use the same
settings and a new output directory; its timing and outcome must remain recorded.
An HTTP 200 alone does not indicate a successful generation: check the response
body and final run status. No automatic retry is performed.

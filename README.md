# What Can We Verify?

Research repository for evaluating claims in LLM-generated security findings.

The first step prepares **VUL4J-18**, the JSPWiki path-traversal case
**CVE-2019-0225 / CWE-22**, for a localized code review.

Run from this repository with **Python 3.9+** and internet access to
`raw.githubusercontent.com`. No Python packages, Java or Docker are needed for
this preparation step:

```bash
python3 prepare_case.py
```

The script writes `data/VUL4J-18/`. It refuses to overwrite an existing output.
For another copy, choose a new directory:

```bash
python3 prepare_case.py --output data/VUL4J-18-copy
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
This script **does not run the PoV or claim reproduction**. A later execution
step needs the complete benchmark and its Java/Maven setup; see the pinned
[Vul4J instructions](https://github.com/tuhh-softsec/Vul4J/blob/376411da11fa705019f731404de1d0679fe73537/README.md).

Generated data stays untracked. Our code uses this repository's MIT license;
downloaded JSPWiki files keep their upstream licenses and notices. The Vul4J
dataset is [CC BY 4.0](https://github.com/tuhh-softsec/Vul4J/blob/376411da11fa705019f731404de1d0679fe73537/DATA_LICENSE).

Run the small offline checks with:

```bash
python3 -m unittest -v
```

## Generate one localized review

`generate_findings.py` uses the standard library and a single OpenAI Responses
request. This provider is a provisional implementation choice; the experimental
model and budget have not been selected. No real review has been run yet.

Set `OPENAI_API_KEY` in the local environment without putting it in a tracked
file or command argument. After choosing the model (prefer a pinned snapshot)
and budget, replace both placeholders below and use a new output directory:

```bash
python3 generate_findings.py \
  --model MODEL_SNAPSHOT_ID \
  --max-output-tokens OUTPUT_TOKEN_LIMIT \
  --output data/runs/VUL4J-18-review-001
```

The token limit includes reasoning tokens and is **not a monetary budget**;
input tokens also cost money. Choose it with the selected model's pricing in
mind. No model or token limit is silently selected. The HTTP timeout is 180
seconds, with no automatic retry, repair request or follow-up. An uncertain
network outcome is retained as an error, not automatically resubmitted.

Only the five allowlisted files under `--model-input` (default:
`data/VUL4J-18/model_input`) are read into the request. Root/file/directory
symlinks within that input are rejected. Extra files are ignored. The versioned
`review_prompt_v1.txt` and a view with paths and original one-based line numbers
are sent; source bytes are separately preserved unchanged. No reference,
manifest, case ID, project instructions, chat history, external sources or
agent tools are supplied. The request disables input truncation and response
storage, and requests JSON with only finding titles and reports, without claim
type categories. This is report generation, not independent verification.

| Run output | Purpose |
|---|---|
| `model_input/`, `review_prompt_v1.txt` | Exact source and prompt bytes |
| `request.json` | Exact HTTP request body, excluding the authorization header |
| `generation_raw.json` | Unmodified provider response body, including HTTP errors; may not be valid JSON |
| `findings.jsonl` | Validated titles/reports with stable IDs scoped to the saved run; report text is not corrected |
| `run_manifest.json` | Case/run IDs, timestamps, duration, requested/returned model, sent parameters, hashes, status, available usage and errors |

`completed` means structurally valid findings were saved, not that their claims
are true. An explicit empty list produces `no_findings` and an empty JSONL file.
Malformed output, refusals and incomplete responses produce `invalid_output`;
HTTP/network failures or a missing key produce `run_error`. Neither error
status produces a findings file. Raw response bytes are saved whenever received;
there is no response file if the request was not sent or no body was received.
Usage is saved as returned; `cost_usd` stays `null` (not zero), since the script
does not calculate billing. Provider defaults not explicitly set remain visible
only insofar as the provider returns them in the raw response.

Input/configuration errors before a run is created leave no run directory.
Started runs remain on disk, and an existing output is always refused. A
process killed before finalization can leave `running` in the manifest: that
is an unfinished run, not evidence of no findings. All experimental outputs
should remain under the ignored `data/` directory.

The seven generator tests use synthetic responses and no network; together
with the three preparation tests they cover the concrete isolation, preservation
and failure risks. They do not establish live API/model compatibility. Protocol
references: [OpenAI text generation](https://developers.openai.com/api/docs/guides/text),
[JSON output](https://developers.openai.com/api/docs/guides/structured-outputs),
[reasoning token limits](https://developers.openai.com/api/docs/guides/reasoning).

Next: select the experimental model and budget, make an API key available, and
save one real review (including an empty result or failure). Then manually
inspect any findings and their claims. Java-PoV reproduction is still pending.

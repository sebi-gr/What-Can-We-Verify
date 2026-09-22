# What Can We Verify?

Research code for evaluating claims in LLM-generated security findings.
Keep it small: readable scripts, explicit inputs and saved outputs. Add a component
only when an experiment needs it to answer a research question.

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

Next: generate and save one finding from this context, then manually inspect its
claim decomposition before adding automated verification.

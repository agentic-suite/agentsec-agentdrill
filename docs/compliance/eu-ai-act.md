# EU AI Act Mapping (Art. 12)

The EU AI Act Art. 12 requires **record-keeping / logging** for high-risk AI systems. agentdrill produces
continuously-verified evidence that the logging-adjacent controls actually work. Design intent.

## What agentdrill contributes

| Need | agentdrill artifact |
|---|---|
| Logs conforming to a recognized standard | results/evidence in the **agentwatch** schema; evidence bundles verifiable offline |
| Demonstrated control effectiveness | efficacy-backed blocked/missed/degraded per release |
| Change management evidence | CI gate rejecting un-blocking policy changes; fix-validation (`fix_decay`) |
| Continuous assurance | trigger-driven re-drills on config/model/policy change; per-release benchmark |
| Transparency (incl. misses) | limitations register; adjudication process with a resolution SLA |

## Honesty

agentdrill **supports** Art. 12 evidence; it does not itself certify compliance. Evidence exports to
**agentcomply** for the compliance report, and every row cites a third-party-verifiable artifact
(`agentdrill verify`).

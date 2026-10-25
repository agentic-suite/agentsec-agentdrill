"""Pack templates (M20 20.3, F70).

``init --template …`` scaffolds attack cases with oracle stubs, **benign twins**
(for the efficacy review), cleanup and ATLAS/OWASP tags. A scaffolded pack
passes lint + the efficacy review. Design:
``docs/prd/22-frontier-dx-features.md``.
"""

from __future__ import annotations

import yaml

from agentdrill.models.attack_pack import AttackPack


class TemplateError(ValueError):
    """Raised when an unknown pack template is requested."""


#: A template spec: (tool, target, ATLAS tag, OWASP tag).
_TEMPLATES: dict[str, tuple[str, str, str, str]] = {
    "mcp-poisoning": ("mcp_tool_poison", "agentgate", "ATLAS-AML.T0051", "OWASP-LLM01"),
    "exfil-chain": ("send_message", "agentgate", "ATLAS-AML.T0057", "OWASP-LLM02"),
    "destructive-command": ("shell", "policyweave-output", "ATLAS-AML.T0049", "OWASP-LLM01"),
    "supply-chain": ("hijack_update", "agentgate", "ATLAS-AML.T0011", "OWASP-LLM03"),
}

#: The available templates.
TEMPLATES: tuple[str, ...] = tuple(_TEMPLATES)


def _case(
    case_id: str, *, tool: str, target: str, tags: list[str], expect: str
) -> dict[str, object]:
    return {
        "id": case_id,
        "title": f"{case_id} (scaffolded)",
        "goal": f"Verify the stack handles {case_id}",
        "incident_ref": "incident-register#1",
        "target": {"type": target},
        "driver": {"type": "subprocess"},
        "attack": {"steps": [{"tool": tool, "args": {}}]},
        "oracle": {"expect": expect},
        "cleanup": [{"cmd": "reset", "expect": "success"}],
        "tags": tags,
    }


def scaffold(template: str, *, name: str) -> AttackPack:
    """Scaffold a pack from ``template`` (attack + benign twin).

    Raises:
        TemplateError: The template is unknown.
    """
    spec = _TEMPLATES.get(template)
    if spec is None:
        raise TemplateError(f"unknown template: {template!r}; known: {list(TEMPLATES)}")
    tool, target, atlas, owasp = spec
    tags = [atlas, owasp, template]
    data = {
        "pack": {
            "name": name,
            "version": "0.1.0",
            "description": f"Scaffolded from the {template} template",
            "min_agentdrill": "0.1.0",
            "license": "Apache-2.0",
            "trust": "local",
        },
        "cases": [
            {
                **_case(template, tool=tool, target=target, tags=tags, expect="blocked"),
                "benign_twin": f"{template}-benign",
            },
            _case(
                f"{template}-benign",
                tool=tool,
                target=target,
                tags=[atlas, owasp, f"{template}-benign"],
                expect="missed",
            ),
        ],
    }
    return AttackPack.model_validate(data)


def scaffold_yaml(template: str, *, name: str) -> str:
    """Render the scaffolded pack as YAML."""
    return yaml.safe_dump(scaffold(template, name=name).model_dump(), sort_keys=False)

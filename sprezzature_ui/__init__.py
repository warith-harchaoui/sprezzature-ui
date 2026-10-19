"""
sprezzature-ui — vanilla JavaScript and Tailwind, for people without a designer.

The skill half of this brick writes interfaces: components, pages, forms,
dialogs, dashboards, in semantic HTML with Tailwind utilities and plain ES
modules — no framework runtime, dark-mode peers, focus rings and
reduced-motion guards included. That half is prose and judgement, and it
lives in `SKILL.md` where Claude reads it.

This package is the **deterministic** half: the two tools that can be run
rather than reasoned about.

* **audit** — `sprezzature-ui-i18n-audit` finds the translations embedded in
  JavaScript and HTML, and the LLM prompts inlined in Python. Both belong in
  `locales/i18n.yaml`, and both are invisible until somebody needs a second
  language and discovers the strings are scattered through the source.
* **make** — `sprezzature-ui-i18n-make` scaffolds that catalogue, compiles it
  to JSON and emits the loader that reads it.

Why the package stops there
---------------------------
Writing a component is the model's work, guided by `SKILL.md`. No HTTP route
can carry it, and offering one would be the forced surface the house contract
(`SURFACES.md`) exists to prevent. The exemption is declared there by name,
with this as the reason.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Warith HARCHAOUI"
__email__ = "warithmetics@deraison.ai"
__license__ = "BSD-3-Clause"

from typing import Any  # noqa: E402

#: Names resolved on first use, mapped to the module that owns them. Lazy for
#: the same reason as every brick in this suite: ``import sprezzature_ui``
#: must work after a bare ``pip install``, and the i18n catalogue needs PyYAML
#: that a caller who only audits never touches.
_EXPORTS: dict[str, str] = {
    # audit
    "audit_js": "audit_i18n",
    "audit_py": "audit_i18n",
    "audit_path": "audit_i18n",
    "gather": "audit_i18n",
    # make
    "scaffold": "i18n_make",
    "compile_json": "i18n_make",
    "emit_loader": "i18n_make",
}


def __getattr__(name: str) -> Any:
    """Resolve an export on first use, per PEP 562."""
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    try:
        module = importlib.import_module(f"sprezzature_ui_scripts.{module_name}")
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ImportError(
            f"`{name}` lives in {module_name}, whose dependencies are an "
            f"optional extra. Install them with: "
            f"pip install 'sprezzature-ui[i18n]'"
        ) from exc
    return getattr(module, name)


__all__ = ["__version__", *sorted(_EXPORTS)]

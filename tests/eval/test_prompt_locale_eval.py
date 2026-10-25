"""
Why a prompt's missing translation falls back to the validated locale.

The catalogue treats a prompt differently from a label: a label that goes
missing falls back to any locale, or to its own id, because a human reads it
and sees something is wrong. A prompt falls into a model, which reads whatever
it is handed and answers plausibly. So every ``prompts:`` entry names the one
locale it was engineered and tested in, and a locale with no entry resolves to
*that* text — never to the first declared locale, never to the id, and never to
a translation produced on the spot.

That is a claim about model behaviour, and the deterministic suite cannot test
it: ``tests/test_i18n_catalogue.py`` proves the resolvers *obey* the rule, not
that the rule is right. This module calls a model and measures.

What is asserted, and what is only measured
-------------------------------------------

**Asserted — the ordering.** The validated locale must honour the prompt's
contract at least as often as any translation of it. If a translation scored
better, ``validated:`` would be pointing at the wrong locale, and the fallback
would be sending callers to the weaker text. This holds regardless of how
capable the local model is, which is why it is the assertion that carries the
rule.

**Asserted — something was measured.** The validated prompt has to conform on
at least one input. A run where nothing conformed has compared two zeroes and
proved nothing, and would otherwise pass.

**Measured, not asserted — that the translation is worse.** Asserting a gap
would be asserting a bug: a carefully validated French prompt *should* score
the same as the English one, and the day somebody validates it the entry gains
``validated: fr`` and this suite should not object. What the rule needs is not
"translations are bad" but "an unvalidated translation is unmeasured" — so the
numbers are printed, and the resolver's job is to flag, not to refuse.

Contract, and why it is checked mechanically
--------------------------------------------

The prompt under test says "in three bullet points". Counting bullets needs no
judge, and a mechanical check cannot be talked into a generous reading — which
is the failure mode of scoring a format with a model. A judge earns its place
on the part that is not countable: whether the three bullets are faithful to
the input. That is what the DeepEval ``GEval`` case below is for, scored by the
same house model through the same ``llm.chat`` every other call in this project
uses.

On Giskard
----------

Giskard scans an LLM application for *vulnerabilities* — injection, harmful
completions, robustness to perturbed inputs. That is a real question about this
catalogue, since a prompt assembled from a YAML file is a prompt somebody can
edit, and it deserves its own pass. It is not this question: a Giskard scan of
the English prompt tells you nothing about whether the French one behaves like
it. Measuring cross-locale conformance is a comparison of two prompts on the
same inputs, which is what this module does directly.

Author
------
`Warith HARCHAOUI, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import re
from collections.abc import Callable

import i18n_make  # noqa: E402 — via tests/conftest.py sys.path
import pytest

pytestmark = pytest.mark.eval

#: The prompt under test, taken from the starter catalogue rather than written
#: here: the point is to measure what ``--init`` hands a reader, and a copy in
#: this file would drift from it quietly.
PROMPT_ID = "summarize.system"

#: Three short inputs. Short because each locale costs one model call per
#: input, and three because a majority of one is not a majority.
INPUTS: tuple[str, ...] = (
    "The city council approved a new tram line on Tuesday. Construction starts "
    "in March and will last two years. Fares will not rise.",
    "The library will close for refurbishment from June. Books can be returned "
    "to the mobile van on Saturdays. It reopens in the autumn.",
    "Heavy rain is forecast for the weekend. The festival moves indoors to the "
    "sports hall. Tickets stay valid and refunds are available until Friday.",
)

#: A line that is a bullet: dash, asterisk, bullet character, or "1." / "1)".
_BULLET = re.compile(r"^\s*(?:[-*•–]\s+|\d+[.)]\s+)")

#: Number words the prompt may use, in the catalogue's locales. The count is
#: read out of the prompt text rather than written here, so the expectation
#: cannot drift from the instruction it is checking.
_NUMBER_WORDS: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "un": 1,
    "une": 1,
    "deux": 2,
    "trois": 3,
    "quatre": 4,
    "cinq": 5,
}

#: The number has to sit immediately before the thing being counted. Scanning
#: the whole prompt for any number word read "Vous êtes **un** assistant
#: concis" as a request for one bullet, so the French prompt was measured
#: against a contract it never stated — and scored 0 for the wrong reason while
#: the right reason was also there. A measurement that is wrong in the
#: direction you expected is the hardest kind to notice.
_ASKS_FOR = re.compile(
    r"\b(?P<n>" + "|".join(_NUMBER_WORDS) + r")\b\s+(?:bullet\s+points?|bullets?|puces?)",
    re.IGNORECASE,
)


def _bullets(answer: str) -> list[str]:
    """The bullet lines in `answer`, stripped of their markers."""
    return [_BULLET.sub("", line).strip() for line in answer.splitlines() if _BULLET.match(line)]


def _looks_like(text: str, locale: str) -> bool:
    """Is `text` written in `locale`?

    ``langdetect`` is what the rest of this project uses to answer this (see
    ``scripts/_lang.py``), so it is what is used here. Skips rather than guesses
    when it is absent: a hand-rolled stopword test would report its own
    vocabulary.
    """
    langdetect = pytest.importorskip(
        "langdetect",
        reason="langdetect is the [lang] extra; it is how this project detects "
        "a language and the measurement needs it",
    )
    langdetect.DetectorFactory.seed = 0
    try:
        return langdetect.detect(text) == locale
    except langdetect.lang_detect_exception.LangDetectException:
        return False


def _catalogue_prompt(locale: str) -> str:
    """The starter catalogue's text for :data:`PROMPT_ID` in `locale`."""
    entry = i18n_make._STARTER["prompts"][PROMPT_ID]
    return entry[locale]


def _conformance(ask: Callable[..., str], locale: str) -> tuple[int, list[str]]:
    """How often the prompt in `locale` honours its own contract.

    Returns
    -------
    tuple
        ``(conforming, notes)`` over :data:`INPUTS`. An answer conforms when it
        has exactly the number of bullets the prompt asks for **and** is written
        in the prompt's own language — a "translation" that still answers in
        English is the silent breakage the validated locale exists to avoid,
        and it is invisible to a bullet count alone.
    """
    system = _catalogue_prompt(locale)
    asked = _ASKS_FOR.search(system)
    assert asked, (
        f"the {locale} prompt names no number of bullets, so there is no "
        f"contract to count against: {system!r}. A prompt in this catalogue "
        f"whose format cannot be checked mechanically is one this suite has no "
        f"way to call validated."
    )
    wanted = _NUMBER_WORDS[asked.group("n").lower()]
    conforming = 0
    notes: list[str] = []
    for index, text in enumerate(INPUTS, 1):
        answer = ask(text, system=system)
        bullets = _bullets(answer)
        right_count = len(bullets) == wanted
        right_language = _looks_like(" ".join(bullets) or answer, locale)
        if right_count and right_language:
            conforming += 1
        notes.append(
            f"  {locale} input {index}: {len(bullets)} bullet(s) "
            f"[{'ok' if right_count else f'wanted {wanted}'}], "
            f"language {'ok' if right_language else 'not ' + locale}"
        )
    return conforming, notes


@pytest.fixture(scope="module")
def conformance(ask: Callable[..., str]) -> dict[str, int]:
    """Conformance per locale, measured once and reported.

    One fixture rather than one call per test: the measurement is the expensive
    part — two locales times three inputs — and both assertions below read the
    same numbers. Printed in full so a failure shows what the model actually
    did, not only which comparison went the wrong way.
    """
    entry = i18n_make._STARTER["prompts"][PROMPT_ID]
    validated = entry[i18n_make.VALIDATED_KEY]
    locales = [loc for loc in entry if loc != i18n_make.VALIDATED_KEY]

    scores: dict[str, int] = {}
    report: list[str] = []
    for locale in sorted(locales, key=lambda loc: loc != validated):
        count, notes = _conformance(ask, locale)
        scores[locale] = count
        marker = " (validated)" if locale == validated else ""
        report.append(f"{locale}{marker}: {count}/{len(INPUTS)}")
        report.extend(notes)
    print("\n" + "\n".join(report))
    scores["__validated__"] = scores[validated]  # type: ignore[index]
    scores["__validated_locale__"] = validated  # type: ignore[assignment]
    return scores


def test_the_validated_prompt_honours_its_contract_at_least_once(
    conformance: dict[str, int],
) -> None:
    """Otherwise the run compared two zeroes and proved nothing.

    This is the guard against the whole module passing vacuously: if the model
    on this machine cannot produce three bullets from any of the three inputs,
    the ordering test below holds trivially (0 ≥ 0) and would read as support
    for a rule nothing was measured about.
    """
    validated = conformance["__validated_locale__"]
    assert conformance[validated] >= 1, (  # type: ignore[index]
        f"the validated prompt ({validated}) honoured its contract on none of "
        f"{len(INPUTS)} inputs. Either the model on this machine cannot follow "
        f"it — in which case this suite is measuring the model, not the prompt "
        f"— or `validated: {validated}` is a claim the catalogue cannot back."
    )


def test_the_validated_locale_is_not_beaten_by_a_translation(
    conformance: dict[str, int],
) -> None:
    """The ordering that makes the fallback the right default.

    A translation scoring higher than the validated text is not a nice surprise:
    it means every locale with no entry of its own is being sent to the weaker
    prompt. The fix would be to move ``validated:`` — which is a decision about
    which language was actually tested, and belongs in the catalogue, not here.
    """
    validated = conformance["__validated_locale__"]
    best = conformance[validated]  # type: ignore[index]
    beaten = {
        locale: score
        for locale, score in conformance.items()
        if not locale.startswith("__") and locale != validated and score > best
    }
    assert not beaten, (
        f"{beaten} scored above the validated locale {validated!r} "
        f"({best}/{len(INPUTS)}). Either `validated:` names the wrong language, "
        f"or the validated text has drifted since it was tested."
    )


def test_the_judge_finds_the_validated_summary_faithful(
    ask: Callable[..., str], text_model: str
) -> None:
    """The part no bullet count can answer: is the summary true to the input?

    DeepEval's ``GEval`` with the house model as judge — the same ``llm.chat``
    and the same resolved tag as the answer under test, because a judge from a
    different family would be measuring the disagreement between two models as
    much as the quality of one answer.

    The threshold is deliberately modest. A local 4b judge scoring a local 4b
    answer is a weak instrument, and a strict threshold here would fail on the
    instrument rather than on the prompt. What it is good for is catching an
    answer that is fluent and about something else.
    """
    deepeval = pytest.importorskip(
        "deepeval", reason="deepeval is the optional LLM-evaluation dependency"
    )
    from deepeval.metrics import GEval
    from deepeval.models.base_model import DeepEvalBaseLLM
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams

    class HouseJudge(DeepEvalBaseLLM):
        """The project's one model, wearing DeepEval's interface."""

        def load_model(self) -> str:
            return text_model

        def get_model_name(self) -> str:
            return f"{text_model} via best_engine_ai_helper.llm.chat"

        def generate(self, prompt: str, schema: object = None) -> str:
            return ask(prompt)

        async def a_generate(self, prompt: str, schema: object = None) -> str:
            return self.generate(prompt, schema)

    source = INPUTS[0]
    answer = ask(source, system=_catalogue_prompt("en"))

    metric = GEval(
        name="Faithful summary",
        criteria=(
            "Does the output summarise the input without adding facts the input "
            "does not contain, and without contradicting it?"
        ),
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=HouseJudge(),
        threshold=0.5,
        async_mode=False,
    )
    case = LLMTestCase(input=source, actual_output=answer)
    try:
        metric.measure(case)
    except RuntimeError as exc:
        # A judge that ran out of time has measured nothing, and failing on it
        # would report this machine's throughput as a defect in the prompt. The
        # two assertions that carry the rule — the ordering, and that something
        # was measured — do not need a judge at all.
        if "timed out" not in str(exc).lower():
            raise
        pytest.skip(
            f"the judge ({text_model}) did not answer within "
            f"SPREZZATURE_LLM_TIMEOUT. Raise it, or point this at a larger tag."
        )
    print(f"\nGEval faithfulness: {metric.score} — {metric.reason}")
    assert metric.score is not None and metric.score >= metric.threshold, (
        f"the validated prompt produced an answer the judge scored "
        f"{metric.score} on faithfulness: {metric.reason}\n\n{answer}"
    )
    assert deepeval is not None  # the import is the dependency under use

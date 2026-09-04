"""Eval runner. Phase 0 supports JSON suites with simple matchers.

A suite file is a JSON array of objects:
    [
      {"name": "case_1", "input": {...}, "expect": {"contains": ["..."]}},
      {"name": "case_2", "input": {...}, "expect": {"equals": {...}}}
    ]
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class EvalCase:
    name: str
    input: dict[str, Any]
    expect: dict[str, Any]


@dataclass
class EvalCaseResult:
    name: str
    passed: bool
    message: str


@dataclass
class EvalResult:
    passed: int = 0
    failed: int = 0
    cases: list[EvalCaseResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.passed + self.failed

    @property
    def score(self) -> float:
        return 0.0 if self.total == 0 else self.passed / self.total


class EvalRunner:
    def __init__(self, suite_path: Path) -> None:
        self.suite_path = Path(suite_path)

    def load(self) -> list[EvalCase]:
        if not self.suite_path.exists():
            return []
        raw = json.loads(self.suite_path.read_text())
        return [EvalCase(**c) for c in raw]

    def run(
        self, fn: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> EvalResult:
        result = EvalResult()
        for case in self.load():
            try:
                out = fn(case.input)
            except Exception as e:  # noqa: BLE001
                result.failed += 1
                result.cases.append(
                    EvalCaseResult(case.name, False, f"raised: {e!r}")
                )
                continue
            ok, msg = _match(out, case.expect)
            (result.cases.append(EvalCaseResult(case.name, True, msg))
             if ok
             else result.cases.append(EvalCaseResult(case.name, False, msg)))
            if ok:
                result.passed += 1
            else:
                result.failed += 1
        return result


def _match(output: dict, expect: dict) -> tuple[bool, str]:
    if "equals" in expect:
        if output == expect["equals"]:
            return True, "ok"
        return False, "output != expected"
    if "contains" in expect:
        haystack = json.dumps(output, default=str)
        for needle in expect["contains"]:
            if needle not in haystack:
                return False, f"missing substring {needle!r}"
        return True, "ok"
    return False, "no matcher specified"

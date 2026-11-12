"""The comparison counts, on a made-up pair of runs and on the two committed runs."""

import hashlib
import json
import re
from pathlib import Path

import pytest

import compare

ROOT = Path(__file__).resolve().parents[1]


def row(face: str, size: int, mode: str, dist: int) -> dict[str, str]:
    return {
        "face": face, "size_pt": str(size), "mode": mode, "truth_chars": "1000",
        "edit_distance": str(dist), "char_accuracy": f"{1 - dist / 1000:.4f}",
    }


def run(dists: list[int]) -> dict[compare.Case, dict[str, str]]:
    cases = [("A", 6, "standard"), ("A", 7, "standard"), ("A", 6, "fine"), ("A", 7, "fine")]
    return {case: row(*case, dist) for case, dist in zip(cases, dists, strict=True)}


def test_summary_counts_changes_and_pass_mark_crossings():
    s = compare.summary(run([30, 5, 10, 0]), run([10, 5, 12, 0]))
    assert (s["cases"], s["changed"], s["fewer_errors"], s["more_errors"]) == (4, 2, 1, 1)
    assert s["changed_by_mode"] == {"standard": 1, "fine": 1, "control-300-gray": 0}
    assert s["crossed_pass_mark"] == [["A", 6, "standard"]]
    assert s["smallest_passing_size_changed"] == [["A", "standard"]]
    assert round(s["largest_change_points"], 2) == 2.0
    assert s["total_errors"] == [45, 27]


def test_identical_runs_report_no_change():
    s = compare.summary(run([30, 5, 10, 0]), run([30, 5, 10, 0]))
    assert (s["changed"], s["crossed_pass_mark"], s["smallest_passing_size_changed"]) == (0, [], [])
    assert s["largest_change_points"] == 0.0


def test_runs_over_different_passages_are_refused():
    other = run([30, 5, 10, 0])
    other[("A", 6, "fine")]["truth_chars"] = "999"
    with pytest.raises(SystemExit):
        compare.changed(run([30, 5, 10, 0]), other)


def test_runs_with_different_passage_files_are_refused(tmp_path):
    for name, digest in (("a", "1" * 64), ("b", "2" * 64)):
        (tmp_path / name).mkdir()
        (tmp_path / name / "environment.json").write_text(json.dumps({"tesseract": "t", "passage_sha256": digest}))
    with pytest.raises(SystemExit):
        compare.same_passage(tmp_path / "a", tmp_path / "b")
    compare.same_passage(tmp_path / "a", tmp_path / "a")


def test_committed_comparison_matches_the_two_result_files():
    first, second = ROOT / "results", ROOT / "results-tesseract-5.5.4"
    assert (second / "comparison.md").read_text() == compare.report(first, second)


def test_readme_figures_of_the_second_run_come_from_the_two_result_files():
    a, b = compare.load(ROOT / "results"), compare.load(ROOT / "results-tesseract-5.5.4")
    s = compare.summary(a, b)
    readme = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
    section = readme.split("## Tesseract 5.5.4 run, 2026-11-12", 1)[1].split("## Method", 1)[0]
    by_mode = s["changed_by_mode"]
    each = len(a) // len(by_mode)
    assert f"| Cases | {each} | {each} | {each} | {s['cases']} |" in section
    assert f"| {by_mode['standard']} | {by_mode['fine']} | {by_mode['control-300-gray']} | {s['changed']} |" in section
    assert f"Of the {s['changed']} changed cases, 5.5.4 made fewer errors in {s['fewer_errors']} and more in {s['more_errors']}." in section
    assert f"went from {s['total_errors'][0]:,} to {s['total_errors'][1]:,}" in section
    assert s["crossed_pass_mark"] == [] and s["smallest_passing_size_changed"] == []
    assert "The smallest passing size is the same for every font in every mode" in section
    assert f"No case crossed the {compare.SURVIVES:.0%} mark in either direction." in section
    env = compare.environment(ROOT / "results-tesseract-5.5.4")
    versions = (ROOT / "results-tesseract-5.5.4" / "versions.txt").read_text()
    assert env["tesseract"] == "tesseract 5.5.4" and versions.startswith("tesseract 5.5.4\n leptonica-1.82.0\n")
    assert "linked to Leptonica 1.82.0" in section
    commit = re.search(r"^source commit ([0-9a-f]{40})$", versions, re.M)
    assert commit and f"(commit `{commit[1][:7]}`)" in section
    assert env["eng_traineddata_sha256"] == compare.environment(ROOT / "results")["eng_traineddata_sha256"]
    assert f"Its sha256 starts `{str(env['eng_traineddata_sha256'])[:8]}`" in section
    assert env["typst"].startswith("typst 0.15.1 ") and env["ghostscript"] == "Ghostscript 10.02.1"  # type: ignore[union-attr]
    assert "The same Typst 0.15.1, Ghostscript 10.02.1, font files and settings." in section
    top = max(a, key=lambda k: abs(float(b[k]["char_accuracy"]) - float(a[k]["char_accuracy"])))
    face, size, mode = top
    assert f"The largest change was {s['largest_change_points']:.2f} percentage points, for {face} at {size} pt {mode}" in section
    assert f"({float(a[top]['char_accuracy']) * 100:.2f}% to {float(b[top]['char_accuracy']) * 100:.2f}%)" in section
    from_seven = max(abs(int(b[k]["edit_distance"]) - int(a[k]["edit_distance"])) for k in a if k[1] >= 7)
    assert f"From 7 pt up, no case changed by more than {from_seven} characters out of 1,201." in section
    five = sorted(float(b[k]["char_accuracy"]) * 100 for k in b if k[1] == 5 and k[2] == "standard")
    assert f"At 5 pt standard the scores now run from {five[0]:.2f}% to {five[-1]:.2f}%." in section


def test_the_control_run_wrote_the_files_of_the_first_run():
    """SHA256SUMS is from the 5.3.4 build of the Dockerfile. Every file it names is in results/ with that hash."""
    sums = (ROOT / "results-tesseract-5.5.4" / "control-5.3.4" / "SHA256SUMS").read_text().splitlines()
    names = {line.split("  ", 1)[1] for line in sums}
    assert "results.csv" in names
    assert {f"ocr/{p.name}" for p in (ROOT / "results" / "ocr").glob("*.txt")} <= names
    for line in sums:
        digest, name = line.split("  ", 1)
        assert hashlib.sha256((ROOT / "results" / name).read_bytes()).hexdigest() == digest, name

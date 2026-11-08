import bench


def slow_levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def test_normalise_folds_quotes_dashes_and_whitespace():
    assert bench.normalise("“My dear” — it’s\n\n  let") == '"My dear" - it\'s let'


def test_normalise_keeps_case_and_punctuation():
    assert bench.normalise("Mr. Bennet") != bench.normalise("mr Bennet")


def test_exact_match_is_full_accuracy():
    assert bench.char_accuracy("a b\nc", "a  b c") == (1.0, 0, 5)


def test_accuracy_matches_reference_distance():
    truth, ocr = "Netherfield Park is let at last?", "Netherfie1d Park is Iet at 1ast"
    acc, dist, n = bench.char_accuracy(truth, ocr)
    assert dist == slow_levenshtein(truth, ocr)
    assert acc == 1 - dist / n


def test_accuracy_never_negative():
    assert bench.char_accuracy("ab", "completely different and much longer")[0] == 0.0


def test_paragraphs_join_hard_breaks():
    assert bench.paragraphs("one\ntwo\n\nthree\n") == ["one two", "three"]


def test_parse_sizes():
    assert bench.parse_sizes("6-8") == [6, 7, 8]
    assert bench.parse_sizes("6,10") == [6, 10]


def test_smallest_surviving_needs_every_larger_size():
    rows = [
        {"face": "F", "mode": "m", "size_pt": s, "char_accuracy": a}
        for s, a in [(6, 0.99), (7, 0.5), (8, 0.985), (9, 0.99)]
    ]
    assert bench.smallest_surviving(rows, "F", "m") == 8

"""CITATION.cff agrees with pyproject.toml and with the BibTeX block in the README."""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cff() -> dict[str, str]:
    """The top-level scalar fields. The file is flat enough that no YAML parser is needed."""
    fields = {}
    for line in (ROOT / "CITATION.cff").read_text(encoding="utf-8").splitlines():
        found = re.fullmatch(r'([a-z-]+): "?([^"]+)"?', line)
        if found:
            fields[found[1]] = found[2]
    return fields


def test_citation_matches_the_project_metadata():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    fields = cff()
    assert fields["cff-version"] == "1.2.0"
    assert fields["title"] == project["name"]
    assert fields["version"] == project["version"]
    assert fields["license"] == project["license"]
    assert fields["abstract"] == project["description"]
    assert fields["repository-code"] == project["urls"]["Repository"]
    assert fields["url"] == project["urls"]["Documentation"]
    # The first author is the organisation as an entity: `name`, never `family-names` or `given-names`.
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    authors = re.search(r"^authors:\n((?:  .*\n)+)", text, re.M)
    assert authors, "CITATION.cff has no authors block"
    assert authors[1].startswith(f'  - name: "{project["authors"][0]["name"]}"\n')
    assert authors[1].count("  - ") == 1
    assert "family-names" not in authors[1] and "given-names" not in authors[1]


def test_readme_bibtex_matches_the_citation_file():
    fields = cff()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    block = re.search(r"```bibtex\n(.*?)```", readme, re.S)
    assert block, "README.md has no BibTeX block"
    year, month, _day = fields["date-released"].split("-")
    # cffconvert writes the month without a leading zero.
    # The README gives the entry a real key. cffconvert writes a placeholder, so the key is put back before
    # the whole entry is compared.
    key = "faxlegibilitybench" + year
    assert block[1].startswith(f"@misc{{{key},\n")
    assert block[1].replace(f"@misc{{{key},", "@misc{YourReferenceHere,", 1) == (
        "@misc{YourReferenceHere,\n"
        "author = {JSB Holdings LLC},\n"
        f"month = {{{int(month)}}},\n"
        f"title = {{{fields['title']}}},\n"
        f"url = {{{fields['url']}}},\n"
        f"year = {{{year}}}\n"
        "}\n"
    )

import pytest

from patching import PatchError, apply_edits, validate_edits


def test_exact_edit_is_validated_and_applied():
    source = "x = 1\n"; edits = validate_edits({"edits":[{"old":"x = 1","new":"x = 2"}]}, source)
    assert apply_edits(source, edits) == "x = 2\n"

@pytest.mark.parametrize("proposal", [{}, {"edits": []}, {"edits":[{"old":"x","new":"("}]}])
def test_malformed_or_invalid_edits_are_rejected(proposal):
    with pytest.raises(PatchError): validate_edits(proposal, "x = 1\n")

def test_ambiguous_text_is_rejected():
    with pytest.raises(PatchError): validate_edits({"edits":[{"old":"x","new":"y"}]}, "x\nx\n")

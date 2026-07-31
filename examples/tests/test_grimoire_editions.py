import pytest

from mantle.vcw.grimoire_editions import (
    GrimoireEditionError,
    decode_statement,
    get_edition,
    known_editions,
)


def test_registry_has_both_explicit_profiles():
    assert known_editions() == ("grimoire-v0.9", "grimoire-v0.10")
    assert get_edition("grimoire-v0.9").profile == "grimoire-v0.9"
    assert get_edition("grimoire-v0.10").profile == "grimoire-v0.10"


def test_unknown_profile_is_refused():
    with pytest.raises(GrimoireEditionError):
        get_edition("grimoire-v9.9")


def test_v010_decoder_is_not_available_before_g03():
    with pytest.raises(GrimoireEditionError, match="not implemented"):
        decode_statement(b"\x01\x01\x01\x0f", profile="grimoire-v0.10")

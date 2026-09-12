"""
tests/test_registry.py — Unit tests for the mudra registry.
"""

import pytest
from data.mudra_registry import (
    get_all_mudras, get_mudra_by_name,
    get_mudra_names, get_mudras_by_category,
)


def test_registry_not_empty():
    assert len(get_all_mudras()) > 0


def test_all_mudras_have_required_fields():
    for m in get_all_mudras():
        assert m.name, f"Missing name: {m}"
        assert m.description, f"Missing description: {m.name}"
        assert len(m.finger_pattern) == 5, f"Pattern must have 5 elements: {m.name}"


def test_get_mudra_by_name_found():
    m = get_mudra_by_name("Pataka")
    assert m is not None
    assert m.name == "Pataka"


def test_get_mudra_by_name_case_insensitive():
    assert get_mudra_by_name("pataka") is not None


def test_get_mudra_by_name_not_found():
    assert get_mudra_by_name("NonExistentMudra") is None


def test_get_mudra_names_sorted():
    names = get_mudra_names()
    assert names == sorted(names)


def test_get_mudras_by_category():
    asamyuta = get_mudras_by_category("Asamyuta")
    assert all(m.category == "Asamyuta" for m in asamyuta)

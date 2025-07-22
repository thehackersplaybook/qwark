"""Tests for qwark core functionality."""

import pytest
from qwark import optimize_query


def test_optimize_query_not_implemented():
    """Test that optimize_query raises NotImplementedError."""
    config = {"test": "config"}

    with pytest.raises(NotImplementedError, match="Project not released yet"):
        optimize_query(config)


def test_optimize_query_signature():
    """Test that optimize_query has the correct signature."""
    import inspect
    from typing import Dict, Any

    sig = inspect.signature(optimize_query)
    params = list(sig.parameters.keys())

    assert len(params) == 1
    assert params[0] == "config"
    assert sig.parameters["config"].annotation == Dict[str, Any]
    assert sig.return_annotation == Dict[str, Any]

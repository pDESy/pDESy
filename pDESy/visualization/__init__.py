#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Visualization submodule for pDESy.

This submodule provides visualization functionality using matplotlib, plotly, and networkx.
It is separated from the core pDESy package to avoid mandatory dependencies
on visualization libraries (matplotlib, plotly, kaleido).

To use visualization features, install pDESy with the visualization extra:
    pip install pdesy[vis]

Or install the required dependencies manually:
    pip install matplotlib plotly kaleido networkx
"""

# Check if visualization dependencies are available
_VISUALIZATION_AVAILABLE = True
_MISSING_DEPS = []

try:
    import matplotlib.pyplot as plt  # noqa: F401
except ImportError:
    _VISUALIZATION_AVAILABLE = False
    _MISSING_DEPS.append("matplotlib")

try:
    import plotly.graph_objects as go  # noqa: F401
    import plotly.figure_factory as ff  # noqa: F401
except ImportError:
    _VISUALIZATION_AVAILABLE = False
    _MISSING_DEPS.append("plotly")

try:
    import networkx as nx  # noqa: F401
except ImportError:
    _VISUALIZATION_AVAILABLE = False
    _MISSING_DEPS.append("networkx")

# Note: kaleido is only required for static image export with plotly
# We check for it but don't add it to _VISUALIZATION_AVAILABLE as it's optional
_KALEIDO_AVAILABLE = True
try:
    import kaleido  # noqa: F401
except ImportError:
    _KALEIDO_AVAILABLE = False


def check_visualization_available():
    """Check if visualization dependencies are available.
    
    Raises:
        ImportError: If visualization dependencies are not installed.
    """
    if not _VISUALIZATION_AVAILABLE:
        raise ImportError(
            f"Visualization dependencies are not installed: {', '.join(_MISSING_DEPS)}. "
            "Please install them with: pip install pdesy[vis] "
            "or: pip install matplotlib plotly networkx kaleido"
        )

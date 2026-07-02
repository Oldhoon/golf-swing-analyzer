from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


def test_main_invokes_streamlit() -> None:
    with patch("subprocess.call", return_value=0) as call:
        from swing_analyzer.__main__ import main

        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        assert call.called


def test_main_script_entrypoint() -> None:
    main_path = Path(__file__).resolve().parents[2] / "src/swing_analyzer/__main__.py"
    with patch("subprocess.call", return_value=0):
        import runpy

        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(main_path), run_name="__main__")
        assert exc.value.code == 0

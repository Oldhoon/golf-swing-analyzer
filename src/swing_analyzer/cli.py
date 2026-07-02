from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from swing_analyzer.config.settings import load_settings
from swing_analyzer.diagnostics.report import report_to_json
from swing_analyzer.diagnostics.runner import exit_code_for_status, run_diagnostics
from swing_analyzer.logging.setup import configure_logging, get_logger
from swing_analyzer.models.diagnostic import OverallStatus

app = typer.Typer(
    name="swing-analyzer",
    help="Golf Swing Analyzer environment diagnostics and configuration",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback()
def cli_root() -> None:
    """Golf Swing Analyzer CLI."""


@app.command("diagnose")
def diagnose(
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Optional TOML config file override"),
    ] = None,
    pretty: Annotated[
        bool,
        typer.Option("--pretty", help="Pretty-print JSON output"),
    ] = False,
) -> None:
    """Run environment capability checks and print JSON to stdout."""
    try:
        settings = load_settings(config_file=config)
        configure_logging(settings)
        logger = get_logger("swing_analyzer.cli")
        report = run_diagnostics(settings)
        typer.echo(report_to_json(report, pretty=pretty))

        if report.overall_status == OverallStatus.FAIL:
            for check in report.checks:
                if check.status.value == "fail":
                    logger.error(
                        "capability_check_failed",
                        operation="diagnose",
                        capability=check.name.value,
                        message=check.message,
                        remediation=check.remediation,
                    )

        code = exit_code_for_status(report.overall_status)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        typer.echo(f"internal error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    else:
        raise typer.Exit(code=code)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

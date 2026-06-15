"""
Offline-mode support for in-house / air-gapped deployments.

When offline mode is enabled, Serena performs **no outbound network access**:

* usage statistics reporting is disabled (see :meth:`SerenaAgent._send_usage_info`),
* the dashboard news feed is not fetched and the web dashboard is not started,
* language servers are **not** auto-downloaded/installed; instead an informative
  error with manual installation guidance is raised,
* the Anthropic-based token estimator is unavailable (the build never calls the
  Anthropic API).

Offline mode is controlled by the ``SERENA_OFFLINE`` environment variable.
Accepted truthy values (case-insensitive): ``1``, ``true``, ``yes``, ``on``.

This module deliberately has no third-party dependencies so that it can be
imported from both the ``serena`` and ``solidlsp`` packages without creating
import cycles.
"""

import os

OFFLINE_ENV_VAR = "SERENA_OFFLINE"
"""Name of the environment variable that toggles offline mode."""

_TRUTHY_VALUES = frozenset({"1", "true", "yes", "on"})


def is_offline_mode() -> bool:
    """
    :return: whether Serena is running in offline mode (no outbound network access),
        as determined by the ``SERENA_OFFLINE`` environment variable.
    """
    return os.getenv(OFFLINE_ENV_VAR, "false").strip().lower() in _TRUTHY_VALUES


def raise_if_offline(context: str) -> None:
    """
    Raises a :class:`RuntimeError` with installation guidance if offline mode is enabled.

    :param context: a human-readable description of the network operation that was
        about to be attempted (e.g. the URL or the language server name).
    """
    if is_offline_mode():
        raise RuntimeError(offline_guidance(context))


def offline_guidance(context: str) -> str:
    """
    Builds an informative, user-facing message explaining that a network operation
    was skipped because offline mode is enabled, including how to proceed.

    :param context: a human-readable description of the blocked network operation.
    :return: the guidance message.
    """
    return (
        f"Offline mode is enabled (environment variable {OFFLINE_ENV_VAR}); "
        f"refusing to perform network access for: {context}.\n"
        "Serena will not download or install anything automatically in offline mode.\n"
        "To proceed, either:\n"
        "  1. Install the required component manually (see the URL(s)/package name above) "
        "and make it available on PATH or at the expected install location, or\n"
        f"  2. Disable offline mode by unsetting the {OFFLINE_ENV_VAR} environment variable "
        "(or setting it to 'false') to allow automatic installation."
    )

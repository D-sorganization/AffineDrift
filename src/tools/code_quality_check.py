#!/usr/bin/env python3
"""Quality check script to verify AI-generated code meets standards.

.. deprecated::
    This file is a backward-compatibility shim.  All logic has been
    moved to the ``src.tools.code_quality`` package (Phase 3.1).

    Import directly from the package instead::

        from src.tools.code_quality import check_file, main
        from src.tools.code_quality import check_banned_patterns
        from src.tools.code_quality import check_ast_issues
"""

import logging

from src.tools.code_quality import (  # noqa: F401
    Colors,
    check_ast_issues,
    check_banned_patterns,
    check_file,
    check_magic_numbers,
    is_legitimate_pass_context,
    main,
)

# Re-export configuration constants for callers that accessed them directly
from src.tools.code_quality.pattern_checker import (  # noqa: F401
    ALLOWED_CONSTANTS,
    BANNED_PATTERNS,
    MAGIC_NUMBERS,
    PASS_PATTERNS,
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    main()

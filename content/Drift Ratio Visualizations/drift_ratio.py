
Skip to content
Navigation Menu
D-sorganization
Gasification_Model

Code
Issues
Pull requests 1
Actions
Projects
Security
Insights

    Settings

Back to pull request #187
fix(ruff): Remove global ICN003 ignore and add per-file exceptions #418

Jobs

Run details

Annotations
1 error
Lint and Format
failed 1 minute ago in 50s
1s
1s
3s
3s
2s
2s
21s
21s
19s
19s
1s
Run isort --check-only --diff --profile black --line-length 100 python/
ERROR: /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py Imports are incorrectly sorted and/or formatted.
--- /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py:before	2025-11-29 17:54:12.983069
+++ /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py:after	2025-11-29 17:54:56.486831
@@ -18,9 +18,9 @@
 import os
 import shutil
 import tempfile
+from collections.abc import Iterable
 from contextlib import suppress
 from dataclasses import dataclass
-from collections.abc import Iterable
 from datetime import datetime
 from pathlib import Path
 from typing import Any
Error: Process completed with exit code 1.
1s
Run isort --check-only --diff --profile black --line-length 100 python/
ERROR: /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py Imports are incorrectly sorted and/or formatted.
--- /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py:before	2025-11-29 17:54:12.983069
+++ /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py:after	2025-11-29 17:54:56.486831
@@ -18,9 +18,9 @@
 import os
 import shutil
 import tempfile
+from collections.abc import Iterable
 from contextlib import suppress
 from dataclasses import dataclass
-from collections.abc import Iterable
 from datetime import datetime
 from pathlib import Path
 from typing import Any
Error: Process completed with exit code 1.
Run isort --check-only --diff --profile black --line-length 100 python/
ERROR: /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py Imports are incorrectly sorted and/or formatted.
--- /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py:before	2025-11-29 17:54:12.983069
+++ /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py:after	2025-11-29 17:54:56.486831
@@ -18,9 +18,9 @@
 import os
 import shutil
 import tempfile
+from collections.abc import Iterable
 from contextlib import suppress
 from dataclasses import dataclass
-from collections.abc import Iterable
 from datetime import datetime
 from pathlib import Path
 from typing import Any
1s
Run isort --check-only --diff --profile black --line-length 100 python/
ERROR: /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py Imports are incorrectly sorted and/or formatted.
--- /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py:before	2025-11-29 17:54:12.983069
+++ /home/runner/work/Gasification_Model/Gasification_Model/python/integrated_process_simulator/ui/tabs/process_summary_tab.py:after	2025-11-29 17:54:56.486831
@@ -18,9 +18,9 @@
 import os
 import shutil
 import tempfile
+from collections.abc import Iterable
 from contextlib import suppress
 from dataclasses import dataclass
-from collections.abc import Iterable
 from datetime import datetime
 from pathlib import Path
 from typing import Any
Error: Process completed with exit code 1.
0s
0s
0s
0s
0s
0s
0s
0s
0s
0s
fix(ruff): Remove global ICN003 ignore and add per-file exceptions · D-sorganization/Gasification_Model@03cf5b5
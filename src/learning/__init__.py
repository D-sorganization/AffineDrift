"""Site index for UpstreamDrift learning modules covered by #5625 reference pages.

This package is documentation metadata only. Implementations live in UpstreamDrift at
``UPSTREAM_PIN``.
"""

UPSTREAM_PIN = "3afe09c1ed0247a459d16bf75cf0b28bb64f584a"

# Modules cited on articles/upstreamdrift-learning-analytics.qmd (issue #5625).
RL_ENV_MODULES: tuple[str, ...] = (
    "src/learning/rl/configs.py",
    "src/learning/rl/humanoid_envs.py",
)

SIM2REAL_MODULES: tuple[str, ...] = ("src/learning/sim2real/domain_randomization.py",)

IMITATION_MODULES: tuple[str, ...] = (
    "src/learning/imitation/_bc.py",
    "src/learning/imitation/_dagger.py",
    "src/learning/imitation/_gail.py",
    "src/learning/retargeting/retargeter.py",
)

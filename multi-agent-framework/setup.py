"""
Packages this directory as the importable `atlas_assistant` package, so downstream
code (e.g. platform/backend) can depend on it without needing a matching directory name.
"""

from setuptools import setup

with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f
        if line.strip() and not line.strip().startswith("#")
    ]

setup(
    name="atlas_assistant",
    version="0.1.0",
    description="ProjAtlas multi-agent framework (paper interpretation, neuron selection, "
                "brain visualization, and textual summarization agents)",
    package_dir={"atlas_assistant": "."},
    packages=[
        "atlas_assistant",
        "atlas_assistant.function_calling",
        "atlas_assistant.summarization",
    ],
    install_requires=requirements,
    python_requires=">=3.10",
)

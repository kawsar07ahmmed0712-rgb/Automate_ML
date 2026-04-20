    from setuptools import setup, find_packages
    from pathlib import Path

    BASE_DIR = Path(__file__).parent
    README = (BASE_DIR / "README.md").read_text(encoding="utf-8")

    def read_requirements(path: str) -> list[str]:
        req_path = BASE_DIR / path
        if not req_path.exists():
            return []
        lines = []
        for line in req_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
        return lines

    setup(
        name="audit-engine",
        version="0.1.0",
        description="Column-level data audit engine for master reports and feature-engineering reports",
        long_description=README,
        long_description_content_type="text/markdown",
        author="Your Name",
        python_requires=">=3.10",
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        include_package_data=True,
        install_requires=read_requirements("requirements.txt"),
        extras_require={
            "profiling": ["ydata-profiling>=4.9"],
            "advanced": ["deepchecks>=0.19", "pyod>=2.0", "ftfy>=6.3", "dateparser>=1.2"],
            "web": ["streamlit>=1.44"],
            "dev": ["pytest>=8.2", "pytest-cov>=5.0", "ruff>=0.6", "mypy>=1.11"],
        },
        entry_points={
            "console_scripts": [
                "audit-engine=audit_engine.cli:main",
            ]
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
    

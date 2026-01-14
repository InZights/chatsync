"""Setup configuration for Teams to Slack Migration Pipeline"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="teams-to-slack-migration",
    version="1.0.0",
    author="Data Pipeline Team",
    author_email="team@example.com",
    description="Production-grade migration tool for Teams to Slack conversations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/teams-to-slack",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
    install_requires=[
        "slack-sdk>=3.23.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "teams-to-slack=teams_to_slack.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

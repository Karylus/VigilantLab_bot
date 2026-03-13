"""Setup configuration for WATCHMAN bot."""

from setuptools import setup

setup(
    name="watchman",
    version="1.0.0",
    description="Home Lab Security Monitor Bot - Telegram bot for remote system monitoring and security auditing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="WATCHMAN Contributors",
    license="Apache-2.0",
    url="https://github.com/yourusername/WATCHMAN",
    packages=["src", "src.commands", "src.config", "src.handlers", "src.services", "src.utils"],
    package_dir={"": "."},
    python_requires=">=3.11",
    install_requires=[
        "python-telegram-bot>=22.5",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0",
            "isort>=5.0",
            "mypy>=1.0",
            "ruff>=0.1.0",
            "coverage>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: Spanish",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    keywords=[
        "telegram",
        "bot",
        "security",
        "monitoring",
        "home-lab",
    ],
    entry_points={
        "console_scripts": [
            "watchman=src.main:main",
        ],
    },
)

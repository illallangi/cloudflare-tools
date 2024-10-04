from setuptools import setup, find_packages

setup(
    name="cloudflare_tools",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "appdirs",
        "Click",
        "requests_cache",
        "yarl",
    ],
    entry_points={
        "console_scripts": [
            "cloudflare-account=cloudflare_tools.scripts.cloudflare_account:cli",
        ],
    },
)

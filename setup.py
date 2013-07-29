from setuptools import setup

try:
    with open("README.md") as readmefile:
        long_description = readmefile.read()
except IOError:
    long_description = ""

setup(
    name = "PsiTurk",
    version = "1.0b1",
    packages = ["psiturk"],
    include_package_data = True,
    zip_safe = False,
    entry_points = {
        'console_scripts': [
            'psiturk = psiturk.dashboard_server:launch',
            'psiturk-dashboard = psiturk.dashboard_server:launch',
            'psiturk-server = psiturk.experiment_server:launch',
            'psiturk-setup-example = psiturk.setup_example:setup_example'
        ]
    },
    setup_requires = [],
    install_requires = ["argparse", "Flask", "SQLAlchemy", "gunicorn", "boto>=2.9"],
    author = "NYU Computation and Cognition Lab",
    author_email = "http://nyuccl.org",
    description = "A web framework for dynamic behavioral experiments",
    long_description = long_description,
    url = "http://github.com/NYUCCL/psiturk"
)


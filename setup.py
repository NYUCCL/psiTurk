from setuptools import setup

setup(
    name = "PsiTurk",
    version = "1.0a1",
    packages = ["psiturk"],
    include_package_data = True,
    zip_safe = False,
    entry_points = {
        'console_scripts': [
            'psiturk = psiturk.dashboard_server:launch',
            'psiturk-dashboard = psiturk.dashboard_server:launch',
            'psiturk-server = psiturk.psiturk_server:launch',
            'psiturk-setup-example = psiturk.setup_example:setup_example'
        ]
    },
    setup_requires = [],
    install_requires = ["argparse", "Flask", "SQLAlchemy", "gunicorn", "boto>=2.9"],
    author = "NYU Computation and Cognition Lab",
    author_email = "http://nyuccl.org",
    description = "A web framework for dynamic behavioral experiments",
    url = "http://github.com/NYUCCL/psiturk"
)


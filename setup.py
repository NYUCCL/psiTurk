from setuptools import setup

setup(
    name = "PsiTurk",
    version = "0.1",
    packages = ["psiturk"],
    entry_points = {
        'console_scripts': ['psiturk = psiturk.launch:launch']
    },
    setup_requires = [],
    install_requires = ["Flask", "boto", "SQLAlchemy", "gevent", "gevent-socketio", "gunicorn", "iso8601"],
    extras_require = {},
    author = "NYU Computation and Cognition Lab",
    author_email = "http://nyuccl.org",
    description = "A web framework for dynamic behavioral experiments",
    url = "http://github.com/NYUCCL/psiturk"
)


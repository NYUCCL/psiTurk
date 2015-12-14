import sys
from setuptools import setup
from psiturk.version import version_number

try:
    with open("README.md") as readmefile:
        readme_text = readmefile.readlines()
        long_description = ''
        for line in readme_text:
            if line[0]!='<' and line[0]!='[': # drop lines that are html/markdown
                long_description += line
except IOError:
    long_description = ""


if __name__ == "__main__":
    # remove file if it exists and re-write with current version number
    fp = open('psiturk/version.py',"w+")
    fp.write("version_number = '%s'\n" % version_number)
    fp.flush()
    fp.close()

    setup_args = dict(
        name = "PsiTurk",
        version = version_number,
        packages = ["psiturk"],
        include_package_data = True,
        zip_safe = False,
        entry_points = {
            'console_scripts': [
                'psiturk-shell = psiturk.psiturk_shell:run',
                'psiturk = psiturk.command_line:process',
                'psiturk-server = psiturk.command_line:process',
                'psiturk-setup-example = psiturk.command_line:process',
                'psiturk-install = psiturk.command_line:process'
            ]
        },
        setup_requires = [],
        author = "NYU Computation and Cognition Lab",
        author_email = "authors@psiturk.org",
        description = "An open platform for science on Amazon Mechanical Turk",
        long_description = long_description,
        url = "http://github.com/NYUCCL/psiturk",
        test_suite='test_psiturk'
    )

    # read in requirements.txt for dependencies
    setup_args['install_requires'] = install_requires = []
    with open('requirements.txt') as f:
        for line in f.readlines():
            req = line.strip()
            if not req or req.startswith('#'): # ignore comments
                continue
            else:
                install_requires.append(req)

    # add readline only on osx
    if sys.platform == 'darwin':
        install_requires.append('gnureadline==6.3.3')

    setup(**setup_args)

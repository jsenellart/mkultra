import re
import subprocess

site_dir = 'site'


def build():
    subprocess.check_call(['mkdocs', 'build'])


def version():
    output = subprocess.check_output(['mkdocs', '--version'])
    m = re.search('^mkdocs, version (.*)$', output)
    return m.group(1)

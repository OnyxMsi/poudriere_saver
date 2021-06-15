from setuptools import setup, find_packages

setup(
    name="poudriere_saver",
    version="0.1",
    entry_points={"console_scripts": ["poudsaver = poudriere_saver.ps:main"]},
    description="Poudriere configuration to YAML file and back",
    url="http://github.com/onyxmsi/poudriere_saver",
    author="Guillaume Pelure",
    author_email="onyxmsi@laposte.com",
    license="GPL",
    packages=find_packages(),
    install_requires=("pyyaml", "ply", "attrs"),
    py_modules="poudriere_saver",
    zip_safe=False,
)

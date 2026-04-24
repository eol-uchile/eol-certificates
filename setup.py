import setuptools

setuptools.setup(
    name="eol_certificates",
    version="0.0.1",
    author="Oficina EOL UChile",
    author_email="eol-ing@uchile.cl",
    description="EOL Certificates",
    long_description="EOL Certificates",
    url="https://github.com/eol-uchile/eol_certificates",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "lms.djangoapp": [
            "eol_certificates = eol_certificates.apps:EolCertificateConfig",
        ]
    },
)

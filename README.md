# Eol api

![Coverage Status](/coverage-badge.svg)

![https://github.com/eol-uchile/eol-certificates/actions](https://github.com/eol-uchile/eol-certificates/workflows/Python%20application/badge.svg)

Allows to validate a certificate, showing a html to enter a uuid

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/eol_certificates

# Translations:
To add new words to be translated you need to follow these steps.
1. Create the container where the commands will be run:
    ```
    docker run -it --rm -w /code -v $(pwd):/code python:3.8 bash
    ```

2. Install the requirements:
    ```
    pip install -r requirements-i18n.in
    ```

3. Update the translations:

    ```
    make update_translations
    ```

4. Modify .po:
> [!WARNING]
> REMEMBER: Remember to add the Spanish translation.

5. Compile the modified .po into .mo
    ```
    make compile_translations
    ```

## TESTS
**Prepare tests:**

- Install **act** following the instructions in [https://nektosact.com/installation/index.html](https://nektosact.com/installation/index.html)

**Run tests:**
- In a terminal at the root of the project
    ```
    act -W .github/workflows/pythonapp.yml
    ```

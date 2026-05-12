# Eol api

![Coverage Status](/coverage-badge.svg)

![https://github.com/eol-uchile/eol-certificates/actions](https://github.com/eol-uchile/eol-certificates/workflows/Python%20application/badge.svg)

Allows to validate a certificate, showing a html to enter a uuid

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/eol_certificates


# Install Theme

To enable the export issued certificates button, add the following code to your theme. This includes a conditional check to ensure the template only renders if the app is installed.

- _../themes/your_theme/lms/templates/instructor/instructor_dashboard_2/data_download.html_

    **add eol_report_certificate template to the data_download template**

        <%
        eolreportcertificate_url = None
        eolreportcertificate_traceback = None
        try:
          eolreportcertificate_url = reverse('eol_certificates:issued_certificates')
        except Exception:
          if settings.DEBUG:
            eolreportcertificate_traceback = traceback.format_exc()
        %>  
        %if eolreportcertificate_traceback:
          <div class="eolreportcertificate_traceback">
          <pre>${eolreportcertificate_traceback}</pre>
          </div>
        %elif eolreportcertificate_url:
          <%include file="eol_report_certificate.html"/>
        %endif

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

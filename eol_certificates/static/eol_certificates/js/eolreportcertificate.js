function generate_eolreportcertificate(input){
    cleanEolReportCertificate()
    var success_div = document.getElementById('eolreportcertificate-success-msg');
    var error_div = document.getElementById('eolreportcertificate-error-msg');
    var warning_div = document.getElementById('eolreportcertificate-warning-msg');
    var post_url = input.dataset.endpoint;
    $.ajax({
        dataType: 'json',
        type: 'GET',
        url: post_url,
        success: function(data) {
            if (data["status"] == 'Generating'){
              success_div.textContent = gettext("The report is being generated and will be available for download shortly.");
              success_div.style.display = "block";
            }
            if (data["status"] == 'AlreadyRunningError'){
              warning_div.textContent = gettext("The report is being generated. Please wait.")
              warning_div.style.display = "block";
            }
            if (data["status"] == 'Error'){
                return EolReportCertificateDataError(data);
            }
        },
        error: function() {
            error_div.textContent = gettext("An error occurred during export. Please refresh the page and try again. If the error persists, please contact support (eol-ayuda@uchile.cl).")
            error_div.style.display = "block";
        }
    })
}
function cleanEolReportCertificate(){
    document.getElementById('eolreportcertificate-success-msg').style.display = "none";
    document.getElementById('eolreportcertificate-success-msg').textContent = "";
    document.getElementById('eolreportcertificate-error-msg').style.display = "none";
    document.getElementById('eolreportcertificate-error-msg').textContent = "";
    document.getElementById('eolreportcertificate-warning-msg').style.display = "none";
    document.getElementById('eolreportcertificate-warning-msg').textContent = "";
}
function EolReportCertificateDataError(data){
    var error_msg = document.getElementById('eolreportcertificate-error-msg');
    if (data['user_permission']){
      error_msg.textContent = gettext("The user does not have permission to perform this action.");
    }
    else{
      error_msg.textContent = gettext("An error occurred during export. Please refresh the page and try again. If the error persists, please contact support (eol-ayuda@uchile.cl).")
    }
    
    error_msg.style.display = "block";
}

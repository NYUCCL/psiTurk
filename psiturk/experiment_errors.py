# ----------------------------------------------
# ExperimentError Exception, for db errors, etc.
# ----------------------------------------------
# Possible ExperimentError values.
from __future__ import generator_stop
from flask import render_template


def unwrap(string):
    return " ".join([x.strip() for x in string.split("\n")]).strip()


class ExperimentError(Exception):
    """
    Error class for experimental errors, such as subject not being found in
    the database.
    """

    experiment_errors = dict(
        status_incorrectly_set=1000,
        hit_assign_worker_id_not_set_in_mturk=1001,
        hit_assign_worker_id_not_set_in_consent=1002,
        hit_assign_worker_id_not_set_in_exp=1003,
        hit_assign_appears_in_database_more_than_once=1004,
        already_started_exp=1008,
        already_started_exp_mturk=1009,
        already_did_exp_hit=1010,
        tried_to_quit=1011,
        intermediate_save=1012,
        improper_inputs=1013,
        browser_type_not_allowed=1014,
        api_server_not_reachable=1015,
        ad_not_found=1016,
        error_setting_worker_complete=1017,
        hit_not_registered_with_ad_server=1018,
        template_unsafe=1019,
        insert_mode_failed=1020,
        page_not_found=404,
        in_debug=2005,
        unknown_error=9999
    )

    error_descriptions = dict()
    error_descriptions['status_incorrectly_set'] = unwrap(
        """
        Participant tried to access the ad, but their status in the database
        isn't something I know how to handle.
        """)

    error_descriptions['hit_assign_worker_id_not_set_in_mturk'] = unwrap(
        """
        Either the HIT id or the assignment id were not provided in the URL for
        the ad page.
        """)

    error_descriptions['hit_assign_worker_id_not_set_in_consent'] = unwrap(
        """
        Either the HIT id, the assignment id, or the worker id were not
        provided in the URL for the consent form page.
        """)

    error_descriptions['hit_assign_worker_id_not_set_in_exp'] = unwrap(
        """
        Either the HIT id, the assignment id, the worker id, or the mode were
        not provided in the URL for the experiment page.
        """)

    error_descriptions['hit_assign_appears_in_database_more_than_once'] = unwrap(
        """
        The requested HIT or assignment appears in the database more than once.
        """)

    error_descriptions['already_started_exp'] = unwrap(
        """
        The experiment was requested, but cannot be continued because it was
        already started and ended prematurely.
        """)

    error_descriptions['already_started_exp_mturk'] = unwrap(
        """
        The ad was requested, but the experiment cannot be continued because it
        was already started and ended prematurely.
        """)

    error_descriptions['already_did_exp_hit'] = unwrap(
        """
        The experiment has already been completed.
        """)

    error_descriptions['tried_to_quit'] = unwrap(
        """
        The experiment was ended prematurely and something went wrong while
        writing to the database.
        """)

    error_descriptions['improper_inputs'] = unwrap(
        """
        The uniqueId was not provided in the URL, but it is required.
        """)

    error_descriptions['browser_type_not_allowed'] = unwrap(
        """
        The browser you are using is not allowed by this experiment.
        """)

    error_descriptions['api_server_not_reachable'] = unwrap(
        """
        The psiTurk API server is unreachable.
        """)

    error_descriptions['error_setting_worker_complete'] = unwrap(
        """
        The experiment was completed but something went wrong while writing to
        the database.
        """)

    error_descriptions['hit_not_registered_with_ad_server'] = unwrap(
        """
        The requested HIT is not registered with the psiTurk ad server.
        """)

    error_descriptions['insert_mode_failed'] = unwrap(
        """
        Failed to insert the 'mode' query string argument in the URL.
        """)

    error_descriptions['page_not_found'] = unwrap(
        """
        The requested page does not exist.
        """)

    error_descriptions['intermediate_save'] = ""
    error_descriptions['ad_not_found'] = ""
    error_descriptions['template_unsafe'] = ""
    error_descriptions['in_debug'] = ""
    error_descriptions['unknown_error'] = ""

    def __init__(self, value):
        self.value = value
        self.errornum = self.experiment_errors[self.value]
        self.errordesc = self.error_descriptions[self.value]
        self.template = "error.html"

    def __str__(self):
        return repr(self.value)

    def error_page(self, request, contact_on_error):
        return render_template(
            self.template,
            errornum=self.errornum,
            errordesc=self.errordesc,
            contact_address=contact_on_error,
            **request.args)


class ExperimentApiError(Exception):

    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class InvalidUsageError(ExperimentApiError):

    def __init__(self, *args, **kwargs):
        if 'status_code' not in kwargs:
            kwargs['status_code'] = 400
        super(InvalidUsageError, self).__init__(*args, **kwargs)

class InvalidUsage(InvalidUsageError):
    # backwards compatibility with psiturk v2's custom.py files
    # generated by psiturk-setup-example
    pass

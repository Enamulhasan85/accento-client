from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    # TODO (wasim) HIGH: Override send_mail method to process in background
    pass

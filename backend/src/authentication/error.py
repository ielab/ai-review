class CustomError(Exception):
    pass

class CustomErrorAsDict(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict
        super().__init__(str(error_dict))

    def __getattr__(self, name):
        if name in self.error_dict:
            return self.error_dict[name]
        else:
            # If the requested attribute is not in the error_dict, raise AttributeError
            raise AttributeError(f"'CustomException' object has no attribute '{name}'")


class SmsError(Exception):
    pass

class ContentSmsError(Exception):
    pass

class ValidationError(Exception):
    pass

def make_i18n_keyword(message):
    """
    Make i18n keyword from message (ex: 'Hello World' -> 'helloWorld')
    """
    capitalized_messages = list(map(lambda m: m.capitalize(), message.split(' ')))
    capitalized_messages[0] = capitalized_messages[0].lower()
    return f"error.{''.join(capitalized_messages)}"
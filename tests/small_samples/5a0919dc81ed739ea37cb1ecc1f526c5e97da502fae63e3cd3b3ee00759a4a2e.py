
def http_error(status):
        match status:
            case 400:
                return 'Bad request'
            case 401 | 404:
                return 'Not allowed'
            case 418:
                return "I'm a teapot"



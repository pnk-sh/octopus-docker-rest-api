code_list = {
    # Code 1xx - Validation errors
    100: 'image name need in body data'
}

def get_error(code: int):
    return code_list.get(code)
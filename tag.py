import json


class ApiTag:
    FILEUPLOAD = 'fileupload'
    AUTH= 'authentication'
    USER_PROFILE = 'user profile'
    IDENTITY = 'identity'


def analyze_tag(path, method, yaml_data):
    """
    Analyze the tags of the API Entry

    Parameters
    ----------
    path: str
        Path of the API
    method: str
        Method of the API
    yaml_data: dict
        The yaml data of the swagger file

    Returns
    -------
    tags: list
        List of tags
    """
    tags = []

    check_data = yaml_data['paths'][path][method]
    try:
        check_str = json.dumps(check_data)
    except:
        check_str = None
        

    # file upload
    if method == 'PUT' or method == 'POST':
         tags.append(ApiTag.FILEUPLOAD)

    # authorization and authentication 
    if any(word.lower() in path or word.lower() in check_str for word in ['auth','token','login','logout','password','credential','key']):
        tags.append(ApiTag.AUTH)

    # user profile
    if any(word.lower() in path or word.lower() in check_str for word in ['user','profile','account','firstname','lastname','email', 'info']):
        tags.append(ApiTag.USER_PROFILE)

    # identity
    if any(word.lower() in path or word.lower() in check_str for word in ['identity','id','uuid']):
        tags.append(ApiTag.IDENTITY)

    return tags





import yaml
import json


def generate_auth(swfile, api_type = None):
    if '.yaml' in swfile:
        with open(swfile, 'r') as file:
            swagger_data = yaml.safe_load(file)
    elif '.json' in swfile:
        with open(swfile) as file:
            swagger_data = json.load(file)
    else:
        raise ValueError("Only swagger.yaml or swagger.json are allowed")


    # Default value
    security_schemes = {
                        "username": {
                            "value": "PLEASE_ENTER_YOUR_VALUE"
                        },
                        "password": {
                            "value": "PLEASE_ENTER_YOUR_VALUE"
                        },
                        "ID":{
                            "value": "PLEASE_ENTER_YOUR_VALUE"
                        }
                        }

    # read from swagger
    if 'securitySchemes' in swagger_data['components']:
        for scheme_name, scheme_data in swagger_data['components']['securitySchemes'].items():
            security_schemes[scheme_name] = scheme_data
            security_schemes[scheme_name]['value'] = "PLEASE_ENTER_YOUR_VALUE"

    # Based on API type 
    IBM_data = {
        "x-ibm-client-id": {
        "type": "parameters",
        "name": "x-ibm-client-id",
        "in" : "header",
        "value": "PLEASE_ENTER_YOUR_VALUE"
        },
        "x-ibm-client-secret": {
        "type": "parameters",
        "name": "x-ibm-client-secret",
        "in" : "header",
        "value": "PLEASE_ENTER_YOUR_VALUE"
        }}
    Azure_data = {}
    #  https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md Use Oath2.0 and http bearer

    AWS_data = {
        "x-amazon-apigateway-authorizer": {
        "value": "PLEASE_ENTER_YOUR_VALUE"
        }}

    if api_type == "IBM":
        security_schemes.update(IBM_data)
    elif api_type == 'Azure':
        security_schemes.update(Azure_data)
    elif api_type == 'AWS':
        security_schemes.update(AWS_data)

    # Save the extracted security schemes to a JSON file
    output_filename = 'security_schemes_output.json'
    with open(output_filename, 'w') as output_file:
        json.dump(security_schemes, output_file, indent=2)



if __name__ == '__main__':
    generate_auth('openapi.json','IBM')
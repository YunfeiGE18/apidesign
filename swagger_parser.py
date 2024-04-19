import json
import yaml
from api_entry import ApiEntry
from tag import analyze_tag
from generate_auth_file import generate_auth


class SwaggerParser:
    """

    The SwaggerParser class tries to parse the swagger file.
    
    Attributes
    ----------
    swagger_file: str 
        Path to the swagger_file (yaml or json)
    version:
        OpenAPI version (2 or 3)
    """
    def __init__(self, 
                 swagger_file: str, 
                 version: int,
                 api_type: str = None):
        self.swagger_file = swagger_file
        self.version = version
        self.api_type = api_type


    def parse_swagger(self):

        if '.yaml' in self.swagger_file:
            with open(self.swagger_file, 'r') as file:
                yaml_data = yaml.safe_load(file)
        elif '.json' in self.swagger_file:
            with open(self.swagger_file) as file:
                yaml_data = json.load(file)
        else:
            raise ValueError("Only swagger.yaml or swagger.json are allowed")
        

        if self.version == 2:
            return self.parse_swagger_2(yaml_data)
        elif self.version == 3:
            return self.parse_swagger_3(yaml_data)
        else:
            raise  ValueError("Only OpenAPI version 2 or version 3 are allowded.")
    

    def parse_swagger_3(self, yaml_data):

        # get base url
        try:
            base_url = yaml_data['servers'][0]['url']
        except KeyError:
            raise KeyError("No URL provided")
        
        api_entry = []
    
        for path, path_data in yaml_data['paths'].items():
            for method in path_data.keys():
                header_parameter, body_parameter, query_parameter, securitySchemes, response_data = self.analyze_parameters_3(path, method, yaml_data)
                tags = analyze_tag(path, method, yaml_data)
                api_entry.append(ApiEntry(base_url, path, method, header_parameter, body_parameter, query_parameter, securitySchemes, response_data, tags))
        return api_entry


    def analyze_parameters_3(self, path, method, yaml_data):
        method_data = yaml_data['paths'][path][method]

        header_parameter = []
        body_parameter = {}
        query_parameter = []
        securitySchemes = []
        response_data = {}

        if 'parameters' in method_data:
            for parameter in method_data['parameters']:
                # get ref details
                if parameter['schema']['type'] == 'array':
                    if '$ref' in parameter['schema']['items']:
                        ref = parameter['schema']['items']['$ref']
                        para_schema = self.get_referenced_schema_3(yaml_data,ref)
                        parameter['schema']['items']['referenced_schema'] = para_schema
                elif '$ref' in parameter['schema']:
                    ref = parameter['schema']['$ref']
                    para_schema = self.get_referenced_schema_3(yaml_data,ref)
                    parameter['schema']['referenced_schema'] = para_schema

                if parameter['in'] == 'header' or parameter['in'] == 'cookie':
                    header_parameter.append(parameter)
                elif parameter['in'] == 'query':
                    query_parameter.append(parameter)

        if 'security' in method_data:
            securitySchemes = method_data['security']
        
        if 'requestBody' in method_data:
            request_body = method_data['requestBody']
            request_data = request_body['content']
            for content_type, form_details in request_data.items():
                if '$ref' in form_details['schema']:
                    ref = form_details['schema']['$ref']
                    body_schema = self.get_referenced_schema_3(yaml_data,ref)
                    form_details['schema']['referenced_schema'] = body_schema
                elif form_details['schema']['type'] == 'array':
                    if '$ref' in form_details['schema']['items']:
                        ref = form_details['schema']['items']['$ref']
                        body_schema = self.get_referenced_schema_3(yaml_data,ref)
                        form_details['schema']['items']['referenced_schema'] = body_schema
                body_parameter[content_type] = form_details


        if 'responses' in method_data:
            for status_code, response_data in method_data.get('responses', {}).items():
                # TODO: currently only consider 200 responses
                if status_code.startswith('2') and 'content' in response_data:
                    response_data[status_code] = response_data['content']
                    for content_type, content_details in response_data[status_code].items():
                        if '$ref' in content_details['schema']:
                            ref = content_details['schema']['$ref']
                            response_schema = self.get_referenced_schema_3(yaml_data,ref)
                            content_details['schema']['referenced_schema'] = response_schema
                        elif content_details['schema']['type'] == 'array':
                            if '$ref' in content_details['schema']['items']:
                                ref = content_details['schema']['items']['$ref']
                                response_schema = self.get_referenced_schema_3(yaml_data,ref)
                                content_details['schema']['items']['referenced_schema'] = response_schema
                        response_data[status_code][content_type] = content_details

        return header_parameter, body_parameter, query_parameter, securitySchemes, response_data


    def get_referenced_schema_3(self, yaml_data, ref):
        # Split the reference string to get the component and schema names
        _, _, _, schema = ref.split('/')
        # Retrieve the referenced schema from the components/schemas section
        referenced_schema = yaml_data['components']['schemas'][schema]

        return referenced_schema



    def generate_auth_file(self):
        generate_auth(self.swagger_file, self.api_type)


from tag import ApiTag
import json

class ApiEntry:

    def __init__(self, base_url, path, method, header_parameter = None, body_parameter = None, query_parameter = None, securitySchemes = None, response_data = None, tags = None):

        self.url = base_url
        self.path = path
        self.method = method
        self.header_parameter = header_parameter
        self.body_parameter = body_parameter
        self.query_parameter = query_parameter
        self.securitySchemes = securitySchemes
        self.response_data = response_data
        self.tags  = tags


    def get_base_url(self):
        return self.url
    
    def get_path(self):
        return self.path
    
    def get_method(self):
        return self.method
    
    def get_header_parameter(self):
        return self.header_parameter
    
    def get_body_parameter(self):
        return self.body_parameter
    
    def get_query_parameter(self):
        return self.query_parameter
    
    def get_securitySchemes(self):
        return self.securitySchemes
    
    def get_api_tags(self):
        return self.tags
    
    def get_response_data(self):
        return self.response_data
    


    def get_all_info(self):
        base_url = self.get_base_url()
        path = self.get_path()
        method = self.get_method()
        header_parameter = self.get_header_parameter()
        body_parameter = self.get_body_parameter()
        query_parameter = self.get_query_parameter()
        security_schemes = self.get_securitySchemes()
        tags = self.get_api_tags()
        response_data = self.get_response_data()
        
        # Create a dictionary object
        info = {
            "Base URL": base_url,
            "Path": path,
            "Method": method,
            "Header Parameter": header_parameter,
            "Body Parameter": body_parameter,
            "Query Parameter": query_parameter,
            "Security Schemes": security_schemes,
            "Tags": tags,
            "Response Data": response_data
        }
        
        # Convert the dictionary to JSON
        json_info = json.dumps(info)
        
        # Return the JSON object
        return json_info
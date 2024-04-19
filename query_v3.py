import yaml
import json


def read_swagger(swfile):
    """
    Input: swagger file (yaml or json)
    Output: json data
    """
    if '.yaml' in swfile:
        with open(swfile, 'r') as file:
            swagger_data = yaml.safe_load(file)
    elif '.json' in swfile:
        with open(swfile) as file:
            swagger_data = json.load(file)
    else:
        raise ValueError("Only swagger.yaml or swagger.json are allowed")
    
    return swagger_data

# path + method + query name

def query_object(swagger_data):

    query_list = []
    all_obj = {}


    # Login Info
    login_request = {}
    login_response = {}

    for path, path_data in swagger_data['paths'].items():
        for method, method_data in path_data.items():

            # record all queries
            if 'parameters' in method_data:
                for parameter in method_data['parameters']:
                    if parameter['in'] == 'query':
                        para_name = parameter['name']
                        query = path + ' ' + method + ' ' + para_name
                        query_list.append(query)
            


            # record all objects obtained from the output
            # TODO: do we need to record objects also from request or ref?
            for _ , response_data in method_data.get('responses', {}).items():
                if  'content' in response_data:
                    for _, content in response_data['content'].items():
                        if not content.get('schema'):
                            continue
                        schema  = content['schema']
                        # get ref and possible schema details
                        schema_details = []
                        if '$ref' in schema:
                            ref = schema['$ref']
                            schemaname, schema_details = get_referenced_schema(swagger_data,ref)
                        else:
                            schema_details = schema

                        if schema_details:
                            all_obj[path+' '+method] = schema_details



            # record all request info related to login
            if 'parameters' in method_data:
                for parameter in method_data['parameters']:
                    try:
                        check_data = json.dumps(parameter)
                    except:
                        check_data = None
                    if any(word.lower() in check_data for word in ['id','uuid','name','password','authorization','authentication','token','login','credential']):
                        login_request[path+' '+method] = parameter

            # record all response info related to login
            for _ , response_data in method_data.get('responses', {}).items():
                try:
                    check_out_data = json.dumps(response_data)
                except:
                    check_out_data = None
                if any(word.lower() in check_out_data for word in ['id','uuid','name','password','authorization','authentication','token','login','credential']):
                    login_response[path+' '+method] = response_data
        
            


    return query_list, all_obj, login_request, login_response



def get_referenced_schema(swagger_data, ref):
    # Split the reference string to get the component and schema names
    parts = ref.split('/')
    schemaname = parts[-1]
    # Retrieve the referenced schema from the components/schemas section
    referenced_schema = swagger_data['components']['schemas'][schemaname]

    return schemaname,referenced_schema





if __name__ == '__main__':
    import sys
    with open('openapi_query.txt', 'w') as f:
        sys.stdout = f  # Redirect stdout to the file


        data = read_swagger('openapi.json')

        print('------query------')
        query_list, all_obj, login_request, login_response = query_object(data)
        for query in query_list:
            print(query)
        
        print()
        print('------returned obj schema------')
        for key, obj in all_obj.items():
            print(key)
            print(obj)

        print()
        print('------login info (request)------')
        for key, obj in login_request.items():
            print(key)
            print(obj)
        
        print()
        print('------login info (request)------')
        for key, obj in login_response.items():
            print(key)
            print(obj)
        

    sys.stdout = sys.__stdout__


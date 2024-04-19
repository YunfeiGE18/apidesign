
import json
from rapidfuzz import fuzz
import itertools


def find_bussiness_logic(base_entry_list, level = 1): 
    

    # Generate dependency sequence
    dep_seq,dep_seq_names = generate_dep_seq(base_entry_list, level)
    crud_seq, crud_names = crud_logic_seq(base_entry_list)

    print('------Dependency K=3-------')
    for seq in dep_seq_names:
        print(seq)
    print()


    print('------CRUD Logic-------')
    for seq in crud_names:
        print(seq)
    print()


    set1 = set(dep_seq_names)
    set2 = set(crud_names)
    # Find the common strings using set intersection
    common_strings = set1.intersection(set2)
    # Print the common strings
    if common_strings:
        print("Common sequence found:")
        print()
        for string in common_strings:
            print(string)
    else:
        print("No common sequence")






def generate_dep_seq(base_entry_list, K = 1):
    # list of list of dict
    all_seq = []
    seq_names = []

    single_set = single_seq(base_entry_list)
    for req in single_set:
        com = req[0].get_path()+ ' ' + req[0].get_method()
        seq_names.append(com)

    all_seq.append(single_set)

    if K == 1:
        return all_seq, seq_names

    pre_set = single_set
    for i in range(1,K):
        new_set = []
        new_set = extend_one(base_entry_list, pre_set)
        if not new_set :
            print('No dependency found')
            return all_seq, seq_names
        else:
            all_seq.append(new_set)

            for seq in new_set:
                seq_name = ''
                for req in seq:
                    com = req.get_path()+ ' ' + req.get_method()
                    if seq_name == '':
                        seq_name = seq_name + com
                    else:
                        seq_name = seq_name + ' ---> ' +  com
                seq_names.append(seq_name)

            pre_set = new_set

    return all_seq, seq_names



def single_seq(base_entry_list):
    single_seq_set = []
    for item in base_entry_list:
        req = [item]
        single_seq_set.append(req)
    return single_seq_set



def extend_one(base_entry_list, pre_seq_set):
    new_seq_set = []

    for sequences in pre_seq_set:
        # extend the last request
        
        req = sequences[-1]
        output_names = get_output_info(req)

        # check next request
        for next_req in base_entry_list:
            if req == next_req:
                continue
            input_names = get_input_info(next_req)

            # Fuzzy compare for entry names
            for s1 in input_names:
                for s2 in output_names:
                    score = fuzz.ratio(s1,s2)
                    if score > 90:
                        new_sequences = sequences[:]
                        new_sequences.append(next_req)
                        new_seq_set.append(new_sequences)
            # # exact comparison
            # if output_ref.intersection(input_ref) or output_names.intersection(input_names):
            #     new_sequences = sequences[:]
            #     new_sequences.append(next_req)
            #     new_seq_set.append(new_sequences)

    return new_seq_set




def get_input_info(next_req):
    input_names = set()

    #  Use the function for header parameters
    header_input_names = process_parameters(next_req.get_header_parameter())

    # Use the function for query parameters
    query_input_names = process_parameters(next_req.get_query_parameter())


    # Use the function for request body parameters
    body_input_names = process_requestbody(next_req.get_body_parameter())

    input_names.update(header_input_names)
    input_names.update(query_input_names)
    input_names.update(body_input_names)


    return input_names


    

def get_output_info(req):

    # get the output names
    output_names = set()

    pre_output = req.get_response_data()
    if not pre_output:
        return output_names
    
    for content_type, content in pre_output.items():
        # TODO: currently only consider JSON    
        for media_type in ["application/json", "application/xml", "application/x-www-form-urlencoded"]:
            if content_type in media_type:
                schema = content[content_type].get('schema')
                break
        else:
            continue
        # get ref and possible schema details
        if schema:
            schema_details = []
            if '$ref' in schema:
                ref = schema['$ref']
                parts = ref.split('/')
                schemaname = parts[-1]
                output_names.add(schemaname.lower())
                schema_details = schema_details['referenced_schema']
            elif schema['type'] == 'array':
                if '$ref' in schema['items']:
                    ref = schema['items']['$ref']
                    parts = ref.split('/')
                    schemaname = parts[-1]
                    output_names.add(schemaname.lower())
                    schema_details  = schema['items']['referenced_schema']
            elif schema['type'] == 'object':
                schema_details = schema

            # extract all entry names
            if 'properties' in schema_details:
                prop_names = get_property_names(schema_details)
                output_names.update(prop_names)

    return output_names
    


def process_parameters(parameters):
    input_names = set()
    for parameter in parameters:
        input_names.add(parameter['name'].lower())
        if 'schema' in parameter:
            if 'type' in parameter['schema']:
                if parameter['schema']['type'] == 'array':
                    if '$ref' in parameter['schema']['items']:
                        ref = parameter['schema']['items']['$ref']
                        parts = ref.split('/')
                        schemaname = parts[-1]
                        input_names.add(schemaname.lower())
                        if 'properties' in parameter['schema']['items']['referenced_schema']:
                            prop_names = get_property_names(parameter['schema']['items']['referenced_schema'])
                            input_names.update(prop_names)
                    elif 'object' in parameter['schema']['items']:
                        prop_names = get_property_names(parameter['schema']['items'])
                        input_names.update(prop_names)
                elif '$ref' in parameter['schema']:
                    parts = ref.split('/')
                    schemaname = parts[-1]
                    input_names.add(schemaname.lower())
                    if 'properties' in parameter['schema']['referenced_schema']:
                        prop_names = get_property_names(parameter['schema']['referenced_schema'])
                        input_names.update(prop_names)
    return input_names



def process_requestbody(next_body):
    input_names = set()
    if next_body:
        for _, form_details in next_body.items():
            if '$ref' in form_details['schema']:
                ref = form_details['schema']['$ref']
                parts = ref.split('/')
                schemaname = parts[-1]
                input_names.add(schemaname.lower())
                if 'properties' in form_details['schema']['referenced_schema']:
                    prop_names = get_property_names(form_details['schema']['referenced_schema'])
                    input_names.update(prop_names)
            elif 'example' in form_details['schema']:
                entry_names = get_entry_names(form_details['schema']['example'])
                input_names.update(entry_names)
            elif form_details['schema']['type'] == 'array':
                if '$ref' in form_details['schema']['items']:
                    ref = form_details['schema']['items']['$ref']
                    parts = ref.split('/')
                    schemaname = parts[-1]
                    input_names.add(schemaname.lower())
                    if 'properties' in form_details['schema']['items']['referenced_schema']:
                        prop_names = get_property_names(form_details['schema']['items']['referenced_schema'])
                        input_names.update(prop_names)
            elif form_details['schema']['type'] == 'object':
                schema_details = form_details['schema']
                if 'properties' in schema_details:
                    prop_names = get_property_names(schema_details)
                    input_names.update(prop_names)
    return input_names



def get_entry_names(data):
    entry_names = set()
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                entry_names.update(get_entry_names(value))
            else:
                entry_names.add(key.lower())
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                entry_names.update(get_entry_names(item))
    return entry_names



def get_property_names(schema):
    property_names = set()

    def collect_names(subschema):
        if 'properties' in subschema:
            for prop_name, prop_schema in subschema['properties'].items():
                property_names.add(prop_name.lower())
                if 'properties' in prop_schema:
                    collect_names(prop_schema)
                elif 'items' in prop_schema and 'properties' in prop_schema['items']:
                    collect_names(prop_schema['items'])
    collect_names(schema)
    return property_names

        
            


def crud_logic_seq(base_entry_list):
    create_req = []
    read_req = []
    update_req = []
    delete_req = []


    for seq in base_entry_list:
        path = seq.get_path()
        method = seq.get_method()
        check_data = seq.get_all_info()
        try:
            check_str = json.dumps(check_data)
        except:
            check_str = None

        # Create: POST, PUT if we have `id` or `uuid`
        if any(word.lower() in path for word in ['id','uuid','create','start','initialize','register']):
            create_req.append(seq)
        if method == 'post' or method == 'put':
            if any(word.lower() in check_str for word in ['id','uuid','create','start','initialize','register']):
                    create_req.append(seq)

        # Read: GET
        if any(word.lower() in path for word in ['check','statistic','read','get']):
            read_req.append(seq)
        if method  == 'get' or any(word.lower() in check_str for word in ['check','statistic','read','get']):
            read_req.append(seq)

        # Update: PUT to replace, PATCH to modify
        if any(word.lower() in path for word in ['update','upgrade','restore']):
            update_req.append(seq)
        if method  == 'put' or method  == 'patch':
            if any(word.lower() in check_str for word in ['update','upgrade','restore']):
                update_req.append(seq)

        # Delete: DELETE
        if any(word.lower() in path for word in  ['delete','remove','cancel']):
            delete_req.append(seq)
        if method  == 'delete' or any(word.lower() in check_str for word in ['delete','remove','cancel']):
            delete_req.append(seq)

    # generate combinations
    all_combinations = []
    for create in itertools.chain([[]], itertools.permutations(create_req, 1)):
        for read in itertools.chain([[]] if not read_req else [], itertools.permutations(read_req, 1)):
            for update in itertools.chain([[]], itertools.permutations(update_req, 1)):
                for delete in itertools.chain([[]], itertools.permutations(delete_req, 1)):
                    # Combine the requests in the current combination
                    combination = list(create) + list(read) + list(update) + list(delete)
                    if len(combination) > 1:
                        all_combinations.append(combination) 

    seq_names = []
    for seq in all_combinations:
        seq_name = ''
        for req in seq:
            com = req.get_path()+ ' ' + req.get_method()
            if seq_name == '':
                seq_name = seq_name + com
            else:
                seq_name = seq_name + ' ---> ' +  com
        seq_names.append(seq_name)

    return all_combinations, seq_names
               

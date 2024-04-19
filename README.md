# Currently only works for swagger 3.0

### swagger_parser.py

Read the swagger file and convert each request into a list of ApiEntry object

(the goal is to record the $ref details under each entry so that we don't need to read the swagger file again)

### api_entry.py

Define the class of ApiEntry 

### tag.py

Analyze and give tag to each ApiEntry (currently only based on request itself, but not on the response yet)

### generate_auth_file.py

Generate the authentication template for the user to fill in.

### bussiness_logic.py

Find the business logic among the ApiEntry list. Both dependence logic and CRUD logic.

### send_request.py

Send individual HTTP request


# Not Fully Compatible Yet

### token_analyze.py

Try to decode JWT token or verify MD5 Hash


### bola_query.py

Based on different levels of authorization, try to compare if we can get any new schema

### query.py

To find the entry that could be used for SQL injection or file upload. Find the entry that requires / returns login information

# TODO

### fuzz.py

Conduct fuzzing for each request

### api_testing.py

Define the testing logic

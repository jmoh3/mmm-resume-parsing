import json
from base64 import b64decode
from tika import parser
import io
import re

def find_keywords(resume_string):
    with open('keywords.txt', 'r') as f:
        keywords = f.readlines()
    keywords = [re.sub('\n', '', word) for word in keywords]
    found = []
    for word in keywords:
        if word in resume_string:
            found.append(word)
    return found

def get_keyword_dict():
    lines = []
    with open('keyword_weights.csv', 'r') as f:
        lines = f.readlines()
    name_to_weights = {}
    terms = lines[0].split(',')[1:]
    for i in range(1,len(lines)):
        split_line = lines[i].split(',')
        name = split_line[0]
        weights = [float(num) for num in split_line[1:]]
        name_to_weights[name] = {}
        for idx, term in enumerate(terms):
            name_to_weights[name][term] = weights[idx]
    return name_to_weights
    
def parse_resume(event, context):
    try:
        data = json.loads(event['body'])

        b64_resume = data['resume']
        resume_bytes_IO = io.BytesIO(b64decode(re.sub("data:application/pdf;base64", '', b64_resume)))
        resume_bytes_IO.name = 'tmp_resume.pdf'
        resume_text = parser.from_file(resume_bytes_IO)['content']

        resume_keywords = find_keywords(resume_text)
        keyword_weights = get_keyword_dict()

        relevant_keywords = set()

        for user_interest in resume_keywords:
            for event_tag in keyword_weights.keys(): # instead of using the keywords from from 
                try:
                    weight = keyword_weights[event_tag][user_interest]
                    if weight > 0.5:
                        relevant_keywords.add(event_tag)
                except:
                    continue

        relevant_keywords = list(relevant_keywords)

        body = {
            "message": "Go Serverless v1.0! Your function executed successfully!",
            "relevant_event_tags": relevant_keywords
        }
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

        return response
    except:
        body = {
            "message": "You fucked up"
        }
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }
        return response

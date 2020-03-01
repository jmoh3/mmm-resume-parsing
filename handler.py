import json
from base64 import b64decode
from tika import parser
import io
import re
import requests

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
    for i in range(1, len(lines)):
        split_line = lines[i].split(',')
        name = split_line[0]
        weights = [float(num) for num in split_line[1:]]
        name_to_weights[name] = {}
        for idx, term in enumerate(terms):
            name_to_weights[name][term] = weights[idx]
    return name_to_weights

def get_resume_text(b64_resume):
    resume_bytes_IO = io.BytesIO(
    b64decode(re.sub("data:application/pdf;base64", '', b64_resume)))
    resume_bytes_IO.name = 'tmp_resume.pdf'
    resume_text = parser.from_file(resume_bytes_IO)['content']
    return resume_text

def create_user_topics_body(email, relevant_keywords):
    keywords_list = []

    for keyword in relevant_keywords:
        keywords_list.append({
            "name" : keyword,
            "weight" : relevant_keywords[keyword]
        })
    
    return {
        "email": email,
        "topics": keywords_list
        }

def parse_resume(event, context):
    data = json.loads(event['body'])

    try:
        resume_text = get_resume_text(data['resume'])
    except:
        body = {
            "message": "Error parsing resume",
        }
        response = {
            "statusCode": 400,
            "body": json.dumps(body),
            "headers": {
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Authorization, Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': ['POST', 'OPTIONS']
            }
        }
        return response

    resume_keywords = find_keywords(resume_text)
    keyword_weights = get_keyword_dict()

    relevant_keywords = {}

    for user_interest in resume_keywords:
        for event_tag in keyword_weights.keys():  # instead of using the keywords from from
            try:
                weight = keyword_weights[event_tag][user_interest]
                if event_tag not in relevant_keywords.keys():
                    relevant_keywords[event_tag] = weight
                elif weight > relevant_keywords[event_tag]:
                    relevant_keywords[event_tag] = weight
            except:
                continue
    
    user_topics_body = create_user_topics_body(data['email'], relevant_keywords)

    user_topics_headers = {
        "Authorization" : "Bearer ChristmasTree4AllSeasons"
    }

    user_topics_response = requests.post('http://192.168.0.115:3000/dev/service/updatemember',
                                            json=user_topics_body,
                                            headers=user_topics_headers)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "user_email": data['email'],
        "user_post_status" : user_topics_response.status_code
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body),
        "headers": {
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Headers': 'Authorization, Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': ['POST', 'OPTIONS']
            }
    }

    return response
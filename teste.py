import requests

endpoint = 'https://projeto-een251.cognitiveservices.azure.com'
key = '2c0a6ae783374aca99fe12e1e32d3250'

personGroupId = '1'

url = f'{endpoint}/face/v1.0/persongroups/{personGroupId}'

headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': key
}

body = {
    'name': 'teste',
    'userData': "user data provided",
    "recognitionModel": "recognition_03"
}

res = requests.get(url, headers=headers, data=body)

print(res.status_code)
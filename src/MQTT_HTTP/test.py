import requests

url = 'http://10.210.211.43:42069/door/code'
myobj = {'somekey': 'somevalue'}

x = requests.post(url, json = myobj)

#print the response text (the content of the requested file):

print(x.status_code)

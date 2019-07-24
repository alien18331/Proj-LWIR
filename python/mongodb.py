import pymongo

hostIP = "10.192.213.155"
port = 10000

client = pymongo.MongoClient(host = hostIP, port = port)
db = client['IR']
collection = db['data']

tmpDic = {
    'userID': '00048766',
    'temp': 38
}

result = collection.insert(tmpDic)
print(result)
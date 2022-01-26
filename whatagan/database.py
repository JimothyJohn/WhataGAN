from utils import get_collection

collection = get_collection()

item_details = collection.find({"number": 4})
print(item_details[0])
'''
for item in item_details[:10]:
    # This does not give a very readable output
    print(item["number"])
'''

category_index = collection.create_index("number")
print("New Index!")

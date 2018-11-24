import json

#
json1_file = open("laptop_features.json")
json1_str = json1_file.read()
json1_data = json.loads(json1_str)

new_dict = []

outfile = open('laptop_features_second.json', 'w')
outfile.write("[\n")

for x in json1_data:

    temp_dict = {}
    temp_dict["name"] = list(x.keys())[0]
    x= x[list(x.keys())[0]]
    temp_dict['positive'] = x['positive']
    temp_dict['negative'] = x['negative']
    temp_dict['price'] = x['metadata']['price']
    temp_dict['imUrl'] = x['metadata']['imUrl']

    new_dict.append(temp_dict)

    outfile.write(json.dumps(temp_dict))
    outfile.write(",\n")


outfile.write("]")


print(new_dict)
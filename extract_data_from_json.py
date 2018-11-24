# each JSON is small, there's no need in iterative processing
import json
import pandas as pd

count = 0

main_list = []
reset = False
with open('/Users/gielderks/Desktop/amazon/reviews_Electronics.json', 'r') as f:

    for line in f:

        if reset == True:

            print('reset = True')

            main_list = []

        reset = False
        data = json.loads(line)

       # print(data)

        temp_list = [data['asin'], data['reviewText'], data['overall']]

        main_list.append(temp_list)

        count += 1

        if count % 100000 == 0:
            print(count)

        if count % 1000000 == 0:

            reset = True
            print(len(main_list))
            print('creating file')
            df = pd.DataFrame(main_list, columns=['asin', 'reviewText', 'overall'])
            path = 'laptop_review_data/laptop_metadata' + str(count) + '.csv'
            df.to_csv(path, index=False)
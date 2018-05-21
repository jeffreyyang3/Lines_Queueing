import random
'''
    - Data holds the data for one session.
    - Each inner list represents a group.
    - Each inner inner list represents a period. 
    - Period lists can have no more dictionaries than there are participants.
    - Each dict represents a player.
    - The data can be shuffled with the optoinal shuffle argument. It defaults to true.

    - for now, all groups must be the same size
'''
data =  [
            [ # Group 1
                [ # Period 1
                    {'s':1, 'pay_rate': 0.05, 'service_time': 1000},
                    {'s':2, 'pay_rate': 0.04, 'service_time': 1000},
                    {'s':3, 'pay_rate': 0.03, 'service_time': 1000},
                    # { 'pay_rate': 0.05, 'service_time': 30},
                    # { 'pay_rate': 0.06, 'service_time': 30},
                    # { 'pay_rate': 0.07, 'service_time': 30},
                    # { 'pay_rate': 0.08, 'service_time': 13},
                    # { 'pay_rate': 0.20, 'service_time': 10},
                ],
                # [ # Period 2
                #     { 'pay_rate': 0.03, 'service_time': 1000},
                #     { 'pay_rate': 0.05, 'service_time': 1000},
                #     { 'pay_rate': 0.06, 'service_time': 1000},
                #     # { 'pay_rate': 0.07, 'service_time': 30},
                #     # { 'pay_rate': 0.08, 'service_time': 13},
                #     # { 'pay_rate': 0.20, 'service_time': 10},
                #     # { 'pay_rate': 0.01, 'service_time': 15},
                #     # { 'pay_rate': 0.03, 'service_time': 20},
                # ],
            ],
            # [ # Group 2
            #     [ # Period 1
            #         { 'pay_rate': 0.05, 'service_time': 20},
            #         { 'pay_rate': 0.04, 'service_time': 30},
            #         { 'pay_rate': 0.03, 'service_time': 10},
            #         { 'pay_rate': 0.05, 'service_time': 30},
            #         { 'pay_rate': 0.06, 'service_time': 30},
            #         { 'pay_rate': 0.07, 'service_time': 30},
            #         { 'pay_rate': 0.08, 'service_time': 13},
            #         { 'pay_rate': 0.20, 'service_time': 10},
            #     ],
            #     [ # Period 2
            #         { 'pay_rate': 0.03, 'service_time': 20},
            #         { 'pay_rate': 0.05, 'service_time': 30},
            #         { 'pay_rate': 0.06, 'service_time': 30},
            #         { 'pay_rate': 0.07, 'service_time': 30},
            #         { 'pay_rate': 0.08, 'service_time': 13},
            #         { 'pay_rate': 0.20, 'service_time': 10},
            #         { 'pay_rate': 0.01, 'service_time': 15},
            #         { 'pay_rate': 0.03, 'service_time': 20},
            #     ],
            # ],
        ]

# fills missing values with the defaults
# I do not think we will use this function unless more config values are added
def fill_defaults(data):
    for group in data:
        for period in group:
            for index,player in enumerate(period):
                if 'start_pos' not in player:
                    player['start_pos'] = index
    return data

# shuffles order of groups, the order of periods within the group, and the order of players
# withing the period
def shuffle(data):
    for i,group in enumerate(data):
        for j,_ in enumerate(group):
            random.shuffle(data[i][j]) # shuffle order of players within periods
        random.shuffle(data[i]) # shuffle order of periods withing groups
    random.shuffle(data) # shuffle order of groups

    return data

# exports data to a csv format
def export_csv(fname, data):
    pass

# exports data to models.py
# formats data to make it easier for models.py to parse it
def export_data(shuf=True):
    if shuf == False:
        return data
    else:
        return shuffle(data)


import random
'''
    - Data holds the data for one session.
    - Each inner list represents a group.
    - Each inner inner list represents a period. 
    - Period lists can have no more dictionaries than there are participants.
    - Each dict represents a player.

    - for now, all groups must be the same size

    - if you define starting positions here, make sure every player has a starting position,
    - otherwise the behavior is undefined

    - Defining the starting position does not affect which player (in the room) gets assigned to
    - each dictionary here. Rather, it keeps a person's starting position in the line consistent
    - with their pay rate and their service time

    - periods lengths is a list containing the total time for each period
    - need to incorporate K into this!!

    - might make period a dict with players, a list of dicts, and period data, a dict of data for the entire period
'''
period_lengths = [35]
data =  [
            [ # Group 1
                [ # Period 1
                    {'pay_rate': 0.05, 'service_time': 30},
                    {'pay_rate': 0.04, 'service_time': 30},
                    {'pay_rate': 0.03, 'service_time': 30},
                    # { 'pay_rate': 0.05, 'service_time': 30},
                    # { 'pay_rate': 0.06, 'service_time': 30},
                    # { 'pay_rate': 0.07, 'service_time': 30},
                    # { 'pay_rate': 0.08, 'service_time': 13},
                    # { 'pay_rate': 0.20, 'service_time': 10},
                ],
                # [ # Period 2
                #     {'pay_rate': 0.03, 'service_time': 10},
                #     {'pay_rate': 0.05, 'service_time': 10},
                #     {'pay_rate': 0.06, 'service_time': 10},
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

# shuffles order of groups, the order of periods within the group, and the order of players
# within the period.
# also fills default start_pos's with random positions
def shuffle(data):
    for i,group in enumerate(data):
        for j,period in enumerate(group):
            if 'start_pos' not in data[i][j][0]:
                positions = [n for n in range(1,len(period) + 1)]
                random.shuffle(positions)
                for k,player in enumerate(period):
                    data[i][j][k]['start_pos'] = positions[k]
            random.shuffle(data[i][j]) # shuffle order of players within periods
        random.shuffle(data[i]) # shuffle order of periods withing groups
    random.shuffle(data) # shuffle order of groups

    return data

# exports data to a csv format
def export_csv(fname, data):
    pass

# exports data to models.py
# formats data to make it easier for models.py to parse it
def export_data():
    if len(period_lengths) != len(data[0]):
        raise ValueError('Number of periods differs in data and period_lengths')
    return shuffle(data), period_lengths

'''
Sample exported player dict:
{ 'start_pos': 2, 'pay_rate': 0.03, 'service_time': 20},
'''
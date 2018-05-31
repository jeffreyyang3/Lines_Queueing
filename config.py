import random
'''
    - Data holds the data for one session.
    - Each inner list represents a group.
    - Each inner inner dict represents a period. 
    - Period dicts can have no more dictionaries than there are participants.
    - Each dict represents a player.

    - for now, all groups must be the same size

    - if you define starting positions here, make sure every player has a starting position,
    - otherwise the behavior is undefined

    - Defining the starting position does not affect which player (in the room) gets assigned to
    - each dictionary here. Rather, it keeps a person's starting position in the line consistent
    - with their pay rate and their service time

    - periods lengths is a list containing the total time for each period
    - need to incorporate K into this!!

    - might make period a dict with players, a list of dicts, and period data,
    - a dict of data for the entire period
'''

data =  [
            [ # Group 1
                { # Period 1
                    'settings': {
                        'duration': 35,
                        'switch': 'swap'
                    },
                    'players': [
                        {'pay_rate': 0.05, 'service_time': 10},
                        {'pay_rate': 0.04, 'service_time': 10},
                        {'pay_rate': 0.03, 'service_time': 10},
                        # { 'pay_rate': 0.05, 'service_time': 30},
                        # { 'pay_rate': 0.06, 'service_time': 30},
                        # { 'pay_rate': 0.07, 'service_time': 30},
                        # { 'pay_rate': 0.08, 'service_time': 13},
                        # { 'pay_rate': 0.20, 'service_time': 10},
                    ]
                },
                { # Period 2
                    'settings': {
                        'duration': 45,
                        'switch': 'cut'
                    },
                    'players': [
                        {'pay_rate': 0.05, 'service_time': 10},
                        {'pay_rate': 0.04, 'service_time': 10},
                        {'pay_rate': 0.03, 'service_time': 10},
                        # { 'pay_rate': 0.05, 'service_time': 30},
                        # { 'pay_rate': 0.06, 'service_time': 30},
                        # { 'pay_rate': 0.07, 'service_time': 30},
                        # { 'pay_rate': 0.08, 'service_time': 13},
                        # { 'pay_rate': 0.20, 'service_time': 10},
                    ]
                },
            ],
        ]

# shuffles order of groups, the order of periods within the group, and the order of players
# within the period.
# also fills default start_pos's with random positions
def shuffle(data):
    for i,group in enumerate(data):
        for j,period in enumerate(group):
            if 'start_pos' not in data[i][j]['players'][0]:
                positions = [n for n in range(1,len(period['players']) + 1)]
                random.shuffle(positions)
                for k,player in enumerate(period['players']):
                    data[i][j]['players'][k]['start_pos'] = positions[k]
            random.shuffle(data[i][j]['players']) # shuffle order of players within periods
        random.shuffle(data[i]) # shuffle order of periods withing groups
    random.shuffle(data) # shuffle order of groups

    return data

# exports data to a csv format
def export_csv(fname, data):
    pass

# exports data to models.py
# formats data to make it easier for models.py to parse it
def export_data():
    # error handling
    for group in data:
        for period in group:
            if 'settings' not in period:
                raise ValueError('Each period must contain settings dict')
            if 'players' not in period:
                raise ValueError('Each period must contain players dict')
            if 'duration' not in period['settings']:
                raise ValueError('Each period settings must have a duration')
            if 'switch' not in period['settings']:
                raise ValueError('Each period settings must have a switch variable')
            if period['settings']['switch'] not in ['cut', 'swap']:
                raise ValueError('Each period settings switch variable \
                    must be either \'swap\' or \'cut\'')
    return shuffle(data)

'''
Sample exported player dict:
{ 'start_pos': 2, 'pay_rate': 0.03, 'service_time': 20},
'''
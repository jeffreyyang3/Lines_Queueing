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

    settings data:
        'duration': 100,
        # duration of the round in seconds
        
        'swap_method': 'swap',
        # mode defining how trades occur
            # bid: players offer a portion of their endowment in exchange for a swap
            # swap: players ask to swap with no monetary incentive
            # cut: players can cut to any position in line
                # this might take some money or something
       
        'pay_method': 'gain',
        # treatment for paying
            # gain: accumulated $ increases every second in paying room (and not
            # in the queue/service room) by pay_rate
            # lose: accumulated $ decreases every second in queue & service room
                # by pay_rate
        
        'k': .5,
        # portion of the total round time that makes up everyone's service times
        
        'service_distribution': 5,
        # how service times are assigned
        # if service times are explicitly defined for each player, this is ignored.
        # if not, this must be here; throws error if not
        # number represents the max possible factor by which one person's service time is greater
            # than another. If 1, everyone will have the same service time.
            # If 10, service times are assigned randomly such that no person will have a service
            # time more than 10x longer than any other person
        
'''

"""
data =  [
            [ # Group 1
                { # Period 1
                    'settings': {
                        'duration': 45,
                        'swap_method': 'swap',
                        'pay_method': 'gain',
                        'k': .8,
                        'service_distribution': 1,
                    },
                    'players': [
                        {'pay_rate': 0.05, 'endowment': 5},
                        {'pay_rate': 0.04, 'endowment': 6},
                        {'pay_rate': 0.03, 'endowment': 7},
                        {'pay_rate': 0.02, 'endowment': 8}
                    ]
                },
                { # Period 2
                    'settings': {
                        'duration': 45,
                        'swap_method': 'swap',
                        'pay_method': 'lose',
                        'k': .8,
                        'service_distribution': 5,
                    },
                    'players': [
                        {'pay_rate': 0.05, 'endowment': 5},
                        {'pay_rate': 0.04, 'endowment': 6},
                        {'pay_rate': 0.03, 'endowment': 7},
                        {'pay_rate': 0.02, 'endowment': 8}
                    ]
                },
                { # Period 3
                    'settings': {
                        'duration': 45,
                        'swap_method': 'bid',
                        'pay_method': 'lose',
                        'k': .8,
                        'service_distribution': 100,
                    },
                    'players': [
                        {'pay_rate': 0.01, 'endowment': 5, 'service_time': 10},
                        {'pay_rate': 0.02, 'endowment': 6, 'service_time': 20},
                        {'pay_rate': 0.03, 'endowment': 7, 'service_time': 30},
                        {'pay_rate': 0.02, 'endowment': 8, 'service_time': 40}

                    ]
                },
                { # Period 5
                    'settings': {
                        'duration': 45,
                        'swap_method': 'bid',
                        'pay_method': 'gain',
                        'k': .8,
                        'service_distribution': 1,
                    },
                    'players': [
                        {'pay_rate': 0.01, 'endowment': 5},
                        {'pay_rate': 0.02, 'endowment': 6},
                        {'pay_rate': 0.03, 'endowment': 7},
                        {'pay_rate': 0.04, 'endowment': 8},
                    ]
                },
            ],
        ]
"""

data =  [
            [ # Group 1
                { # Period 2: testing for double auction format
                    'settings': {
                        'duration': 120,
                        'swap_method': 'swap',
                        'pay_method': 'gain',
                        'k': .8,
                        'service_distribution': 1,
                    },
                    'players': [
                        {'pay_rate': 0.05, 'endowment': 5},
                        {'pay_rate': 0.04, 'endowment': 6},
                        {'pay_rate': 0.03, 'endowment': 7},
                        {'pay_rate': 0.02, 'endowment': 8}
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
    # error handling & filling defaults
    for i, group in enumerate(data):
        for j,period in enumerate(group):
            if 'settings' not in period:
                raise ValueError('Each period must contain settings dict')
            
            if 'players' not in period:
                raise ValueError('Each period must contain players dict')

            settings = period['settings']
            players = period['players']
            
            if 'duration' not in settings:
                raise ValueError('Each period settings must have a duration')
            
            if 'swap_method' not in settings:
                raise ValueError('Each period settings must have a swap_method variable')

            # For now, will comment out this swap_method check to allow for testing
            # of the double auction
            """
            if settings['swap_method'] not in ['cut', 'swap', 'bid']:
                raise ValueError('Each period settings swap_method variable \
                    must be either \'bid\', \'swap\' or \'cut\'')
            """

            if 'pay_method' not in settings:
                raise ValueError('Each period settings must have a pay_method variable')
            
            if settings['pay_method'] not in ['gain', 'lose']:
                raise ValueError('Each period settings pay_method variable \
                    must be either \'gain\' or \'lose\'')
            if 'pay_rate' not in players[0]:
                raise ValueError('Players must have pay_rates')
            
            if 'service_time' not in players[0]:
                if 'k' not in settings:
                    raise ValueError('Period settings must have a k variable if players \
                        do not define service times')
                
                if 'service_distribution' not in settings:
                    data[i][j]['settings']['service_distribution'] = 1

                sd = settings['service_distribution']
                t = settings['duration']
                k = settings['k']

                vals = [random.randrange(sd) + 1 for p in players]
                vals = [v / sum(vals) for v in vals]
                vals = [round(v * k * t) for v in vals]
                for k,_ in enumerate(players):
                    data[i][j]['players'][k]['service_time'] = vals[k]

    print('exported data is')
    print(data[0][0])

    return shuffle(data)

'''
Sample exported player dict:
{ 'start_pos': 2, 'pay_rate': 0.03, 'service_time': 20, 'endowment': 5},
'''
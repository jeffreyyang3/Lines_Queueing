import random
import math
data = [[
    {  # Period 17-18: double, no communication, 8 players (1 group)
        #
        "settings": {
            "duration": 180,
            "swap_method": "double",
            "pay_method": "gain",
            "k": 0.8,
            "service_distribution": 1,
            "discrete": True,
            "messaging": False,
        },
        "players": [
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
        ],
    },

    {  # Period 19-20: take it or leave it, no communication, 8 players (1 group)
        #
        "settings": {
            "duration": 100,
            "swap_method": "bid",
            "pay_method": "gain",
            "k": 0.8,
            "service_distribution": 1,
            "discrete": True,
            "messaging": False,
        },
        "players": [
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
        ],
    },

    {  # Period 21-22: swap, with communication, 8 players (1 group)
        #
        "settings": {
            "duration": 100,
            "swap_method": "swap",
            "pay_method": "gain",
            "k": 0.8,
            "service_distribution": 1,
            "discrete": True,
            "messaging": True,
        },
        "players": [
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
        ],
    },

    {  # Period 23-24: double, no communication, 8 players (1 group)
        # never added communication to double
        "settings": {
            "duration": 100,
            "swap_method": "double",
            "pay_method": "gain",
            "k": 0.8,
            "service_distribution": 1,
            "discrete": True,
            "messaging": False,
        },
        "players": [
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
            {"pay_rate": 8, "endowment": 8, "c": random.random()},
        ],
    },
]]


def shuffle(data):
    for i, group in enumerate(data):
        for j, period in enumerate(group):
            if "start_pos" not in data[i][j]["players"][0]:
                positions = [n for n in range(1, len(period["players"]) + 1)]
                random.shuffle(positions)
                for k, player in enumerate(period["players"]):
                    data[i][j]["players"][k]["start_pos"] = positions[k]
            random.shuffle(
                data[i][j]["players"]
            )  # shuffle order of players within periods
        random.shuffle(data[i])  # shuffle order of periods withing groups
    random.shuffle(data)  # shuffle order of groups

    return data


# exports data to a csv format
def export_csv(fname, data):
    pass


# exports data to models.py
# formats data to make it easier for models.py to parse it
def export_data():
    # error handling & filling defaults
    for i, group in enumerate(data):
        for j, period in enumerate(group):
            if "settings" not in period:
                raise ValueError("Each period must contain settings dict")

            if "players" not in period:
                raise ValueError("Each period must contain players dict")

            settings = period["settings"]
            players = period["players"]

            if "duration" not in settings:
                raise ValueError("Each period settings must have a duration")

            if "swap_method" not in settings:
                raise ValueError(
                    "Each period settings must have a swap_method variable"
                )

            # For now, will comment out this swap_method check to allow for testing
            # of the double auction
            """
            if settings['swap_method'] not in ['cut', 'swap', 'bid']:
                raise ValueError('Each period settings swap_method variable \
                    must be either \'bid\', \'swap\' or \'cut\'')
            """

            if "pay_method" not in settings:
                raise ValueError(
                    "Each period settings must have a pay_method variable")

            if settings["pay_method"] not in ["gain", "lose"]:
                raise ValueError(
                    "Each period settings pay_method variable \
                    must be either 'gain' or 'lose'"
                )
            if "pay_rate" not in players[0]:
                raise ValueError("Players must have pay_rates")

            if "service_time" not in players[0]:
                if "k" not in settings:
                    raise ValueError(
                        "Period settings must have a k variable if players \
                        do not define service ti"
                    )

                if "service_distribution" not in settings:
                    data[i][j]["settings"]["service_distribution"] = 1

                sd = settings["service_distribution"]
                t = settings["duration"]
                k = settings["k"]

                vals = [random.randrange(sd) + 1 for p in players]
                vals = [v / sum(vals) for v in vals]
                vals = [round(v * k * t) for v in vals]
                positions = [n for n in range(1, len(period["players"]) + 1)]
                for k, _ in enumerate(players):
                    data[i][j]["players"][k]["service_time"] = vals[k]
                    data[i][j]["players"][k]["start_pos"] = positions[k]

    print("exported data is")
    print(data[0][0])

    return data

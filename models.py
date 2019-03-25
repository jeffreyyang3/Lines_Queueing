from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BasePlayer,
    Currency as c,
    currency_range,
)
from otree_redwood.models import Group as RedwoodGroup
from . import config as config_py
import random

"""
Eli Pandolfo <epandolf@ucsc.edu>

Notes to ask Kristian:
    state of queue
    num players
    different num players in a group
"""


class Constants(BaseConstants):
    name_in_url = "Lines_Queueing"
    participation_fee = c(5)

    config = config_py.export_data()

    num_rounds = len(config[0])
    num_players = sum([len(group[0]["players"]) for group in config])
    players_per_group = len(config[0][0]["players"])

    # these will be displayed to players in the UI. Defined here for consistency and
    # a central location
    alert_messages = {
        "cutting": "You have cut the line",
        "cutted": "Someone has cut in front of you",
        "requested": "You have been requested to swap",
        "requesting": "You have requested to swap",
        "accepted": "Your swap request has been accepted",
        "accepting": "You have accepted a swap request",
        "declined": "Your swap request has been declined",
        "declining": "You have declined a swap request",
        "unv_other": "Requestee is currently in a trade",
        "next_self": "You have entered the service room.",
        "next_queue": "You have advanced one position in the queue",
        "next_queue2": "You have advanced one position in the queue ",
        "bad_bid": "Your bid must be between 0 and your current payoff",
        "none": "",
    }


class Player(BasePlayer):

    time_Instructions = models.LongStringField()
    time_Queue = models.LongStringField()
    time_Service = models.LongStringField()
    time_BP = models.LongStringField()
    time_Results = models.LongStringField()

    # amount of money player starts with
    endowment = models.FloatField()

    # position in queue player starts at
    start_pos = models.IntegerField()

    # time player takes to get serviced
    service_time = models.FloatField()

    # time player is waiting in the queue before being serviced
    waiting_time = models.FloatField()

    # $ per second player makes after being serviced, for gain mode
    # OR $ per second player loses in waiting & service rooms, for lose mode
    pay_rate = models.FloatField()

    # Adding double action now (which is technically still swapping by bid, but
    # for now will separate the two
    # method by which players swap: bid, swap, or cut
    swap_method = models.StringField()

    # method by which players accumulate money: gain or lose
    pay_method = models.StringField()

    # money player leaves the round with
    round_payoff = models.FloatField()

    # data holding information on the entire group's trades
    # including bid prices, which are chosen each trade
    metadata = models.LongStringField()
    allMetadata = models.LongStringField()

    # discrete and messaging enabled/disabled
    discrete = models.BooleanField()
    messaging = models.BooleanField()
    # c (cost per time not in service)
    cost = models.FloatField()


    def set_payoffs(self):
        self.payoff = self.in_round(self.session.vars["pr"]).round_payoff


class Group(RedwoodGroup):

    # needed for otree redwood; this should replace the need for the get_timeout_seconds method
    # in pages.QueueService, but for some reason does has no effect. This is essentially a wrapper
    # for the timeout_seconds variable anyway.

    def period_length(self):
        g_index = self.get_player_by_id(1).participant.vars[self.round_number]["group"]
        return Constants.config[g_index][self.round_number - 1]["settings"]["duration"]

    # takes in the data transferred back and forth by channels,
    # and generates a list representing the queue, where each element in the list
    # IMPORTANT: this list represents the the entire queue, including players in the service room,
    # organized by when they arrived. This means that the 0th element in the returned list is the
    # first person to have entered the service room, and the last element in the list is the person
    # in the back of the queue.
    def queue_state(self, data):
        print("data before sorting queue is:")
        print(data)

        queue = {}
        for p in self.get_players():
            pp = data[str(p.id_in_group)]
            queue[pp["pos"]] = pp["id"]
        return [queue.get(k) for k in sorted(queue)]

    """
        On swap event: this is a method defined by redwood. It is called when channel.send() is
        called in the javascript. That happens when
            1) someone starts a trade request by pressing the trade button,
            2) someone responds to a trade request by pressing the yes or no button,
            3) someone enters the service room and the entire queue moves forward.
        
        This method essentially defines a state machine. Each player has a state, represented by
        a dictionary with keys:
            id: id in group; a number from 1 to Constants.players_per_group,
            
            pos: position in queue at time of input; a number from -Constants.players_per_group to
                Constants.players_per_group,
            
            in_trade: boolean - true if this player has 
                1) requested a trade and awaits a response;
                2) has been requested and has not yet responded,
            
            last_trade_request: timestamp of the last time this player clicked the trade button,
            
            requested: if this player has been requested to swap, the id of the player who made
                the request; None, or a number from 1 to Constants.players_per_group,
            
            requesting: if this player has made a request to swap, the id of the player who the
                request was made to; None, or a number from 1 to Constants.players_per_group,
            
            accepted: status of trade acceptance; 2 if requesting/no response/not in trade,
                1 if accepted, 0 if declined,
            
            alert: the current alert displayed to a player; a value in Constants.alert_messages,
            
            num_players_queue: the number of players who have not entered the service room at
                time of input; a number from 0 to Constants.players_per_group,
            
            num_players_service: the number of players who have entered the service room at
                time of input; a number from 0 to Constants.players_per_group,
            
            next; boolean: true if someone's service time has just run out, false otherwise;
                this is true when someone has passed into the service room, and everyone in
                the queue should move forward one position.

        The state machine takes in the state of each player, and alters the states of that
        player and other players accordingly.

        Note that upon this method being called, only one player's state can be different than it was 
        directly before the method was called; because each time an event occurs,
        (request, response, or next) this method gets called.

        After updating all player's states, sends the data back to the client.

        - Need to ensure that this is true; otherwise, we might need a queue of pending events
    """

    def _on_swap_event(self, event=None, **kwargs):

        # updates states of all players involved in the most recent event that triggered this
        # method call
        for p in self.get_players():
            """
            fields 'requesting', 'accepted', and 'next' of the player who initiated the event
            will be updated client-side;
            all other fields (the aggregate of which is the player state) are updated here

            player states; every player in the round is in exactly one of these states upon the
            initiation of an event (when this method gets called)
            
            - reset: no event that involves this player has been initiated by the most recent
                call to this method. There is no case for this, as the player's state
                is not updated.
            - service_clean: this player is not in trade and service time has run out
            - service_dirty: this player is in trade and service time has run out.
                This is an extension of service_clean.
            - service_other: other player's service time has run out
            - requesting_clean: player is not in_trade and requesting someone who is not in_trade
            - requesting_dirty: player is not in_trade and requesting someone who is in_trade
                the JS should make this impossible (disable trade button)
            - accepting: player is in_trade and accepting
            - declining: player is in_trade and declining
            """

            # gets this player's dict from the transmitted event
            p1 = event.value[str(p.id_in_group)]
            g_index = p.participant.vars[self.round_number]["group"]
            swap_method = Constants.config[g_index][self.round_number - 1]["settings"][
                "swap_method"
            ]

            # someone has entered the service room
            if p1["next"] == True:
                if p1["pos"] == 0:
                    # service_clean
                    p1["alert"] = Constants.alert_messages["next_self"]
                    # service_dirty
                    if p1["in_trade"]:
                        p2_id = str(p1["requested"])
                        p2 = event.value[p2_id]
                        metadata = {}

                        p1["in_trade"] = False
                        p2["in_trade"] = False
                        p1["requested"] = None
                        p2["requesting"] = None
                        p1["accepted"] = 2  # this should be unnecessary

                        metadata["status"] = "cancelled"
                        metadata["requester"] = p2["id"]
                        metadata["requestee"] = p1["id"]
                        timestamp = p2["last_trade_request"]
                        p2["last_trade_request"] = None
                        event.value[p2_id] = p2
                        event.value[str(p.id_in_group)] = p1
                        metadata["queue"] = self.queue_state(event.value)
                        event.value["metadata"][timestamp] = metadata
                # service_other
                elif p1["pos"] > 0:
                    # this is the only case I know of where you can get the same alert twice in a row (except none)
                    # if you get the same alert twice in a row the alert will not display because the watch function
                    # that displays alerts only get called when the alert changes.
                    if p1["alert"] == Constants.alert_messages["next_queue"]:
                        p1["alert"] = Constants.alert_messages["next_queue2"]
                    else:
                        p1["alert"] = Constants.alert_messages["next_queue"]
                else:
                    p1["alert"] = Constants.alert_messages["none"]
                p1["next"] = False

            # someone has initiated a trade request
            elif not p1["in_trade"] and p1["requesting"] != None:
                if swap_method == "cut":
                    p2 = event.value[str(p1["requesting"])]
                    temp = p2["pos"]
                    for i in event.value:
                        if i != "metadata" and i != str(p.id_in_group):
                            if (
                                event.value[i]["pos"] < p1["pos"]
                                and event.value[i]["pos"] >= p2["pos"]
                            ):
                                event.value[i]["alert"] = Constants.alert_messages[
                                    "cutted"
                                ]
                                event.value[i]["pos"] += 1

                    p1["pos"] = temp
                    p1["alert"] = Constants.alert_messages["cutting"]
                    metadata = {}
                    metadata["status"] = "cut"
                    metadata["requester"] = p1["id"]
                    p1["requesting"] = None
                    metadata["requestee"] = p2["id"]
                    timestamp = p1["last_trade_request"]
                    p1["last_trade_request"] = None
                    event.value[str(p.id_in_group)] = p1
                    metadata["queue"] = self.queue_state(event.value)
                    event.value["metadata"][timestamp] = metadata

                else:
                    p2 = event.value[str(p1["requesting"])]
                    # requesting_clean
                    if not p2["in_trade"]:
                        print("CORRECT ")
                        message = p1.get("message")
                        print(message)
                        p1["in_trade"] = True
                        p2["in_trade"] = True
                        p2["requested"] = p1["id"]
                        p2["bid"] = p1["bid"]
                        p2["message"] = message
                        p1["alert"] = Constants.alert_messages["requesting"]
                        p2["alert"] = Constants.alert_messages["requested"]
                        event.value[str(p1["requesting"])] = p2
                    # requesting_dirty; the js should prevent the logic from ever reaching this
                    else:
                        p1["requesting"] = None
                        p1["alert"] = Constants.alert_messages["unv_other"]

            # someone has responded to a trade request
            elif p1["in_trade"] and p1["requested"] != None:
                if p1["accepted"] != 2:

                    p2_id = str(p1["requested"])
                    p2 = event.value[p2_id]
                    metadata = {}

                    # declining
                    if p1["accepted"] == 0:
                        p1["in_trade"] = False
                        p2["in_trade"] = False
                        p1["requested"] = None
                        p2["requesting"] = None
                        p1["accepted"] = 2
                        p1["alert"] = Constants.alert_messages["declining"]
                        p2["alert"] = Constants.alert_messages["declined"]
                        p2["bid"] = None
                        p1["bid"] = None

                        metadata["status"] = "declined"

                    # accepting
                    elif p1["accepted"] == 1:

                        p1["in_trade"] = False
                        p2["in_trade"] = False
                        p1["requested"] = None
                        p2["requesting"] = None
                        p1["accepted"] = 2
                        temp = p1["pos"]
                        p1["pos"] = p2["pos"]
                        p2["pos"] = temp
                        p1["alert"] = Constants.alert_messages["accepting"]
                        p2["alert"] = Constants.alert_messages["accepted"]

                        # fix for typeError when accepting a swap during which
                        # the swapMethod is 'swap'
                        if swap_method == "swap":
                            p2["bid"] = None
                        else:
                            p2["bid"] = -float(p1["bid"])

                        # p2['bid'] = -float(p1['bid'])
                        metadata["status"] = "accepted"

                    metadata["requester"] = p2["id"]
                    metadata["requestee"] = p1["id"]
                    metadata["message"] = p1.get("message")
                    metadata["bid"] = p1["bid"]
                    timestamp = p2["last_trade_request"]
                    p2["last_trade_request"] = None
                    event.value[p2_id] = p2
                    event.value[str(p.id_in_group)] = p1
                    metadata["queue"] = self.queue_state(event.value)
                    event.value["metadata"][timestamp] = metadata

            event.value[str(p.id_in_group)] = p1  # partially redundant

        # broadcast the updated data out to all subjects
        self.send("swap", event.value)


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            self.session.vars["pr"] = random.randrange(Constants.num_rounds) + 1

        self.group_randomly()

        # since there is no group.vars, all group data is stored in session.vars,
        for g_index, g in enumerate(self.get_groups()):
            self.session.vars[self.round_number] = []
            for i in range(Constants.num_rounds):
                self.session.vars[self.round_number].append({})
            g_data = Constants.config[g_index][self.round_number - 1]["players"]

            # sets up each player's starting values
            for p in g.get_players():
                p.participant.vars[self.round_number] = {}
                p.participant.vars[self.round_number]["pay_rate"] = g_data[
                    p.id_in_group - 1
                ]["pay_rate"]
                p.participant.vars[self.round_number]["c"] = g_data[p.id_in_group - 1][
                    "c"
                ]
                p.participant.vars[self.round_number]["service_time"] = g_data[
                    p.id_in_group - 1
                ]["service_time"]
                p.participant.vars[self.round_number]["start_pos"] = g_data[
                    p.id_in_group - 1
                ]["start_pos"]
                p.participant.vars[self.round_number]["endowment"] = g_data[
                    p.id_in_group - 1
                ]["endowment"]
                p.participant.vars[self.round_number]["group"] = g_index
                p_data = {
                    "id": p.id_in_group,
                    "pos": p.participant.vars[self.round_number]["start_pos"],
                    "in_trade": False,
                    "last_trade_request": None,
                    "requested": None,
                    "requesting": None,
                    "bid": None,
                    "accepted": 2,
                    "alert": Constants.alert_messages["none"],
                    "num_players_queue": Constants.num_players,
                    "num_players_service": 0,
                    "next": False,
                }
                self.session.vars[self.round_number][g_index][p.id_in_group] = p_data
                self.session.vars[self.round_number][g_index]["metadata"] = {}


"""
metadata structure:
    { 'timestamp': {'bid': None/$, status': 'accepted/declined/cancelled/cut', 'requester': #, 'requestee': #, 'queue': [#,#,#...]}, ... }
"""


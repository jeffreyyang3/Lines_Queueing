from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BasePlayer,
    Currency as c, currency_range
)
from otree_redwood.models import DecisionGroup, Event
#from otree.api import BaseGroup as DecisionGroup

'''
Eli Pandolfo <epandolf@ucsc.edu>
otree-redwood>=0.7.0
'''

class Constants(BaseConstants):

    name_in_url = 'Lines_Queueing'
    num_rounds = 1
    participation_fee = c(5)

    # can this vary? 
    players_per_group = 2

    # combined length in seconds players are in the queue room and the payoff room
    # 240 seconds = 4 minutes. There are 2 different rooms players can be in
    # during those 4 minutes, the queue room, where they are not accumulating money,
    # and the payoff room, where they are accumulating money.
    period_length = 240

    # once a player is at the front of the line, it takes 30 seconds for them to pass through to the next room
    # should this be static across all players, or do players all have their own individual wait times?
    wait_from_front = 30

# player attributes:
    # - time for all pages
    # - pay rate
    # - position in queue
    # - id in group (what determines a player's starting position in the queue?)
    # - list of transactions that that player has sent/received (this could be 2 lists)

    # time remaining in line and potential payoff should be done all in js
class Player(BasePlayer):

    time_Instructions = models.LongStringField()
    time_Queue = models.LongStringField()
    time_Service = models.LongStringField()
    time_Results = models.LongStringField()

    waiting_cost = models.FloatField()
    bid_price = models.FloatField()
    service_time = models.FloatField() # this can be calcualted dynamically when they enter the service room

    trades = models.LongStringField()
            

# the group can get messages from all players. group attributes:
#   - position of each player in queue? (group knows but sends to player so player knows also? probably dont need both)
#   - current requests. should be stored in group because they always involve 2 players
#   - past transactions: can be stored as list of transaction objects, where each obj is a dict holding the players
#       involved, the positions that were switched, who was the sender and who was the receiver, and any other metadata:
#       time it took to be accepted or denied, time at which request was sent, what the optional message was, etc

# redwood (I think) enables us to send info from the page's js itself to this class. 
# should a message get sent when someone sends a switch request, or when the request gets accepted or denied?
#   - if when it gets accepted or denied, we have all the info needed to add a transaction to the log
#   - needs to be when request sent because players can send websocket messages to group only, not to other individual
#       players.

# Tentative control flow:
#   1. Player requests switch by clicking button on page
#   2. Button calls JS function which sends packet of data to group.
#       This data includes the sender, recipient, and any metadata.
#       send('decision', value) is how to actually send a message to the server
#   3. Group receives data packet.
#       - group identifies the 2 players involved
#       - uses getPlayerById to update the players' corresponding fields (what fields are needed?)
#       - send messages back to players that updates their html and shows the in progress request
#   4. Receiving players accepts or denies request which sends data packet back to group
#   5. Group identifies which in progress transaction this packet belongs to, resolves the transaction, 
#       and updates the player fields for position in queue if the switch goes through. Also appends to group
#       transaction log, and player transaction logs (why do both? pick one).
#       Player's html updates their new positions, and computes all required data from that (time remaining
#       and potential payoff)

# each player in the group has 1 decision value active at all times.
# the group_decisions dict maps each players participant code to their current decision value.
#   is group_decisions a dict itself or a channel, a data structure containing a dict?
#
# each player sends decisions to the group via the decisions channel, and the group sends 
# updates to all players at one time on the group_decisions channel
# I can also make my own channels. the redwood-channel tag is what we are going to use in templates
# https://leeps-lab.github.io/otree-redwood/otree_redwood/static/otree-redwood/webcomponents/redwood-channel/
#   this is example of redwood channel

# redwood-decision is the thing that allows each player to have 1 decision. need to clear up difference between decision and channel
# ASK MORGAN
#   difference between redwood-decision and redwood-channel
#   can each player have one decision at a time per channel, or one at a time period?
class Group(DecisionGroup):

    group_trades = models.LongStringField()

    def period_length(self):
        return Constants.period_length

    # broadcasts payload on a given channel to all members of the group
    # send(self, 'decision_group', payload)
    

class Subsession(BaseSubsession):
    
    def creating_session(self):
        self.group_randomly()    


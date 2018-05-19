from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BasePlayer,
    Currency as c, currency_range
)
from otree_redwood.models import Group as RedwoodGroup
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

    num_players = 2

    # combined length in seconds players are in the queue room and the payoff room
    # 240 seconds = 4 minutes. There are 2 different rooms players can be in
    # during those 4 minutes, the queue room, where they are not accumulating money,
    # and the payoff room, where they are accumulating money.
    period_length = 240

    alert_messages = {
        'requested': 'You have been requested to swap',
        'requesting': 'You have requested to swap',
        'accepted': 'Your swap request has been accepted',
        'accepting': 'You have accepted a swap request',
        'declined': 'Your swap request has been declined',
        'declining': 'You have declined a swap request',
        'unv_self': 'You must resolve your swap request before requesting again',
        'unv_other': 'You cannot request to swap with this person until they resolve their current swap',
        'none': ''
    }

    config = [
        # each inner list is a group
        [
            {'start_pos': 1, 'pay_rate': 0.55, 'service_time': 30},
            {'start_pos': 2, 'pay_rate': 0.45, 'service_time': 20}
        ]
    ]

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

    #bid_price = models.FloatField()
    service_time = models.FloatField() # this is the time it takes them 
    pay_rate = models.FloatField()

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
class Group(RedwoodGroup):

    group_trades = models.LongStringField()

    def period_length(self):
        return Constants.period_length

    def _on_swap_event(self, event=None, **kwargs):

        print(event.value)
        for p in self.get_players():

            # relies on only one thing being changed every click, we'll see what happens when two people click at nearly the same time
            
            # fields 'requesting' and  'accepted' of the person who clicked the button will be updated client-side;
            # all other fields are updated here based on the other fields' states
            # case 1: person is not in_trade and requesting someone who is not in_trade
            # case 2: person is not in_trade and requesting someone who is in_trade
            # case 3: person is in_trade and accepting
            # case 4: person is in_trade and denying
            # Note that the JS will prevent anyone in trade from requesting another trade
            p1 = event.value[str(p.id_in_group)]
            if not p1['in_trade'] and p1['requesting'] != None:
                p2 = event.value[str(p1['requesting'])]
                if not p2['in_trade']:
                    p1['in_trade'] = True
                    p2['in_trade'] = True
                    p2['requested'] = p1['id']
                    p1['alert'] = Constants.alert_messages['requesting']
                    p2['alert'] = Constants.alert_messages['requested']
                    event.value[str(p1['requesting'])] = p2
                else:
                    p1['requesting'] = None
                    p1['alert'] = Constants.alert_messages['unv_other']
            elif p1['in_trade']:
                p2 = event.value[str(p1['requested'])]
                if p1['accepted'] == 0:
                    p1['in_trade'] = False
                    p2['in_trade'] = False
                    p1['requested'] = None
                    p2['requesting'] = None
                    p1['accepted'] = 2
                    p1['alert'] = Constants.alert_messages['declining']
                    p2['alert'] = Constants.alert_messages['declined']
                elif p1['accepted'] == 1:
                    p1['in_trade'] = False
                    p2['in_trade'] = False
                    p1['requested'] = None
                    p2['requesting'] = None
                    p1['accepted'] = 2
                    temp = p1['pos']
                    p1['pos'] = p2['pos']
                    p2['pos'] = temp
                    p1['alert'] = Constants.alert_messages['accepting']
                    p2['alert'] = Constants.alert_messages['accepted']
                event.value[p1['requested']] = p2
            event.value[str(p.id_in_group)] = p1

        # broadcast the updated data out to all subjects
        self.send("swap", event.value)
    

class Subsession(BaseSubsession):
    
    def creating_session(self):
        self.group_randomly()

        for g_index, g in enumerate(self.get_groups()):
            self.session.vars[g_index] = {}
            g_data = Constants.config[g_index]
            for p in g.get_players():
                p.participant.vars['pay_rate'] = g_data[p.id_in_group - 1]['pay_rate']
                p.participant.vars['service_time'] = g_data[p.id_in_group - 1]['service_time']
                p.participant.vars['start_pos'] = g_data[p.id_in_group - 1]['start_pos']
                p.participant.vars['group'] = g_index
                p_data = {
                    'id': p.id_in_group,
                    'pos': p.participant.vars['start_pos'],
                    'in_trade': False,
                    'requested': None,
                    'requesting': None, # clicking a trade button changes this value
                    'accepted': 2, # 2 is None, 1 is True, 0 is False; clicking a yes/no button changes this value
                    'alert': Constants.alert_messages['none'],
                    'served': False,
                    'metadata': None
                }
                self.session.vars[g_index][p.id_in_group] = p_data



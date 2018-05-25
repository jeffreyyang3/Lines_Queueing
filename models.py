from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BasePlayer,
    Currency as c, currency_range
)
from otree_redwood.models import Group as RedwoodGroup
from . import config as config_py

'''
Eli Pandolfo <epandolf@ucsc.edu>
otree-redwood>=0.7.0
'''

class Constants(BaseConstants):

    name_in_url = 'Lines_Queueing'
    participation_fee = c(5)

    config, period_lengths = config_py.export_data()
    # period lengths: combined length in seconds players are in the 
    # queue room and the payoff room per period.
    
    num_rounds = len(config[0])
    num_players = sum([len(group[0]) for group in config])
    players_per_group = len(config[0][0])


    alert_messages = {
        'requested': 'You have been requested to swap',
        'requesting': 'You have requested to swap',
        'accepted': 'Your swap request has been accepted',
        'accepting': 'You have accepted a swap request',
        'declined': 'Your swap request has been declined',
        'declining': 'You have declined a swap request',
        'unv_other': 'Requestee is currently in a trade',
        'next_self': 'You have entered the service room.',
        'next_queue': 'You have advanced one position in the queue',
        'next_queue2': 'You have advanced one position in the queue ',
        'none': '',
    }

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
    time_BP = models.LongStringField()
    time_Results = models.LongStringField()

    start_pos = models.IntegerField()
    service_time = models.FloatField() # this is the time it takes them to go thru door once first in line
    pay_rate = models.FloatField()
    accumulated = models.FloatField()
    metadata = models.LongStringField()

    # bid_price = models.FloatField()

class Group(RedwoodGroup):

    def period_length(self):
        return Constants.period_lengths[self.round_number - 1]

    def queue_state(self, data):
        queue = {}
        for p in self.get_players():
            pp = data[str(p.id_in_group)]
            queue[pp['pos']] = pp['id']
        return [queue.get(k) for k in sorted(queue)]

    def _on_swap_event(self, event=None, **kwargs):

        for p in self.get_players():    
            # fields 'requesting' and  'accepted' of the person who clicked the button will be updated client-side;
            # all other fields are updated here based on the other fields' states
            # case 1: person is not in_trade and requesting someone who is not in_trade
            # case 2: person is not in_trade and requesting someone who is in_trade
            # case 3: person is in_trade and accepting
            # case 4: person is in_trade and denying
            # add other cases for next
            # Note that the JS will prevent anyone in trade from requesting another trade
            
            p1 = event.value[str(p.id_in_group)]
            g_index = p.participant.vars[self.round_number]['group']

            # someone has gone into the service room, and everyone in the queue advances one position
            if p1['next'] == True:
                if p1['pos'] == 0:
                    p1['alert'] = Constants.alert_messages['next_self']
                    if p1['in_trade']: # requested != None

                        p2_id = str(p1['requested'])
                        p2 = event.value[p2_id]
                        metadata = {}

                        p1['in_trade'] = False
                        p2['in_trade'] = False
                        p1['requested'] = None
                        p2['requesting'] = None
                        p1['accepted'] = 2 # this should be unnecessary

                        metadata['status'] = 'cancelled'
                        metadata['requester'] = p2['id']
                        metadata['requestee'] = p1['id']
                        timestamp = p2['last_trade_request']
                        p2['last_trade_request'] = None
                        event.value[p2_id] = p2
                        event.value[str(p.id_in_group)] = p1
                        metadata['queue'] = self.queue_state(event.value)
                        event.value['metadata'][timestamp] = metadata

                elif p1['pos'] > 0:
                    if p1['alert'] == Constants.alert_messages['next_queue']:
                        p1['alert'] = Constants.alert_messages['next_queue2']
                    else:
                        p1['alert'] = Constants.alert_messages['next_queue']
                    # this is the only case I know of where you can get the same alert twice in a row (except none)
                    # if you get the same alert twice in a row the alert will not display because the watch function
                    # that displays alerts only get called when the alert changes.
                else:
                    p1['alert'] = Constants.alert_messages['none']
                p1['next'] = False

            # someone has requested a trade
            elif not p1['in_trade'] and p1['requesting'] != None:
                p2 = event.value[str(p1['requesting'])]
                if not p2['in_trade']:
                    p1['in_trade'] = True
                    p2['in_trade'] = True
                    p2['requested'] = p1['id']
                    p1['alert'] = Constants.alert_messages['requesting']
                    p2['alert'] = Constants.alert_messages['requested']
                    event.value[str(p1['requesting'])] = p2
                else:
                    # unless the JS button disabling fails, this will never get executed
                    p1['requesting'] = None
                    p1['alert'] = Constants.alert_messages['unv_other']

            # someone has responded to a trade request
            elif p1['in_trade'] and p1['requested'] != None:
                if p1['accepted'] != 2:
                    
                    p2_id = str(p1['requested'])
                    p2 = event.value[p2_id]
                    metadata = {}
                    
                    if p1['accepted'] == 0:
                        p1['in_trade'] = False
                        p2['in_trade'] = False
                        p1['requested'] = None
                        p2['requesting'] = None
                        p1['accepted'] = 2
                        p1['alert'] = Constants.alert_messages['declining']
                        p2['alert'] = Constants.alert_messages['declined']

                        metadata['status'] = 'declined'
                        
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

                        metadata['status'] = 'accepted'
                        
                    metadata['requester'] = p2['id']
                    metadata['requestee'] = p1['id']
                    timestamp = p2['last_trade_request']    
                    p2['last_trade_request'] = None
                    event.value[p2_id] = p2
                    event.value[str(p.id_in_group)] = p1
                    metadata['queue'] = self.queue_state(event.value)
                    event.value['metadata'][timestamp] = metadata

            event.value[str(p.id_in_group)] = p1 # partially redundant

        # broadcast the updated data out to all subjects
        self.send("swap", event.value)

class Subsession(BaseSubsession):
    
    def creating_session(self):
        self.group_randomly()

        for g_index, g in enumerate(self.get_groups()):
            self.session.vars[self.round_number] = []
            for i in range(Constants.num_rounds):
                self.session.vars[self.round_number].append({})
            g_data = Constants.config[g_index][self.round_number - 1]
            for p in g.get_players():
                p.participant.vars[self.round_number] = {}
                p.participant.vars[self.round_number]['pay_rate'] = g_data[p.id_in_group - 1]['pay_rate']
                p.participant.vars[self.round_number]['service_time'] = g_data[p.id_in_group - 1]['service_time']
                p.participant.vars[self.round_number]['start_pos'] = g_data[p.id_in_group - 1]['start_pos']
                p.participant.vars[self.round_number]['group'] = g_index
                p_data = {
                    'id': p.id_in_group,
                    'pos': p.participant.vars[self.round_number]['start_pos'],
                    'in_trade': False,
                    'last_trade_request': None,
                    'requested': None,
                    'requesting': None, # clicking a trade button changes this value
                    'accepted': 2, # 2 is None, 1 is True, 0 is False; clicking a yes/no button changes this value
                    'alert': Constants.alert_messages['none'],
                    'num_players_queue': Constants.num_players,
                    'num_players_service': 0,
                    'next': False,
                }
                self.session.vars[self.round_number][g_index][p.id_in_group] = p_data
                self.session.vars[self.round_number][g_index]['metadata'] = {}


'''
metadata structure:
    { 'timestamp': {'status': 'accepted/declined/cancelled', 'requester': #, 'requestee': #, 'queue': [#,#,#...]}, ... }
'''



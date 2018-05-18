from ._builtin import Page, WaitPage
from .models import Constants
'''
Eli Pandolfo <epandolf@ucsc.edu>
'''

# initial instructions for the experiment
# has 1 form field, the time the page loads
class Instructions(Page):

    form_model = 'player'
    form_fields = ['time_Instructions']
    def is_displayed(self):
        return self.round_number == 1


# queue room and paying room. Because of otree-redwood's period_length
# requirement, and because the total time in both rooms is set but the time
# each player spends in each room varies, I think the best way to represent
# the rooms is with one page, and using JS to show both rooms.
class QueueService(Page):

    # does this need to be group?
    form_model = 'player'
    form_fields = ['time_Queue']

    def vars_for_template(self):
        return {
            'round_time_': Constants.period_length,
            'pay_rate_': self.participant.vars['pay_rate'],
            'service_time_': self.participant.vars['service_time'],
            'start_pos_': self.participant.vars['start_pos'],
            'round_': self.round_number,
            'num_players_': Constants.num_players,
            'data': self.session.vars[self.participant.vars['group']],
            'id': self.player.id_in_group
        }


class Results(Page):
    form_model = 'player'
    form_fields = ['time_Results']

    def is_dispalyed(self):
        return self.round_number == Constants.num_rounds


# order in which pages are displayed. A page's is_displayed method
# can override this, and not all pages defined above need to be included
page_sequence = [
    Instructions,
    QueueService,
    Results
]
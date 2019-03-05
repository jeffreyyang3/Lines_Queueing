from ._builtin import Page, WaitPage
from .models import Constants

"""
Eli Pandolfo <epandolf@ucsc.edu>
"""


class Instructions(Page):

    form_model = "player"
    form_fields = ["time_Instructions"]

    def is_displayed(self):
        # return self.round_number == 1
        return False


class QueueServiceWaitPage(WaitPage):
    pass


# queue room and service room. Because of otree-redwood's period_length
# requirement, and because the total time in both rooms is set but the time
# each player spends in each room varies, I think the best way to represent
# the rooms is with one page, and using JS to show both rooms.
class QueueService(Page):

    form_model = "player"
    form_fields = [
        "time_Queue",
        "time_Service",
        "start_pos",
        "service_time",
        "pay_rate",
        "round_payoff",
        "metadata",
        "endowment",
        "swap_method",
        "pay_method",
        "waiting_time",
    ]

    def get_timeout_seconds(self):
        g_index = self.participant.vars[self.round_number]["group"]
        return Constants.config[g_index][self.round_number - 1]["settings"]["duration"]

    def vars_for_template(self):
        g_index = self.participant.vars[self.round_number]["group"]
        return {
            "round_time_": Constants.config[g_index][self.round_number - 1]["settings"][
                "duration"
            ],
            "pay_rate_": self.participant.vars[self.round_number]["pay_rate"],
            "c_": self.participant.vars[self.round_number]["c"],
            "service_time_": self.participant.vars[self.round_number]["service_time"],
            "start_pos_": self.participant.vars[self.round_number]["start_pos"],
            "round_": self.round_number,
            "num_players_": Constants.num_players,
            "data": self.session.vars[self.round_number][g_index],
            "id": self.player.id_in_group,
            "swap_method_": Constants.config[g_index][self.round_number - 1][
                "settings"
            ]["swap_method"],
            "pay_method_": Constants.config[g_index][self.round_number - 1]["settings"][
                "pay_method"
            ],
            "discrete": Constants.config[g_index][self.round_number - 1]["settings"][
                "discrete"
            ],
            "endowment_": self.participant.vars[self.round_number]["endowment"],
        }

    def before_next_page(self):
        if self.round_number == Constants.num_rounds:
            self.player.set_payoffs()


# round debrief, displayed after queue service page. Has no specific data yet
class BetweenPages(Page):
    form_model = "player"
    form_fields = ["time_BP"]

    def vars_for_template(self):
        all_players = self.group.get_players()
        print("len of all_players is: ", len(all_players))
        print("all_players is: ", all_players)

        startLine = {}
        displayStartLine = []

        for p in all_players:
            print("p.start_pos is: ", p.start_pos)
            startLine[str(p.start_pos)] = p.id_in_group

        """

        print("start line is: ", str(startLine))

        for i in range(len(startLine)):
            displayStartLine.append(startLine[str(i + 1)])

        print("displaystartline is: ", displayStartLine)
        """

        return {
            "round": self.round_number,
            "startLine": displayStartLine,
            "numPlayers": len(all_players),
            "history": self.player.metadata,
            "id": self.player.id_in_group,
        }


# displays experiment results. Has no specific data set yet.
class Results(Page):
    form_model = "player"
    form_fields = ["time_Results"]

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


# order in which pages are displayed. A page's is_displayed method
# can override this, and not all pages defined above need to be included
page_sequence = [
    Instructions,
    QueueServiceWaitPage,
    QueueService,
    BetweenPages,
    Results,
]

#!/usr/bin/env python
# [SublimeLinter pep8-max-line-length:150]
# -*- coding: utf-8 -*-

"""
black_rhino is a multi-agent simulator for financial network analysis
Copyright (C) 2016 Co-Pierre Georg (co-pierre.georg@keble.ox.ac.uk)
Pawel Fiedor (pawel@fiedor.eu)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from abm_template.src.basemodel import BaseModel
import logging

# -------------------------------------------------------------------------
#  class Updater
# -------------------------------------------------------------------------


class Updater(BaseModel):
    #
    #
    # VARIABLES
    #
    #

    identifier = ""

    model_parameters = {}
    #
    #
    # METHODS
    #

    def get_identifier(self):
        return self.identifier

    def set_identifier(self, value):
        super(Updater, self).set_identifier(value)

    def __str__(self):
        super(Updater, self).__str__(self)

    def get_model_parameters(self):
        return self.model_parameters

    def set_model_parameters(self, values):
        super(Updater, self).set_model_parameters(values)

    def get_interactions(self):
        return self.interactions

    def interactions(self):
        super(Updater, self).interactions(self)

    def set_interactions(self, values):
        super(Updater, self).set_interactions(values)

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self, environment):
        self.environment = environment
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # do_update
    # -------------------------------------------------------------------------
    def do_update(self, environment, time):

        self.endow_returns_expectations(environment, time)

        #pre-update stuff, could also be in environment
        for fund in (environment.funds):
            fund.calc_optimal_pf(environment)
        logging.info(" Optimal portfolio for %s funds calculated", len(environment.funds))

        # Initialize investment shares:
        for i in environment.funds:
            i.endow_funds_with_shares(environment, time)
        logging.info(" Endowed funds with %s transactions and investment_shares ", len(i.accounts))

        "endow firms with equity (add transaction to accounts)"
        for i in environment.firms:
            i.endow_firms_with_equity(environment, time)
        logging.info(" Endowed firms with equity  ")

        # Now we're talking
        self.sell_ama_priced(environment, time)
        self.sell_eme_priced(environment, time)


    # -----------------------------------------------------------------------

    def sell_ama_priced(self, environment, time):
        # First, we find the market equilibrium price yay!
        # Important to note that this currently does
        # not depend on the wealth of the buyers
        # That is their demand may be higher than
        # what they can actually buy, which may be ok
        # We set the values necessary for tatonnement
        # The list of suppliers and their supply functions
        suppliers = []
        for agent in environment.firms:
            print agent.supply_of_labour
            suppliers.append([agent, agent.supply_of_labour])


    def sell_eme_priced(self, environment, time):
        pass


    #This function is used in the beginning so funds have expected returns
    def endow_returns_expectations(self, environment, time):
        for i, value in enumerate(environment.initialize_ame_returns()):
            for k, v in enumerate(environment.funds):
                if i == k:
                    dict={"r_ame" : value}
                    v.append_state_variables(dict)


        for i, value in enumerate(environment.initialize_eme_returns()):
            for k, v in enumerate(environment.funds):
                if i == k:
                    dict={"r_eme" : value}
                    v.append_state_variables(dict)


    def divide_sum(self, n, total):
    #Return a randomly chosen list of n positive integers summing to total.
    #Each such list is equally likely to occur.
        import random
        random.seed(9001)
        dividers = sorted(random.sample(xrange(1, total), n - 1))
        return [a - b for a, b in zip(dividers + [total], [0] + dividers)]

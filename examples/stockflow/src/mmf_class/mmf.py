#!/usr/bin/env python -W ignore::DeprecationWarning
# [SublimeLinter pep8-max-line-length:150]
# -*- coding: utf-8 -*-


class MMF():

    # -------------------------------------------------------------------------
    # __init__
    # -------------------------------------------------------------------------
    def __init__(self):

        self.results_df = 0
        self.identifier = ""  # identifier
        self.parameters = {}  # parameters
        self.stock_variables = {}  # stock variables
        self.stock_variables['net_income'] = 0.0

        self.parameters['Cash_share'] = 0
        self.parameters['GB_share'] = 0
        self.parameters['CB_share'] = 0

        self.parameters["institution_specific_interest_rate"] = 0.0  # interest rate
        self.parameters["dividends"] = 0.0
        self.parameters["active"] = 0  # this is a control parameter
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __del__
    # -------------------------------------------------------------------------
    def __del__(self):
        pass
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # __str__
    # returns a string describing the bank and its properties
    # based on the implementation in the abstract class
    # but adds the type of agent () and lists all transactions
    # -------------------------------------------------------------------------
    def __str__(self):

            ret_str = "  <agent identifier='" + self.identifier + "'>\n "

            for entry in self.parameters:
                value = self.parameters[entry]
                ret_str = ret_str + " <parameter type='parameters' name=" + entry + "' value='" + str(value) + "'></parameter>\n"

            for entry in self.stock_variables:
                value = self.stock_variables[entry]
                if isinstance(value, int) or isinstance(value, float) or isinstance(value, str):
                    ret_str = ret_str + "  <parameter type='stock_variables' name='" + entry + "' value='" + str(value) + "'></parameter>\n"
                else:
                    raise TypeError
            ret_str = ret_str + "</agent>\n"
            return ret_str
    # -------------------------------------------------------------------------
    # get_parameters_from_file
    # reads the specified config file given the environment
    # and sets parameters to the ones found in the config file
    # the config file should be an xml file
    # -------------------------------------------------------------------------
    def get_parameters_from_file(self,  agent_filename, environment):
        from xml.etree import ElementTree

        xmlText = open(agent_filename).read()
        element = ElementTree.XML(xmlText)
        # we get the identifier
        self.identifier = element.attrib['identifier']
        # and then we're only interested in <parameter> fields
        element = element.findall('parameter')

        # loop over all <parameter> entries in the xml file
        for subelement in element:

            if subelement.attrib['type'] == 'stock_variables':

                name = subelement.attrib['name']
                try: # we see whether the value is a float
                    value = float(subelement.attrib['value'])
                except:
                    value = str(subelement.attrib['value'])
                # add them to stock_variables list
                self.stock_variables[name] = value

            if subelement.attrib['type'] == 'parameters':
                name = subelement.attrib['name']
                value = subelement.attrib['value']
                # add them to stock_variables list
                self.parameters[name] = float(value)
    # ------------------------------------------------------------------------
    def initialize_assets(self, updater, current_step, environment):

        for dealer in environment.dealers:
            self.stock_variables['Reverse_repo'] = dealer.stock_variables['Repo']

            "****************MMF******************"
        self.stock_variables['Invshares'] =  self.stock_variables['Cash'] + self.stock_variables['Reverse_repo']
        self.stock_variables['Total_assets'] = self.stock_variables['Cash'] + self.stock_variables['Reverse_repo']
        self.stock_variables['Total_liabilities'] = self.stock_variables['Cash'] + self.stock_variables['Reverse_repo']

        self.append_results_to_dataframe(current_step)


    def profit(self, updater, environment, current_step):
        self.stock_variables['net_income'] = self.stock_variables['Reverse_repo'] * updater.i_R

        print "******* The", self.identifier, " has profit in t=", current_step, "of", self.stock_variables['net_income']
        return self.stock_variables['net_income']

    # check_consistency
    # checks whether the assets and liabilities have the same total value
    # -------------------------------------------------------------------------
    def check_consistency(self, current_step):

        print self.identifier, "total assets:", self.stock_variables['Total_assets']
        print self.identifier, "total liabilities:", self.stock_variables['Total_liabilities']

        if self.stock_variables['Total_assets'] == self.stock_variables['Total_liabilities']:
            print "balance sheet identity for", self.identifier, "in t=", current_step, "holds."
        else:
            print("ooups, balance sheet identity for %s does not hold" % self.identifier)
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def print_balance_sheet(self):
        print "***********"
        print  self.identifier,
        print "Assets:" , "\n"
        print "Cash:", self.Cash, "\n"
        print "Reverse_repo:", self.stock_variables['Reverse_repo']  , " \n"

        print  "Total:", self.stock_variables['Total_assets'] , "\n"
        print "Liabilities:" , "\n"

        print "Invshares:", self.stock_variables['Invshares'], " \n"

    def update_balance_sheets(self, updater, environment, current_step, scenario):

        if current_step > 0 and scenario=='benchmark':

            self.stock_variables['Total_assets'] = self.stock_variables['Total_assets'] + self.stock_variables['net_income']

            self.stock_variables['Cash'] = self.stock_variables['Total_assets'] - self.stock_variables['Reverse_repo']
            self.stock_variables['Invshares'] = self.stock_variables['Total_assets']
            self.stock_variables['Total_liabilities'] = self.stock_variables['Invshares']


            self.update_results_to_dataframe(current_step)


    def append_results_to_dataframe(self, current_step):
        import pandas as pd

        results_stock_variables = []
        results_stock_varnames =[]

        for i in self.stock_variables:
            if i != "does_repo":
                results_stock_varnames.append(i + " " + self.identifier)
                results_stock_variables.append(self.stock_variables[i])

        df = pd.DataFrame(columns=results_stock_varnames)
        df = df.append(pd.Series(results_stock_variables, index=results_stock_varnames), ignore_index=True)

        df2 = pd.DataFrame({'current_step':[current_step]})

        self.results_df = pd.concat([df, df2], axis=1)
        return self.results_df

    def update_results_to_dataframe(self, current_step):
        import pandas as pd

        if current_step >0:
            temp = []
            timer = []
            results_stock_variables = []

            for i in self.stock_variables:
                if i != "does_repo":
                    temp.append(self.stock_variables[i])
                    timer = current_step
            temp.append(timer)

            x = list(self.results_df.columns.values)

            dftemp = pd.DataFrame([temp], columns=x)


            self.results_df = pd.concat([self.results_df, dftemp])


    # def __getattr__(self):
    #     if the attribute isn't found by Python we tell Python
    #     to look for it first in parameters and then in stock variables
    #     which allows for directly fetching parameters from the Agent class

    def __getattr__(self, attr):
        if (attr in self.parameters) and (attr in self.stock_variables):
            raise AttributeError('The same name exists in both parameters and stock variables.')
        else:
            try:
                return self.parameters[attr]
            except:
                try:
                    return self.stock_variables[attr]
                except:
                    raise AttributeError('Agent %s has no attribute "%s".' % self.identifier, attr)
        # a standard method for retrieving items from dictionaries as class attributes

    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # functions for setting/changing id, parameters, and stock variables
    # these either return or set specific value to the above variables
    # with the exception of append (2 last ones) which append the dictionaries
    # which contain parameters or stock variables
    # -------------------------------------------------------------------------
    def get_identifier(self):
        return self.identifier

    def get_parameters(self):
        return self.parameters

    def get_stock_variables(self):
        return self.stock_variables

    # -------------------------------------------------------------------------
    # functions needed to make HF() hashable
    # -------------------------------------------------------------------------
    def __key__(self):
        return self.identifier

    def __eq__(self, other):
        return self.__key__() == other.__key__()

    def __hash__(self):
        return hash(self.__key__())
    # -------------------------------------------------------------------------

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

import os
import logging
from xml.etree import ElementTree
# -------------------------------------------------------------------------
#
#  class Environment
#
# -------------------------------------------------------------------------


class Environment(object):
    #
    #
    # VARIABLES
    #
    #
    identifier = ""  # identifier of the environment
    env_parameters = {}  # a dictionary containing all environmenet parameters

    env_parameters["num_simulations"] = 0  # number of simulations
    env_parameters["num_sweeps"] = 0  # numbers of runs in a single simulation
    env_parameters["num_agents"] = 0  # number of agents in a simulation
    env_parameters["agent_directory"] = ""  # directory containing agent xmls

    #
    # CODE
    #
    def __init__(self, environment_directory, identifier):
        self.initialize(environment_directory, identifier)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # read_xml_config_file(self, config_file_name)
    # reads an xml file with config and sets identifier and env_parameters
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def read_xml_config_file(self, env_filename):

        try:
            xmlText = open(env_filename).read()
            element = ElementTree.XML(xmlText)  # we tell python it's an xml
            self.identifier = element.attrib['identifier']

            # loop over all entries in the xml file
            for subelement in element:

                try:  # we see whether the value is a float
                    value = float(subelement.attrib['value'])
                    type = subelement.attrib['value']
                    self.env_parameters[type] = value

                except:  # if not, it is a string
                    value = str(subelement.attrib['value'])
                    self.env_parameters[type] = value

        except:
            logging.error("    ERROR: %s could not be parsed", env_filename)
    # -------------------------------------------------------------------------
    # the next function
    # initializes the environment, initializing all the variables
    # reading the env_config file from supplied environment_directory and
    # identifier, and initializes all agents from the directories
    # supplied in the main config file
    # -------------------------------------------------------------------------

    def initialize(self, environment_directory, identifier):
        self.identifier = identifier

        self.env_parameters = {}
        self.env_parameters["num_simulations"] = 0
        self.env_parameters["num_sweeps"] = 0
        self.env_parameters["num_agents"] = 0
        self.env_parameters["agent_directory"] = ""

        # first, read in the environment file
        environment_filename = environment_directory + identifier + ".xml"
        self.read_xml_config_file(environment_filename)
        logging.info(" environment file read: %s", environment_filename)

        # then read in all the agents
        if (self._directory != ""):
            if (self.agent_directory != "none"):  # none is used for tests only
                self.initialize_agents_from_files(self.agent_directory)
                logging.info("  agents read from directory: %s", self.agent_directory)

    # -------------------------------------------------------------------------
    # initialize_agents_from_files(self,  agent_directory)
    # agents have to be initialized for each simulation as a number of
    # agents might become inactive in the previous simulation
    # this reads all config files in the provided directory and
    # initializes agents with the contents of these configs
    # -------------------------------------------------------------------------
    def initialize_agents_from_files(self, agent_directory):
        from src.agent import Agent
        # this routine is called more than once, so we have to
        # reset the list of agent each time
        while len(self.agent) > 0:
            self.agent.pop()
        # we list all the files in the specified directory
        listing = os.listdir(agent_directory)
        # and check if the number of files is in line with the parameters
        if (len(listing) != self.agent):
            logging.error("    ERROR: number of configuration files in %s (=%s) does not match num_agents (=%s)",
                          agent_directory,  str(len(listing)), str(self.num_agents))
        # we read the files sequentially
        for infile in listing:
            agent = Agent()
            agent.get_parameters_from_file(agent_directory + infile,  self)
            # and read parameters to the agents, only to add them
            # to the environment
            self.agent.append(agent)
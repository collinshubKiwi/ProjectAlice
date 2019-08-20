# -*- coding: utf-8 -*-

import json
import os
import requests
import random

from terminaltables import DoubleTable

from core.console.Command import Command
from core.console.input.InputArgument import InputArgument
from core.console.input.InputOption import InputOption
from core.snips.SamkillaManager import SamkillaManager
from core.base.ModuleManager import ModuleManager
from core.snips.SnipsConsoleManager import SnipsConsoleManager
from core.voice.LanguageManager import LanguageManager
from core.util.ThreadManager import ThreadManager
from core.util.DatabaseManager import DatabaseManager
from core.dialog.ProtectedIntentManager import ProtectedIntentManager
from core.base.ConfigManager import ConfigManager
from core.user.UserManager import UserManager
from core.base.model.GithubCloner import GithubCloner

#
# ModuleIntentListCommand list modules from dedicated repository
#
class ModuleIntentListCommand(Command):

	DESCRIPTION_MAX = 100

	def __init__(self):
		super().__init__()

		configManager = ConfigManager(self)
		configManager.onStart()

		languageManager = LanguageManager(self)
		languageManager.onStart()

		threadManager = ThreadManager(self)
		threadManager.onStart()

		protectedIntentManager = ProtectedIntentManager(self)
		protectedIntentManager.onStart()

		databaseManager = DatabaseManager(self)
		databaseManager.onStart()

		userManager = UserManager(self)
		userManager.onStart()

		moduleManager = ModuleManager(self)
		moduleManager.onStart()

		snipsConsoleManager = SnipsConsoleManager(self)
		snipsConsoleManager.onStart()

		samkillaManager = SamkillaManager(self)

		self._slotTypesModulesValues, self._intentsModulesValues, self._intentNameSkillMatching = samkillaManager.getDialogTemplatesMaps(
			runOnAssistantId=languageManager.activeSnipsProjectId,
			languageFilter=languageManager.activeLanguage
		)

	def create(self):
		self.setName('module:intent:list')
		self.setDescription('List intents and utterances for a given module')
		self.setDefinition([
			InputArgument(name='moduleName', mode=InputArgument.REQUIRED, description='Module\'s name'),
			InputOption(name='--full', shortcut='-f', mode=InputOption.VALUE_NONE, description='Display full description instead of truncated one'),
			InputOption(name='--intent', shortcut='-i', mode=InputOption.VALUE_OPTIONAL, description='Show more data about specific intent'),
		])
		self.setHelp('> The %command.name% list intents and utterances for a given module:\n'
					 '  <fg:magenta>%command.full_name%<fg:reset> <fg:cyan>moduleName<fg:reset> <fg:yellow>[-f|--full]<fg:reset> <fg:yellow>[-i|--intent=intentName]<fg:reset>')

	def execute(self, input):
		TABLE_DATA = [['Intents of module ' + input.getArgument('moduleName')]]
		table_instance = DoubleTable(TABLE_DATA)
		self.write('\n' + table_instance.table + '\n', 'yellow')



		if input.getOption('intent'):
			return self.intentMode(input)

		return self.moduleMode(input)


	def intentMode(self, input):
		TABLE_DATA = [['Utterances']]
		table_instance = DoubleTable(TABLE_DATA)

		intentFound = False

		for dtIntentName, dtModuleName in self._intentNameSkillMatching.items():
			if dtIntentName == input.getOption('intent'):
				intentFound = True

				for utterance, _ in self._intentsModulesValues[dtIntentName]['utterances'].items():
					tDesc = utterance

					if not input.getOption('full'):
						tDesc = (tDesc[:self.DESCRIPTION_MAX] + '..') if len(tDesc) > self.DESCRIPTION_MAX else tDesc

					TABLE_DATA.append([
						'-' if len(tDesc) == 0 else tDesc
					])

		if not intentFound:
			self.nl()
			self.write('No intent found')
			self.nl()
			return

		self.write(table_instance.table)

	def moduleMode(self, input):
		TABLE_DATA = [['Intent', 'Description']]
		table_instance = DoubleTable(TABLE_DATA)

		moduleFound = False

		for dtIntentName, dtModuleName in self._intentNameSkillMatching.items():
			if dtModuleName == input.getArgument('moduleName'):
				moduleFound = True
				tDesc = self._intentsModulesValues[dtIntentName]['__otherattributes__']['description']

				if not input.getOption('full'):
					tDesc = (tDesc[:self.DESCRIPTION_MAX] + '..') if len(tDesc) > self.DESCRIPTION_MAX else tDesc

				TABLE_DATA.append([
					dtIntentName,
					'-' if len(tDesc) == 0 else tDesc
				])

		if not moduleFound:
			self.nl()
			self.write('No intent found')
			self.nl()
			return

		self.write(table_instance.table)
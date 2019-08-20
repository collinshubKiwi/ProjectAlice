# -*- coding: utf-8 -*-

import logging

import os
import requests
import shutil
import json

class GithubCloner:

	NAME = 'GithubCloner'

	def __init__(self, baseUrl: str, path: str, dest: str):
		self._logger = logging.getLogger('ProjectAlice')
		self._baseUrl = baseUrl
		self._path = path
		self._dest = dest


	def clone(self) -> bool:
		if os.path.isdir(self._dest):
			self._cleanDestDir()
		else:
			os.mkdir(self._dest)

		try:
			return self._doClone(os.path.join('https://api.github.com', self._baseUrl, self._path))
		except Exception as e:
			return False


	def _doClone(self, url):
		try:
			req = requests.get(url)
			result = req.content
			data = json.loads(result.decode())
			for item in data:
				path = item['path'].split('/')[3:]
				path = '/'.join(path)
				if item['type'] == 'file' and not path.endswith('.install'):
					fileStream = requests.get(item['download_url'])

					with open(os.path.join(self._dest, path), 'wb') as f:
						f.write(fileStream.content)

				elif item['type'] == 'dir':
					os.mkdir(os.path.join(self._dest, path))
					self._doClone(url = os.path.join(url, path))

		except Exception as e:
			self._logger.error('[{}] Error downloading module: {}'.format(self.NAME, e))
			raise

		return True


	def _cleanDestDir(self):
		filesToDelete = list()
		directoriesToDelete = list()
		for file in os.listdir(self._dest):
			filename = os.fsdecode(file)
			if (os.path.isdir(os.path.join(self._dest, filename)) and not filename.startswith('_')) or filename == '__pycache__':
				directoriesToDelete.append(filename)
			elif not os.path.isfile(os.path.join(self._dest, filename + '.dist')) and not filename.endswith('.conf'):
				filesToDelete.append(filename)

		# Not deleting directories and files directly because they are needed for the .dist check
		for directory in directoriesToDelete:
			shutil.rmtree(os.path.join(self._dest, directory))

		for file in filesToDelete:
			os.remove(os.path.join(self._dest, file))
import os
import sys

import yaml

from shared import GITHUB_USERNAME

from typing import Dict, Iterable, List, Optional, TypedDict

ProjectText = TypedDict('ProjectText', { 'header': str, 'title': str, 'content': str, 'alt': str, 'description': Optional[str] })
ProjectURLs = TypedDict('ProjectURLs', { 'source': str })
ProjectSource = TypedDict('ProjectURLs', { 'repo': Optional[str], 'gist': Optional[str] })
Project = TypedDict('Project', { 'slug': str, 'definitions': List[str], 'source': Optional[ProjectSource], 'urls': ProjectURLs, 'text': ProjectText })


ProjectsIterable = Iterable[Project]

IMAGE_LINKABLE = ['href', 'video', 'external_video']

URL_ORDER = ['live', 'source', 'video', 'external_video', 'image']


SOURCE_PREFIXES = {
	'repo': 'https://github.com/' + GITHUB_USERNAME + '/',
	'gist': 'https://gist.github.com/' + GITHUB_USERNAME + '/'
}


def get_project_page_path(slug: str):
	return os.path.join('docs', 'projects', slug + '.md')


def load_projects(input_filepath: str) -> ProjectsIterable:
	"""Load and populate Projects from input_filepath."""
	with open(input_filepath, 'r') as file:
		raw_projects: Dict[str, Project] = yaml.safe_load(file)

	for slug, project in raw_projects.items():
		project['slug'] = slug

		if 'source' not in project.setdefault('urls', {}) and 'source' in project:
			source_type, source = list(project['source'].items())[0]  # type: ignore
			project.setdefault('urls', {})['source'] = SOURCE_PREFIXES.get(source_type, '') + source  # type: ignore


		project.setdefault('definitions', [])
		references: Dict[str, str] = {}
		for key, url in project['urls'].items():
			reference = f'{slug} {key}'
			references[key] = reference
			project['definitions'].append(f'[{reference}]: {url}')


		if title := project['text'].get('title', None):
			project['text']['header'] = f'[{title}]({get_project_page_path(slug)}) <sup>[&#x1F5D7;][{references["source"]}]</sup>'


		if 'image' in project['urls']:
			alt_text = project['text'].get('alt', '')

			if alt_text:
				image_referece_key = list(references.keys()).index('image')
				project['definitions'][image_referece_key] += f' "{alt_text}"'

			markdown = f'![{alt_text}][{references["image"]}]'
			for key in IMAGE_LINKABLE:
				if key in project['urls']:
					markdown = f'[{markdown}][{references[key]}]'
					break

			project['text']['content'] = markdown
		if 'content' not in project['text']:
			project['text']['content'] = project['text']['alt']

		project['urls'] = dict(sorted(  # type: ignore
			project['urls'].items(),
			key = lambda pair: URL_ORDER.index(pair[0]) if pair[0] in URL_ORDER else sys.maxsize
		))

		yield project

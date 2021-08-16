import yaml

from shared import GITHUB_USERNAME

from typing import Dict, Iterable, List, Optional, Tuple, TypedDict

ProjectText = TypedDict('ProjecText', { 'header': str, 'content': str })
ProjectURLs = TypedDict('ProjectURLs', { 'source': str })
ProjectSource = TypedDict('ProjectURLs', { 'repo': Optional[str], 'gist': Optional[str], 'url': Optional[str] })
Project = TypedDict('Project', { 'slug': str, 'definitions': List[str], 'source': ProjectSource, 'urls': ProjectURLs, 'text': ProjectText })


ProjectsIterable = Iterable[Project]



SOURCE_PREFIXES = {
	'repo': 'https://github.com/' + GITHUB_USERNAME + '/',
	'gist': 'https://gist.github.com/' + GITHUB_USERNAME + '/'
}


def load_projects(input_filepath: str) -> ProjectsIterable:
	"""Load and populate Projects from input_filepath."""
	with open(input_filepath, 'r') as file:
		raw_projects: Dict[str, Project] = yaml.safe_load(file)

	for slug, project in raw_projects.items():
		project['slug'] = slug

		source_type, source = list(project['source'].items())[0]
		project.setdefault('urls', {})['source'] = SOURCE_PREFIXES.get(source_type, '') + source  # type: ignore


		project.setdefault('definitions', [])
		references: Dict[str, str] = {}
		for key, url in project['urls'].items():
			reference = f'{slug} {key}'
			references[key] = reference
			project['definitions'].append(f'[{reference}]: {url}')


		if title := project['text'].get('title', None):
			project['text']['header'] = f'[{title}][{references["source"]}]'


		if 'image' in project['urls']:
			raw_url = project['definitions'][list(references.keys()).index('image')].split(']: ')[1]
			alt_text = raw_url.split('"')[1] if '"' in raw_url else ''

			markdown = f'![{alt_text}][{references["image"]}]'
			if 'href' in project['urls']:
				markdown = f'[{markdown}][{references["href"]}]'

			project['text']['content'] = markdown

		yield project

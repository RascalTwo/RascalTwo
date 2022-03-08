"""
Automatically update Projects markdown section from data
"""
import sys

import yaml

from shared import insert_template
from projects import Project, load_projects, get_project_page_path

from typing import Dict, List


def generate_project_page(project: Project):
	"""Generate markdown page for project."""
	markdown = '\n'.join(project['definitions']) + '\n\n'
	markdown += '# ' + project['text']['title'] + '\n\n'


	# Table of URLs
	headers: List[str] = []
	for key in project['urls'].keys():
		headers.append(f'[{key.capitalize().replace("_", " ")}][{project["slug"]} {key}]')
	markdown += '| ' + ' | '.join(headers) + ' |\n'
	markdown += '| ' + ' | '.join('-' for _ in range(len(headers))) + ' |\n\n'

	has_image = 'image' in project['urls']

	# Use description if available, fallback to alt text if not used by image
	if desc := project['text'].get('description', project['text']['alt'] if not has_image else None):
		markdown += desc + '\n\n'


	# Media - video or image
	direct_video_url = project['urls'].get('video', None)
	if direct_video_url and 'raw.githubusercontent' not in direct_video_url:
		markdown += direct_video_url
	elif '![' in project['text']['content']:
		markdown += project['text']['content']
	elif has_image:
		markdown += f'![{project["text"]["alt"]}][{project["slug"]} image]'


	with open(get_project_page_path(project['slug']), 'w') as markdown_file:
		markdown_file.write(markdown.strip() + '\n')


def generate_projects(input_filepath: str, projects: Dict[str, Project]):
	"""Generate projects Markdown from the YAMl at input_filepath."""
	with open(input_filepath, 'r') as file:
		data: Dict[str, List[str]] = yaml.safe_load(file)

	html: str = ''

	for category, slugs in data.items():
		definitions: List[str] = []

		headers: List[str] = []
		alignments: List[str] = []
		contents: List[str] = []
		for slug in slugs:
			project = projects.get(slug, None)
			if not project:
				print(f'Project could not be found: "{slug}"')
				sys.exit(1)
			definitions += project['definitions']

			header, content = project['text']['header'], project['text']['content']
			width = len(max(header, content, key = lambda string: len(string)))
			headers.append(header.center(width))
			alignments.append(':' + '-'.center(width - 2, '-') + ':')
			contents.append(content.center(width))

		table = '\n'.join('| ' + ' | '.join(row) + ' |' for row in (headers, alignments, contents))

		html += '\n'.join(definition for definition in definitions if definition.split(':')[0] in table) + '\n\n'
		html += f'<details open>\n  <summary>{category}</summary>\n\n{table}\n\n</details>\n\n'

	return html.strip()


if __name__ == '__main__':
	projects = list(load_projects('./data/projects.yaml'))

	html = generate_projects(
		'./data/project_categories.yaml',
		dict(
			(project['slug'], project)
			for project in projects
		)
	)
	insert_template('PROJECTS', html)


	for project in projects:
		generate_project_page(project)

"""
Automatically update Projects markdown section from data
"""
import sys

import yaml

from shared import insert_template
from projects import Project, load_projects

from typing import Dict, List


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

		html += '\n'.join(definitions) + '\n\n'
		html += f'<details open>\n  <summary>{category}</summary>\n\n{table}\n\n</details>\n\n'

	return html.strip()


if __name__ == '__main__':
	html = generate_projects(
		'./data/project_categories.yaml',
		dict(
			(project['slug'], project)
			for project in load_projects('./data/projects.yaml')
		)
	)
	insert_template('PROJECTS', html)

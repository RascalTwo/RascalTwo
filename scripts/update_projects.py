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


def get_techs():
	with open('./data/technologies.yaml', 'r') as file:
		data: Dict[str, Dict[str, Technology]] = yaml.safe_load(file)

	for technologies in data.values():
		for slug, technology in technologies.items():
			yield { 'slug': slug, **technology }

def generate_projects(order_filepath: str, projects: Dict[str, Project]):
	"""Generate projects Markdown from the YAMl at order_filepath."""
	with open(order_filepath, 'r') as file:
		order: List[str] = yaml.safe_load(file)
	
	techs = list(get_techs())

	html = '\n<table bordercolor="#33bef5">\n'
	rows: List[str] = []
	row = ['  <tr>']
	for slug in order[:6]:
		project = projects.get(slug, None)
		if not project:
			continue
		print(project['slug'])
		media_is_video = project['urls'].get('video', '').endswith('mp4')
		source_html = f'        <a href="{project["urls"]["source"]}" target="_blank">\n          <img src="https://img.shields.io/badge/-Repo-000?style=for-the-badge&logo=Github&logoColor=white" />\n        </a>\n' if 'source' in project["urls"] else ''
		live_html = f'        <a href="{project["urls"]["live"]}" target="_blank">\n          <img src="https://img.shields.io/badge/-Website-fff?style=for-the-badge&logo=Wordpress&logoColor=black" />\n        </a>\n' if 'live' in project['urls'] else ''
		tech_slugs = project['tags']['technologies'].split(' ')
		ptechs = []
		for slug in tech_slugs:
			for tech in techs:
				if tech['slug'] == slug:
					ptechs.append(tech['name'])
					break
		
		row.append('    <td width="50%" valign="top">\n'
f'      <h3 align="center">{project["text"]["title"]}</h3>\n'
'      <br />\n'
f'      <a href="{project["urls"].get("live", project["urls"]["source"])}" target="_blank">\n'
f'        <{"video" if media_is_video else "img"} src="{project["urls"]["video" if media_is_video else "image"]}" />\n'
'      </a>\n'
'      <br />\n'
'      <p align="center">\n' + source_html + live_html + 
'      </p>\n'
'      <p>\n'
f'        <strong>{", ".join(ptechs[:-1]) + ", and " + ptechs[-1]}</strong> - {project["text"].get("description", project["text"]["alt"])}\n'
'      </p>\n'
'    </td>')
		print(len(row))
		if len(row) == 3:
			row.append('  </tr>')
			rows.append('\n'.join(row))
			row = ['  <tr>']
	if len(rows) == 4:
		row.append('  </tr>')
		rows.append('\n'.join(row))
		row = []

	html += '\n'.join(rows) + '\n</table>\n\n'

	definitions: List[str] = []

	headers: List[str] = []
	alignments: List[str] = []
	contents: List[str] = []

	for slug in order[6:]:
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

	html += table + '\n\n'

	html += '\n'.join(definition for definition in definitions if definition.split(':')[0] in html) + '\n\n'

	return html.strip()


if __name__ == '__main__':
	projects = list(load_projects('./data/projects.yaml'))

	html = generate_projects(
		'./data/order.yaml',
		dict(
			(project['slug'], project)
			for project in projects
		)
	)
	insert_template('PROJECTS', html)


	for project in projects:
		generate_project_page(project)

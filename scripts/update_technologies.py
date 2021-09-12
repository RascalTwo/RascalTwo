"""
Automatically update Technoloogies markdown section from data
"""
import yaml

import string

from shared import insert_template

from typing import Dict, Optional, TypedDict

Technology = TypedDict('Technology', { 'image': str, 'name': str, 'query': Optional[str] })



QUERY_PREFIX = 'https://github.com/search?q=user%3ARascalTwo'


def generate_technologies(input_filepath: str):
	"""Generate technologies HTML from the YAMl at input_filepath."""
	with open(input_filepath, 'r') as file:
		data: Dict[str, Dict[str, Technology]] = yaml.safe_load(file)

	html: str = ''

	for category, technologies in data.items():
		section = f'<table>\n  <tr><td>{category}</td></tr>\n  <tr>'
		for technology in technologies.values():
			image, name, query, background = technology['image'], technology['name'], technology.get('query', None), technology.get('background', 'dark')

			td_styles = '' if background == 'dark' else ' class="color-bg-tertiary"'
			section += f'\n    <td>\n      <table>\n        <tr>\n          <td{td_styles}>\n            '
			section += f'<img height="100px" src="{image}" alt="{name}" title="{name}" />'
			section += '\n          </td>\n        </tr>\n        <tr>\n          <td>\n            <p align="center">\n              '

			if query:
				section += f'<a href="{QUERY_PREFIX}{string.Template(query).substitute(n=name)}">\n                {name}\n              </a>'
			else:
				section += f'{name}'

			section += '\n            </p>\n          </td>\n        </tr>\n      </table>\n    </td>'

		html += f'{section}\n  </tr>\n</table>\n\n'

	return html.strip()


if __name__ == '__main__':
	html = generate_technologies('./data/technologies.yaml')
	insert_template('TECHNOLOGIES', html)

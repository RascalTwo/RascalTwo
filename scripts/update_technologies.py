"""
Automatically update Markdown files from data files
"""
import yaml

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
			image, name, query = technology['image'], technology['name'], technology.get('query', None)

			section += '\n    <td>\n      <table>\n        <tr>\n          <td>\n            '
			section += f'<img height="100px" src="{image}" alt="{name}" title="{name}" />'
			section += '\n          </td>\n        </tr>\n        <tr>\n          <td>\n            <p align="center">\n              '

			if query:
				section += f'<a href="{QUERY_PREFIX}{query}">\n                {name}\n              </a>'
			else:
				section += f'{name}'

			section += '\n            </p>\n          </td>\n        </tr>\n      </table>\n    </td>'

		html += f'{section}\n  </tr>\n</table>\n\n'

	return html.strip()


def insert_template(template: str, content: str):
	"""Insert content into template in file."""
	with open('./README.md', 'r') as file:
		raw_markdown = file.read()

	# Begin and End HTML comment tags
	tags = [f'<!-- {template} {suffix} -->' for suffix in ['BEGIN', 'END']]
	# Location of last character of start tag
	start = raw_markdown.index(tags[0]) + len(tags[0])
	# Get prefix of tag line, to maintain indentation level
	prefix = raw_markdown[raw_markdown.rfind('\n', 0, start) + 1:start].replace(tags[0], '')

	markdown = list(raw_markdown)
	# Set content at correct position to all linex prefixed accordingly
	markdown[start + 1:raw_markdown.index(tags[1])] = '\n'.join([
		(prefix + line) if line else line
		for line in content.split('\n')
	]) + '\n' + prefix

	with open('README.md', 'w') as f:
		f.write(''.join(markdown))


if __name__ == '__main__':
	html = generate_technologies('./data/technologies.yaml')
	insert_template('TECHNOLOGIES', html)

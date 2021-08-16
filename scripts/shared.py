GITHUB_USERNAME = 'RascalTwo'


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

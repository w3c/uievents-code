import os.path
import re
import subprocess
import sys

def error(msg):
	print 'Error: %s' % (msg)
	sys.exit(1)

class Parser():
	"""Parser for uievents-code spec."""

	def __init__(self):
		self.in_table = False

		self.code = ''
		self.desc = ''

	def table_row(self):
		if self.code == '':
			return ''

		return (
			'<tr><td class="code-table-code"><code class="code" id="code-%s">"%s"</code></td>\n'
			'<td>%s</td></tr>\n') % (self.code, self.code, self.desc)

	def process_text(self, desc):
		m = re.match(r'^(.*)CODE{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = '%s<code class="code">"<a href="#code-%s">%s</a>"</code>%s' % (pre, name, name, post)

		m = re.match(r'^(.*)CODE_NOLINK{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="code">"' + name + '"</code>' + post

		m = re.match(r'^(.*)KEY{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = '%s<code class="key">"<a href="http://www.w3.org/TR/uievents-key/#key-%s">%s</a>"</code>%s' % (pre, name, name, post)

		m = re.match(r'^(.*)KEY_NOLINK{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = '%s<code class="key">"%s"</code>%s' % (pre, name, post)

		m = re.match(r'^(.*)KEYCAP{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="keycap">' + name + '</code>' + post

		m = re.match(r'^(.*)GLYPH{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="glyph">"' + name + '"</code>' + post

		m = re.match(r'^(.*)UNI{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="unicode">' + name + '</code>' + post

		m = re.match(r'^(.*)PHONETIC{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<span class="unicode">' + name + '</span>' + post

		return desc

	def process_line(self, line):
		m = re.match(r'^.*CODE (\w+)\s*(.*)$', line)
		if m:
			# Write out previous code.
			result = self.table_row()
			self.code = m.group(1)
			self.desc = self.process_text(m.group(2))
			return result

		m = re.match(r'^.*BEGIN_CODE_TABLE ([a-z0-9-]+) \"(.*)\"', line)
		if m:
			self.code = ''
			self.in_table = True
			name = m.group(1)
			caption = m.group(2)
			return (
				'<table id="table-key-code-%s" class="data-table full-width">\n'
				'<caption>%s</caption>\n'
				'<thead><tr><th style="width:20%%">Code Value</th><th style="width:80%%">Notes (Non-normative)</th></tr></thead>\n'
				'<tbody>\n') % (name, caption)

		m = re.match(r'^.*END_CODE_TABLE', line)
		if m:
			self.in_table = False
			return self.table_row() + '</tbody></table>\n'

		if self.in_table:
			self.desc += self.process_text(line)
			return ''

		return self.process_text(line)

	def process(self, src, dst):
		if not os.path.isfile(src):
			error('File "%s" doesn\'t exist' % src)

		try:
			infile = open(src, 'r')
		except IOError as e:
			error('Unable to open "%s" for reading: %s' % (src, e))

		try:
			outfile = open(dst, 'w')
		except IOError as e:
			error('Unable to open "%s" for writing: %s' % (dst, e))

		for line in infile:
			new_line = self.process_line(line)
			outfile.write(new_line)

		outfile.close()
		infile.close()


def main():
	infilename = 'index-source.txt'
	outfilename = 'index.bs'

	# Generate the full bikeshed file.
	parser = Parser()
	parser.process(infilename, outfilename)

	subprocess.call(["bikeshed"])

if __name__ == '__main__':
	main()

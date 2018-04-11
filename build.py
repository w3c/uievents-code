import os.path
import re
import subprocess
import sys

USER_AGENTS = ['Chrome', 'Edge', 'Firefox', 'Safari']


def error(msg):
	print 'Error: %s' % (msg)
	sys.exit(1)

class Parser():
	"""Parser for uievents-code spec."""

	def __init__(self):
		self.in_table = False

		self.code = None
		self.desc = ''

		# Only used for IMPL tables
		self.in_impl_table = False
		self.impl_info = {}
		self.impl_notes = ''
		self.impl_section = False
		self.impl_section_name = ''

	def table_row(self):
		if self.code == None:
			return ''

		return (
			'<tr><td class="code-table-code"><code class="code" id="code-%s">"%s"</code></td>\n'
			'<td>%s</td></tr>\n') % (self.code, self.code, self.desc)

	def table_row_impl(self):
		if self.impl_section:
			return '<tr><td style="background-color: #B9C9FE" colspan="6">%s</td></tr>\n' % self.impl_section_name

		if self.code == None:
			return ''

		result = '<tr><td class="key-table-key">'
		result += '<a href="https://w3c.github.io/uievents-code/#code-%s">' % self.code
		result += '<code class="code">"%s"</code>' % self.code
		result += '</a>'
		result += '</td>\n'
		for ua in USER_AGENTS:
			value = self.impl_info[ua]
			data = ''
			if value == 'Y':
				data = '<span class="code-impl-yes">Yes</span>'
			elif value == 'N':
				data = '<span class="code-impl-no">No</span>'
			else:
				data = '<span>?</span>'
			result += '<td class="code-impl-data">%s</td>' % (data)
		notes = self.impl_notes
		if notes == None:
			notes = ''
		result += '<td>%s</td>' % notes
		result += '</tr>\n'
		return result

	def process_text(self, desc):
		has_newline = False
		if desc[-1:] == '\n':
			has_newline = True
		
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
			if name[0:2] != 'U+':
				error('Invalid Unicode value (expected U+xxxx): %s\n' % name)
			desc = pre + '<code class="unicode">' + name + '</code>' + post

		m = re.match(r'^(.*)PHONETIC{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<span class="unicode">' + name + '</span>' + post

		if has_newline and desc[-1:] != '\n':
			desc += '\n'
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
			self.code = None
			self.in_table = True
			name = m.group(1)
			caption = m.group(2)
			return (
				'<table id="table-key-code-%s" class="data-table full-width">\n'
				'<caption>%s</caption>\n'
				'<thead><tr><th style="width:20%%">{{KeyboardEvent}} {{KeyboardEvent/code}}</th><th style="width:80%%">Notes (Non-normative)</th></tr></thead>\n'
				'<tbody>\n') % (name, caption)

		m = re.match(r'^.*END_CODE_TABLE', line)
		if m:
			result = self.table_row()
			self.code = None
			self.in_table = False
			return result + '</tbody></table>\n'

		pattern = r'^\s*CODE_IMPL(?P<nolink>_NOLINK)? (?P<code>[\w-]+)'
		for ua in USER_AGENTS:
			pattern += r'\s+(?P<%s>[YN\?\-])' % ua
		pattern += r'\s*(?P<Notes>\w.*)?$'
		m = re.match(pattern, line)
		if m:
			# Write previous row.
			result = self.table_row_impl()
			self.code = m.group('code')
			self.nolink = m.group('nolink')
			self.impl_info = {}
			self.impl_section = False
			for ua in USER_AGENTS:
				self.impl_info[ua] = m.group(ua)
			self.impl_notes = m.group('Notes')
			return result

		m = re.match(r'^\s*CODE_IMPL_SECTION (.+)$', line)
		if m:
			result = self.table_row_impl()
			self.code = None
			self.impl_section = True
			self.impl_section_name = m.group(1)
			return result

		m = re.match(r'^\s*BEGIN_CODE_IMPL_TABLE ([a-z0-9-]+)', line)
		if m:
			self.code = None
			self.in_impl_table = True
			name = m.group(1)
			header = '<thead><tr><th>[=code attribute value=]</th>'
			for ua in USER_AGENTS:
				header += '<th class="code-impl-data">%s</th>' % ua
			header += '<th>Notes</th></tr></thead>\n'
			return (
				'<table id="code-table-%s" class="data-table full-width">\n'
				'%s'
				'<tbody>\n') % (name, header)

		m = re.match(r'^\s*END_CODE_IMPL_TABLE', line)
		if m:
			result = self.table_row_impl()
			self.code = None
			self.in_impl_table = False
			return result + '</tbody></table>\n'

		if self.in_table:
			self.desc += self.process_text(line)
			return ''

		if self.in_impl_table:
			m = re.match(r'^(\s*)(<!--.+-->)?(\s*)$', line)
			if m:
				return ''
			print '*** ERROR *** unrecognized line in IMPL table: ' + line
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
	files = [
		['index-source.txt', 'index.bs'],
		['impl-report.txt', 'impl-report.bs'],
	]
	
	# Generate the full bikeshed file.
	parser = Parser()
	for f in files:
		src = f[0]
		dst = f[1]
		
		print 'Pre-processing %s -> %s' % (src, dst)
		parser.process(src, dst)

		print 'Bikeshedding %s...' % dst
		subprocess.call(["bikeshed", "spec", dst])

if __name__ == '__main__':
	main()

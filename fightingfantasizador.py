import sys
import re
import random

re_sections = re.compile("::([^\[<]*)\s*(?:\[(.*)\])?\s*(?:<(\d+,\d+)>)?")
re_choices = re.compile("\[\[(.*?)(?:(?:->|\|)(.*))?\]\]")


def cleanup_text(text):
    return text[0].lower() + text[1:].rstrip(".")

class Section:
    def __init__(self, title, tags, position):
        self.title = title
        self.tags = tags
        self.position = position
        self.lines = []

    def append(self, line):
        self.lines.append(line)

    def __repr__(self):
        return repr(dict(title=self.title, tags=self.tags,
            position=self.position, lines=self.lines))

    def dump(self, converted=None):
        if self.title in converted:
            title = converted[self.title]
            tags = self.title
            position = self.position
        else:
            title = self.title
            tags = self.tags
            position = self.position
        ret = "::" + title

        if tags:
            ret += " [%s]" % tags
        if position:
            ret += " <%s>" % position
        ret += "\n"

        if converted and title not in ("StoryTitle", "Twee2Settings"):
            n = int(title)
            if n > 1:
                ret += "[[<<|%d]] " % (n - 1)
            ret += "%d" % n
            if n < len(converted):
                ret += " [[>>|%d]]" % (n + 1)
            ret += "\n"

        options = []
        for line in self.lines:
            line_match = re_choices.match(line)
            if line_match:
                text, link = line_match.groups()
                if converted:
                    options.append((text, link))
                else:
                    ret += line + "\n"
            else:
                ret += line + "\n"

        for text, link in options:
            if not link:
                link = text
            text = cleanup_text(text)
            if converted:
                if link in converted:
                    link = converted[link]
            if len(options) > 1:
                ret += "Si "
            ret += "%s, pasá a %s.\n" % (text, link)
        return ret

sections = {}
current_section = ""

for line in sys.stdin.readlines():
    line = line.strip()
    match = re_sections.match(line)
    if match:
        title, tags, position = match.groups()
        title = title.strip()
        current_section = title
        sections[current_section] = Section(title, tags, position)
    else:
        sections[current_section].append(line)


keys = list(sections.keys())
keys.remove("StoryTitle")
keys.remove("Twee2Settings")
start = keys.pop(0)
random.shuffle(keys)
keys.insert(0, start)


converted = { section:str(n+1) for n, section in enumerate(keys)}

for s in sections.values():
    print(s.dump(converted))

import re

def wordWrap (text, width):
    words = re.findall(r'\w+', text)

    lines = []

    rem = width
    curr = ""
    for i, word in enumerate(words):
        l = len(word)
        if l < rem:
            curr += " {}".format(word) if i != 0 else word
            rem -= l + 1
        else:
            lines.append(curr)
            curr = "{}".format(word)
            rem = width - l
    lines.append(curr)
    return lines

def change_lines_starting_with(text, start, new_line_content):
    """changes the line in text starting with a given string start.
    Replaces it with new_line_content. Return the altered text."""
    return "\n".join(
        line if not line.startswith(start) else new_line_content
        for line in text.splitlines())


def extract_lines(text, from_line, to_line):
    """Extracts the lines from the text, and return a new text"""
    return "\n".join(text.splitlines()[from_line:to_line])

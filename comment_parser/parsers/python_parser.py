#!/usr/bin/python
"""This module provides methods
for parsing comments from Python."""

from comment_parser.parsers import common as common
import tokenize
import ast
import io


def extract_comments(filename):
    """Extracts a list of comments from the given Python source file.

        Comments are represented with the Comment class found in the common module.
        Python comments come in two forms, single and multi-line comments.
            - Single-line comments begin with '#' and continue to the end of line.
            - Multi-line comments are enclosed within triple double quotes as docstrings and can span
                multiple lines of code.

        Note that this doesn't take language-specific preprocessor directives into
        consideration.

        Args:
            filename: String name of the file to extract comments from.
        Returns:
            Python list of common.Comment in the order that they appear in the file.
        Raises:
            common.FileError: File was unable to be open or read.
        """
    try:
        comments = []
        # Parse single line comments
        with open(filename, 'r') as source_file:
            file_contents = source_file.read()
            buf = io.StringIO(file_contents)
            for token_type, token, start, end, line in tokenize.generate_tokens(buf.readline):
                if token_type == tokenize.COMMENT:
                    token = token.replace('#', '', 1)
                    # Create comment using token and line number
                    comment = common.Comment(token, start[0])
                    comments.append(comment)

            # Parse multi-line comments/docstrings
            module = ast.parse(file_contents)
            for node in ast.walk(module):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                        token = node.body[0].value.s
                        # Find beginning of comment
                        end_line = node.body[0].value.lineno
                        line_count = token.count('\n')
                        start_line = end_line - line_count
                        # Create comment using token and line number
                        comment = common.Comment(token, start_line, multiline=True)
                        comments.append(comment)

            source_file.close()
        return comments
    except OSError as exception:
        raise common.FileError(str(exception))

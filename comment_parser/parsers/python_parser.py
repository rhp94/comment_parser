#!/usr/bin/python
"""This module provides methods
for parsing comments from Python."""

from comment_parser.parsers import common as common
import tokenize
import ast
import asttokens
import io
import re


def parse_single_line_comments(file_contents, comments, end_lines_dict):
    """ Extracts single line comments and adds them to a list.
        Also stores line numbers on which the comments occur.

        Args:
            file_contents: (str) from which to extract comments
            comments: list of comments. Each entry is a Comment class object
            end_lines_dict:
                key - line number on which a comment occurs
                value - index of comment
    """
    buf = io.StringIO(file_contents)
    comment_index = len(comments)
    for token_type, token, start, end, line in tokenize.generate_tokens(buf.readline):
        if token_type == tokenize.COMMENT:
            token = token.replace('#', '', 1)
            line_number = start[0]

            # Create comment using token text and line number
            comment = common.Comment(text=token, start_line=line_number, end_line=line_number)
            comments.append(comment)

            # Add key-value pair of line number and comment index
            end_lines_dict[line_number] = comment_index
            comment_index += 1


def parse_multi_line_comments(file_contents, comments, start_lines_dict, end_lines_dict):
    """ Extracts multi line comments and adds them to a list.
        Also stores start and end line numbers of each comment.

        Args:
            file_contents: (str) from which to extract comments
            comments: list of comments. Each entry is a Comment class object
            start_lines_dict:
                key - starting line number of comment
                value - index of comment
            end_lines_dict:
                key - ending line number of comment
                value - index of comment
    """

    # Store line numbers
    end = '.*\n'
    line = []
    for match in re.finditer(end, file_contents):
        line.append(match.end())

    # Match triple double quoted strings spanning multiple lines
    pattern = re.compile('^[ \t]*("{3}([^"]|\n)*"{3})$', re.MULTILINE | re.DOTALL)
    comment_index = len(comments)
    for match in re.finditer(pattern, file_contents):

        # Store text and start and end line numbers of match
        start_line = next(i for i in range(len(line)) if line[i] > match.start(1)) + 1
        match = match.group(1)
        end_line = start_line + match.count("\n")
        match = match.replace('"""', '')

        # Create a comment using matching group and line numbers
        comment = common.Comment(text=match, start_line=start_line, end_line=end_line, multiline=True)
        comments.append(comment)

        # Add key-value pair of line number and comment index
        start_lines_dict[start_line] = comment_index
        end_lines_dict[end_line] = comment_index
        comment_index += 1


def tag_comment(comments, comment_index, node, ast_tokens, is_on_next_line=False):
    """
    Tags comments extracted from source file with the name of class/function/identifier they are associated with.
    Additionally in the case of class/function definitions, the context is also stores (body of the block)

        Args:
            comments: (list) single and multiline comments that have been extracted
            comment_index: (int) index of current comment in the 'comments' list
            node: (Node) current Node object of Python Abstract Syntax Tree
            ast_tokens: Abstract Syntax Tree with tagged tokens
            is_on_next_line: (boolean) true if comment starts after the current source code line
    """

    # current node is a variable name and comment is present on either the previous or the same line as the node
    # tag comment with the variable name
    if isinstance(node, ast.Name) and comments[comment_index].identifier_name() is None and is_on_next_line is False:
        comments[comment_index].set_identifier_name(node.id)
    # current node is a class or function definition
    # tag comment with name and class/function body
    elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
        # get source code text corresponding to the node
        node_text = ast_tokens.get_text(node)
        # get body of the definition by removing the class/function signature on the first line
        body = '\n'.join(node_text.split('\n')[1:])
        if isinstance(node, ast.ClassDef) and comments[comment_index].class_name() is None:
            comments[comment_index].set_class_name(node.name)
        elif isinstance(node, ast.FunctionDef) and comments[comment_index].function_name() is None:
            comments[comment_index].set_function_name(node.name)
        comments[comment_index].set_context(body)
    return


def extract_comments(filename):
    """Extracts a list of comments from the given Python source file.
        Tags comment with piece of source code it is associated with

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
    comments = []
    start_lines_dict = {}
    end_lines_dict = {}
    try:
        with open(filename, 'r') as source_file:
            file_contents = source_file.read()

            # extract single and multiline comments from source code file
            parse_single_line_comments(file_contents, comments, end_lines_dict)
            parse_multi_line_comments(file_contents, comments, start_lines_dict, end_lines_dict)

            ast_tokens = asttokens.ASTTokens(file_contents, parse=True)

            # for each node in the parse tree, find if any comments are before/after/same line as the source code text
            # tag each comment with the source code it is associated with
            for node in ast.walk(ast_tokens.tree):
                if hasattr(node, 'lineno'):
                    current_line = node.lineno
                    prev_line = current_line - 1
                    next_line = current_line + 1

                    # comment starts and ends on current line
                    if current_line in end_lines_dict:
                        comment_index = end_lines_dict[current_line]
                        tag_comment(comments, comment_index, node, ast_tokens)
                    # comment ends on previous line
                    if prev_line in end_lines_dict:
                        comment_index = end_lines_dict[prev_line]
                        tag_comment(comments, comment_index, node, ast_tokens)
                    # comment starts on next line
                    if next_line in start_lines_dict:
                        comment_index = start_lines_dict[next_line]
                        tag_comment(comments, comment_index, node, ast_tokens, is_on_next_line=True)

            source_file.close()
        comments.sort(key=lambda x: x.start_line())
        return comments
    except OSError as exception:
        raise common.FileError(str(exception))

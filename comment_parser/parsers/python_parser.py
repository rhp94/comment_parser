#!/usr/bin/python
"""This module provides methods
for parsing comments from Python."""

from comment_parser.parsers import common as common
from comment_parser.parsers import ast_visitor
import tokenize
import asttokens
import ast
import io
import re


def combine_consecutive_comments(comments, current_comment):
    if len(comments) > 0:
        previous_comment = comments[len(comments) - 1]
        if current_comment.start_line() == previous_comment.end_line() + 1:
            del comments[len(comments) - 1]
            combined_text = previous_comment.text() + ' ' + current_comment.text()
            new_comment = common.Comment(text=combined_text, start_line=previous_comment.start_line(),
                                         end_line=current_comment.end_line())
            return new_comment
    return current_comment


def parse_single_line_comments(file_contents, comments):
    """ Extracts single line comments and adds them to a list.

        Args:
            file_contents: (str) from which comments are to be extracted
            comments: list of comments. Each entry is a Comment class object
    """
    buf = io.StringIO(file_contents)
    prev_line = ''
    prev_token = '-'
    for token_type, token, start, end, line in tokenize.generate_tokens(buf.readline):
        if token_type == tokenize.COMMENT:
            file_contents = file_contents.replace(token, ' ', 1)
            comment_text = token.replace('#', '', 1)
            line_number = start[0]

            # Create comment using token text and line number
            comment = common.Comment(text=comment_text, start_line=line_number, end_line=line_number)
            if re.match(r"^[ \t]*" + re.escape(token) + r"[ \t]*$", line) and \
                    re.match(r"^[ \t]*" + re.escape(prev_token) + r"[ \t]*$", prev_line):
                comment = combine_consecutive_comments(comments, comment)
            comments.append(comment)

            prev_line = line
            prev_token = token
    return file_contents


def parse_multi_line_comments(file_contents, comments):
    """ Extracts multi line comments and adds them to a list.

        Args:
            file_contents: (str) from which comments are to be extracted
            comments: list of comments. Each entry is a Comment class object
    """

    # Store line numbers
    end = '.*\n'
    line = []
    for match in re.finditer(end, file_contents):
        line.append(match.end())

    # Match triple double quoted strings spanning multiple lines
    pattern = re.compile('^[ \t]*"""[^"\\\\]*(?:(?:\\\\.|"{1,2}(?!"))[^"\\\\]*)*"""$', re.MULTILINE | re.DOTALL)
    for match in re.finditer(pattern, file_contents):
        # Store text and start and end line numbers of match
        start_line = next(i for i in range(len(line)) if line[i] > match.start(0)) + 1
        match = match.group(0)
        end_line = start_line + match.count("\n")
        match = match.replace('"""', '').strip()

        # Create a comment using matching group and line numbers
        comment = common.Comment(text=match, start_line=start_line, end_line=end_line, multiline=True)
        comments.append(comment)

    # Match triple single quoted strings spanning multiple lines
    pattern = re.compile("^[ \t]*'''[^'\\\\]*(?:(?:\\\\.|'{1,2}(?!'))[^'\\\\]*)*'''$", re.MULTILINE | re.DOTALL)
    for match in re.finditer(pattern, file_contents):
        # Store text and start and end line numbers of match
        start_line = next(i for i in range(len(line)) if line[i] > match.start(0)) + 1
        match = match.group(0)
        end_line = start_line + match.count("\n")
        match = match.replace("'''", '').strip()

        # Create a comment using matching group and line numbers
        comment = common.Comment(text=match, start_line=start_line, end_line=end_line, multiline=True)
        comments.append(comment)


def tag_comments(file_content, comments):
    """
    Tag comment with node retrieved from AST. Adds node to a list of nodes used as tags for the comment.

    Args:
        file_content: source file
        comments: list of comments of Comment class to be tagged
    """
    # tag comments at the first line of a block
    ast_tokens = asttokens.ASTTokens(file_content, parse=True)
    root = ast_tokens.tree
    for node in ast.walk(root):
        if node is not None and hasattr(node, 'lineno') and hasattr(node, 'body')\
                and node.body is not None and hasattr(type(node.body), '__getitem__'):
            for comment in comments:
                if node.lineno < comment.start_line() <= node.body[0].lineno and comment.is_multiline() \
                        or node.lineno < comment.start_line() < node.body[0].lineno and not comment.is_multiline():
                    node_text = ast_tokens.get_text(node)
                    singe_quote_comments = re.compile("^[ \t]*'''[^'\\\\]*(?:(?:\\\\.|'{1,2}(?!'))[^'\\\\]*)*'''$",
                                                      re.MULTILINE | re.DOTALL)
                    double_quote_comments = re.compile('^[ \t]*"""[^"\\\\]*(?:(?:\\\\.|"{1,2}(?!"))[^"\\\\]*)*"""$',
                                                       re.MULTILINE | re.DOTALL)
                    node_text = re.sub(singe_quote_comments, " ", node_text)
                    node_text = re.sub(double_quote_comments, " ", node_text)
                    comment.node_list().append((node, node_text))

    # tag comments with source code on the same line/next line
    for comment in comments:
        current_line = comment.end_line()
        next_line = comment.end_line() + 1

        node = ast_visitor.Visitor(ast_tokens).get_node_at_line(root, current_line)
        if (node is not None and not isinstance(node, ast.Expr)) \
                or (node is not None and isinstance(node, ast.Expr) and not isinstance(node.value, ast.Str)):
            node_text = ast_tokens.get_text(node)
            singe_quote_comments = re.compile("^[ \t]*'''[^'\\\\]*(?:(?:\\\\.|'{1,2}(?!'))[^'\\\\]*)*'''$",
                                              re.MULTILINE | re.DOTALL)
            double_quote_comments = re.compile('^[ \t]*"""[^"\\\\]*(?:(?:\\\\.|"{1,2}(?!"))[^"\\\\]*)*"""$',
                                               re.MULTILINE | re.DOTALL)
            node_text = re.sub(singe_quote_comments, " ", node_text)
            node_text = re.sub(double_quote_comments, " ", node_text)
            comment.node_list().append((node, node_text))
            # visitor.visit_subtree(node)
        else:
            node = ast_visitor.Visitor(ast_tokens).get_node_at_line(root, next_line)
            if node is not None:
                node_text = ast_tokens.get_text(node)
                singe_quote_comments = re.compile("^[ \t]*'''[^'\\\\]*(?:(?:\\\\.|'{1,2}(?!'))[^'\\\\]*)*'''$",
                                                  re.MULTILINE | re.DOTALL)
                double_quote_comments = re.compile('^[ \t]*"""[^"\\\\]*(?:(?:\\\\.|"{1,2}(?!"))[^"\\\\]*)*"""$',
                                                   re.MULTILINE | re.DOTALL)
                node_text = re.sub(singe_quote_comments, " ", node_text)
                node_text = re.sub(double_quote_comments, " ", node_text)
                comment.node_list().append((node, node_text))
                # visitor.visit_subtree(node)


def extract_comments(filename):
    """Extracts a list of comments from the given Python source file.
        Tags comment with piece of source code it is associated with

        Comments are represented with the Comment class found in the common module.
        Python comments come in two forms, single and multi-line comments.
            - Single-line comments begin with '#' and continue to the end of line.
            - Multi-line comments are enclosed within triple double quotes as docstrings and can span
                multiple lines of code.

        Args:
            filename: String name of the file to extract comments from.
        Returns:
            Python list of common.Comment in the order that they appear in the file.
        Raises:
            common.FileError: File was unable to be open or read.
    """
    comments = []
    try:
        with open(filename, 'r') as source_file:
            file_contents = source_file.read()

            # extract single and multiline comments from source code file
            file_contents = parse_single_line_comments(file_contents, comments)
            parse_multi_line_comments(file_contents, comments)
            comments.sort(key=lambda x: x.start_line())

            tag_comments(file_contents, comments)

            source_file.close()
        return comments
    except OSError as exception:
        raise common.FileError(str(exception))

#!/usr/bin/python
"""This module provides methods for parsing comments from Java source files."""

from comment_parser.parsers import common as common
from javalang_dev import javalang
import re


def tag_comments(comments, file_content, eof_line_number):
    tree = javalang.parse.parse(file_content)

    for comment in comments:
        for path, node in tree:
            if node.position.start is not None and type(node).__name__ != 'CompilationUnit':
                node_start_line = node.position.start[0]
                if node_start_line == comment.end_line() or node_start_line == comment.end_line() + 1 \
                        and len(comment.node_list()) == 0:

                    if node.position.end is not None:
                        node_end_line = node.position.end[0] - 1
                        if type(node).__name__ == 'PackageDeclaration':
                            node_end_line += 1
                    else:
                        node_end_line = eof_line_number

                    node_text = ''
                    line_counter = 0
                    for line in file_content.splitlines():
                        if node_start_line - 1 <= line_counter <= node_end_line - 1:
                            node_text = node_text + line + '\n'
                        elif line_counter > node_end_line - 1:
                            break
                        line_counter += 1
                    comment.node_list().append((node, node_text))

    # debug: print comment + code context
    index = 1
    for comment in comments:
        print('\n' + str(index) + '. COMMENT: ' + comment.text())
        print('START: ' + str(comment.start_line()))
        print('END: ' + str(comment.end_line()))
        if len(comment.node_list()) > 0:
            print('NODE: ' + type(comment.node_list()[0][0]).__name__)
            print('CODE: ' + comment.node_list()[0][1])
        index += 1


def remove_comment(file_content, comment_text, multiline):
    replace_with = ' '
    if multiline:
        comment_text = '/*' + comment_text + '*/'
        for i in range(1, comment_text.count('\n') + 1):
            replace_with = replace_with + ' \n'
    else:
        comment_text = '//' + comment_text
    file_content = file_content.replace(comment_text, replace_with, 1)
    return file_content


def combine_consecutive_comments(comments, current_comment):
    if len(comments) > 0:
        previous_comment = comments[len(comments) - 1]
        if not previous_comment.is_multiline() and current_comment.start_line() == previous_comment.end_line() + 1:
            del comments[len(comments) - 1]
            combined_text = previous_comment.text() + ' ' + current_comment.text()
            new_comment = common.Comment(text=combined_text, start_line=previous_comment.start_line(),
                                         end_line=current_comment.end_line())
            return new_comment
    return current_comment


def extract_comments(filename):
    """Extracts a list of comments from the given source file.

    Comments are represented with the Comment class found in the common module.
    Comments come in two forms, single and multi-line comments.
        - Single-line comments begin with '//' and continue to the end of line.
        - Multi-line comments begin with '/*' and end with '*/' and can span
            multiple lines of code. If a multi-line comment does not terminate
            before EOF is reached, then an exception is raised.

    Note that this doesn't take language-specific preprocessor directives into consideration.

    Args:
        filename: String name of the file to extract comments from.
    Returns:
        Python list of common.Comment in the order that they appear in the file.
    Raises:
        common.FileError: File was unable to be open or read.
        common.UnterminatedCommentError: Encountered an unterminated multi-line
            comment.
    """
    try:
        with open(filename, 'r') as source_file:
            comments = []
            file_content = source_file.read()
            tokens = list(javalang.tokenizer.tokenize(file_content))

            prev_line = ''
            prev_comment_text = '-'
            for token in tokens:
                if token.__class__.__name__ == 'Comment':
                    comment_text = token.value
                    if comment_text.startswith('/*'):
                        is_multiline = True
                        comment_text = comment_text.replace('/*', '', 1)
                        comment_text = comment_text.replace('*/', '', 1)
                        end_line = token.position[0]
                        start_line = end_line - comment_text.count('\n')
                    else:
                        is_multiline = False
                        comment_text = token.value.rstrip().replace('//', '', 1)
                        end_line = token.position[0] - 1
                        start_line = token.position[0] - 1

                    comment = common.Comment(comment_text, start_line, end_line, is_multiline)

                    if not is_multiline:
                        line_counter = 0
                        for line in file_content.splitlines():
                            if start_line - 1 == line_counter:
                                if re.match(r"^[ \t]*//" + re.escape(comment_text) + r"[ \t]*$", line) and \
                                        re.match(r"^[ \t]*//" + re.escape(prev_comment_text) + r"[ \t]*$", prev_line):
                                    comment = combine_consecutive_comments(comments, comment)

                                prev_comment_text = comment_text
                                prev_line = line
                                break
                            line_counter += 1
                    file_content = remove_comment(file_content, comment_text, is_multiline)
                    comments.append(comment)
            tag_comments(comments, file_content, eof_line_number=file_content.count('\n'))
    except OSError as exception:
        raise common.FileError(str(exception))

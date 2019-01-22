#!/usr/bin/python
"""This module provides constructs common to all comment parsers."""


class Error(Exception):
    """Base Error class for all comment parsers."""
    pass


class FileError(Error):
    """Raised if there is an issue reading a given file."""
    pass


class UnterminatedCommentError(Error):
    """Raised if an Unterminated multi-line comment is encountered."""
    pass


class Comment(object):
    """Represents comments found in source files."""

    def __init__(self, text, start_line, end_line, multiline=False):
        """Initializes Comment.

        Args:
            text: String text of comment.
            multiline: Boolean whether this comment was a multiline comment.
            start_line: Line number (int) comment was found on.
            end_line: Line number (int) comment ends on.

        Params:
            node_list: (list) list of AST nodes to retrieve the code context for which the comment is written
        """
        self._text = text
        self._start_line = start_line
        self._end_line = end_line
        self._multiline = multiline
        self._node_list = []

    def text(self):
        """Returns the comment's text.

        Returns:
            String
        """
        return self._text

    def start_line(self):
        """Returns the line number the comment was found on.

        Returns:
            Int
        """
        return self._start_line

    def end_line(self):
        """Returns the line number the comment ends on.

        Returns:
            Int
        """
        return self._end_line

    def is_multiline(self):
        """Returns whether this comment was a multiline comment.

        Returns:
            True if comment was a multiline comment, False if not.
        """
        return self._multiline

    def node_list(self):
        """Returns list of AST nodes the comment is associated with"""
        return self._node_list

    def set_node_list(self, node_list):
        """Set context of the class/function the comment is associated with"""
        self._node_list = node_list

    def __str__(self):
        return self._text

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.__dict__ == other.__dict__:
                return True
        return False

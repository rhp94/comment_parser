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

    def __init__(self, text, start_line, end_line, multiline=False,
                 function_name=None, class_name=None, identifier_name=None, context=None):
        """Initializes Comment.

        Args:
            text: String text of comment.
            multiline: Boolean whether this comment was a multiline comment.
            start_line: Line number (int) comment was found on.
            end_line: Line number (int) comment ends on.
            function_name: (String) name of the method for which comment is written
            class_name: (String) name of the class for which comment is written
            identifier_name: (String) name of the identifier for which comment is written
            context: (String) body of method for which comment is written
        """
        self._text = text
        self._start_line = start_line
        self._end_line = end_line
        self._multiline = multiline
        self._function_name = function_name
        self._class_name = class_name
        self._identifier_name = identifier_name
        self._context = context

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

    def function_name(self):
        """Returns name of function the comment is associated with"""
        return self._function_name

    def set_function_name(self, function_name):
        """Set name of the function the comment is associated with"""

        self._function_name = function_name

    def class_name(self):
        """Returns name of class the comment is associated with"""
        return self._class_name

    def set_class_name(self, class_name):
        """Set name of the class the comment is associated with"""
        self._class_name = class_name

    def identifier_name(self):
        """Returns name of identifier the comment is associated with"""
        return self._identifier_name

    def set_identifier_name(self, identifier_name):
        """Set name of the identifier the comment is associated with"""
        self._identifier_name = identifier_name

    def context(self):
        """Returns body of the class/function the comment is associated with"""
        return self._context

    def set_context(self, context):
        """Set context of the class/function the comment is associated with"""
        self._context = context

    def __str__(self):
        return self._text

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.__dict__ == other.__dict__:
                return True
        return False

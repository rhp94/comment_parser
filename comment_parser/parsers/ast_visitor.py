import ast
import asttokens


class Visitor(ast.NodeVisitor):

    def __init__(self, ast_tokens):
        self._ast_tokens = ast_tokens
        self._result = None
        self._found_node = False

    def get_node_at_line(self, root, line):
        if hasattr(root, 'lineno') and self._found_node is False:
            if root.lineno == line:
                self._found_node = True
                self._result = root
        for field, value in ast.iter_fields(root):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.get_node_at_line(item, line)
            elif isinstance(value, ast.AST):
                self.get_node_at_line(value, line)
        return self._result

    def visit_subtree(self, node):
        super(Visitor, self).generic_visit(node)

    def visit_Name(self, node):
        print(node.lineno)
        print(node.__class__.__name__)
        print(node.id)
        # print('token: ' + self._ast_tokens.get_text(node))
        print('-----------------')
        super(Visitor, self).generic_visit(node)

    def visit_Num(self, node):
        print(node.lineno)
        print(node.__class__.__name__)
        print(node.__dict__['n'])
        print('-----------------')
        super(Visitor, self).generic_visit(node)

    def visit_Str(self, node):
        print(node.lineno)
        print(node.__class__.__name__)
        print(node.s)
        print('-----------------')
        super(Visitor, self).generic_visit(node)

    def visit_FunctionDef(self, node):
        print(node.lineno)
        print(node.__class__.__name__)
        print(node.name)
        print('-----------------')
        super(Visitor, self).generic_visit(node)

    def visit_ClassDef(self, node):
        print(node.lineno)
        print(node.__class__.__name__)
        print(node.name)
        print('-----------------')
        super(Visitor, self).generic_visit(node)

    def generic_visit(self, node):
        if hasattr(node, 'lineno'):
            print(node.lineno)
        print(node.__class__.__name__)
        print('-----------------')
        super(Visitor, self).generic_visit(node)

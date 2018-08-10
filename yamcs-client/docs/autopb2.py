from docutils import nodes
from docutils.parsers.rst import Directive


class autopb2(nodes.Admonition, nodes.Element):
    pass

class todolist(nodes.General, nodes.Element):
    pass

def visit_autopb2_node(self, node):
    self.visit_admonition(node)

def depart_autopb2_node(self, node):
    self.depart_admonition(node)


class TodolistDirective(Directive):

    def run(self):
        return [todolist('')]


class Autopb2Directive(Directive):

    # this enables content in the directive
    has_content = True

    def run(self):
        env = self.state.document.settings.env

        targetid = "todo-%d" % env.new_serialno('todo')
        targetnode = nodes.target('', '', ids=[targetid])

        todo_node = autopb2('\n'.join(self.content))
        todo_node += nodes.title('Todo', 'Todo')
        self.state.nested_parse(self.content, self.content_offset, todo_node)

        if not hasattr(env, 'todo_all_todos'):
            env.todo_all_todos = []
        env.todo_all_todos.append({
            'docname': env.docname,
            'lineno': self.lineno,
            'todo': todo_node.deepcopy(),
            'target': targetnode,
        })

        return [targetnode, todo_node]

def purge_todos(app, env, docname):
    if not hasattr(env, 'todo_all_todos'):
        return
    env.todo_all_todos = [todo for todo in env.todo_all_todos
                          if todo['docname'] != docname]

def process_todo_nodes(app, doctree, fromdocname):

    # Replace all todolist nodes with a list of the collected todos.
    # Augment each todo with a backlink to the original location.
    env = app.builder.env

    for node in doctree.traverse(todolist):
        content = []

        for todo_info in env.todo_all_todos:
            para = nodes.paragraph()
            filename = env.doc2path(todo_info['docname'], base=None)
            description = (
                '(The original entry is located in %s, line %d and can be found ' %
                (filename, todo_info['lineno']))
            para += nodes.Text(description, description)

            # Create a reference
            newnode = nodes.reference('', '')
            innernode = nodes.emphasis('here', 'here')
            newnode['refdocname'] = todo_info['docname']
            newnode['refuri'] = app.builder.get_relative_uri(
                fromdocname, todo_info['docname'])
            newnode['refuri'] += '#' + todo_info['target']['refid']
            newnode.append(innernode)
            para += newnode
            para += nodes.Text('.)', '.)')

            # Insert into the todolist
            content.append(todo_info['todo'])
            content.append(para)

        node.replace_self(content)

def setup(app):
    app.add_node(todolist)
    app.add_node(autopb2,
                 html=(visit_autopb2_node, depart_autopb2_node),
                 latex=(visit_autopb2_node, depart_autopb2_node),
                 text=(visit_autopb2_node, depart_autopb2_node))

    app.add_directive('autopb2', Autopb2Directive)
    app.add_directive('todolist', TodolistDirective)
    app.connect('doctree-resolved', process_todo_nodes)
    app.connect('env-purge-doc', purge_todos)

    return {'version': '0.1'}

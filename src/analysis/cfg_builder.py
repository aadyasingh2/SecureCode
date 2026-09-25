import networkx as nx

from src.parser.ast_nodes import (
    BlockNode,
    VarDeclNode,
    AssignNode,
    IfNode,
    WhileNode,
    ForNode,
    ReturnNode,
    ExprStmtNode
)


class CFGBuilder:

    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_counter = 0

    def new_node(self, statements=None, label=None):
        """Create a new CFG node."""

        node_id = self.node_counter
        self.node_counter += 1

        if statements is None:
            statements = []

        self.graph.add_node(
            node_id,
            statements=statements,
            label=label if label is not None else f"Block {node_id}"
        )

        return node_id

    def add_edge(self, source, target, edge_type="normal"):
        """Add an edge between two CFG nodes."""

        self.graph.add_edge(
            source,
            target,
            edge_type=edge_type
        )

    def build(self, function_node):
        """Build CFG for a function."""

        self.graph = nx.DiGraph()
        self.node_counter = 0

        entry = self.new_node(label="ENTRY")

        exit_node = self.new_node(label="EXIT")

        self.graph.graph["entry"] = entry
        self.graph.graph["exit"] = exit_node
        self.graph.graph["function"] = function_node.name

        first_node, last_nodes = self.build_block(function_node.body)

        if first_node is not None:
            self.add_edge(entry, first_node)

            for item in last_nodes:
                if isinstance(item, tuple):
                    node, edge_type = item
                    self.add_edge(node, exit_node, edge_type=edge_type)
                else:
                    self.add_edge(item, exit_node)

    # Return statements terminate the function.
            for node, data in self.graph.nodes(data=True):
                if data.get("label") == "RETURN":
                    self.add_edge(node, exit_node)

        else:
            self.add_edge(entry, exit_node)
    
        return self.graph

    def build_block(self, block):
        """
        Build CFG for a block.

        Returns:
            first node
            list of nodes where control can continue
        """

        first_node = None
        current_nodes = []

        for statement in block.statements:

            statement_first, statement_last = self.build_statement(
                statement
            )

            if statement_first is None:
                continue

            if first_node is None:
                first_node = statement_first

            # Connect previous statements to current statement.
            for item in current_nodes:
                if isinstance(item, tuple):
                    node, edge_type = item
                    self.add_edge(node, statement_first, edge_type=edge_type)
                else:
                    self.add_edge(item, statement_first)

            current_nodes = statement_last

        return first_node, current_nodes

    def build_statement(self, statement):

        # ---------------------------------------------
        # SIMPLE STATEMENTS
        # ---------------------------------------------

        if isinstance(
            statement,
            (VarDeclNode, AssignNode, ExprStmtNode)
        ):
            node = self.new_node(
                statements=[statement]
            )

            return node, [node]

        # ---------------------------------------------
        # RETURN
        # ---------------------------------------------

        if isinstance(statement, ReturnNode):

            node = self.new_node(
                statements=[statement],
                label="RETURN"
            )

            # Return does not continue to the next statement.
            return node, []

        # ---------------------------------------------
        # IF / ELSE
        # ---------------------------------------------

        if isinstance(statement, IfNode):

            # The condition expression is attached to the node so that
            # data-flow analysis can see the variables it reads.
            # A condition is pure USE: it never defines a variable.
            condition_node = self.new_node(
                statements=[statement.condition] if statement.condition is not None else [],
                label="IF CONDITION"
            )

            self.graph.nodes[condition_node]["condition"] = statement.condition

            then_first, then_last = self.build_block(
                statement.then_block
            )

            # THEN branch
            if then_first is not None:
                self.add_edge(
                    condition_node,
                    then_first,
                    edge_type="true"
                )
            else:
                then_last = [(condition_node, "true")]

            # ELSE branch
            if statement.else_block is not None:

                # Special case:
                # else { if (...) { ... } }
                # This is how the parser represents else-if.
                if (
                    len(statement.else_block.statements) == 1
                    and isinstance(
                        statement.else_block.statements[0],
                        IfNode
                    )
                ):
                    else_if = statement.else_block.statements[0]

                    else_first, else_last = self.build_statement(
                        else_if
                    )

                else:
                    else_first, else_last = self.build_block(
                        statement.else_block
                    )

                if else_first is not None:
                    self.add_edge(
                        condition_node,
                        else_first,
                        edge_type="false"
                    )
                else:
                    else_last = [(condition_node, "false")]

            else:
                else_last = [(condition_node, "false")]

            # If both branches never return control (e.g. both return from function)
            if not then_last and not else_last:
                return condition_node, []

            # Merge point
            merge_node = self.new_node(
                statements=[],
                label="IF MERGE"
            )

            for item in then_last:
                if isinstance(item, tuple):
                    node, edge_type = item
                    self.add_edge(node, merge_node, edge_type=edge_type)
                else:
                    self.add_edge(item, merge_node)

            for item in else_last:
                if isinstance(item, tuple):
                    node, edge_type = item
                    self.add_edge(node, merge_node, edge_type=edge_type)
                else:
                    self.add_edge(item, merge_node)

            return condition_node, [merge_node]

        # ---------------------------------------------
        # WHILE LOOP
        # ---------------------------------------------

        if isinstance(statement, WhileNode):

            # The condition expression is attached to the node so that
            # data-flow analysis can see the variables it reads.
            # A condition is pure USE: it never defines a variable.
            condition_node = self.new_node(
                statements=[statement.condition] if statement.condition is not None else [],
                label="WHILE CONDITION"
            )

            self.graph.nodes[condition_node]["condition"] = statement.condition

            body_first, body_last = self.build_block(
                statement.body
            )

            # True → loop body
            if body_first is not None:
                self.add_edge(
                    condition_node,
                    body_first,
                    edge_type="true"
                )

                # Body → condition
                for item in body_last:
                    if isinstance(item, tuple):
                        node = item[0]
                    else:
                        node = item
                    self.add_edge(
                        node,
                        condition_node,
                        edge_type="back"
                    )

            # False → next statement
            return condition_node, [(condition_node, "false")]

        # ---------------------------------------------
        # FOR LOOP
        # ---------------------------------------------

        if isinstance(statement, ForNode):

            init_node = None

            if statement.init is not None:
                init_node = self.new_node(
                    statements=[statement.init],
                    label="FOR INIT"
                )

            # The condition expression is attached to the node so that
            # data-flow analysis can see the variables it reads.
            # A condition is pure USE: it never defines a variable.
            condition_node = self.new_node(
                statements=[statement.condition] if statement.condition is not None else [],
                label="FOR CONDITION"
            )

            self.graph.nodes[condition_node]["condition"] = statement.condition

            update_node = None

            if statement.update is not None:
                update_node = self.new_node(
                    statements=[statement.update],
                    label="FOR UPDATE"
                )

            body_first, body_last = self.build_block(
                statement.body
            )

            # Init → condition
            if init_node is not None:
                self.add_edge(
                    init_node,
                    condition_node
                )
                first_node = init_node
            else:
                first_node = condition_node

            # Condition → body
            if body_first is not None:
                self.add_edge(
                    condition_node,
                    body_first,
                    edge_type="true"
                )

                # Body → update
                if update_node is not None:
                    for item in body_last:
                        if isinstance(item, tuple):
                            node = item[0]
                        else:
                            node = item
                        self.add_edge(
                            node,
                            update_node
                        )

                    # Update → condition
                    self.add_edge(
                        update_node,
                        condition_node,
                        edge_type="back"
                    )

                else:
                    for item in body_last:
                        if isinstance(item, tuple):
                            node = item[0]
                        else:
                            node = item
                        self.add_edge(
                            node,
                            condition_node,
                            edge_type="back"
                        )

            # False condition continues forward.
            return first_node, [(condition_node, "false")]

        # ---------------------------------------------
        # UNKNOWN STATEMENT
        # ---------------------------------------------

        node = self.new_node(
            statements=[statement]
        )

        return node, [node]

    def export_dot(self, filename):
        """Export CFG to Graphviz DOT format."""

        nx.drawing.nx_pydot.write_dot(
            self.graph,
            filename
        )
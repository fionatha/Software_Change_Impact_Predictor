
import ast
import os
import networkx as nx


def analyze_dependencies(repo_path):

    graph = nx.DiGraph()
    module_map = {}

    # Find Python files and map their module names
    for root, dirs, files in os.walk(repo_path):

        dirs[:] = [
            d for d in dirs
            if d not in {".git", "venv", "__pycache__"}
        ]

        for file in files:

            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)

            relative_path = os.path.relpath(
                file_path, repo_path
            ).replace("\\", "/")

            module_name = relative_path[:-3].replace("/", ".")

            if module_name.endswith(".__init__"):
                module_name = module_name[:-9]

            elif module_name == "__init__":
                module_name = ""

            module_map[module_name] = relative_path
            graph.add_node(relative_path)

    # Analyze imports in each Python file
    for module_name, relative_path in module_map.items():

        file_path = os.path.join(repo_path, relative_path)

        try:
            with open(file_path, "r", encoding="utf-8") as source:
                tree = ast.parse(source.read())

            for node in ast.walk(tree):

                imported_modules = []

                if isinstance(node, ast.Import):

                    for item in node.names:
                        imported_modules.append(item.name)

                elif isinstance(node, ast.ImportFrom):

                    if node.level > 0:
                        # Resolve relative imports
                        current_package = module_name.split(".")

                        if current_package[-1] != "":
                            current_package = current_package[:-1]

                        remove_count = node.level - 1

                        if remove_count:
                            current_package = current_package[:-remove_count]

                        if node.module:
                            parts = current_package + node.module.split(".")
                        else:
                            parts = current_package

                        base_module = ".".join(parts)

                    else:
                        base_module = node.module or ""

                    if base_module:
                        imported_modules.append(base_module)

                    for item in node.names:
                        if item.name != "*":
                            imported_modules.append(
                                base_module + "." + item.name
                                if base_module else item.name
                            )

                for imported in imported_modules:

                    parts = imported.split(".")

                    for i in range(len(parts), 0, -1):

                        candidate = ".".join(parts[:i])
                        target = module_map.get(candidate)

                        if target and target != relative_path:
                            graph.add_edge(relative_path, target)
                            break

        except (SyntaxError, UnicodeDecodeError, OSError):
            continue

    return graph


def get_affected_files(graph, changed_file):

    if changed_file not in graph:
        return []

    return sorted(nx.ancestors(graph, changed_file))

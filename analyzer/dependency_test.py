from dependency_analyzer import analyze_dependencies

repo_path = "uploads/pallets_flask_eb4add27"

graph = analyze_dependencies(repo_path)

print("\nCode Dependency Analysis Results")
print("--------------------------------")

print("Total Python files:", graph.number_of_nodes())
print("Total Dependencies:", graph.number_of_edges())

print("\nDetected Dependencies:")

for source, target in graph.edges():
    print(source, "depends on", target)
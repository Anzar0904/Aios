import os
import tempfile

from aios.services.docintel.generator import MarkdownGenerator
from aios.services.docintel.graph import DependencyGraphBuilder
from aios.services.docintel.indexer import DocumentationIndexer
from aios.services.docintel.intelligence import DocumentationIntelligenceEngine
from aios.services.docintel.scanner import RepositoryScanner


def test_docintel_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock python packages and modules
        pkg_dir = os.path.join(tmpdir, "mock_pkg")
        os.makedirs(pkg_dir)
        with open(os.path.join(pkg_dir, "__init__.py"), "w") as f:
            f.write("# init\n")
            
        module_path = os.path.join(pkg_dir, "module.py")
        with open(module_path, "w") as f:
            f.write('''
"""Module docstring."""
import os

class MyClass:
    """Class docstring."""
    def method_a(self, x: int) -> str:
        # TODO: Implement method_a
        return str(x)

def my_function():
    pass
''')

        # 1. Test Scanner
        scanner = RepositoryScanner(tmpdir)
        scan_res = scanner.scan()
        assert "mock_pkg" in scan_res["packages"]
        assert "mock_pkg.module" in scan_res["modules"]

        # 2. Test Indexer
        indexer = DocumentationIndexer()
        index_res = indexer.parse_file(module_path)
        assert len(index_res["classes"]) == 1
        assert index_res["classes"][0]["name"] == "MyClass"
        assert index_res["classes"][0]["docstring"] == "Class docstring."
        assert len(index_res["classes"][0]["methods"]) == 1
        assert index_res["classes"][0]["methods"][0]["name"] == "method_a"
        assert len(index_res["functions"]) == 1
        assert index_res["functions"][0]["name"] == "my_function"

        # 3. Test Graph
        graph_builder = DependencyGraphBuilder()
        graph = graph_builder.build_graph(scan_res, {module_path: index_res})
        mermaid = graph_builder.generate_mermaid(graph)
        assert "flowchart TD" in mermaid

        # 4. Test Intelligence Engine
        intel_engine = DocumentationIntelligenceEngine()
        intel_res = intel_engine.analyze({module_path: index_res})
        assert len(intel_res["undocumented_functions"]) == 1
        assert intel_res["undocumented_functions"][0]["function"] == "my_function"
        assert len(intel_res["todos_fixmes"]) == 1
        assert intel_res["todos_fixmes"][0]["type"] == "TODO"

        # 5. Test Markdown Generator
        generator = MarkdownGenerator(os.path.join(tmpdir, "docs"))
        generator.generate(scan_res, intel_res, mermaid)
        
        assert os.path.exists(os.path.join(tmpdir, "docs", "README.md"))
        assert os.path.exists(os.path.join(tmpdir, "docs", "Architecture", "Architecture.md"))
        assert os.path.exists(os.path.join(tmpdir, "docs", "Services", "Services.md"))
        report_path = os.path.join(tmpdir, "docs", "Reports", "Code_Intelligence_Report.md")
        assert os.path.exists(report_path)

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
            f.write(
                '"""Module docstring."""\n'
                "import os\n\n"
                "class MyClass:\n"
                '    """Class docstring."""\n'
                "    def method_a(self, x: int) -> str:\n"
                "        # TODO: Implement method_a\n"
                "        return str(x)\n\n"
                "def my_function():\n"
                "    pass\n"
            )

        # 1. Test Scanner with custom exclusion patterns
        scanner = RepositoryScanner(tmpdir, exclude_patterns=[".git", "ignored_dir"])
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

        # 3. Test Graph Analyzer
        graph_builder = DependencyGraphBuilder()
        dep_graph = graph_builder.build_dependency_graph(scan_res, {module_path: index_res})
        pkg_graph = graph_builder.build_package_graph(scan_res, dep_graph)
        svc_graph = graph_builder.build_service_graph(scan_res, dep_graph)

        dep_mermaid = graph_builder.generate_mermaid(dep_graph, "Dependency Graph")
        pkg_mermaid = graph_builder.generate_mermaid(pkg_graph, "Package Graph")
        svc_mermaid = graph_builder.generate_mermaid(svc_graph, "Service Graph")

        assert "flowchart TD" in dep_mermaid
        assert "flowchart TD" in pkg_mermaid
        assert "flowchart TD" in svc_mermaid

        # 4. Test Intelligence Engine
        intel_engine = DocumentationIntelligenceEngine()
        intel_res = intel_engine.analyze({module_path: index_res})
        assert len(intel_res["undocumented_functions"]) == 1
        assert intel_res["undocumented_functions"][0]["function"] == "my_function"
        assert len(intel_res["todos_fixmes"]) == 1
        assert intel_res["todos_fixmes"][0]["type"] == "TODO"

        # 5. Test Markdown Generator
        generator = MarkdownGenerator(os.path.join(tmpdir, "docs"))
        generator.generate(
            scan_res,
            {module_path: index_res},
            intel_res,
            dep_mermaid,
            pkg_mermaid,
            svc_mermaid,
        )

        assert os.path.exists(os.path.join(tmpdir, "docs", "README.md"))
        assert os.path.exists(os.path.join(tmpdir, "docs", "Architecture.md"))
        assert os.path.exists(os.path.join(tmpdir, "docs", "Services.md"))
        assert os.path.exists(os.path.join(tmpdir, "docs", "Providers.md"))
        assert os.path.exists(os.path.join(tmpdir, "docs", "API.md"))
        assert os.path.exists(os.path.join(tmpdir, "docs", "DependencyGraph.md"))
        report_path = os.path.join(tmpdir, "docs", "Reports", "Code_Completeness_Report.md")
        assert os.path.exists(report_path)

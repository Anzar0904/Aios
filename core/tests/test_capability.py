import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from aios.brain.planner import BrainPlanner
from aios.brain.skill_selector import SkillSelector
from aios.skills.base import BaseSkill
from aios.skills.loader import SkillLoader
from aios.skills.metadata import SkillMetadata
from aios.skills.registry import SkillRegistry


def test_metadata_capability_serialization():
    meta = SkillMetadata(
        id="test_git",
        name="Git Skill",
        version="1.0.0",
        author="Tester",
        description="Version control workflows",
        category="VCS",
        commands=["git checkout", "git commit"],
        capabilities=["git", "vcs"],
    )
    assert meta.id == "test_git"
    assert meta.capabilities == ["git", "vcs"]


def test_loader_capabilities_from_toml():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / "test_cap_skill"
        skill_dir.mkdir()

        toml_content = """
[skill]
id = "test_cap_skill"
name = "Capability Skill"
version = "1.0.0"
author = "Tester"
description = "A skill with capabilities"
category = "Testing"
commands = ["run test"]
capabilities = ["pytest", "quality-gate"]
"""
        (skill_dir / "skill.toml").write_text(toml_content, encoding="utf-8")

        loader = SkillLoader()
        skill = loader.load_skill(skill_dir)

        assert skill is not None
        assert skill.metadata.id == "test_cap_skill"
        assert skill.metadata.capabilities == ["pytest", "quality-gate"]


def test_skill_selector_capability_filtering():
    registry = SkillRegistry()

    git_meta = SkillMetadata(
        id="github_skill",
        name="Git Pro",
        version="1.0.0",
        author="Tester",
        description="Version control workflows",
        category="VCS",
        commands=["git status", "git log"],
        capabilities=["git", "vcs"],
    )
    doc_meta = SkillMetadata(
        id="doc_skill",
        name="Doc writer",
        version="1.0.0",
        author="Tester",
        description="Documentation writing workflows",
        category="Docs",
        commands=["write README", "audit index"],
        capabilities=["documentation"],
    )

    registry.register(BaseSkill(git_meta, "/tmp/git"))
    registry.register(BaseSkill(doc_meta, "/tmp/doc"))

    selector = SkillSelector(registry)

    # 1. Test deterministic match with capability matching
    selections = selector.select_skills("git status", capability="git")
    assert len(selections) == 1
    assert selections[0].skill_id == "github_skill"

    # 2. Match with mismatching capability constraint yields nothing
    selections_mismatch = selector.select_skills("git status", capability="documentation")
    assert len(selections_mismatch) == 0

    # 3. Dynamic capability keyword score boost
    selections_boost = selector.select_skills("write a new documentation guide")
    assert len(selections_boost) >= 1
    # doc_skill should be selected first due to documentation capability keyword boost
    assert selections_boost[0].skill_id == "doc_skill"


def test_planner_capability_propagation():
    registry = SkillRegistry()
    meta = SkillMetadata(
        id="git_skill",
        name="Git",
        version="1.0.0",
        author="Tester",
        description="Git tasks",
        category="VCS",
        commands=["git status"],
        capabilities=["git"],
    )
    registry.register(BaseSkill(meta, "/tmp/git"))
    selector = SkillSelector(registry)
    model_service = MagicMock()

    planner = BrainPlanner(selector, model_service)

    # Valid capability matches
    wf = planner.plan("git status", capability="git")
    assert len(wf.steps) == 1
    assert wf.steps[0].skill_id == "git_skill"

    # Invalid capability yields system fallback
    wf_invalid = planner.plan("git status", capability="documentation")
    assert wf_invalid.steps[0].skill_id == "system"

# API Documentation Reference

## Module: fix_test_defs.py

### def `read_file`
- `def read_file(filepath)`

### def `write_file`
- `def write_file(filepath, content)`

## Module: refactor_lifecycle.py

### def `read_file`
- `def read_file(filepath)`

### def `write_file`
- `def write_file(filepath, content)`

## Module: stabilize_sprint15.py

### def `read_file`
- `def read_file(filepath)`

### def `write_file`
- `def write_file(filepath, content)`

## Module: refactor_providers.py

### def `remove_file`
- `def remove_file(filepath)`

### def `read_file`
- `def read_file(filepath)`

### def `write_file`
- `def write_file(filepath, content)`

## Module: apply_test_fixes.py

### def `read_file`
- `def read_file(filepath)`

### def `write_file`
- `def write_file(filepath, content)`

## Module: test_dummy.py

### class `DummyService`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self)`
- `def start(self)`

## Module: fix_tests.py

### def `read_file`
- `def read_file(filepath)`

### def `write_file`
- `def write_file(filepath, content)`

## Module: fix_config.py

### def `read_file`
- `def read_file(filepath)`

### def `write_file`
- `def write_file(filepath, content)`

## Module: fix_p0_010.py

### def `read_file`
- `def read_file(filepath)`

### def `write_file`
- `def write_file(filepath, content)`

## Module: core/tests/test_workflow_optimization.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `test_knowledge_base`
- `def test_knowledge_base()`

### def `test_cost_analyzer`
- `def test_cost_analyzer()`

### def `test_latency_analyzer`
- `def test_latency_analyzer()`

### def `test_parallelization_analyzer`
- `def test_parallelization_analyzer()`

### def `test_complexity_analyzer`
- `def test_complexity_analyzer()`

### def `test_optimization_validator`
- `def test_optimization_validator()`

### def `test_optimization_service_report`
- `def test_optimization_service_report(tmp_path, mock_memory_service, mock_workspace_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_command.py

### def `test_command_registration_and_matching`
- `def test_command_registration_and_matching()`

### def `test_command_search_and_list`
- `def test_command_search_and_list()`

### def `test_documentation_generation`
- `def test_documentation_generation(tmp_path)`

## Module: core/tests/test_brain.py

### def `test_skill_selection`
- `def test_skill_selection()`

### def `test_provider_selection`
- `def test_provider_selection()`

### def `test_context_assembly`
- `def test_context_assembly()`

### def `test_workflow_planning`
- `def test_workflow_planning()`

### def `test_workflow_execution`
- `def test_workflow_execution()`

## Module: core/tests/test_redis_coordination.py

### def `coordination_env`
- `def coordination_env()`
- **Decorators**: `pytest.fixture`

### def `test_lock_ownership_registry`
- `def test_lock_ownership_registry(coordination_env)`

### def `test_lock_acquisition_exclusive_shared_reentrant`
- `def test_lock_acquisition_exclusive_shared_reentrant(coordination_env)`

### def `test_lease_management_and_heartbeats`
- `def test_lease_management_and_heartbeats(coordination_env)`

### def `test_deadlock_detection_and_recovery`
- `def test_deadlock_detection_and_recovery(coordination_env)`

### def `test_redis_outage_fallback`
- `def test_redis_outage_fallback(coordination_env)`

### def `test_observability_and_recommendations`
- `def test_observability_and_recommendations(coordination_env)`

## Module: core/tests/test_postgresql_pool_regression.py

### class `PoolError`
- **Inherits from**: Exception

### class `MockConnection`

**Methods:**

- `def __init__(self, id_)`
- `def cursor(self)`
- `def close(self)`

### class `MockPool`

**Methods:**

- `def __init__(self, minconn, maxconn)`
- `def getconn(self)`
- `def putconn(self, conn)`
- `def closeall(self)`

### def `pg_transport`
- `def pg_transport()`
- **Decorators**: `pytest.fixture`

### def `test_pg_concurrent_connection_acquisition`
- `def test_pg_concurrent_connection_acquisition(pg_transport)`
> Verify that multiple connections can be acquired concurrently from the pool.

### def `test_pg_connection_release`
- `def test_pg_connection_release(pg_transport)`
> Verify that connection is safely returned/released to the pool

on execution completion or rollback.

### def `test_pg_pool_exhaustion_handling`
- `def test_pg_pool_exhaustion_handling(pg_transport)`
> Verify that pool exhaustion (no connections available) is handled

correctly by raising PoolError.

### def `test_pg_reuse_of_returned_connections`
- `def test_pg_reuse_of_returned_connections(pg_transport)`
> Verify that returned/released connections are reused by subsequent queries.

## Module: core/tests/test_reasoning.py

### def `test_strategy_keyword_routing`
- `def test_strategy_keyword_routing()`

### def `test_evaluator_safety_and_complexity`
- `def test_evaluator_safety_and_complexity()`

### def `test_self_critique`
- `def test_self_critique()`

### def `test_reasoning_session_and_execution`
- `def test_reasoning_session_and_execution()`

## Module: core/tests/test_model.py

### def `test_model_registry`
- `def test_model_registry()`

### def `test_provider_registry`
- `def test_provider_registry()`

### def `test_individual_mock_providers`
- `def test_individual_mock_providers()`

### def `test_local_model_service`
- `def test_local_model_service()`

## Module: core/tests/test_redis_runtime_intelligence.py

### def `intelligence_env`
- `def intelligence_env()`
- **Decorators**: `pytest.fixture`

### def `test_telemetry_aggregation`
- `def test_telemetry_aggregation(intelligence_env)`

### def `test_health_scoring_and_analysis`
- `def test_health_scoring_and_analysis(intelligence_env)`

### def `test_capacity_and_performance_analysis`
- `def test_capacity_and_performance_analysis(intelligence_env)`

### def `test_diagnostics_and_recommendations`
- `def test_diagnostics_and_recommendations(intelligence_env)`

### def `test_global_runtime_intelligence_forwarding`
- `def test_global_runtime_intelligence_forwarding(intelligence_env)`

## Module: core/tests/test_test_coverage.py

### def `dummy_exec_summary`
- `def dummy_exec_summary()`
- **Decorators**: `pytest.fixture`

### def `test_coverage_analyzer`
- `def test_coverage_analyzer(dummy_exec_summary)`

### def `test_regression_analyzer`
- `def test_regression_analyzer(dummy_exec_summary)`

### def `test_validation_gaps_identification`
- `def test_validation_gaps_identification(dummy_exec_summary)`

### def `test_service_evaluation_flow`
- `def test_service_evaluation_flow(dummy_exec_summary)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_developer_agent.py

### def `test_developer_agent_analyze_repository`
- `def test_developer_agent_analyze_repository()`

### def `test_developer_agent_explain_file`
- `def test_developer_agent_explain_file()`

### def `test_developer_agent_git_review`
- `def test_developer_agent_git_review()`

## Module: core/tests/conftest.py

### def `setup_test_env`
- `def setup_test_env()`
- **Decorators**: `pytest.fixture(autouse=True)`

## Module: core/tests/test_diagram_gen.py

### class `TestDiagramGenerationStatus`

> Test that diagram generation completes successfully.

**Methods:**

- `def test_generation_succeeds(self, run_generator_once)`
  * Diagram generation should complete with success status.
- `def test_no_errors(self, run_generator_once)`
  * Diagram generation should produce no errors.
- `def test_ten_diagrams_produced(self, run_generator_once)`
  * Diagram generation should produce exactly 10 files.
- `def test_elapsed_is_positive(self, run_generator_once)`
  * Generation should complete in positive time.

### class `TestDiagramFilesExist`

> Test that all expected diagram files are created.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def test_file_exists(self, diagrams_dir, filename)`
  * Each expected diagram file should exist.
- `def test_file_not_empty(self, diagrams_dir, filename)`
  * Each diagram file should have content.

### class `TestMermaidSyntax`

> Test that generated diagrams have valid Mermaid syntax.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def test_has_mermaid_code_block(self, diagrams_dir, filename)`
  * Each diagram should have a Mermaid code block.
- `def test_has_correct_diagram_type(self, diagrams_dir, filename, diagram_type)`
  * Each diagram should declare the correct Mermaid diagram type.

### class `TestArchitectureDiagram`

> Test the architecture.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load architecture.md content.
- `def test_header_present(self, content)`
  * Architecture diagram should have proper header.
- `def test_generated_banner(self, content)`
  * Architecture diagram should have auto-generated banner.
- `def test_has_component_types_legend(self, content)`
  * Architecture diagram should have legend.
- `def test_has_nodes(self, content)`
  * Architecture diagram should define nodes.
- `def test_has_dependencies(self, content)`
  * Architecture diagram should show dependencies.

### class `TestServiceDependencyGraph`

> Test the dependency_graph.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load dependency_graph.md content.
- `def test_header_present(self, content)`
  * Dependency graph should have proper header.
- `def test_has_legend(self, content)`
  * Dependency graph should have legend.
- `def test_shows_dependencies(self, content)`
  * Dependency graph should show service dependencies.

### class `TestLifecycleDiagram`

> Test the lifecycle.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load lifecycle.md content.
- `def test_header_present(self, content)`
  * Lifecycle diagram should have proper header.
- `def test_has_lifecycle_phases(self, content)`
  * Lifecycle diagram should document phases.

### class `TestBootstrapSequence`

> Test the runtime.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load runtime.md content.
- `def test_header_present(self, content)`
  * Bootstrap sequence should have proper header.
- `def test_has_sequence_diagram(self, content)`
  * Bootstrap sequence should use sequence diagram.
- `def test_has_bootstrap_steps(self, content)`
  * Bootstrap sequence should list steps.

### class `TestPersistenceArchitecture`

> Test the persistence.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load persistence.md content.
- `def test_header_present(self, content)`
  * Persistence diagram should have proper header.
- `def test_has_persistence_layers(self, content)`
  * Persistence diagram should show layers.

### class `TestSemanticMemoryPipeline`

> Test the semantic_memory.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load semantic_memory.md content.
- `def test_header_present(self, content)`
  * Semantic memory diagram should have proper header.
- `def test_has_pipeline_stages(self, content)`
  * Semantic memory diagram should describe pipeline.

### class `TestHybridRetrievalPipeline`

> Test the hybrid_retrieval.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load hybrid_retrieval.md content.
- `def test_header_present(self, content)`
  * Hybrid retrieval diagram should have proper header.
- `def test_has_keyword_and_semantic_paths(self, content)`
  * Hybrid retrieval should show both search paths.

### class `TestOmniRouteArchitecture`

> Test the omniroute.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load omniroute.md content.
- `def test_header_present(self, content)`
  * OmniRoute diagram should have proper header.
- `def test_has_model_selection(self, content)`
  * OmniRoute diagram should show model selection.

### class `TestAgentInteractionFlow`

> Test the agents.md diagram content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load agents.md content.
- `def test_header_present(self, content)`
  * Agent flow diagram should have proper header.
- `def test_has_sequence_diagram(self, content)`
  * Agent flow should use sequence diagram.
- `def test_has_agent_capabilities(self, content)`
  * Agent flow should describe agent types.

### class `TestDiagramsIndex`

> Test the README.md index content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def content(self, diagrams_dir)`
  * Load README.md content.
- `def test_header_present(self, content)`
  * README should have proper header.
- `def test_overview_section(self, content)`
  * README should have overview.
- `def test_diagram_files_table(self, content)`
  * README should list all diagram files.
- `def test_viewing_instructions(self, content)`
  * README should explain how to view diagrams.
- `def test_regeneration_instructions(self, content)`
  * README should have regeneration instructions.
- `def test_cross_references(self, content)`
  * README should have cross-references.

### class `TestDiagramIdempotency`

> Test that diagram generation is idempotent.

**Methods:**

- `def test_same_diagram_count_on_rerun(self, project_root)`
  * Re-running should generate the same number of diagrams.
- `def test_same_file_count_on_rerun(self, project_root)`
  * Re-running should produce the same number of files.

### class `TestHandwrittenDocsUntouched`

> Test that diagram generation doesn't modify handwritten documentation.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def test_handwritten_doc_unchanged(self, project_root, doc_path)`
  * Handwritten documentation should remain unchanged after generation.

### def `project_root`
- `def project_root()`
- **Decorators**: `pytest.fixture`
> Return the project root directory.

### def `diagrams_dir`
- `def diagrams_dir(project_root)`
- **Decorators**: `pytest.fixture`
> Return the diagrams output directory.

### def `run_generator_once`
- `def run_generator_once(project_root)`
- **Decorators**: `pytest.fixture`
> Run the diagram generator once and return the result.

## Module: core/tests/test_n8n.py

### def `test_workflow_translation_and_serialization`
- `def test_workflow_translation_and_serialization()`

### def `test_workflow_graph_validator`
- `def test_workflow_graph_validator()`

### def `test_natural_language_workflow_generator`
- `def test_natural_language_workflow_generator()`

### def `test_workflow_lifecycle_and_health`
- `def test_workflow_lifecycle_and_health()`

## Module: core/tests/test_engineering_intelligence.py

### def `dummy_code_summary`
- `def dummy_code_summary()`
- **Decorators**: `pytest.fixture`

### def `test_change_impact_analyzer`
- `def test_change_impact_analyzer(dummy_code_summary)`

### def `test_complexity_estimator`
- `def test_complexity_estimator(dummy_code_summary)`

### def `test_risk_analyzer`
- `def test_risk_analyzer(dummy_code_summary)`

### def `test_implementation_planner`
- `def test_implementation_planner(dummy_code_summary)`

### def `test_engineering_intelligence_service_integration`
- `def test_engineering_intelligence_service_integration(dummy_code_summary)`

### def `test_backward_compatibility_and_custom_extensions`
- `def test_backward_compatibility_and_custom_extensions()`

## Module: core/tests/test_task.py

### def `test_task_models`
- `def test_task_models()`

### def `test_task_planning`
- `def test_task_planning()`

### def `test_task_execution_success`
- `def test_task_execution_success()`

### def `test_task_execution_failure`
- `def test_task_execution_failure()`

### def `test_task_history_persistence`
- `def test_task_history_persistence()`

## Module: core/tests/test_github_skill.py

### def `test_encrypted_config`
- `def test_encrypted_config()`

### def `test_github_client_mock_fallbacks`
- `def test_github_client_mock_fallbacks()`

### def `test_render_template`
- `def test_render_template(tmp_path)`

### def `test_github_agent_execution`
- `def test_github_agent_execution()`

### def `test_parse_repo_and_args`
- `def test_parse_repo_and_args()`

### def `test_register_commands`
- `def test_register_commands()`

## Module: core/tests/test_ops_gen.py

### class `TestOperationsGenerationStatus`

> Test that operations guide generation completes successfully.

**Methods:**

- `def test_generation_succeeds(self, run_generator_once)`
  * Operations generation should complete with success status.
- `def test_no_errors(self, run_generator_once)`
  * Operations generation should produce no errors.
- `def test_nine_guides_produced(self, run_generator_once)`
  * Operations generation should produce exactly 9 files.
- `def test_elapsed_is_positive(self, run_generator_once)`
  * Generation should complete in positive time.
- `def test_files_written_list_has_nine_entries(self, run_generator_once)`
  * files_written should contain exactly 9 absolute paths.
- `def test_all_written_paths_are_absolute(self, run_generator_once)`
  * All written file paths should be absolute.

### class `TestOperationsFilesExist`

> Test that all expected operations guide files are created.

**Methods:**

- `def test_file_exists(self, operations_dir, run_generator_once, filename)`
  * Each expected guide file should exist.
- `def test_file_not_empty(self, operations_dir, run_generator_once, filename)`
  * Each guide file should have content.
- `def test_file_has_auto_generated_banner(self, operations_dir, run_generator_once, filename)`
  * Every generated file should have the auto-generated banner.
- `def test_file_has_generated_timestamp(self, operations_dir, run_generator_once, filename)`
  * Every generated file should have a timestamp in the banner.

### class `TestReadmeIndex`

> Test the README.md index content.

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_generated_banner(self, all_guide_contents)`
- `def test_overview_section(self, all_guide_contents)`
- `def test_all_guide_files_listed(self, all_guide_contents)`
- `def test_regeneration_instructions(self, all_guide_contents)`
- `def test_cross_references_present(self, all_guide_contents)`

### class `TestLocalSetupGuide`

> Test the local_setup.md guide content.

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_prerequisites_section(self, all_guide_contents)`
- `def test_installation_steps_section(self, all_guide_contents)`
- `def test_clone_step(self, all_guide_contents)`
- `def test_venv_step(self, all_guide_contents)`
- `def test_docker_compose_step(self, all_guide_contents)`
- `def test_external_services_listed(self, all_guide_contents)`
- `def test_minimum_env_vars_example(self, all_guide_contents)`
- `def test_config_toml_step(self, all_guide_contents)`
- `def test_database_migration_step(self, all_guide_contents)`
- `def test_start_aios_step(self, all_guide_contents)`
- `def test_verification_section(self, all_guide_contents)`
- `def test_troubleshooting_cross_ref(self, all_guide_contents)`

### class `TestConfigurationGuide`

> Test the configuration.md guide content for complete parameter coverage.

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_configuration_overview_section(self, all_guide_contents)`
- `def test_priority_order_explained(self, all_guide_contents)`
- `def test_postgres_section_present(self, all_guide_contents)`
- `def test_postgres_param_documented(self, all_guide_contents, param)`
  * Each PostgreSQL env var found in persistence.py must be documented.
- `def test_postgres_sslmode_production_note(self, all_guide_contents)`
- `def test_postgres_implementation_reference(self, all_guide_contents)`
- `def test_redis_section_present(self, all_guide_contents)`
- `def test_redis_param_documented(self, all_guide_contents, param)`
  * Each Redis env var found in redis.py must be documented.
- `def test_redis_usage_note(self, all_guide_contents)`
- `def test_qdrant_section_present(self, all_guide_contents)`
- `def test_qdrant_param_documented(self, all_guide_contents, param)`
  * Each Qdrant env var found in qdrant.py must be documented.
- `def test_qdrant_collections_note(self, all_guide_contents)`
- `def test_n8n_section_present(self, all_guide_contents)`
- `def test_n8n_param_documented(self, all_guide_contents, param)`
  * Each n8n env var from service.py must be documented.
- `def test_n8n_auth_priority_documented(self, all_guide_contents)`
  * Authentication priority order must be documented.
- `def test_omniroute_section_present(self, all_guide_contents)`
- `def test_omniroute_param_documented(self, all_guide_contents, param)`
  * Each OmniRoute provider API key must be documented.
- `def test_config_toml_example(self, all_guide_contents)`
  * config/config.toml example must be included.
- `def test_security_note_present(self, all_guide_contents)`
- `def test_omniroute_diagram_cross_ref(self, all_guide_contents)`
  * Configuration should cross-reference the OmniRoute diagram.

### class `TestDeploymentGuide`

> Test the deployment.md guide content.

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_deployment_architecture_section(self, all_guide_contents)`
- `def test_required_services_listed(self, all_guide_contents)`
- `def test_optional_services_listed(self, all_guide_contents)`
- `def test_pre_deployment_checklist_ref(self, all_guide_contents)`
- `def test_deployment_steps_section(self, all_guide_contents)`
- `def test_environment_configuration_step(self, all_guide_contents)`
- `def test_migrations_step(self, all_guide_contents)`
- `def test_post_deployment_section(self, all_guide_contents)`
- `def test_rollback_procedure(self, all_guide_contents)`

### class `TestStartupGuide`

> Test the startup.md guide content matches the actual bootstrap_kernel.py order.

Expected bootstrap sequence from bootstrap_modules/bootstrap_kernel.py:
  1. PostgreSQL → Persistence Platform
  2. Redis → Redis Platform
  3. Qdrant → Vector Memory Platform
  4. Database Migrations → PersistenceBootstrapper.start()
  5. AIOS Core → full kernel
  6. n8n → optional workflow platform

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_bootstrap_architecture_section(self, all_guide_contents)`
  * Startup guide must document the bootstrap architecture.
- `def test_startup_sequence_section(self, all_guide_contents)`
- `def test_postgres_is_step_1(self, all_guide_contents)`
  * PostgreSQL must be step 1 — required by PersistenceBootstrapper.
- `def test_redis_is_step_2(self, all_guide_contents)`
  * Redis must be step 2 — required by RedisRuntimeService.
- `def test_qdrant_is_step_3(self, all_guide_contents)`
  * Qdrant must be step 3 — required by QdrantPlatform.
- `def test_migration_is_step_4(self, all_guide_contents)`
  * Database Migrations must be step 4 — depends on PostgreSQL.
- `def test_aios_core_is_step_5(self, all_guide_contents)`
  * AIOS Core must be step 5 — depends on all external services.
- `def test_n8n_is_step_6(self, all_guide_contents)`
  * n8n must be step 6 and marked as optional.
- `def test_all_healthchecks_present(self, all_guide_contents)`
  * Each service should have a verification/healthcheck command.
- `def test_postgres_depends_noted(self, all_guide_contents)`
- `def test_bootstrap_order_matches_kernel(self, all_guide_contents)`
  * Verify startup.md step order is consistent with bootstrap_kernel.py.
The bootstrap sequence reads: Persistence → Redis → Qdrant → Runtime → n8n.
- `def test_automated_startup_section(self, all_guide_contents)`
- `def test_shutdown_sequence_present(self, all_guide_contents)`
- `def test_startup_failures_section(self, all_guide_contents)`
- `def test_troubleshooting_cross_ref(self, all_guide_contents)`

### class `TestMonitoringGuide`

> Test the monitoring.md guide content.

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_monitoring_overview_section(self, all_guide_contents)`
- `def test_service_metrics_section(self, all_guide_contents)`
- `def test_database_metrics_section(self, all_guide_contents)`
- `def test_system_metrics_section(self, all_guide_contents)`
- `def test_api_response_time_metric(self, all_guide_contents)`
- `def test_omniroute_metrics(self, all_guide_contents)`
  * OmniRoute provider metrics must be documented.
- `def test_postgres_metric_documented(self, all_guide_contents)`
- `def test_redis_metric_documented(self, all_guide_contents)`
- `def test_qdrant_metric_documented(self, all_guide_contents)`
- `def test_n8n_metric_documented(self, all_guide_contents)`
  * n8n workflow failures metric must be documented.
- `def test_monitoring_stack_section(self, all_guide_contents)`
- `def test_health_check_endpoints(self, all_guide_contents)`
- `def test_log_management_section(self, all_guide_contents)`
- `def test_cross_references_present(self, all_guide_contents)`

### class `TestBackupRestoreGuide`

> Test the backup_restore.md guide content.

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_backup_strategy_section(self, all_guide_contents)`
- `def test_postgres_backup_documented(self, all_guide_contents)`
- `def test_qdrant_backup_documented(self, all_guide_contents)`
- `def test_config_backup_documented(self, all_guide_contents)`
- `def test_postgres_restore_procedure(self, all_guide_contents)`
- `def test_qdrant_restore_procedure(self, all_guide_contents)`
- `def test_disaster_recovery_section(self, all_guide_contents)`
- `def test_rto_rpo_defined(self, all_guide_contents)`
- `def test_backup_summary_table(self, all_guide_contents)`
  * A backup strategy summary table should be present.
- `def test_cross_references_present(self, all_guide_contents)`

### class `TestTroubleshootingGuide`

> Test the troubleshooting.md guide content.

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_quick_diagnostics_section(self, all_guide_contents)`
  * Guide should have quick diagnostics commands.
- `def test_postgres_issue_documented(self, all_guide_contents)`
- `def test_redis_issue_documented(self, all_guide_contents)`
- `def test_qdrant_issue_documented(self, all_guide_contents)`
- `def test_n8n_issue_documented(self, all_guide_contents)`
- `def test_omniroute_issue_documented(self, all_guide_contents)`
  * OmniRoute/provider timeout issues must be documented.
- `def test_migration_issue_documented(self, all_guide_contents)`
  * Migration failures must be documented.
- `def test_common_issues_section(self, all_guide_contents)`
- `def test_general_troubleshooting_steps(self, all_guide_contents)`
- `def test_diagnostic_commands_present(self, all_guide_contents)`
- `def test_getting_help_section(self, all_guide_contents)`
- `def test_cross_references_present(self, all_guide_contents)`

### class `TestProductionChecklist`

> Test the production_checklist.md content for completeness.

**Methods:**

- `def test_header_present(self, all_guide_contents)`
- `def test_infrastructure_section(self, all_guide_contents)`
- `def test_security_section(self, all_guide_contents)`
- `def test_configuration_section(self, all_guide_contents)`
- `def test_database_section(self, all_guide_contents)`
- `def test_application_section(self, all_guide_contents)`
- `def test_monitoring_observability_section(self, all_guide_contents)`
- `def test_backup_dr_section(self, all_guide_contents)`
- `def test_performance_section(self, all_guide_contents)`
- `def test_documentation_section(self, all_guide_contents)`
- `def test_post_deployment_section(self, all_guide_contents)`
- `def test_sign_off_section(self, all_guide_contents)`
- `def test_redis_password_in_security(self, all_guide_contents)`
- `def test_qdrant_api_key_in_security(self, all_guide_contents)`
- `def test_n8n_in_checklist(self, all_guide_contents)`
- `def test_omniroute_in_checklist(self, all_guide_contents)`
- `def test_all_checkbox_items_use_correct_format(self, all_guide_contents)`
  * All checklist items must use standard markdown task syntax.
- `def test_cross_references_all_guides(self, all_guide_contents)`
  * Production checklist should cross-reference all related guides.

### class `TestCrossReferences`

> Test that cross-references between guides are valid.

**Methods:**

- `def test_internal_cross_reference(self, all_guide_contents, source_file, target_file)`
  * Source guide should reference target guide.
- `def test_generated_dir_reference_in_readme(self, all_guide_contents, source_file)`
  * README should reference all generated directories.

### class `TestIdempotency`

> Test that running the generator twice produces identical output.

**Methods:**

- `def test_second_run_succeeds(self, project_root)`
  * Second generation run should succeed.
- `def test_idempotent_output(self, project_root, operations_dir)`
  * Running generator twice produces identical content (modulo timestamp in banner).
- `def test_file_count_stable_across_runs(self, project_root)`
  * Guide count must be stable across multiple runs.

### class `TestHandwrittenDocPreservation`

> Verify that the generator does NOT overwrite handwritten documentation
in other docs/ subdirectories.

**Methods:**

- `def handwritten_dirs(self, project_root: Path) -> list`
  * Return list of handwritten documentation directories.
- `def test_architecture_docs_unchanged(self, project_root, handwritten_dirs, run_generator_once)`
  * Generating operations docs must not touch architecture directory.
- `def test_guides_docs_unchanged(self, project_root, run_generator_once)`
  * Generating operations docs must not touch guides directory.
- `def test_generator_only_writes_to_operations_dir(self, run_generator_once, operations_dir)`
  * All written files must be inside docs/operations/.

### class `TestServiceDeploymentAnalyzer`

> Unit tests for ServiceDeploymentAnalyzer.

**Methods:**

- `def deployments(self, project_root) -> list`
- `def test_returns_list(self, deployments)`
- `def test_all_items_are_service_deployments(self, deployments)`
- `def test_postgres_is_present(self, deployments)`
- `def test_redis_is_present(self, deployments)`
- `def test_qdrant_is_present(self, deployments)`
- `def test_n8n_is_optional(self, deployments)`
- `def test_postgres_port_is_5432(self, deployments)`
- `def test_redis_port_is_6379(self, deployments)`
- `def test_qdrant_port_is_6333(self, deployments)`
- `def test_n8n_port_is_5678(self, deployments)`
- `def test_postgres_has_required_config_keys(self, deployments)`
- `def test_redis_has_password_and_tls_keys(self, deployments)`
- `def test_qdrant_has_grpc_port_key(self, deployments)`
- `def test_n8n_has_auth_keys(self, deployments)`

### class `TestConfigurationAnalyzer`

> Unit tests for ConfigurationAnalyzer.

**Methods:**

- `def configs(self, project_root) -> list`
- `def test_returns_list(self, configs)`
- `def test_all_items_are_config_items(self, configs)`
- `def test_postgres_database_is_canonical_key(self, configs)`
  * POSTGRES_DATABASE (not POSTGRES_DB) is the canonical env var.
- `def test_postgres_sslmode_present(self, configs)`
- `def test_redis_password_present(self, configs)`
- `def test_redis_username_present(self, configs)`
- `def test_redis_tls_present(self, configs)`
- `def test_qdrant_grpc_port_present(self, configs)`
- `def test_qdrant_https_present(self, configs)`
- `def test_qdrant_default_dimensions_present(self, configs)`
- `def test_n8n_server_url_present(self, configs)`
- `def test_n8n_bearer_token_present(self, configs)`
- `def test_openrouter_api_key_present(self, configs)`
- `def test_gemini_api_key_present(self, configs)`
- `def test_configs_have_sections(self, configs)`

### class `TestStartupSequenceAnalyzer`

> Unit tests for StartupSequenceAnalyzer.

**Methods:**

- `def steps(self) -> list`
- `def test_returns_list(self, steps)`
- `def test_six_steps(self, steps)`
- `def test_all_items_are_startup_steps(self, steps)`
- `def test_step_1_is_postgres(self, steps)`
- `def test_step_2_is_redis(self, steps)`
- `def test_step_3_is_qdrant(self, steps)`
- `def test_step_4_is_migrations(self, steps)`
- `def test_step_4_depends_on_postgres(self, steps)`
- `def test_step_5_is_aios_core(self, steps)`
- `def test_step_5_depends_on_all_external_services(self, steps)`
- `def test_step_6_is_n8n(self, steps)`
- `def test_steps_have_healthchecks(self, steps)`
  * All service steps except migrations should have healthcheck commands.
- `def test_steps_have_notes(self, steps)`
  * All steps should have contextual notes.
- `def test_steps_are_ordered_correctly(self, steps)`

### class `TestOmniRouteAnalyzer`

> Unit tests for OmniRouteAnalyzer.

**Methods:**

- `def providers(self) -> list`
- `def test_returns_list(self, providers)`
- `def test_three_providers(self, providers)`
- `def test_all_items_are_omniroute_providers(self, providers)`
- `def test_openrouter_provider_present(self, providers)`
- `def test_anthropic_provider_present(self, providers)`
- `def test_gemini_provider_present(self, providers)`
- `def test_providers_have_env_keys(self, providers)`
- `def test_providers_have_base_urls(self, providers)`
- `def test_providers_have_default_models(self, providers)`
- `def test_openrouter_default_model(self, providers)`
  * Default model for OpenRouter matches config/config.toml.

### class `TestBackupAnalyzer`

> Unit tests for BackupAnalyzer.

**Methods:**

- `def targets(self) -> list`
- `def test_returns_list(self, targets)`
- `def test_four_backup_targets(self, targets)`
- `def test_all_items_are_backup_targets(self, targets)`
- `def test_postgres_backup_daily(self, targets)`
- `def test_qdrant_backup_daily(self, targets)`
- `def test_config_backup_weekly(self, targets)`
- `def test_all_targets_have_retention(self, targets)`
- `def test_all_targets_have_locations(self, targets)`
- `def test_targets_have_notes(self, targets)`

### class `TestMonitoringAnalyzer`

> Unit tests for MonitoringAnalyzer.

**Methods:**

- `def metrics(self) -> list`
- `def test_returns_list(self, metrics)`
- `def test_all_items_are_monitoring_metrics(self, metrics)`
- `def test_has_service_metrics(self, metrics)`
- `def test_has_database_metrics(self, metrics)`
- `def test_has_system_metrics(self, metrics)`
- `def test_omniroute_metrics_present(self, metrics)`
  * OmniRoute-specific metrics must be included.
- `def test_n8n_metric_present(self, metrics)`
- `def test_all_metrics_have_thresholds(self, metrics)`

### class `TestTroubleshootingAnalyzer`

> Unit tests for TroubleshootingAnalyzer.

**Methods:**

- `def entries(self) -> list`
- `def test_returns_list(self, entries)`
- `def test_at_least_seven_entries(self, entries)`
- `def test_all_items_are_troubleshooting_entries(self, entries)`
- `def test_postgres_entry_present(self, entries)`
- `def test_redis_entry_present(self, entries)`
- `def test_qdrant_entry_present(self, entries)`
- `def test_n8n_entry_present(self, entries)`
- `def test_omniroute_entry_present(self, entries)`
  * OmniRoute/provider timeout issues must be documented.
- `def test_migration_entry_present(self, entries)`
- `def test_entries_have_solutions(self, entries)`
- `def test_entries_have_related_logs(self, entries)`
- `def test_entries_have_cross_refs(self, entries)`

### def `project_root`
- `def project_root() -> Path`
- **Decorators**: `pytest.fixture(scope='module')`
> Return the project root directory.

### def `operations_dir`
- `def operations_dir(project_root: Path) -> Path`
- **Decorators**: `pytest.fixture(scope='module')`
> Return the operations output directory.

### def `run_generator_once`
- `def run_generator_once(project_root: Path) -> OperationsGenerationResult`
- **Decorators**: `pytest.fixture(scope='module')`
> Run the operations generator once and return the result.

### def `all_guide_contents`
- `def all_guide_contents(operations_dir: Path, run_generator_once: OperationsGenerationResult) -> dict`
- **Decorators**: `pytest.fixture(scope='module')`
> Load all guide file contents after generation.

### def `_strip_timestamps`
- `def _strip_timestamps(content: str) -> str`
> Strip timestamp values so idempotency check ignores generation time.

## Module: core/tests/test_agent.py

### def `test_agent_registration`
- `def test_agent_registration()`

### def `test_mock_agent_execution_pipeline`
- `def test_mock_agent_execution_pipeline()`

### def `test_agent_runtime_failure_handling`
- `def test_agent_runtime_failure_handling()`

## Module: core/tests/test_workflow_planning.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `test_intent_analysis`
- `def test_intent_analysis()`

### def `test_dependency_resolution`
- `def test_dependency_resolution()`

### def `test_optimizer_merges_and_prunes`
- `def test_optimizer_merges_and_prunes()`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility(mock_memory_service)`

## Module: core/tests/test_ai_memory_persistence.py

### def `ai_setup`
- `def ai_setup()`
- **Decorators**: `pytest.fixture`

### def `test_ai_provider_repo_crud`
- `def test_ai_provider_repo_crud(ai_setup)`

### def `test_ai_memory_repo_crud`
- `def test_ai_memory_repo_crud(ai_setup)`

### def `test_validation_policies`
- `def test_validation_policies(ai_setup)`

### def `test_checkpoint_and_failover`
- `def test_checkpoint_and_failover(ai_setup)`

## Module: core/tests/run_redis_production_validation.py

### def `main`
- `def main()`

### def `update_project_status`
- `def update_project_status(overall_avg, throughput)`

### def `update_knowledge_base`
- `def update_knowledge_base()`

## Module: core/tests/test_event_bus.py

### class `DummyEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

### class `AnotherDummyEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

### def `test_event_bus_registration`
- `def test_event_bus_registration()`

### def `test_event_bus_subscription`
- `def test_event_bus_subscription()`

### def `test_event_bus_unsubscription`
- `def test_event_bus_unsubscription()`

### def `test_event_bus_multiple_subscribers`
- `def test_event_bus_multiple_subscribers()`

### def `test_event_bus_handler_isolation`
- `def test_event_bus_handler_isolation(caplog)`

## Module: core/tests/test_redis_platform.py

### def `redis_env`
- `def redis_env()`
- **Decorators**: `pytest.fixture`

### def `test_redis_configuration`
- `def test_redis_configuration(redis_env)`

### def `test_fake_redis_client`
- `def test_fake_redis_client()`

### def `test_redis_transport_and_provider`
- `def test_redis_transport_and_provider(redis_env)`

### def `test_keyspace_validator`
- `def test_keyspace_validator(redis_env)`

### def `test_telemetry_and_statistics`
- `def test_telemetry_and_statistics(redis_env)`

### def `test_diagnostics_and_recommendations`
- `def test_diagnostics_and_recommendations(redis_env)`

### def `test_report_generation`
- `def test_report_generation(redis_env)`

## Module: core/tests/test_api_documentation.py

### def `sample_code_structure`
- `def sample_code_structure()`
- **Decorators**: `pytest.fixture`

### def `test_api_analyzer`
- `def test_api_analyzer(sample_code_structure)`

### def `test_api_planner`
- `def test_api_planner()`

### def `test_api_validator`
- `def test_api_validator()`

### def `test_api_registry`
- `def test_api_registry()`

### def `test_service_evaluation_flow`
- `def test_service_evaluation_flow(sample_code_structure)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_test_impact.py

### def `mock_code_summary`
- `def mock_code_summary()`
- **Decorators**: `pytest.fixture`

### def `test_impact_graph_generation`
- `def test_impact_graph_generation(mock_code_summary)`

### def `test_affected_modules_suites_detection`
- `def test_affected_modules_suites_detection(mock_code_summary)`

### def `test_regression_candidates`
- `def test_regression_candidates(mock_code_summary)`

### def `test_risk_assessment`
- `def test_risk_assessment(mock_code_summary)`

### def `test_coverage_targets`
- `def test_coverage_targets(mock_code_summary)`

### def `test_service_integrations`
- `def test_service_integrations(mock_code_summary)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_integration_flow.py

### def `test_end_to_end_research_to_n8n_integration`
- `def test_end_to_end_research_to_n8n_integration()`

## Module: core/tests/test_agent_framework.py

### def `test_agent_registry_and_factory`
- `def test_agent_registry_and_factory()`

### def `test_agent_task_and_capabilities`
- `def test_agent_task_and_capabilities()`

### def `test_local_agent_manager_coordination`
- `def test_local_agent_manager_coordination()`

### def `test_career_agent_context_propagation`
- `def test_career_agent_context_propagation()`

## Module: core/tests/test_providers.py

### def `test_provider_health_and_metrics`
- `def test_provider_health_and_metrics()`

### def `test_provider_fallback_execution`
- `def test_provider_fallback_execution()`

## Module: core/tests/test_session.py

### def `test_session_lifecycle`
- `def test_session_lifecycle()`

### def `test_session_auto_end_previous`
- `def test_session_auto_end_previous()`

### def `test_create_session_compatibility`
- `def test_create_session_compatibility()`

## Module: core/tests/test_ai_workspace.py

### def `temp_repo_root`
- `def temp_repo_root(tmp_path)`
- **Decorators**: `pytest.fixture`

### def `test_workspace_creation`
- `def test_workspace_creation(temp_repo_root)`

### def `test_workspace_validation`
- `def test_workspace_validation(temp_repo_root)`

### def `test_session_lifecycle`
- `def test_session_lifecycle(temp_repo_root)`

### def `test_snapshot_creation_and_restoration`
- `def test_snapshot_creation_and_restoration(temp_repo_root)`

### def `test_workspace_cleanup_and_archive`
- `def test_workspace_cleanup_and_archive(temp_repo_root)`

### def `test_memory_and_knowledge_hub_integration`
- `def test_memory_and_knowledge_hub_integration(temp_repo_root)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_github_intelligence.py

### def `test_github_authentication`
- `def test_github_authentication()`

### def `test_repository_retrieval`
- `def test_repository_retrieval(mock_client_class)`
- **Decorators**: `patch('httpx.Client')`

### def `test_pull_requests`
- `def test_pull_requests(mock_client_class)`
- **Decorators**: `patch('httpx.Client')`

### def `test_issues`
- `def test_issues(mock_client_class)`
- **Decorators**: `patch('httpx.Client')`

### def `test_commits_and_branches`
- `def test_commits_and_branches(mock_client_class)`
- **Decorators**: `patch('httpx.Client')`

### def `test_caching`
- `def test_caching(mock_client_class)`
- **Decorators**: `patch('httpx.Client')`

### def `test_retries_transient_failures`
- `def test_retries_transient_failures(mock_client_class)`
- **Decorators**: `patch('httpx.Client')`

### def `test_offline_mode`
- `def test_offline_mode()`

### def `test_rate_limiting`
- `def test_rate_limiting()`

### def `test_brain_integration`
- `def test_brain_integration()`

### def `test_career_agent_integration`
- `def test_career_agent_integration(mock_client_class)`
- **Decorators**: `patch('httpx.Client')`

## Module: core/tests/test_test_execution.py

### def `test_pytest_adapter_validation`
- `def test_pytest_adapter_validation(tmp_path)`

### def `test_pytest_adapter_successful_execution`
- `def test_pytest_adapter_successful_execution(mock_run, tmp_path)`
- **Decorators**: `patch('subprocess.run')`

### def `test_pytest_adapter_timeout`
- `def test_pytest_adapter_timeout(mock_run, tmp_path)`
- **Decorators**: `patch('subprocess.run')`

### def `test_runner_and_executor`
- `def test_runner_and_executor(mock_run, tmp_path)`
- **Decorators**: `patch('subprocess.run')`

### def `test_execution_service_flow`
- `def test_execution_service_flow(mock_run, tmp_path)`
- **Decorators**: `patch('subprocess.run')`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_n8n_integration.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `test_authentication_providers`
- `def test_authentication_providers()`

### def `test_connection_management`
- `def test_connection_management()`

### def `test_health_monitor`
- `def test_health_monitor()`

### def `test_validator`
- `def test_validator()`

### def `test_client_upload_and_trigger`
- `def test_client_upload_and_trigger()`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_workspace_persistence.py

### def `persistence_setup`
- `def persistence_setup()`
- **Decorators**: `pytest.fixture`

### def `test_workspace_lifecycle`
- `def test_workspace_lifecycle(persistence_setup)`

### def `test_session_lifecycle`
- `def test_session_lifecycle(persistence_setup)`

### def `test_project_repository`
- `def test_project_repository(persistence_setup)`

### def `test_engineering_profile_persistence_and_versioning`
- `def test_engineering_profile_persistence_and_versioning(persistence_setup)`

### def `test_configuration_persistence`
- `def test_configuration_persistence(persistence_setup)`

### def `test_transaction_rollback_via_savepoints`
- `def test_transaction_rollback_via_savepoints(persistence_setup)`

### def `test_health_monitor_and_diagnostics`
- `def test_health_monitor_and_diagnostics(persistence_setup)`

## Module: core/tests/test_qdrant_production_validation.py

### def `test_qdrant_production_validation_run`
- `def test_qdrant_production_validation_run()`

## Module: core/tests/test_capability.py

### def `test_metadata_capability_serialization`
- `def test_metadata_capability_serialization()`

### def `test_loader_capabilities_from_toml`
- `def test_loader_capabilities_from_toml()`

### def `test_skill_selector_capability_filtering`
- `def test_skill_selector_capability_filtering()`

### def `test_planner_capability_propagation`
- `def test_planner_capability_propagation()`

## Module: core/tests/test_n8n_production.py

### def `test_n8n_production_auth_with_session`
- `def test_n8n_production_auth_with_session()`

### def `test_n8n_production_client_request`
- `def test_n8n_production_client_request(mock_request)`
- **Decorators**: `patch('httpx.Client.request')`

### def `test_n8n_production_client_retry`
- `def test_n8n_production_client_retry(mock_request)`
- **Decorators**: `patch('httpx.Client.request')`

### def `test_n8n_production_workflow_crud`
- `def test_n8n_production_workflow_crud(mock_request)`
- **Decorators**: `patch('httpx.Client.request')`

### def `test_n8n_production_execution_polling`
- `def test_n8n_production_execution_polling(mock_request)`
- **Decorators**: `patch('httpx.Client.request')`

### def `test_n8n_production_health_monitor`
- `def test_n8n_production_health_monitor(mock_request)`
- **Decorators**: `patch('httpx.Client.request')`

### def `test_n8n_production_version_capability`
- `def test_n8n_production_version_capability()`

### def `test_n8n_production_diagnostics`
- `def test_n8n_production_diagnostics()`

### def `test_n8n_production_report_generation`
- `def test_n8n_production_report_generation(tmp_path)`

## Module: core/tests/test_embedding_cache_regression.py

### def `clean_env`
- `def clean_env()`
- **Decorators**: `pytest.fixture(autouse=True)`

### def `test_cache_lru_eviction`
- `def test_cache_lru_eviction()`
> Verify that the cache evicts the least recently used element when exceeding max_size.

### def `test_cache_ttl_expiration`
- `def test_cache_ttl_expiration()`
> Verify that cached elements expire after their configured TTL.

### def `test_cache_size_limits`
- `def test_cache_size_limits()`
> Verify that the cache size never exceeds EMBEDDING_CACHE_MAX_SIZE.

### def `test_cache_statistics_after_eviction`
- `def test_cache_statistics_after_eviction()`
> Verify hit, miss, size, and ratio stats remain correct after evictions/expirations.

## Module: core/tests/test_career_agent.py

### def `test_career_agent_analyze_job`
- `def test_career_agent_analyze_job()`

### def `test_career_agent_tailor_resume`
- `def test_career_agent_tailor_resume()`

### def `test_career_agent_ats_score`
- `def test_career_agent_ats_score()`

### def `test_career_agent_interview_prep`
- `def test_career_agent_interview_prep()`

### def `test_career_agent_cover_letter`
- `def test_career_agent_cover_letter()`

## Module: core/tests/test_intent_engine.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_reasoning_service`
- `def mock_reasoning_service()`
- **Decorators**: `pytest.fixture`

### def `test_intent_classification_rule_based`
- `def test_intent_classification_rule_based()`

### def `test_intent_classification_llm`
- `def test_intent_classification_llm()`

### def `test_service_composition_and_order`
- `def test_service_composition_and_order()`

### def `test_intent_engine_process_objective`
- `def test_intent_engine_process_objective(mock_memory_service, mock_reasoning_service)`

### def `test_intent_engine_reasoning_rejection`
- `def test_intent_engine_reasoning_rejection(mock_memory_service, mock_reasoning_service)`

### def `test_intent_engine_registry_wiring`
- `def test_intent_engine_registry_wiring(mock_memory_service, mock_reasoning_service)`

## Module: core/tests/test_test_generation.py

### def `test_pattern_analyzer`
- `def test_pattern_analyzer()`

### def `test_template_engine`
- `def test_template_engine()`

### def `test_case_builder`
- `def test_case_builder()`

### def `test_generators`
- `def test_generators()`

### def `test_test_generator`
- `def test_test_generator(tmp_path)`

### def `test_test_generation_service_flow`
- `def test_test_generation_service_flow(tmp_path)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_documentation_intelligence.py

### def `mock_profile_service`
- `def mock_profile_service()`
- **Decorators**: `pytest.fixture`

### def `test_registry_creation`
- `def test_registry_creation()`

### def `test_metadata_validation`
- `def test_metadata_validation()`

### def `test_profile_integration`
- `def test_profile_integration()`

### def `test_document_registration`
- `def test_document_registration()`

### def `test_service_evaluation_flow`
- `def test_service_evaluation_flow(mock_profile_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_career_os.py

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `mock_personal_service`
- `def mock_personal_service()`
- **Decorators**: `pytest.fixture`

### def `mock_github_service`
- `def mock_github_service()`
- **Decorators**: `pytest.fixture`

### def `test_career_profile_manager`
- `def test_career_profile_manager(mock_personal_service)`

### def `test_job_analyzer`
- `def test_job_analyzer(mock_model_service, mock_personal_service)`

### def `test_resume_optimizer_tailoring`
- `def test_resume_optimizer_tailoring(mock_model_service, mock_personal_service)`

### def `test_resume_optimizer_ats_keywords`
- `def test_resume_optimizer_ats_keywords(mock_model_service, mock_personal_service)`

### def `test_ats_analyzer`
- `def test_ats_analyzer(mock_model_service)`

### def `test_cover_letter_generator`
- `def test_cover_letter_generator(mock_model_service)`

### def `test_portfolio_analyzer`
- `def test_portfolio_analyzer(mock_model_service, mock_github_service)`

### def `test_application_tracker`
- `def test_application_tracker(mock_personal_service)`

### def `test_interview_coach`
- `def test_interview_coach(mock_model_service)`

### def `test_career_planner`
- `def test_career_planner(mock_model_service, mock_personal_service)`

### def `test_job_matcher`
- `def test_job_matcher(mock_model_service, mock_personal_service)`

### def `test_career_os_service_unified_creation`
- `def test_career_os_service_unified_creation(mock_model_service, mock_personal_service, mock_github_service)`

## Module: core/tests/test_runtime.py

### class `MockSystemWatcher`
- **Inherits from**: Watcher

**Methods:**

- `def __init__(self, name: str) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def name(self) -> str`

### def `test_runtime_startup_and_shutdown`
- `def test_runtime_startup_and_shutdown()`

### def `test_event_propagation`
- `def test_event_propagation()`

### def `test_background_task_scheduling`
- `def test_background_task_scheduling()`

### def `test_health_monitor`
- `def test_health_monitor()`

## Module: core/tests/test_omniroute.py

### def `test_omniroute_successful_generate`
- `def test_omniroute_successful_generate()`

### def `test_omniroute_authentication_headers`
- `def test_omniroute_authentication_headers()`

### def `test_omniroute_transient_error_retry`
- `def test_omniroute_transient_error_retry()`

### def `test_omniroute_exhausted_retries`
- `def test_omniroute_exhausted_retries()`

### def `test_omniroute_timeout_handling`
- `def test_omniroute_timeout_handling()`

### def `test_omniroute_streaming`
- `def test_omniroute_streaming()`

### def `test_omniroute_health_checks`
- `def test_omniroute_health_checks()`

### def `test_omniroute_metadata_propagation`
- `def test_omniroute_metadata_propagation()`

### def `test_omniroute_response_diagnostics`
- `def test_omniroute_response_diagnostics()`

### def `test_omniroute_config_loading`
- `def test_omniroute_config_loading(tmp_path)`

### def `test_omniroute_metadata_mapping`
- `def test_omniroute_metadata_mapping()`

## Module: core/tests/test_runtime_intelligence.py

### def `ri_setup`
- `def ri_setup()`
- **Decorators**: `pytest.fixture`

### def `test_correlation_manager`
- `def test_correlation_manager()`

### def `test_telemetry_and_performance`
- `def test_telemetry_and_performance(ri_setup)`

### def `test_statistics_engine`
- `def test_statistics_engine(ri_setup)`

### def `test_diagnostics_and_recommendations`
- `def test_diagnostics_and_recommendations(ri_setup)`

### def `test_report_generation`
- `def test_report_generation(ri_setup)`

### def `test_sql_execution_interceptor`
- `def test_sql_execution_interceptor(ri_setup)`

## Module: core/tests/test_approval_history.py

### class `LocalReviewHistoryAnalyzerWrapper`
- **Inherits from**: LocalApprovalHistoryAnalyzer

> Wrapper class assisting test checks on analyzer logic.

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `test_state_machine_valid_transitions`
- `def test_state_machine_valid_transitions()`

### def `test_history_service_transitions`
- `def test_history_service_transitions(mock_memory_service)`

### def `test_analyzer_statistics_and_trends`
- `def test_analyzer_statistics_and_trends()`

### def `test_analyzer_pattern_discovery`
- `def test_analyzer_pattern_discovery()`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility(mock_memory_service)`

## Module: core/tests/test_repository_mixin.py

### class `_FailingError`
- **Inherits from**: Exception

### class `_ConcreteRepo`
- **Inherits from**: _RepositoryMixin

> Minimal concrete class – does NOT override lifecycle methods.

**Methods:**

- `def __init__(self, service)`

### def `_make_service`
- `def _make_service()`
> Return a mock PersistenceService configured for testing.

### def `test_mixin_in_group2_classes`
- `def test_mixin_in_group2_classes()`
> All Group-2 repository classes must inherit _RepositoryMixin.

### def `test_group1_classes_unmodified`
- `def test_group1_classes_unmodified()`
> Group-1 repos (Workspace, Project, EngineeringProfile, Config) must NOT use the mixin.

### def `test_lifecycle_methods_are_noop`
- `def test_lifecycle_methods_are_noop()`
> initialize/start/stop inherited from mixin must be callable and return None.

### def `test_group2_lifecycle_noop`
- `def test_group2_lifecycle_noop()`
> Spot-check a Group-2 repo: initialize/start/stop must still be no-ops.

### def `test_guard_status_returns_none_on_success`
- `def test_guard_status_returns_none_on_success()`

### def `test_guard_status_returns_result_on_failure`
- `def test_guard_status_returns_result_on_failure()`

### def `test_guard_status_raises_on_strict_failure`
- `def test_guard_status_raises_on_strict_failure()`

### def `test_write_success`
- `def test_write_success()`

### def `test_write_failure_best_effort`
- `def test_write_failure_best_effort()`

### def `test_write_failure_strict_raises`
- `def test_write_failure_strict_raises()`

### def `_row`
- `def _row(data: Dict) -> MagicMock`
> Make a mock row that behaves like a sqlite3.Row.

### def `test_fetch_one_found`
- `def test_fetch_one_found()`

### def `test_fetch_one_not_found_best_effort`
- `def test_fetch_one_not_found_best_effort()`

### def `test_fetch_one_not_found_strict_raises`
- `def test_fetch_one_not_found_strict_raises()`

### def `test_fetch_one_db_error_strict_raises`
- `def test_fetch_one_db_error_strict_raises()`

### def `test_fetch_all_empty`
- `def test_fetch_all_empty()`

### def `test_fetch_all_multiple_rows`
- `def test_fetch_all_multiple_rows()`

### def `test_fetch_all_db_error_best_effort`
- `def test_fetch_all_db_error_best_effort()`

### def `test_duplicate_instantiation_is_safe`
- `def test_duplicate_instantiation_is_safe()`
> Instantiating a Group-2 repo twice must not raise or corrupt state.

### def `test_engineering_task_roundtrip`
- `def test_engineering_task_roundtrip()`
> EngineeringTaskRepositoryImpl save→get→delete using mocked service.

### def `test_write_with_cache_no_cache_service`
- `def test_write_with_cache_no_cache_service()`
> _write_with_cache succeeds even when no cache service is available.

### def `test_write_with_cache_failure_best_effort`
- `def test_write_with_cache_failure_best_effort()`
> _write_with_cache returns UNKNOWN_FAILURE on DB error in BEST_EFFORT mode.

### def `test_write_with_cache_failure_strict_raises`
- `def test_write_with_cache_failure_strict_raises()`
> _write_with_cache raises RuntimeError on DB error in STRICT mode.

### def `test_write_with_cache_write_through`
- `def test_write_with_cache_write_through(monkeypatch)`
> _write_with_cache calls cache_payload_fn and caches when WRITE_THROUGH policy.

### def `test_delete_with_cache_no_cache_service`
- `def test_delete_with_cache_no_cache_service()`
> _delete_with_cache succeeds when no cache service is available.

### def `test_delete_with_cache_with_cache_service`
- `def test_delete_with_cache_with_cache_service(monkeypatch)`
> _delete_with_cache calls cache.delete when cache service is available.

### def `test_delete_with_cache_failure_strict_raises`
- `def test_delete_with_cache_failure_strict_raises()`
> _delete_with_cache raises RuntimeError on DB error in STRICT mode.

### def `test_fetch_one_with_cache_found_no_cache`
- `def test_fetch_one_with_cache_found_no_cache()`
> _fetch_one_with_cache returns SUCCESS when row found and no cache available.

### def `test_fetch_one_with_cache_not_found_no_cache`
- `def test_fetch_one_with_cache_not_found_no_cache()`
> _fetch_one_with_cache returns UNKNOWN_FAILURE when no rows found.

### def `test_fetch_one_with_cache_strict_not_found_raises`
- `def test_fetch_one_with_cache_strict_not_found_raises()`
> _fetch_one_with_cache raises RuntimeError in STRICT mode when no rows.

### def `test_fetch_one_with_cache_uses_cache_service`
- `def test_fetch_one_with_cache_uses_cache_service(monkeypatch)`
> _fetch_one_with_cache delegates to cache.get when cache service is available.

### def `test_provider_capability_uses_mixin`
- `def test_provider_capability_uses_mixin()`
> ProviderCapabilityRepositoryImpl.save/get/delete use mixin helpers.

### def `test_provider_health_uses_mixin`
- `def test_provider_health_uses_mixin()`
> ProviderHealthRepositoryImpl.save/get/delete use mixin helpers.

### def `test_provider_routing_uses_mixin`
- `def test_provider_routing_uses_mixin()`
> ProviderRoutingRepositoryImpl.save/get/delete use mixin helpers.

## Module: core/tests/test_project_intelligence.py

### def `test_project_intelligence_analysis`
- `def test_project_intelligence_analysis()`

### def `test_incremental_indexing`
- `def test_incremental_indexing()`

### def `test_brain_context_manager_integration`
- `def test_brain_context_manager_integration()`

## Module: core/tests/test_persistence.py

### class `SQLiteTransportForTests`
- **Inherits from**: DatabaseTransport

> SQLite-backed database transport used strictly inside tests.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService) -> None`
- `def validate_configuration(self) -> List[str]`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute(self, query: str, params: Optional[tuple]) -> TransportResult`
- `def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]`
- `def begin_transaction(self) -> TransportTransaction`
- `def health(self) -> TransportHealth`
- `def capabilities(self) -> TransportCapabilities`

### class `MockDatabaseTransport`
- **Inherits from**: DatabaseTransport

> Mock transport utilized to verify configurations and diagnostics.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService) -> None`
- `def validate_configuration(self) -> List[str]`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute(self, query: str, params: Optional[tuple]) -> TransportResult`
- `def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]`
- `def begin_transaction(self) -> TransportTransaction`
- `def health(self) -> TransportHealth`
- `def capabilities(self) -> TransportCapabilities`

### class `RecordingTransport`
- **Inherits from**: DatabaseTransport

> Records queries sent by the provider without requiring a database driver.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService) -> None`
- `def validate_configuration(self) -> List[str]`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute(self, query: str, params: Optional[tuple]) -> TransportResult`
- `def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]`
- `def begin_transaction(self) -> TransportTransaction`
- `def health(self) -> TransportHealth`
- `def capabilities(self) -> TransportCapabilities`

### def `make_recording_provider`
- `def make_recording_provider(provider_name: str) -> tuple[PostgreSQLProvider, RecordingTransport]`

### def `make_recording_service`
- `def make_recording_service(provider_name: str) -> tuple[PersistenceServiceImpl, RecordingTransport]`

### def `test_sqlite_placeholder_conversion_is_unchanged`
- `def test_sqlite_placeholder_conversion_is_unchanged()`

### def `test_postgresql_placeholder_conversion`
- `def test_postgresql_placeholder_conversion()`

### def `test_postgresql_multiple_placeholder_conversion`
- `def test_postgresql_multiple_placeholder_conversion()`

### def `test_postgresql_query_without_parameters_is_unchanged`
- `def test_postgresql_query_without_parameters_is_unchanged()`

### def `test_migration_history_insert_uses_postgresql_placeholders`
- `def test_migration_history_insert_uses_postgresql_placeholders()`

### def `test_repository_crud_query_uses_postgresql_placeholders`
- `def test_repository_crud_query_uses_postgresql_placeholders()`

### def `test_configuration`
- `def test_configuration()`

### def `test_connection_lifecycle_and_pool`
- `def test_connection_lifecycle_and_pool()`

### def `test_transactions`
- `def test_transactions()`

### def `test_nested_transactions`
- `def test_nested_transactions()`

### def `test_migrations`
- `def test_migrations()`

### def `test_repository_registry`
- `def test_repository_registry()`

### def `test_diagnostics`
- `def test_diagnostics()`

### def `test_health_monitor`
- `def test_health_monitor()`

### def `test_validator`
- `def test_validator()`

### def `test_report_generator`
- `def test_report_generator(tmp_path)`

### def `test_begin_transaction_does_not_raise_when_transport_lacks_tx_depth`
- `def test_begin_transaction_does_not_raise_when_transport_lacks_tx_depth()`
> begin_transaction() must not AttributeError on a transport with no tx_depth.

### def `test_commit_transaction_after_begin_does_not_raise`
- `def test_commit_transaction_after_begin_does_not_raise()`
> A transaction started on a tx_depth-less transport can be committed.

### def `test_rollback_transaction_after_begin_does_not_raise`
- `def test_rollback_transaction_after_begin_does_not_raise()`
> A transaction started on a tx_depth-less transport can be rolled back.

### def `test_nested_begin_transaction_does_not_raise_when_transport_lacks_tx_depth`
- `def test_nested_begin_transaction_does_not_raise_when_transport_lacks_tx_depth()`
> Nested begin_transaction() must not AttributeError on the second call.

### def `test_begin_transaction_nested_flag_defaults_to_false_without_tx_depth`
- `def test_begin_transaction_nested_flag_defaults_to_false_without_tx_depth()`
> When transport has no tx_depth, nested should default to False (not nested).

## Module: core/tests/test_test_failure.py

### def `dummy_failed_summary`
- `def dummy_failed_summary()`
- **Decorators**: `pytest.fixture`

### def `test_failure_analyzer_classification`
- `def test_failure_analyzer_classification()`

### def `test_failure_analyzer_clustering`
- `def test_failure_analyzer_clustering(dummy_failed_summary)`

### def `test_root_cause_analysis`
- `def test_root_cause_analysis(dummy_failed_summary)`

### def `test_failure_analysis_service_flow`
- `def test_failure_analysis_service_flow(dummy_failed_summary)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_test_engineer.py

### def `mock_code_summary`
- `def mock_code_summary()`
- **Decorators**: `pytest.fixture`

### def `test_test_planner_strategy_selection`
- `def test_test_planner_strategy_selection(mock_code_summary)`

### def `test_test_planner_category_selection`
- `def test_test_planner_category_selection(mock_code_summary)`

### def `test_test_planner_prioritization`
- `def test_test_planner_prioritization(mock_code_summary)`

### def `test_test_engineer_service_flow`
- `def test_test_engineer_service_flow(mock_code_summary)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_bootstrap_regression.py

### class `DummyService`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self)`
- `def initialize(self)`
- `def start(self)`
- `def shutdown(self)`

### def `test_single_initialization`
- `def test_single_initialization()`
> Verify that calling initialize, on_ready, and teardown multiple times only executes once.

### def `test_service_registration_uniqueness`
- `def test_service_registration_uniqueness()`
> Verify that registering the same service type more than once raises a ValueError.

### def `test_duplicate_kernel_bootstrap_calls`
- `def test_duplicate_kernel_bootstrap_calls()`
> Verify that duplicate bootstrap/initialization calls on the Kernel

do not trigger duplicate calls on services.

## Module: core/tests/test_n8n_translation.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `dummy_workflow`
- `def dummy_workflow()`
- **Decorators**: `pytest.fixture`

### def `test_ir_compilation`
- `def test_ir_compilation(dummy_workflow)`

### def `test_node_and_connection_mapping`
- `def test_node_and_connection_mapping(dummy_workflow)`

### def `test_validation_errors`
- `def test_validation_errors(dummy_workflow)`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service, dummy_workflow)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service, dummy_workflow)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_patch_generation.py

### def `temp_workspace_and_repo`
- `def temp_workspace_and_repo(tmp_path)`
- **Decorators**: `pytest.fixture`

### def `test_diff_generator`
- `def test_diff_generator()`

### def `test_patch_generator_bundle`
- `def test_patch_generator_bundle(temp_workspace_and_repo)`

### def `test_patch_validator`
- `def test_patch_validator(temp_workspace_and_repo)`

### def `test_conflict_detector`
- `def test_conflict_detector()`

### def `test_serializer`
- `def test_serializer(temp_workspace_and_repo)`

### def `test_patch_service_integration`
- `def test_patch_service_integration(temp_workspace_and_repo)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_workflow_monitoring.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `test_performance_analytics`
- `def test_performance_analytics()`

### def `test_telemetry_validation`
- `def test_telemetry_validation()`

### def `test_monitoring_alerts_and_health_scoring`
- `def test_monitoring_alerts_and_health_scoring(mock_memory_service)`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_release_documentation.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_profile_service`
- `def mock_profile_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `test_release_notes_generation`
- `def test_release_notes_generation()`

### def `test_changelog_generation`
- `def test_changelog_generation()`

### def `test_migration_guide_generation`
- `def test_migration_guide_generation()`

### def `test_upgrade_guide_generation`
- `def test_upgrade_guide_generation()`

### def `test_validation`
- `def test_validation(mock_memory_service)`

### def `test_workspace_generation`
- `def test_workspace_generation(tmp_path, mock_memory_service, mock_profile_service, mock_workspace_service)`

### def `test_profile_integration`
- `def test_profile_integration(mock_memory_service, mock_profile_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service, mock_profile_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service, mock_profile_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility(mock_memory_service, mock_profile_service)`

## Module: core/tests/test_architecture_documentation.py

### def `sample_code_structure`
- `def sample_code_structure()`
- **Decorators**: `pytest.fixture`

### def `test_architecture_analyzer`
- `def test_architecture_analyzer(sample_code_structure)`

### def `test_architecture_planner`
- `def test_architecture_planner()`

### def `test_architecture_validator`
- `def test_architecture_validator()`

### def `test_architecture_registry`
- `def test_architecture_registry()`

### def `test_service_evaluation_flow`
- `def test_service_evaluation_flow(sample_code_structure)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_research.py

### class `CustomTestSearchProvider`
- **Inherits from**: SearchProvider

**Methods:**

- `def name(self) -> str`
- `def search(self, query: str, limit: int) -> List[Source]`

### def `test_research_models_serialization`
- `def test_research_models_serialization()`

### def `test_query_planner_and_ranking`
- `def test_query_planner_and_ranking()`

### def `test_research_execution_and_cache`
- `def test_research_execution_and_cache()`

### def `test_custom_search_provider_registration`
- `def test_custom_search_provider_registration()`

## Module: core/tests/test_software_engineer.py

### def `mock_engineering_report`
- `def mock_engineering_report()`
- **Decorators**: `pytest.fixture`

### def `test_feature_planner`
- `def test_feature_planner(mock_engineering_report)`

### def `test_task_decomposer`
- `def test_task_decomposer(mock_engineering_report)`

### def `test_execution_planner`
- `def test_execution_planner()`

### def `test_file_planner`
- `def test_file_planner(mock_engineering_report)`

### def `test_testing_planner`
- `def test_testing_planner(mock_engineering_report)`

### def `test_documentation_planner`
- `def test_documentation_planner(mock_engineering_report)`

### def `test_software_engineer_service_integration`
- `def test_software_engineer_service_integration(mock_engineering_report)`

### def `test_backward_compatibility_and_custom_extensions`
- `def test_backward_compatibility_and_custom_extensions(mock_engineering_report)`

## Module: core/tests/test_engineering_memory.py

### def `memory_setup`
- `def memory_setup()`
- **Decorators**: `pytest.fixture`

### def `test_record_and_update_task`
- `def test_record_and_update_task(memory_setup)`

### def `test_record_and_update_plan`
- `def test_record_and_update_plan(memory_setup)`

### def `test_archive_and_restore`
- `def test_archive_and_restore(memory_setup)`

### def `test_statistics`
- `def test_statistics(memory_setup)`

### def `test_strict_policy_fails_on_db_issue`
- `def test_strict_policy_fails_on_db_issue(memory_setup)`

## Module: core/tests/test_redis_rate_limit.py

### def `rate_limit_env`
- `def rate_limit_env()`
- **Decorators**: `pytest.fixture`

### def `test_quota_registry`
- `def test_quota_registry(rate_limit_env)`

### def `test_token_bucket_limiting`
- `def test_token_bucket_limiting(rate_limit_env)`

### def `test_sliding_window_limiting`
- `def test_sliding_window_limiting(rate_limit_env)`

### def `test_fixed_window_limiting`
- `def test_fixed_window_limiting(rate_limit_env)`

### def `test_job_state_machine_transitions`
- `def test_job_state_machine_transitions(rate_limit_env)`

### def `test_redis_outage_fallback`
- `def test_redis_outage_fallback(rate_limit_env)`

### def `test_observability_and_recommendations`
- `def test_observability_and_recommendations(rate_limit_env)`

## Module: core/tests/test_orchestrator.py

### def `test_dependency_level_grouping_and_cycles`
- `def test_dependency_level_grouping_and_cycles()`

### def `test_parameter_substitution`
- `def test_parameter_substitution()`

### def `test_multi_skill_flows_orchestration`
- `def test_multi_skill_flows_orchestration()`

### def `test_failure_handling_and_abort`
- `def test_failure_handling_and_abort()`

## Module: core/tests/test_test_validation.py

### def `mock_exec_summary`
- `def mock_exec_summary()`
- **Decorators**: `pytest.fixture`

### def `mock_coverage_report`
- `def mock_coverage_report()`
- **Decorators**: `pytest.fixture`

### def `mock_failure_report`
- `def mock_failure_report()`
- **Decorators**: `pytest.fixture`

### def `test_validation_gate_evaluators`
- `def test_validation_gate_evaluators(mock_exec_summary, mock_coverage_report, mock_failure_report)`

### def `test_weighted_scoring_model`
- `def test_weighted_scoring_model(mock_exec_summary, mock_coverage_report, mock_failure_report)`

### def `test_overall_decision_states`
- `def test_overall_decision_states(mock_exec_summary, mock_coverage_report, mock_failure_report)`

### def `test_service_evaluation_flow`
- `def test_service_evaluation_flow(mock_exec_summary, mock_coverage_report, mock_failure_report)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_qdrant_semantic_memory_integration.py

### def `kernel_setup`
- `def kernel_setup(monkeypatch)`
- **Decorators**: `pytest.fixture`

### def `test_semantic_memory_manager_basic`
- `def test_semantic_memory_manager_basic(kernel_setup)`

### def `test_conversation_indexing`
- `def test_conversation_indexing(kernel_setup)`

### def `test_workspace_indexing`
- `def test_workspace_indexing(kernel_setup)`

### def `test_engineering_indexing`
- `def test_engineering_indexing(kernel_setup)`

### def `test_research_indexing`
- `def test_research_indexing(kernel_setup)`

### def `test_documentation_indexing`
- `def test_documentation_indexing(kernel_setup)`

### def `test_developer_agent_semantic_memory`
- `def test_developer_agent_semantic_memory(kernel_setup)`

### def `test_context_service_enriched_context`
- `def test_context_service_enriched_context(kernel_setup)`

## Module: core/tests/test_automation_persistence.py

### def `automation_setup`
- `def automation_setup()`
- **Decorators**: `pytest.fixture`

### def `test_workflow_repository_crud`
- `def test_workflow_repository_crud(automation_setup)`

### def `test_workflow_execution_repository_crud`
- `def test_workflow_execution_repository_crud(automation_setup)`

### def `test_automation_persistence_service_coordinator`
- `def test_automation_persistence_service_coordinator(automation_setup)`

### def `test_persistence_policy_strict_mode`
- `def test_persistence_policy_strict_mode(automation_setup)`

### def `test_health_monitoring_and_telemetry`
- `def test_health_monitoring_and_telemetry(automation_setup)`

## Module: core/tests/test_intent.py

### def `test_intent_classification`
- `def test_intent_classification()`

### def `test_intent_resolution`
- `def test_intent_resolution()`

### def `test_intent_validation`
- `def test_intent_validation()`

### def `test_kernel_intent_execution`
- `def test_kernel_intent_execution(tmp_path)`

## Module: core/tests/test_docintel.py

### def `test_docintel_pipeline`
- `def test_docintel_pipeline()`

## Module: core/tests/test_canonical_pipeline.py

### def `clean_registries`
- `def clean_registries()`
- **Decorators**: `pytest.fixture`

### def `test_canonical_pipeline_execution`
- `def test_canonical_pipeline_execution(clean_registries)`
> PHASE 1: Verify complete execution flow of the frozen architecture.

### def `test_provider_registry_tests`
- `def test_provider_registry_tests(clean_registries)`
> PHASE 2: Verify Provider Registration.

### def `test_model_registry_tests`
- `def test_model_registry_tests(clean_registries)`
> PHASE 3: Verify Model Registration.

### def `test_routing_engine_tests`
- `def test_routing_engine_tests(clean_registries)`
> PHASE 4: Verify Routing Engine Constraints and Scores.

### def `test_omniroute_tests`
- `def test_omniroute_tests(clean_registries)`
> PHASE 5: Verify OmniRoute Metadata and Error Propagation.

### def `test_configuration_tests`
- `def test_configuration_tests(tmp_path)`
> PHASE 6: Verify Configuration and Overrides.

### def `test_lifecycle_tests`
- `def test_lifecycle_tests()`
> PHASE 7: Verify Service Lifecycle.

### def `test_local_first_tests`
- `def test_local_first_tests()`
> PHASE 8: Verify Local-First Fallbacks.

### def `test_end_to_end_boot_and_shutdown`
- `def test_end_to_end_boot_and_shutdown(tmp_path)`
> PHASE 9: Verify E2E Boot and Shutdown sequence.

### def `test_end_to_end_chat`
- `def test_end_to_end_chat(clean_registries)`
> PHASE 9: Verify E2E Chat Routing.

## Module: core/tests/test_engineering_profile.py

### def `sample_profile_dict`
- `def sample_profile_dict()`
- **Decorators**: `pytest.fixture`

### def `test_profile_serialization`
- `def test_profile_serialization(sample_profile_dict)`

### def `test_profile_validation`
- `def test_profile_validation(sample_profile_dict)`

### def `test_profile_merging_precedence`
- `def test_profile_merging_precedence(sample_profile_dict)`

### def `test_profile_service_integrations`
- `def test_profile_service_integrations(sample_profile_dict)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_automation.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `dummy_workflow`
- `def dummy_workflow()`
- **Decorators**: `pytest.fixture`

### def `test_graph_validation_pass`
- `def test_graph_validation_pass(dummy_workflow)`

### def `test_graph_validation_disconnected_nodes`
- `def test_graph_validation_disconnected_nodes(dummy_workflow)`

### def `test_graph_validation_cycles`
- `def test_graph_validation_cycles(dummy_workflow)`

### def `test_graph_validation_duplicates`
- `def test_graph_validation_duplicates(dummy_workflow)`

### def `test_registry_and_providers_operations`
- `def test_registry_and_providers_operations(mock_memory_service, dummy_workflow)`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service, dummy_workflow)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service, dummy_workflow)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_provider_orchestrator.py

### def `test_provider_orchestrator`
- `def test_provider_orchestrator()`

## Module: core/tests/test_redis_session.py

### def `session_env`
- `def session_env()`
- **Decorators**: `pytest.fixture`

### def `test_session_ownership_registry`
- `def test_session_ownership_registry(session_env)`

### def `test_session_creation_read_update_delete`
- `def test_session_creation_read_update_delete(session_env)`

### def `test_sliding_expiration_and_heartbeat`
- `def test_sliding_expiration_and_heartbeat(session_env)`

### def `test_session_recovery_and_reconstruct`
- `def test_session_recovery_and_reconstruct(session_env)`

### def `test_session_outage_fallback`
- `def test_session_outage_fallback(session_env)`

### def `test_session_statistics_diagnostics_recommendations`
- `def test_session_statistics_diagnostics_recommendations(session_env)`

## Module: core/tests/test_refgen.py

### class `TestReferenceGenerationStatus`

> Test that reference generation completes successfully.

**Methods:**

- `def test_generation_succeeds(self, run_generator_once)`
  * Reference generation should complete with success status.
- `def test_no_errors(self, run_generator_once)`
  * Reference generation should produce no errors.
- `def test_six_files_produced(self, run_generator_once)`
  * Reference generation should produce exactly 6 files.
- `def test_services_discovered(self, run_generator_once)`
  * Reference generation should discover services.
- `def test_elapsed_is_positive(self, run_generator_once)`
  * Generation should complete in positive time.

### class `TestReferenceFilesExist`

> Test that all expected reference files are created.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def test_file_exists(self, reference_dir, filename)`
  * Each expected reference file should exist.
- `def test_file_not_empty(self, reference_dir, filename)`
  * Each reference file should have content.

### class `TestServicesReference`

> Test the services.md reference content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def services_content(self, reference_dir)`
  * Load services.md content.
- `def test_header_present(self, services_content)`
  * Services reference should have proper header.
- `def test_generated_banner(self, services_content)`
  * Services reference should have auto-generated banner.
- `def test_summary_section(self, services_content)`
  * Services reference should have summary statistics.
- `def test_contains_service_entries(self, services_content)`
  * Services reference should contain actual service documentation.
- `def test_method_signatures_present(self, services_content)`
  * Services reference should document method signatures.
- `def test_parameters_documented(self, services_content)`
  * Services reference should document parameters.

### class `TestInterfacesReference`

> Test the interfaces.md reference content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def interfaces_content(self, reference_dir)`
  * Load interfaces.md content.
- `def test_header_present(self, interfaces_content)`
  * Interfaces reference should have proper header.
- `def test_interface_registry_table(self, interfaces_content)`
  * Interfaces reference should have interface registry table.
- `def test_standalone_implementations_section(self, interfaces_content)`
  * Interfaces reference should list standalone implementations.
- `def test_interface_details_section(self, interfaces_content)`
  * Interfaces reference should have detailed interface documentation.

### class `TestLifecycleReference`

> Test the lifecycle.md reference content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def lifecycle_content(self, reference_dir)`
  * Load lifecycle.md content.
- `def test_header_present(self, lifecycle_content)`
  * Lifecycle reference should have proper header.
- `def test_lifecycle_phases_section(self, lifecycle_content)`
  * Lifecycle reference should document lifecycle phases.
- `def test_initialization_phase_section(self, lifecycle_content)`
  * Lifecycle reference should document initialization phase.
- `def test_cleanup_phase_section(self, lifecycle_content)`
  * Lifecycle reference should document cleanup phase.

### class `TestDependencyInjectionReference`

> Test the dependency_injection.md reference content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def di_content(self, reference_dir)`
  * Load dependency_injection.md content.
- `def test_header_present(self, di_content)`
  * DI reference should have proper header.
- `def test_dependency_graph_summary(self, di_content)`
  * DI reference should have dependency graph summary.
- `def test_service_dependencies_section(self, di_content)`
  * DI reference should document service dependencies.
- `def test_injected_dependencies_table(self, di_content)`
  * DI reference should have dependency tables.

### class `TestAPIReference`

> Test the api_reference.md complete reference content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def api_content(self, reference_dir)`
  * Load api_reference.md content.
- `def test_header_present(self, api_content)`
  * API reference should have proper header.
- `def test_table_of_contents(self, api_content)`
  * API reference should have table of contents.
- `def test_service_sections(self, api_content)`
  * API reference should have sections for services.
- `def test_methods_documented(self, api_content)`
  * API reference should document methods.

### class `TestReferenceIndex`

> Test the README.md index content.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def readme_content(self, reference_dir)`
  * Load README.md content.
- `def test_header_present(self, readme_content)`
  * README should have proper header.
- `def test_overview_section(self, readme_content)`
  * README should have overview.
- `def test_documentation_files_table(self, readme_content)`
  * README should list all documentation files.
- `def test_statistics_section(self, readme_content)`
  * README should have statistics.
- `def test_regeneration_instructions(self, readme_content)`
  * README should have regeneration instructions.
- `def test_cross_references_section(self, readme_content)`
  * README should have cross-references to other documentation.

### class `TestReferenceIdempotency`

> Test that reference generation is idempotent.

**Methods:**

- `def test_same_service_count_on_rerun(self, project_root)`
  * Re-running the generator should discover the same number of services.
- `def test_same_file_count_on_rerun(self, project_root)`
  * Re-running the generator should produce the same number of files.
- `def test_same_file_sizes_on_rerun(self, project_root, reference_dir)`
  * Re-running the generator should produce files of the same size (modulo timestamps).

### class `TestHandwrittenDocsUntouched`

> Test that reference generation doesn't modify handwritten documentation.

**Methods:**

- `def setup(self, run_generator_once)`
  * Ensure generator has run before tests.
- `def test_handwritten_doc_unchanged(self, project_root, doc_path)`
  * Handwritten documentation should remain unchanged after generation.

### class `TestServiceReferenceDiscoverer`

> Test the enhanced service discoverer.

**Methods:**

- `def test_discovers_services(self, project_root)`
  * Discoverer should find services.
- `def test_all_services_have_name(self, project_root)`
  * All discovered services should have a name.
- `def test_all_services_have_module(self, project_root)`
  * All discovered services should have a module path.
- `def test_services_have_methods(self, project_root)`
  * Services should have method signatures extracted.
- `def test_sorted_alphabetically(self, project_root)`
  * Services should be sorted alphabetically by name.

### def `project_root`
- `def project_root()`
- **Decorators**: `pytest.fixture`
> Return the project root directory.

### def `reference_dir`
- `def reference_dir(project_root)`
- **Decorators**: `pytest.fixture`
> Return the reference output directory.

### def `run_generator_once`
- `def run_generator_once(project_root)`
- **Decorators**: `pytest.fixture`
> Run the reference generator once and return the result.

## Module: core/tests/test_retry_worker_regression.py

### class `MockDB`

**Methods:**

- `def __init__(self)`
- `def execute(self, query, params)`

### class `MockRepos`

**Methods:**

- `def __init__(self)`
- `def get_repository(self, name)`

### def `clean_env`
- `def clean_env()`
- **Decorators**: `pytest.fixture(autouse=True)`

### def `retry_setup`
- `def retry_setup()`
- **Decorators**: `pytest.fixture`

### def `test_retry_worker_success`
- `def test_retry_worker_success(retry_setup)`
> Verify that a successful retry removes the job and saves the vector.

### def `test_retry_worker_failure`
- `def test_retry_worker_failure(retry_setup)`
> Verify that a failed retry updates attempts and updated_at, without deleting it.

### def `test_retry_worker_exponential_backoff`
- `def test_retry_worker_exponential_backoff(retry_setup)`
> Verify that exponential backoff blocks retries until the backoff period has passed.

### def `test_retry_worker_batched_processing`
- `def test_retry_worker_batched_processing(retry_setup)`
> Verify that multiple eligible jobs are grouped and batched into a single embed_batch call.

## Module: core/tests/test_mission.py

### def `test_mission_planner_and_task_decomposition`
- `def test_mission_planner_and_task_decomposition()`

### def `test_mission_repository_persistence`
- `def test_mission_repository_persistence()`

### def `test_mission_execution_success`
- `def test_mission_execution_success()`

### def `test_mission_execution_cancellation`
- `def test_mission_execution_cancellation()`

### def `test_resume_after_interruption`
- `def test_resume_after_interruption()`

## Module: core/tests/test_conversation.py

### def `test_conversation_persistence_and_loading`
- `def test_conversation_persistence_and_loading(tmp_path)`

### def `test_conversation_manager_lifecycle`
- `def test_conversation_manager_lifecycle(tmp_path)`

### def `test_conversation_summarization`
- `def test_conversation_summarization(tmp_path)`

## Module: core/tests/test_developer_v2.py

### def `test_repository_scanner`
- `def test_repository_scanner(tmp_path)`

### def `test_code_index`
- `def test_code_index(tmp_path)`

### def `test_workspace_summary_generation`
- `def test_workspace_summary_generation()`

### def `test_prompt_builder`
- `def test_prompt_builder(tmp_path)`

## Module: core/tests/test_collaboration.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `test_reviewer_roles`
- `def test_reviewer_roles()`

### def `test_comment_and_thread_lifecycle`
- `def test_comment_and_thread_lifecycle(mock_memory_service)`

### def `test_audit_log_and_timeline`
- `def test_audit_log_and_timeline(mock_memory_service)`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility(mock_memory_service)`

## Module: core/tests/test_workflow_versioning.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `test_version_registry`
- `def test_version_registry()`

### def `test_compatibility_analyzer`
- `def test_compatibility_analyzer()`

### def `test_migration_planner`
- `def test_migration_planner()`

### def `test_version_validator`
- `def test_version_validator()`

### def `test_version_service_creation_and_diff`
- `def test_version_service_creation_and_diff(mock_memory_service)`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_openrouter.py

### def `test_nvidia_provider_init`
- `def test_nvidia_provider_init()`

### def `test_nvidia_provider_generate`
- `def test_nvidia_provider_generate(monkeypatch)`

### def `test_openrouter_api_key_missing`
- `def test_openrouter_api_key_missing()`

### def `test_openrouter_validation`
- `def test_openrouter_validation()`

### def `test_openrouter_successful_generate`
- `def test_openrouter_successful_generate()`

### def `test_openrouter_transient_error_retry`
- `def test_openrouter_transient_error_retry()`

### def `test_openrouter_exhausted_retries`
- `def test_openrouter_exhausted_retries()`

### def `test_openrouter_network_error`
- `def test_openrouter_network_error()`

### def `test_local_model_service_openrouter_routing`
- `def test_local_model_service_openrouter_routing(tmp_path)`

## Module: core/tests/test_personal.py

### def `test_profile_crud_and_switching`
- `def test_profile_crud_and_switching()`

### def `test_resume_and_portfolio_helpers`
- `def test_resume_and_portfolio_helpers()`

### def `test_intelligent_context_selection`
- `def test_intelligent_context_selection()`

### def `test_context_manager_personal_integration`
- `def test_context_manager_personal_integration()`

## Module: core/tests/test_embedding_batch_regression.py

### class `NativeBatchProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `SequentialFallbackProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `PartialFailureProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### def `test_setup`
- `def test_setup()`
- **Decorators**: `pytest.fixture`

### def `test_native_batch_embedding`
- `def test_native_batch_embedding(test_setup)`
> Verify that native batch API is called when supported by the provider.

### def `test_sequential_fallback_embedding`
- `def test_sequential_fallback_embedding(test_setup)`
> Verify that we fall back to sequential calls when embed_batch raises NotImplementedError.

### def `test_partial_failures_in_batch`
- `def test_partial_failures_in_batch(test_setup)`
> Verify that validation failures on a single request don't fail the whole batch.

### def `test_batch_statistics_and_cache_behavior`
- `def test_batch_statistics_and_cache_behavior(test_setup)`
> Verify that cache hits are bypassed, misses are cached, and

statistics are updated correctly.

## Module: core/tests/test_kernel.py

### def `test_kernel_state_transitions`
- `def test_kernel_state_transitions(tmp_path)`

## Module: core/tests/test_redis_cache.py

### def `test_env`
- `def test_env()`
- **Decorators**: `pytest.fixture`

### def `test_cache_policy_and_read_through`
- `def test_cache_policy_and_read_through(test_env)`

### def `test_cache_policy_write_through`
- `def test_cache_policy_write_through(test_env)`

### def `test_cache_policy_cache_aside`
- `def test_cache_policy_cache_aside(test_env)`

### def `test_ttl_expiration`
- `def test_ttl_expiration(test_env)`

### def `test_cache_invalidation_manager`
- `def test_cache_invalidation_manager(test_env)`

### def `test_cache_warmup_service`
- `def test_cache_warmup_service(test_env)`

### def `test_cache_rebuild_service`
- `def test_cache_rebuild_service(test_env)`

### def `test_redis_unavailable_fallback`
- `def test_redis_unavailable_fallback(test_env)`

### def `test_statistics_diagnostics_and_recommendations`
- `def test_statistics_diagnostics_and_recommendations(test_env)`

### def `test_backward_compatibility`
- `def test_backward_compatibility(test_env)`

## Module: core/tests/test_intelligence.py

### def `test_repository_analyzer`
- `def test_repository_analyzer()`

### def `test_memory_ranker`
- `def test_memory_ranker()`

### def `test_context_ranker`
- `def test_context_ranker()`

### def `test_tool_selector`
- `def test_tool_selector()`

### def `test_intent_expander`
- `def test_intent_expander()`

### def `test_reasoning_context_assembly`
- `def test_reasoning_context_assembly()`

## Module: core/tests/test_source_control.py

### def `temp_git_dir`
- `def temp_git_dir(tmp_path)`
- **Decorators**: `pytest.fixture`

### def `test_local_git_lifecycle`
- `def test_local_git_lifecycle(temp_git_dir)`

### def `test_source_control_registry`
- `def test_source_control_registry()`

### def `test_provider_configuration`
- `def test_provider_configuration()`

### def `test_github_provider_adapter`
- `def test_github_provider_adapter(mock_request)`
- **Decorators**: `patch('httpx.Client.request')`

### def `test_diagnostics`
- `def test_diagnostics()`

### def `test_validator`
- `def test_validator()`

### def `test_telemetry_recording`
- `def test_telemetry_recording()`

### def `test_report_generation`
- `def test_report_generation(tmp_path)`

## Module: core/tests/test_nvidia_foundation.py

### def `test_nvidia_provider_foundation_registration`
- `def test_nvidia_provider_foundation_registration()`
> Verify that the NVIDIA provider registers automatically and routes via OmniRoute.

### def `test_nvidia_provider_authentication_failure`
- `def test_nvidia_provider_authentication_failure()`
> Verify that a 401 Unauthorized response raises the expected RuntimeError.

### def `test_nvidia_provider_rate_limiting`
- `def test_nvidia_provider_rate_limiting()`
> Verify that a 429 Too Many Requests response raises the expected RuntimeError.

### def `test_nvidia_provider_timeout_failure`
- `def test_nvidia_provider_timeout_failure()`
> Verify that a network timeout raises the expected RuntimeError.

### def `test_cli_provider_list`
- `def test_cli_provider_list()`
> Verify that aios provider list routes correctly non-interactively.

### def `test_cli_model_list`
- `def test_cli_model_list()`
> Verify that aios model list routes correctly non-interactively.

### def `test_cli_health`
- `def test_cli_health()`
> Verify that aios health routes correctly non-interactively.

### def `test_cli_route`
- `def test_cli_route()`
> Verify that aios route routes correctly non-interactively.

## Module: core/tests/test_skills.py

### def `test_skill_metadata`
- `def test_skill_metadata()`

### def `test_skill_registry_and_manager`
- `def test_skill_registry_and_manager()`

## Module: core/tests/test_postgresql_production_validation.py

### def `validation_env`
- `def validation_env()`
- **Decorators**: `pytest.fixture`

### def `test_production_live_validation`
- `def test_production_live_validation(validation_env)`

## Module: core/tests/test_readme_intelligence.py

### def `test_readme_analyzer`
- `def test_readme_analyzer()`

### def `test_readme_planner`
- `def test_readme_planner()`

### def `test_readme_validator`
- `def test_readme_validator()`

### def `test_readme_generation`
- `def test_readme_generation()`

### def `test_readme_updating`
- `def test_readme_updating()`

### def `test_service_evaluation_flow`
- `def test_service_evaluation_flow()`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_daily_os.py

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `mock_personal_service`
- `def mock_personal_service()`
- **Decorators**: `pytest.fixture`

### def `mock_github_service`
- `def mock_github_service()`
- **Decorators**: `pytest.fixture`

### def `mock_project_intel`
- `def mock_project_intel()`
- **Decorators**: `pytest.fixture`

### def `mock_career_os`
- `def mock_career_os()`
- **Decorators**: `pytest.fixture`

### def `mock_registry`
- `def mock_registry()`
- **Decorators**: `pytest.fixture`

### def `test_priority_calculator`
- `def test_priority_calculator(mock_model_service, mock_personal_service, mock_career_os, mock_registry, mock_project_intel)`

### def `test_workload_estimator`
- `def test_workload_estimator()`

### def `test_schedule_optimizer`
- `def test_schedule_optimizer(mock_model_service)`

### def `test_progress_tracking`
- `def test_progress_tracking(mock_personal_service)`

### def `test_session_recording`
- `def test_session_recording(mock_personal_service)`

### def `test_daily_review`
- `def test_daily_review(mock_model_service, mock_personal_service, mock_career_os, mock_registry, mock_project_intel, mock_github_service)`

### def `test_productivity_analyzer`
- `def test_productivity_analyzer(mock_personal_service, mock_registry)`

### def `test_daily_planner`
- `def test_daily_planner(mock_model_service, mock_personal_service, mock_github_service, mock_project_intel, mock_career_os, mock_registry)`

## Module: core/tests/test_context.py

### def `test_context_detection_git`
- `def test_context_detection_git()`

### def `test_context_detection_fallback`
- `def test_context_detection_fallback()`

### def `test_context_change_event`
- `def test_context_change_event()`

## Module: core/tests/test_memory.py

### def `test_memory_storage_crud`
- `def test_memory_storage_crud(tmp_path)`

### def `test_memory_intelligence_milestone1`
- `def test_memory_intelligence_milestone1(tmp_path)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

### def `test_memory_retrieval_milestone2`
- `def test_memory_retrieval_milestone2(tmp_path)`

## Module: core/tests/test_code_generation.py

### def `test_code_planner`
- `def test_code_planner()`

### def `test_context_assembler`
- `def test_context_assembler()`

### def `test_prompt_builder_policies`
- `def test_prompt_builder_policies()`

### def `test_file_generator_editor`
- `def test_file_generator_editor(tmp_path)`

### def `test_syntax_style_validators`
- `def test_syntax_style_validators()`

### def `test_code_generation_service_flow`
- `def test_code_generation_service_flow(tmp_path)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_file_planner.py

### def `mock_code_structure`
- `def mock_code_structure()`
- **Decorators**: `pytest.fixture`

### def `test_file_impact_analyzer`
- `def test_file_impact_analyzer(mock_code_structure)`

### def `test_file_dependency_resolver`
- `def test_file_dependency_resolver(mock_code_structure)`

### def `test_change_planner`
- `def test_change_planner(mock_code_structure)`

### def `test_file_planner_service_integration`
- `def test_file_planner_service_integration(mock_code_structure)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_postgresql_bulk_regression.py

### class `DatabaseError`
- **Inherits from**: Exception

### class `MockConnection`

**Methods:**

- `def __init__(self, id_)`
- `def cursor(self)`
- `def execute(self, query, params)`
- `def executemany(self, query, params_list)`
- `def commit(self)`
- `def rollback(self)`
- `def close(self)`

### class `MockPool`

**Methods:**

- `def __init__(self, minconn, maxconn)`
- `def getconn(self)`
- `def putconn(self, conn)`
- `def closeall(self)`

### def `setup_mock_psycopg`
- `def setup_mock_psycopg()`
- **Decorators**: `pytest.fixture(autouse=True)`

### def `pg_transport`
- `def pg_transport(setup_mock_psycopg)`
- **Decorators**: `pytest.fixture`

### def `test_pg_bulk_insert`
- `def test_pg_bulk_insert(pg_transport)`
> Verify that execute_many successfully executes bulk INSERT

via native executemany/execute_batch.

### def `test_pg_bulk_update`
- `def test_pg_bulk_update(pg_transport)`
> Verify that execute_many successfully executes bulk UPDATE.

### def `test_pg_empty_batch_execution`
- `def test_pg_empty_batch_execution(pg_transport)`
> Verify that execute_many returns an empty list immediately when given an empty batch.

### def `test_pg_partial_failure_rollback_behavior`
- `def test_pg_partial_failure_rollback_behavior(pg_transport)`
> Verify that if execute_many is inside a transaction and fails,

the transaction is rolled back.

### def `test_pg_transaction_consistency_after_bulk_operations`
- `def test_pg_transaction_consistency_after_bulk_operations(pg_transport)`
> Verify that transaction depth and state remain fully consistent

after successful bulk operations.

### def `test_benchmark_bulk_vs_sequential`
- `def test_benchmark_bulk_vs_sequential(pg_transport)`
> Benchmark optimized native execute_batch vs simulated sequential execution.

## Module: core/tests/test_redis_queue.py

### def `queue_env`
- `def queue_env()`
- **Decorators**: `pytest.fixture`

### def `test_queue_ownership_registry`
- `def test_queue_ownership_registry(queue_env)`

### def `test_enqueue_dequeue_and_acknowledgement`
- `def test_enqueue_dequeue_and_acknowledgement(queue_env)`

### def `test_priority_ordering`
- `def test_priority_ordering(queue_env)`

### def `test_delayed_jobs`
- `def test_delayed_jobs(queue_env)`

### def `test_retry_and_dead_letter_queue`
- `def test_retry_and_dead_letter_queue(queue_env)`

### def `test_pause_resume_and_purge`
- `def test_pause_resume_and_purge(queue_env)`

### def `test_redis_outage_fallback`
- `def test_redis_outage_fallback(queue_env)`

### def `test_observability_and_recommendations`
- `def test_observability_and_recommendations(queue_env)`

## Module: core/tests/run_qdrant_production_validation.py

### def `run_connectivity_tests`
- `def run_connectivity_tests(config: QdrantConfigurationService) -> Dict[str, Any]`

### def `run_collection_tests`
- `def run_collection_tests(col_mgr: CollectionManager) -> Dict[str, Any]`

### def `run_crud_tests`
- `def run_crud_tests(sem_mgr: SemanticMemoryManager) -> Dict[str, Any]`

### def `run_search_tests`
- `def run_search_tests(sem_mgr: SemanticMemoryManager, hybrid_svc: HybridRetrievalService) -> Dict[str, Any]`

### def `run_embedding_tests`
- `def run_embedding_tests(engine: EmbeddingEngine) -> Dict[str, Any]`

### def `run_failure_recovery_tests`
- `def run_failure_recovery_tests(sem_mgr: SemanticMemoryManager) -> Dict[str, Any]`

### def `run_runtime_intelligence_tests`
- `def run_runtime_intelligence_tests(ri_svc: QdrantRuntimeService) -> Dict[str, Any]`

### def `run_performance_benchmarks`
- `def run_performance_benchmarks(sem_mgr: SemanticMemoryManager, engine: EmbeddingEngine, hybrid_svc: HybridRetrievalService) -> Dict[str, Any]`

### def `compile_reports`
- `def compile_reports(docs_dir: str, conn_res: Dict[str, Any], col_res: Dict[str, Any], crud_res: Dict[str, Any], search_res: Dict[str, Any], embed_res: Dict[str, Any], fail_res: Dict[str, Any], ri_res: Dict[str, Any], perf_res: Dict[str, Any])`

### def `update_project_status`
- `def update_project_status(latency: float, throughput: float)`

### def `update_knowledge_base`
- `def update_knowledge_base()`

### def `copy_reports_to_artifacts`
- `def copy_reports_to_artifacts(docs_dir: str)`

### def `main`
- `def main()`

## Module: core/tests/test_tool.py

### def `test_filesystem_tool`
- `def test_filesystem_tool(tmp_path)`

### def `test_filesystem_tool_traversal_attempts`
- `def test_filesystem_tool_traversal_attempts(tmp_path)`

### def `test_git_tool`
- `def test_git_tool()`

### def `test_terminal_tool`
- `def test_terminal_tool()`

### def `test_terminal_tool_security_safeguards`
- `def test_terminal_tool_security_safeguards()`

### def `test_tool_manager_and_events`
- `def test_tool_manager_and_events()`

## Module: core/tests/test_qdrant_platform.py

### def `test_qdrant_configuration`
- `def test_qdrant_configuration()`

### def `test_qdrant_connection_manager_and_transport`
- `def test_qdrant_connection_manager_and_transport()`

### def `test_qdrant_provider_and_collection_manager`
- `def test_qdrant_provider_and_collection_manager()`

### def `test_embedding_cache`
- `def test_embedding_cache()`

### def `test_chunking_service`
- `def test_chunking_service()`

### def `test_context_builder`
- `def test_context_builder()`

### def `test_dependency_injection_and_runtime_intelligence`
- `def test_dependency_injection_and_runtime_intelligence()`

### def `test_repositories_dependency_injection`
- `def test_repositories_dependency_injection()`

### def `test_repository_operations`
- `def test_repository_operations()`

### def `test_embedding_engine_and_semantic_search`
- `def test_embedding_engine_and_semantic_search()`

### def `test_hybrid_retrieval_pipeline`
- `def test_hybrid_retrieval_pipeline()`

### def `test_qdrant_runtime_intelligence`
- `def test_qdrant_runtime_intelligence()`

## Module: core/tests/test_developer_workspace.py

### def `test_git_status_parsing`
- `def test_git_status_parsing()`

### def `test_test_discovery_and_build_detection`
- `def test_test_discovery_and_build_detection()`

### def `test_safe_command_execution`
- `def test_safe_command_execution()`

### def `test_context_manager_developer_workspace_integration`
- `def test_context_manager_developer_workspace_integration()`

## Module: core/tests/test_workflow_graph.py

### def `test_linear_workflow_grouping`
- `def test_linear_workflow_grouping()`

### def `test_parallel_workflow_grouping`
- `def test_parallel_workflow_grouping()`

### def `test_invalid_dependency_error`
- `def test_invalid_dependency_error()`

### def `test_circular_dependency_error`
- `def test_circular_dependency_error()`

### def `test_visualization_output`
- `def test_visualization_output()`

### def `test_executor_executes_by_levels`
- `def test_executor_executes_by_levels()`

## Module: core/tests/test_cli.py

### def `test_handle_conversation_command_list_empty`
- `def test_handle_conversation_command_list_empty()`

### def `test_handle_conversation_command_current_empty`
- `def test_handle_conversation_command_current_empty()`

### def `test_print_help_table`
- `def test_print_help_table()`

### def `test_print_skills_table`
- `def test_print_skills_table()`

### def `test_print_providers_table`
- `def test_print_providers_table()`

### def `test_handle_model_switch`
- `def test_handle_model_switch()`

## Module: core/tests/test_knowledge_hub.py

### def `mock_personal_service`
- `def mock_personal_service()`
- **Decorators**: `pytest.fixture`

### def `test_notion_provider_offline_mode`
- `def test_notion_provider_offline_mode()`

### def `test_notion_provider_http_calls`
- `def test_notion_provider_http_calls(mock_urlopen)`
- **Decorators**: `patch('urllib.request.urlopen')`

### def `test_knowledge_hub_sync_lifecycle`
- `def test_knowledge_hub_sync_lifecycle(mock_personal_service)`

### def `test_subsystem_integrations_mocked`
- `def test_subsystem_integrations_mocked(mock_personal_service)`

## Module: core/tests/test_persistence_policy.py

### class `OfflineDatabaseTransport`
- **Inherits from**: DatabaseTransport

> Database transport simulating an offline state.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService) -> None`
- `def validate_configuration(self) -> List[str]`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute(self, query: str, params: Optional[tuple]) -> TransportResult`
- `def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]`
- `def begin_transaction(self) -> TransportTransaction`
- `def health(self) -> TransportHealth`
- `def capabilities(self) -> TransportCapabilities`

### class `AwaitingConfigDatabaseTransport`
- **Inherits from**: OfflineDatabaseTransport

> Database transport simulating awaiting configuration state.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService) -> None`
- `def health(self) -> TransportHealth`

### class `MockOfflinePostgreSQLProvider`
- **Inherits from**: PostgreSQLProvider

**Methods:**

- `def initialize(self, config: PersistenceConfigurationService) -> None`

### class `MockAwaitingConfigPostgreSQLProvider`
- **Inherits from**: PostgreSQLProvider

**Methods:**

- `def initialize(self, config: PersistenceConfigurationService) -> None`

### def `test_strict_policy_fails_immediately`
- `def test_strict_policy_fails_immediately()`

### def `test_awaiting_config_fails_immediately_in_strict`
- `def test_awaiting_config_fails_immediately_in_strict()`

### def `test_best_effort_policy_returns_failure_result`
- `def test_best_effort_policy_returns_failure_result()`

### def `test_read_only_policy_blocks_writes`
- `def test_read_only_policy_blocks_writes()`

### def `test_persistence_result_attributes`
- `def test_persistence_result_attributes()`

### def `test_profile_service_strict_policy_fails_on_db_disconnect`
- `def test_profile_service_strict_policy_fails_on_db_disconnect()`

### def `test_profile_service_best_effort_policy_registers_in_memory`
- `def test_profile_service_best_effort_policy_registers_in_memory()`

## Module: core/tests/test_embedding_provider_selection.py

### def `make_service_with_providers`
- `def make_service_with_providers() -> EmbeddingServiceImpl`
> Return an EmbeddingServiceImpl pre-loaded with named stub providers.

### def `make_engine`
- `def make_engine(service: EmbeddingServiceImpl, provider_env: Optional[str]) -> EmbeddingEngineImpl`
> Construct EmbeddingEngineImpl with optional EMBEDDING_PROVIDER override.

### def `test_default_active_provider_is_not_mock`
- `def test_default_active_provider_is_not_mock()`
> When EMBEDDING_PROVIDER is unset the default must NOT be 'mock'.

### def `test_default_active_provider_is_sentence_transformer`
- `def test_default_active_provider_is_sentence_transformer()`
> When EMBEDDING_PROVIDER is unset the default must be 'sentence_transformer'.

### def `test_initialize_raises_when_provider_not_registered`
- `def test_initialize_raises_when_provider_not_registered()`
> initialize() must raise ValueError when the configured provider is missing.

### def `test_initialize_error_message_lists_available_providers`
- `def test_initialize_error_message_lists_available_providers()`
> The ValueError from initialize() must list available providers.

### def `test_initialize_succeeds_with_sentence_transformer_registered`
- `def test_initialize_succeeds_with_sentence_transformer_registered()`
> Production default 'sentence_transformer' must pass initialize() validation.

### def `test_embed_text_uses_sentence_transformer_by_default`
- `def test_embed_text_uses_sentence_transformer_by_default()`
> embed_text() with no provider_name must route to sentence_transformer, not mock.

### def `test_mock_provider_works_when_explicitly_requested_via_env`
- `def test_mock_provider_works_when_explicitly_requested_via_env()`
> EMBEDDING_PROVIDER=mock must still work -- useful for tests.

### def `test_mock_provider_works_when_explicitly_requested_per_request`
- `def test_mock_provider_works_when_explicitly_requested_per_request()`
> Passing provider_name='mock' on an EmbeddingRequest must use mock even in production.

### def `test_initialize_skips_validation_when_no_providers_registered`
- `def test_initialize_skips_validation_when_no_providers_registered()`
> If no providers are registered yet, initialize() must not raise (deferred registration).

## Module: core/tests/test_execution_engine.py

### def `mock_swe_plan`
- `def mock_swe_plan()`
- **Decorators**: `pytest.fixture`

### def `test_validation_pre_flight`
- `def test_validation_pre_flight(mock_swe_plan)`

### def `test_task_executor_user_gate`
- `def test_task_executor_user_gate()`

### def `test_execution_engine_lifecycle`
- `def test_execution_engine_lifecycle(mock_swe_plan)`

### def `test_execution_engine_pause_resume`
- `def test_execution_engine_pause_resume(mock_swe_plan)`

### def `test_rollback_generation`
- `def test_rollback_generation(mock_swe_plan)`

### def `test_memory_and_knowledge_hub_integration`
- `def test_memory_and_knowledge_hub_integration(mock_swe_plan)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_docgen.py

### class `TestGenerationStatus`

**Methods:**

- `def test_generation_succeeds(self, generation_result)`
  * Generator must complete with SUCCESS status.
- `def test_no_errors(self, generation_result)`
  * No hard errors should be raised during generation.
- `def test_eight_files_produced(self, generation_result)`
  * Exactly 8 files must be produced (7 catalogs + README index).
- `def test_elapsed_is_positive(self, generation_result)`
  * Elapsed time must be measured and positive.

### class `TestGeneratedFilesExist`

**Methods:**

- `def test_file_exists(self, output_dir, fname)`
- `def test_file_not_empty(self, output_dir, fname)`

### class `TestServiceCatalog`

**Methods:**

- `def content(self, output_dir)`
- `def test_header_present(self, content)`
- `def test_generated_banner(self, content)`
- `def test_contains_known_service(self, content)`
- `def test_contains_event_bus(self, content)`
- `def test_contains_session_service(self, content)`
- `def test_services_count_positive(self, generation_result)`
- `def test_services_count_reasonable(self, generation_result)`
- `def test_summary_statistics_section(self, content)`
- `def test_has_module_column(self, content)`

### class `TestRepositoryCatalog`

**Methods:**

- `def content(self, output_dir)`
- `def test_header_present(self, content)`
- `def test_contains_workspace_repo(self, content)`
- `def test_contains_project_repo(self, content)`
- `def test_repositories_count_positive(self, generation_result)`
- `def test_repositories_count_reasonable(self, generation_result)`
- `def test_entity_column_present(self, content)`

### class `TestSkillCatalog`

**Methods:**

- `def content(self, output_dir)`
- `def test_header_present(self, content)`
- `def test_contains_research_skill(self, content)`
- `def test_skills_count_equals_toml_count(self, generation_result)`
- `def test_skill_matrix_present(self, content)`
- `def test_version_column_present(self, content)`
- `def test_category_column_present(self, content)`

### class `TestProviderCatalog`

**Methods:**

- `def content(self, output_dir)`
- `def test_header_present(self, content)`
- `def test_contains_claude_provider(self, content)`
- `def test_contains_gemini_provider(self, content)`
- `def test_providers_count_positive(self, generation_result)`
- `def test_cost_comparison_section(self, content)`
- `def test_capability_matrix_section(self, content)`
- `def test_context_window_present(self, content)`

### class `TestRuntimeCatalog`

**Methods:**

- `def content(self, output_dir)`
- `def test_header_present(self, content)`
- `def test_runtime_count_positive(self, generation_result)`
- `def test_runtime_count_reasonable(self, generation_result)`
- `def test_summary_statistics_section(self, content)`

### class `TestDependencyGraph`

**Methods:**

- `def content(self, output_dir)`
- `def test_header_present(self, content)`
- `def test_mermaid_block_present(self, content)`
- `def test_di_table_present(self, content)`
- `def test_di_bindings_count_positive(self, generation_result)`
- `def test_di_bindings_count_reasonable(self, generation_result)`
- `def test_graph_lr_directive(self, content)`

### class `TestDbModelCatalog`

**Methods:**

- `def content(self, output_dir)`
- `def test_header_present(self, content)`
- `def test_enumerations_section(self, content)`
- `def test_dataclasses_section(self, content)`
- `def test_db_models_count_positive(self, generation_result)`
- `def test_db_models_count_reasonable(self, generation_result)`

### class `TestIdempotency`

**Methods:**

- `def test_same_discovery_counts_on_rerun(self, tmp_path)`
  * Two consecutive runs on the same source must yield identical counts.
- `def test_same_file_count_on_rerun(self, tmp_path)`
  * Two consecutive runs must produce exactly the same number of files.
- `def test_same_file_sizes_on_rerun(self, tmp_path)`
  * Content sizes must match between runs (timestamps differ but sections are equal).
We compare content stripped of lines containing the timestamp.

### class `TestHandwrittenDocsUntouched`

**Methods:**

- `def test_handwritten_doc_unchanged(self, rel_path)`
  * Generator must never write to handwritten documentation files.

### class `TestServiceDiscoverer`

**Methods:**

- `def test_discovers_memory_service(self)`
- `def test_all_entries_have_name(self)`
- `def test_all_entries_have_module(self)`
- `def test_sorted_alphabetically(self)`

### class `TestRepositoryDiscoverer`

**Methods:**

- `def test_discovers_workspace_repository(self)`
- `def test_all_entries_have_entity(self)`
- `def test_sorted_alphabetically(self)`

### class `TestSkillDiscoverer`

**Methods:**

- `def test_discovers_research_skill(self)`
- `def test_all_skills_have_name(self)`
- `def test_all_skills_have_description(self)`
- `def test_missing_skills_dir_returns_empty(self, tmp_path)`

### class `TestProviderDiscoverer`

**Methods:**

- `def test_discovers_providers(self)`
- `def test_all_providers_have_name(self)`
- `def test_context_window_positive(self)`

### class `TestDbModelDiscoverer`

**Methods:**

- `def test_discovers_enums(self)`
- `def test_discovers_dataclasses(self)`
- `def test_all_models_have_module(self)`

### class `TestDIBindingDiscoverer`

**Methods:**

- `def test_discovers_bindings(self)`
- `def test_all_bindings_have_interface(self)`
- `def test_all_bindings_have_concrete(self)`

### class `TestRenderers`

**Methods:**

- `def test_service_catalog_renderer_produces_markdown(self)`
- `def test_skill_catalog_renderer_produces_markdown(self)`
- `def test_dependency_graph_renderer_has_mermaid(self)`
- `def test_provider_catalog_renderer_has_cost_table(self)`
- `def test_repository_catalog_renderer(self)`
- `def test_index_renderer(self)`

### class `TestGenerationResultModel`

**Methods:**

- `def test_default_status_no_errors(self)`
- `def test_failed_status(self)`
- `def test_partial_status(self)`

### def `generated_dir`
- `def generated_dir(tmp_path_factory)`
- **Decorators**: `pytest.fixture(scope='module')`
> Run the generator once against the real source tree but write output
to a temp directory so handwritten docs are untouched.

### def `generation_result`
- `def generation_result(generated_dir)`
- **Decorators**: `pytest.fixture(scope='module')`

### def `output_dir`
- `def output_dir(generated_dir)`
- **Decorators**: `pytest.fixture(scope='module')`

### def `_strip_timestamps`
- `def _strip_timestamps(content: str) -> str`
> Remove lines containing ISO 8601 timestamps for idempotency comparison.

## Module: core/tests/test_engineering_documentation.py

### def `test_adr_generation`
- `def test_adr_generation()`

### def `test_engineering_reports`
- `def test_engineering_reports()`

### def `test_decision_records_planning`
- `def test_decision_records_planning()`

### def `test_document_validator`
- `def test_document_validator()`

### def `test_service_evaluation_flow`
- `def test_service_evaluation_flow()`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_redis_fallback_regression.py

### def `clean_env`
- `def clean_env()`
- **Decorators**: `pytest.fixture(autouse=True)`

### def `test_production_mode_redis_unavailable_raises`
- `def test_production_mode_redis_unavailable_raises()`
> Production mode must never silently fall back; it must raise on failure.

### def `test_development_mode_fallback_enabled`
- `def test_development_mode_fallback_enabled()`
> Development/Test mode with fallback enabled should return FakeRedisClient on failure.

### def `test_development_mode_fallback_disabled_raises`
- `def test_development_mode_fallback_disabled_raises()`
> Development/Test mode with fallback disabled must raise on failure.

### def `test_successful_redis_reconnection`
- `def test_successful_redis_reconnection()`
> If Redis becomes available later, connection manager should successfully reconnect.

## Module: core/tests/test_approval.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `test_rules_evaluation`
- `def test_rules_evaluation()`

### def `test_package_construction`
- `def test_package_construction()`

### def `test_decision_generation_approved`
- `def test_decision_generation_approved()`

### def `test_decision_generation_rejected`
- `def test_decision_generation_rejected()`

### def `test_validator`
- `def test_validator()`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service)`

### def `test_backward_compatibility`
- `def test_backward_compatibility()`

## Module: core/tests/test_action.py

### def `test_action_models`
- `def test_action_models()`

### def `test_action_planning`
- `def test_action_planning()`

### def `test_action_approval`
- `def test_action_approval()`

### def `test_action_execution_success`
- `def test_action_execution_success()`

### def `test_action_execution_failure_and_rollback`
- `def test_action_execution_failure_and_rollback()`

### def `test_action_history`
- `def test_action_history()`

## Module: core/tests/test_workspace_intelligence.py

### def `mock_project_context`
- `def mock_project_context()`
- **Decorators**: `pytest.fixture`

### def `mock_project_intel`
- `def mock_project_intel(mock_project_context)`
- **Decorators**: `pytest.fixture`

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_knowledge_hub`
- `def mock_knowledge_hub()`
- **Decorators**: `pytest.fixture`

### def `test_repository_analyzer`
- `def test_repository_analyzer(mock_project_intel)`

### def `test_architecture_analyzer`
- `def test_architecture_analyzer()`

### def `test_dependency_analyzer`
- `def test_dependency_analyzer(mock_project_context)`

### def `test_technology_analyzer`
- `def test_technology_analyzer(mock_project_context)`

### def `test_documentation_analyzer`
- `def test_documentation_analyzer(mock_project_context)`

### def `test_workspace_intelligence_service`
- `def test_workspace_intelligence_service(mock_project_intel, mock_memory_service, mock_knowledge_hub)`

### def `test_python_ast_parsing_and_symbol_extraction`
- `def test_python_ast_parsing_and_symbol_extraction()`

### def `test_typescript_ast_parsing_and_symbol_extraction`
- `def test_typescript_ast_parsing_and_symbol_extraction()`

### def `test_dependency_graph_builder`
- `def test_dependency_graph_builder()`

### def `test_call_graph_builder`
- `def test_call_graph_builder(tmp_path)`

### def `test_code_intelligence_service_integration`
- `def test_code_intelligence_service_integration(mock_project_intel, mock_memory_service, mock_knowledge_hub, tmp_path)`

### def `test_backward_compatibility_and_future_languages`
- `def test_backward_compatibility_and_future_languages()`

## Module: core/tests/test_review.py

### def `mock_memory_service`
- `def mock_memory_service()`
- **Decorators**: `pytest.fixture`

### def `mock_workspace_service`
- `def mock_workspace_service()`
- **Decorators**: `pytest.fixture`

### def `mock_model_service`
- `def mock_model_service()`
- **Decorators**: `pytest.fixture`

### def `dummy_package`
- `def dummy_package()`
- **Decorators**: `pytest.fixture`

### def `test_review_analysis`
- `def test_review_analysis(dummy_package)`

### def `test_review_validation`
- `def test_review_validation()`

### def `test_workspace_integration`
- `def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service, dummy_package)`

### def `test_memory_integration`
- `def test_memory_integration(mock_memory_service, dummy_package)`

### def `test_knowledge_hub_integration`
- `def test_knowledge_hub_integration(mock_memory_service, dummy_package)`

### def `test_backward_compatibility`
- `def test_backward_compatibility(dummy_package)`

## Module: core/src/aios/bootstrap.py

### def `bootstrap_kernel`
- `def bootstrap_kernel(config_path: Path) -> Kernel`
> Composition Root for Personal AI OS.
Constructs, wires, and registers all concrete services.
Returns a configured Kernel instance.

## Module: core/src/aios/config.py

### class `RuntimeConfig`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

### class `OpenRouterConfig`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

### class `OmniRouteConfig`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

### class `LLMConfig`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

### class `GitHubConfig`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

### class `NotionConfig`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

### class `PersistenceConfig`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

### class `OSConfig`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

### def `load_config`
- `def load_config(config_path: Path) -> OSConfig`
> Loads and parses the TOML configuration file.

## Module: core/src/aios/kernel.py

### class `RuntimeState`
- **Inherits from**: Enum
- **Type**: Enum

> Represents the operating state of the AI OS runtime lifecycle.

### class `Kernel`

> The orchestrator and runtime engine of the Personal AI OS.
Owns configuration loading, service lifecycle transitions, and the service registry.
Exposes only lifecycle and runtime state methods.

**Methods:**

- `def __init__(self, config_path: Path, registry: ServiceRegistry | None) -> None`
- `def state(self) -> RuntimeState`
  * Returns the current state of the runtime.
- `def active_session_id(self) -> str | None`
  * Returns the ID of the active session, if any.
- `def uptime(self) -> float`
  * Returns the uptime in seconds since the boot sequence started.
- `def boot(self) -> None`
  * Executes the Kernel startup lifecycle sequence.
- `def start_session(self, session_id: str) -> None`
  * Transitions the runtime state to associate with an active session.
- `def end_session(self) -> None`
  * Disassociates the active session from the runtime.
- `def execute_intent(self, intent: Intent) -> IntentResult`
  * Executes a structured Intent by delegating to the Agent Runtime.
- `def mark_busy(self, busy: bool) -> None`
  * Transitions the runtime state between READY and BUSY.
- `def _initialize_services(self) -> None`
  * Invokes the initialize stage on all registered services.
- `def _transition_to_ready(self) -> None`
  * Invokes the on_ready stage on all registered services and publishes startup event.
- `def shutdown(self) -> None`
  * Executes a graceful shutdown, tearing down all registered services in reverse order.

## Module: core/src/aios/registry.py

### class `ServiceRegistry`

> Manages core service registration and lookup.

**Methods:**

- `def __init__(self) -> None`
- `def register(self, service_type: Type[T], instance: T) -> None`
  * Registers a service instance under its interface class.
- `def get(self, service_type: Type[T]) -> T`
  * Retrieves a registered service instance.
- `def get_all(self) -> List[ServiceLifecycle]`
  * Returns all registered service instances.

## Module: core/src/aios/cli.py

### def `handle_conversation_command`
- `def handle_conversation_command(user_input: str, conv_manager: ConversationManager) -> bool`

### def `print_help_table`
- `def print_help_table(registry: CommandRegistry) -> None`

### def `print_skills_table`
- `def print_skills_table(skill_registry: SkillRegistry) -> None`

### def `print_providers_table`
- `def print_providers_table(model_service: ModelService) -> None`

### def `handle_model_switch`
- `def handle_model_switch(model_service: ModelService, model_name: str) -> None`

### def `print_conversation_history`
- `def print_conversation_history(conv_manager: ConversationManager) -> None`

### def `print_status_line`
- `def print_status_line(model_service: ModelService, conv_manager: ConversationManager) -> None`

### def `read_input`
- `def read_input(multiline_mode: bool) -> str`
> Reads input from the user, supporting multi-line formatting.

### def `handle_general_chat`
- `def handle_general_chat(user_input: str, conv_manager: ConversationManager, model_service: ModelService) -> None`

### def `execute_builtin_cli_command`
- `def execute_builtin_cli_command(args: list[str], exit_on_complete: bool) -> bool`

### def `main`
- `def main() -> None`
> CLI entry point for aios.

## Module: core/src/aios/providers/metrics.py

### class `ProviderMetricsCollector`

**Methods:**

- `def __init__(self) -> None`
- `def record_usage(self, provider_name: str, model_name: str, prompt_tokens: int, completion_tokens: int, cost: float) -> None`
- `def get_summary(self) -> dict`

## Module: core/src/aios/providers/nvidia.py

### class `NVIDIAProviderAdapter`

> Separates the NVIDIA Inference API request/response translation from AI OS routing logic.

**Methods:**

- `def __init__(self, api_key: Optional[str]) -> None`
- `def translate_request(self, model: str, prompt: str, system_prompt: Optional[str]) -> Dict[str, Any]`
  * Translates generic AI OS arguments to NVIDIA Inference API payload.
- `def translate_response(self, response_data: Dict[str, Any]) -> str`
  * Translates raw response JSON structure from NVIDIA API to standard string.
- `def execute_completion(self, model: str, prompt: str, system_prompt: Optional[str]) -> str`
  * Sends HTTPS request to NVIDIA API with error handling.

### class `NVIDIAProvider`
- **Inherits from**: AIProvider

> Concrete NVIDIA Inference API provider implementation.

**Methods:**

- `def __init__(self, adapter: Optional[NVIDIAProviderAdapter]) -> None`
- `def name(self) -> str`
- `def generate(self, model: str, prompt: str, system_prompt: Optional[str]) -> str`
- `def stream(self, model: str, prompt: str, system_prompt: Optional[str]) -> Iterator[str]`
  * Not implemented in foundation milestone.
- `def embeddings(self, model: str, text: str) -> List[float]`
  * Not implemented in foundation milestone.
- `def health(self) -> bool`
  * Checks provider health based on key presence.
- `def capabilities(self) -> ProviderCapabilities`
  * Returns capabilities of NVIDIA provider.

### def `register_nvidia_provider`
- `def register_nvidia_provider() -> None`
> Bootstraps and registers NVIDIA provider and its metadata inside the registries.

## Module: core/src/aios/providers/config.py

### class `ProviderConfig`
- **Decorators**: `dataclass`
- **Type**: Dataclass

## Module: core/src/aios/providers/models.py

### class `ProviderStatus`
- **Inherits from**: str, Enum
- **Type**: Enum

### class `ProviderCapabilities`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ProviderStatistics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ProviderMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `DIInitializeMixin`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def shutdown(self) -> None`

### class `ExecutionContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ExecutionSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ProviderDiagnostics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

## Module: core/src/aios/providers/health.py

### class `ProviderTokenUsageTracker`
- **Inherits from**: DIInitializeMixin

> Tracks daily and monthly input/output token counts.

**Methods:**

- `def __init__(self, registry: Optional[Any]) -> None`
- `def record_tokens(self, provider_name: str, input_tokens: int, output_tokens: int) -> None`
- `def get_usage(self, provider_name: str) -> Dict[str, int]`

### class `ProviderLatencyAnalyzer`
- **Inherits from**: DIInitializeMixin

> Tracks and calculates latency history statistics.

**Methods:**

- `def __init__(self) -> None`
- `def record_latency(self, provider_name: str, latency: float) -> None`
- `def get_average_latency(self, provider_name: str) -> float`
- `def get_p95_latency(self, provider_name: str) -> float`

### class `ProviderCostAnalyzer`
- **Inherits from**: DIInitializeMixin

> Computes cost model values based on token rates.

**Methods:**

- `def __init__(self, registry: Any) -> None`
- `def estimate_cost(self, provider_name: str, input_tokens: int, output_tokens: int) -> float`
- `def record_cost(self, provider_name: str, cost: float) -> None`
- `def get_total_cost(self, provider_name: str) -> float`

### class `ProviderSuccessAnalyzer`
- **Inherits from**: DIInitializeMixin

> Tracks positive requests execution counts and timestamps.

**Methods:**

- `def __init__(self) -> None`
- `def record_success(self, provider_name: str) -> None`
- `def get_success_count(self, provider_name: str) -> int`
- `def get_last_success_time(self, provider_name: str) -> float`

### class `ProviderFailureAnalyzer`
- **Inherits from**: DIInitializeMixin

> Tracks failed request executions and stores log details.

**Methods:**

- `def __init__(self) -> None`
- `def record_failure(self, provider_name: str, error_message: str) -> None`
- `def get_failure_count(self, provider_name: str) -> int`
- `def get_last_failure_time(self, provider_name: str) -> float`

### class `ProviderRateLimitManager`
- **Inherits from**: DIInitializeMixin

> Manages provider rate limit cooldown parameters.

**Methods:**

- `def __init__(self) -> None`
- `def trigger_rate_limit(self, provider_name: str, retry_after: float) -> None`
- `def is_rate_limited(self, provider_name: str) -> bool`

### class `ProviderQuotaManager`
- **Inherits from**: DIInitializeMixin

> Monitors daily/monthly budget quotas and raises failover triggers.

**Methods:**

- `def __init__(self, registry: Optional[Any]) -> None`
- `def record_cost(self, provider_name: str, cost: float) -> None`
- `def is_quota_exhausted(self, provider_name: str) -> bool`
- `def get_remaining_quota(self, provider_name: str) -> float`

### class `ProviderHealthMonitor`
- **Inherits from**: DIInitializeMixin

> Consolidated provider health, latency, rate limits, and quota manager.

**Methods:**

- `def __init__(self, registry: Optional[Any]) -> None`
- `def record_success(self, provider_name: str, latency: float) -> None`
- `def record_failure(self, provider_name: str, error_message: str) -> None`
- `def get_average_latency(self, provider_name: str) -> float`
- `def get_success_rate(self, provider_name: str) -> float`
- `def get_availability_pct(self, provider_name: str) -> float`
- `def is_healthy(self, provider_name: str) -> bool`

## Module: core/src/aios/providers/interface.py

### class `AIProvider`
- **Inherits from**: abc.ABC

> Universal abstract interface for all AI provider engines.

**Methods:**

- `def name(self) -> str`
  * Returns the identifier name of the provider.
- `def generate(self, model: str, prompt: str, system_prompt: Optional[str]) -> str`
  * Executes content generation for a prompt.
- `def stream(self, model: str, prompt: str, system_prompt: Optional[str]) -> Iterator[str]`
  * Streams content generation for a prompt.
- `def embeddings(self, model: str, text: str) -> List[float]`
  * Generates embedding vector for text.
- `def health(self) -> bool`
  * Checks the health and availability of the provider.
- `def capabilities(self) -> ProviderCapabilities`
  * Returns the capabilities of the provider.

### class `AIProviderRegistry`

> Universal registry to manage, register, and look up AIProvider instances.

**Methods:**

- `def __init__(self) -> None`
- `def register(self, provider: AIProvider) -> None`
  * Registers a concrete AIProvider instance.
- `def lookup(self, name: str) -> Optional[AIProvider]`
  * Retrieves a registered AIProvider instance by name.
- `def list_providers(self) -> List[str]`
  * Lists the names of all registered providers.

### class `ModelInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents metadata and capabilities of a specific AI model.

### class `ModelRegistry`

> Universal registry managing metadata for AI models and their provider mappings.

**Methods:**

- `def __init__(self, provider_registry: Optional[AIProviderRegistry]) -> None`
- `def register_model(self, model: ModelInfo) -> None`
  * Registers a ModelInfo metadata profile.
- `def get_model(self, model_id: str) -> Optional[ModelInfo]`
  * Looks up a ModelInfo metadata profile by its model_id.
- `def list_models(self, provider_name: Optional[str]) -> List[ModelInfo]`
  * Lists all registered models, optionally filtering by provider.
- `def get_provider_for_model(self, model_id: str) -> Optional[str]`
  * Finds the provider name mapped to the specified model_id.
- `def register_model_resolution(self, provider: str, canonical_id: str, provider_id: str) -> None`
  * Allows dynamic registration of canonical-to-provider model mappings.
- `def resolve_provider_model(self, provider: str, model_id: str) -> str`
  * Resolves a canonical model ID to its provider-specific model ID.

### class `CapabilityRegistry`

> Universal registry describing the capabilities of AI providers and models.

**Methods:**

- `def __init__(self, provider_registry: Optional[AIProviderRegistry]) -> None`
- `def register_provider_capabilities(self, provider_name: str, caps: ProviderCapabilities) -> None`
  * Registers capabilities for a provider.
- `def register_model_capabilities(self, model_name: str, caps: ProviderCapabilities) -> None`
  * Registers capabilities for a specific model.
- `def get_capabilities(self, provider_name: str, model_name: Optional[str]) -> Optional[ProviderCapabilities]`
  * Retrieves capabilities for a provider or model.

Falls back to provider capabilities if model caps not found.

### class `ProviderHealth`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents health status metrics of an AI provider.

### class `ProviderHealthRegistry`

> Registry managing dynamic health metrics for AI providers.

**Methods:**

- `def __init__(self, provider_registry: Optional[AIProviderRegistry]) -> None`
- `def get_health(self, provider_name: str) -> ProviderHealth`
  * Retrieves current health details for a provider.

Returns default health if none registered.
- `def update_health(self, provider_name: str) -> None`
  * Updates health attributes dynamically for a provider.

### class `ProviderCost`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents the token pricing model for a provider or specific model.

**Methods:**

- `def estimated_request_cost(self, input_tokens: int, output_tokens: int) -> float`
  * Estimates the cost of a single request based on token counts.

### class `ProviderQuota`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents the quota limits and remaining budgets of a provider.

### class `ProviderCostRegistry`

> Registry managing pricing/costs of providers and models.

**Methods:**

- `def __init__(self, provider_registry: Optional[AIProviderRegistry]) -> None`
- `def register_provider_cost(self, provider_name: str, cost: ProviderCost) -> None`
  * Registers cost profile for a provider.
- `def register_model_cost(self, model_name: str, cost: ProviderCost) -> None`
  * Registers cost profile for a specific model.
- `def get_cost(self, provider_name: str, model_name: Optional[str]) -> Optional[ProviderCost]`
  * Retrieves cost profile for a model or provider.

Falls back to provider cost.

### class `ProviderQuotaRegistry`

> Registry managing quotas (requests/tokens remaining) for providers.

**Methods:**

- `def __init__(self, provider_registry: Optional[AIProviderRegistry]) -> None`
- `def get_quota(self, provider_name: str) -> ProviderQuota`
  * Retrieves quota tracking details for a provider.

Returns default unlimited quota if none registered.
- `def update_quota(self, provider_name: str) -> None`
  * Updates quota parameters dynamically for a provider.

### class `RoutingRequest`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a request to select the optimal AI provider/model endpoint.

### class `RoutingDecision`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents the final provider/model routing choice determined by the RoutingEngine.

### class `RoutingEngine`

> Routing engine that dynamically selects the best provider/model endpoint.

**Methods:**

- `def __init__(self, provider_registry: Optional[AIProviderRegistry], capability_registry: Optional[CapabilityRegistry], health_registry: Optional[ProviderHealthRegistry], cost_registry: Optional[ProviderCostRegistry], quota_registry: Optional[ProviderQuotaRegistry], model_registry: Optional[ModelRegistry]) -> None`
- `def route(self, request: RoutingRequest) -> RoutingDecision`
  * Determines the best provider/model routing decision based on active registry metrics.

### class `OmniRouteRequest`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a unified prompt execution request to the OmniRoute Engine.

### class `OmniRouteResponse`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a unified, provider-independent response from the OmniRoute Engine.

### class `OmniRouteEngine`

> Core execution engine coordinating routing, quota, and provider execution.

**Methods:**

- `def __init__(self, provider_registry: Optional[AIProviderRegistry], capability_registry: Optional[CapabilityRegistry], health_registry: Optional[ProviderHealthRegistry], cost_registry: Optional[ProviderCostRegistry], quota_registry: Optional[ProviderQuotaRegistry], routing_engine: Optional[RoutingEngine], model_registry: Optional[ModelRegistry]) -> None`
- `def execute(self, request: OmniRouteRequest) -> OmniRouteResponse`
  * Routes, executes, and updates telemetry/metadata for the request.

## Module: core/src/aios/providers/adapters.py

### class `MockProvider`
- **Inherits from**: AIProvider

**Methods:**

- `def name(self) -> str`
- `def generate(self, model: str, prompt: str, system_prompt: Optional[str]) -> str`
- `def stream(self, model: str, prompt: str, system_prompt: Optional[str]) -> Iterator[str]`
- `def embeddings(self, model: str, text: str) -> List[float]`
- `def health(self) -> bool`
- `def capabilities(self) -> ProviderCapabilities`

### class `OpenAIProvider`
- **Inherits from**: AIProvider

**Methods:**

- `def __init__(self, api_key: Optional[str], timeout: int) -> None`
- `def name(self) -> str`
- `def generate(self, model: str, prompt: str, system_prompt: Optional[str]) -> str`
- `def stream(self, model: str, prompt: str, system_prompt: Optional[str]) -> Iterator[str]`
- `def embeddings(self, model: str, text: str) -> List[float]`
- `def health(self) -> bool`
- `def capabilities(self) -> ProviderCapabilities`

### class `ClaudeProvider`
- **Inherits from**: AIProvider

**Methods:**

- `def __init__(self, api_key: Optional[str], timeout: int) -> None`
- `def name(self) -> str`
- `def generate(self, model: str, prompt: str, system_prompt: Optional[str]) -> str`
- `def stream(self, model: str, prompt: str, system_prompt: Optional[str]) -> Iterator[str]`
- `def embeddings(self, model: str, text: str) -> List[float]`
- `def health(self) -> bool`
- `def capabilities(self) -> ProviderCapabilities`

### class `GeminiProvider`
- **Inherits from**: AIProvider

**Methods:**

- `def __init__(self, api_key: Optional[str], timeout: int) -> None`
- `def name(self) -> str`
- `def generate(self, model: str, prompt: str, system_prompt: Optional[str]) -> str`
- `def stream(self, model: str, prompt: str, system_prompt: Optional[str]) -> Iterator[str]`
- `def embeddings(self, model: str, text: str) -> List[float]`
- `def health(self) -> bool`
- `def capabilities(self) -> ProviderCapabilities`

## Module: core/src/aios/bootstrap_modules/services.py

### def `bootstrap_services`
- `def bootstrap_services(registry, config_path: Path, config, event_bus, infra_ctx: dict, workspace_repo_ctx: dict, memory_ctx: dict, command_registry) -> dict`
> Wires, initializes, and registers core local and domain services.

## Module: core/src/aios/bootstrap_modules/kernel.py

### def `bootstrap_kernel_instance`
- `def bootstrap_kernel_instance(config_path: Path, registry, runtime_service) -> Kernel`
> Constructs the Kernel and links the runtime service.

## Module: core/src/aios/bootstrap_modules/memory.py

### def `bootstrap_memory`
- `def bootstrap_memory(registry, config_path: Path, infra_ctx: dict, event_bus) -> dict`
> Wires, initializes, and registers memory repositories, embeddings and search systems.

## Module: core/src/aios/bootstrap_modules/events.py

### def `bootstrap_events`
- `def bootstrap_events(registry) -> LocalEventBus`
> Constructs, registers, and returns the Event Bus.

## Module: core/src/aios/bootstrap_modules/infrastructure.py

### def `bootstrap_infrastructure`
- `def bootstrap_infrastructure(registry, config_path: Path) -> dict`
> Wires, initializes and registers foundation infrastructure components.

## Module: core/src/aios/bootstrap_modules/agents.py

### def `bootstrap_agents`
- `def bootstrap_agents(registry, event_bus, memory_service, context_service, tool_service, model_service, github_service, career_os, daily_os, orchestrator_service) -> dict`
> Wires and registers agents, runtime services, and mission engine.

## Module: core/src/aios/bootstrap_modules/providers.py

### def `bootstrap_providers`
- `def bootstrap_providers(registry, embedding_service) -> dict`
> Constructs, initializes, and registers embedding providers into embedding_service.

## Module: core/src/aios/bootstrap_modules/cli.py

### def `bootstrap_cli`
- `def bootstrap_cli(registry) -> CommandRegistry`
> Constructs, initializes, and registers CLI components.

## Module: core/src/aios/bootstrap_modules/workspace.py

### def `bootstrap_workspace_repos_and_persistence`
- `def bootstrap_workspace_repos_and_persistence(registry, infra_ctx: dict) -> dict`
> Constructs, initializes, and registers SQL workspace repositories and persistence service.

### def `bootstrap_workspace_intelligence_services`
- `def bootstrap_workspace_intelligence_services(registry, project_intelligence, memory_service, knowledge_hub, model_service) -> dict`
> Wires and registers higher-level workspace intelligence services.

## Module: core/src/aios/n8n/service.py

### class `N8NConfigurationService`
- **Inherits from**: DIInitializeMixin

> Manages connection configuration preferences loaded from Engineering Profiles.

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`

### class `N8NSessionManager`
- **Inherits from**: DIInitializeMixin

> Manages session cookie login, renewal, and validation against self-hosted n8n.

**Methods:**

- `def __init__(self, config_service: N8NConfigurationService) -> None`
- `def login(self) -> bool`
- `def get_auth_headers(self) -> Dict[str, str]`
- `def renew_session(self) -> bool`
- `def is_session_expired(self) -> bool`

### class `N8NAuthenticationManager`
- **Inherits from**: DIInitializeMixin

> Generates credentials headers and runs diagnostic auth checks.

**Methods:**

- `def __init__(self, config_service: N8NConfigurationService, session_manager: Optional[N8NSessionManager]) -> None`
- `def get_auth_headers(self) -> Dict[str, str]`
- `def validate_credentials(self) -> Dict[str, Any]`

### class `N8NConnectionManager`
- **Inherits from**: DIInitializeMixin

> Constructs configured HTTP clients.

**Methods:**

- `def __init__(self, config_service: N8NConfigurationService, auth_manager: N8NAuthenticationManager) -> None`
- `def get_client(self) -> httpx.Client`

### class `N8NClient`
- **Inherits from**: DIInitializeMixin

> Executes HTTP REST calls with linear retries and connection error mappings.

**Methods:**

- `def __init__(self, connection_manager: N8NConnectionManager, session_manager: Optional[N8NSessionManager]) -> None`
- `def request(self, method: str, url: str) -> httpx.Response`

### class `N8NWorkflowManager`
- **Inherits from**: DIInitializeMixin

> Manages workflow creation, deletion, JSON validations, and state updates.

**Methods:**

- `def __init__(self, client: N8NClient) -> None`
- `def list_workflows(self) -> List[Dict[str, Any]]`
- `def get_workflow(self, workflow_id: str) -> Dict[str, Any]`
- `def upload_workflow(self, name: str, nodes: List[Dict[str, Any]], connections: Dict[str, Any], settings: Optional[Dict[str, Any]]) -> Dict[str, Any]`
- `def update_workflow(self, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]`
- `def delete_workflow(self, workflow_id: str) -> bool`
- `def activate_workflow(self, workflow_id: str) -> bool`
- `def deactivate_workflow(self, workflow_id: str) -> bool`
- `def export_workflow(self, workflow_id: str) -> Dict[str, Any]`
- `def import_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]`
- `def validate_workflow(self, workflow_json: Dict[str, Any]) -> List[str]`

### class `N8NExecutionManager`
- **Inherits from**: DIInitializeMixin

> Handles workflow executions and execution history polling.

**Methods:**

- `def __init__(self, client: N8NClient) -> None`
- `def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]`
- `def list_executions(self, workflow_id: Optional[str]) -> List[Dict[str, Any]]`
- `def get_execution(self, execution_id: str) -> Dict[str, Any]`
- `def delete_execution(self, execution_id: str) -> bool`
- `def get_execution_logs(self, execution_id: str) -> Dict[str, Any]`
- `def retry_execution(self, execution_id: str) -> Dict[str, Any]`
- `def cancel_execution(self, execution_id: str) -> bool`

### class `N8NCredentialManager`
- **Inherits from**: DIInitializeMixin

> Indexes references to external credential vaults.

**Methods:**

- `def __init__(self, client: N8NClient) -> None`
- `def create_credential(self, name: str, type_name: str, data: Dict[str, Any]) -> Dict[str, Any]`

### class `N8NWorkspaceManager`
- **Inherits from**: DIInitializeMixin

> Maps workflows ownership to specific workspaces.

**Methods:**

- `def __init__(self) -> None`
- `def map_workflow_to_workspace(self, workflow_id: str, workspace_id: str) -> None`
- `def get_workspace_for_workflow(self, workflow_id: str) -> Optional[str]`

### class `N8NVersionDetector`
- **Inherits from**: DIInitializeMixin

> Detects n8n server version and compatibility properties.

**Methods:**

- `def __init__(self, client: N8NClient) -> None`
- `def detect_version(self) -> str`

### class `N8NCapabilityDetector`
- **Inherits from**: DIInitializeMixin

> Probes the running n8n server to discover supported API features and endpoints.

**Methods:**

- `def __init__(self, client: Optional[N8NClient]) -> None`
- `def discover_capabilities(self) -> List[str]`
- `def get_capabilities(self) -> List[str]`

### class `N8NHealthMonitor`
- **Inherits from**: DIInitializeMixin

> Tracks latency averages, P95 metrics, and authentication statuses.

**Methods:**

- `def __init__(self, client: N8NClient, auth_manager: N8NAuthenticationManager, workflow_manager: N8NWorkflowManager, execution_manager: Optional[N8NExecutionManager], version_detector: Optional[N8NVersionDetector], capability_detector: Optional[N8NCapabilityDetector]) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `N8NTelemetryCollector`
- **Inherits from**: DIInitializeMixin

> Collects average runtimes, failure rates, and execution counts.

**Methods:**

- `def __init__(self, health_monitor: N8NHealthMonitor) -> None`
- `def collect_telemetry(self) -> Dict[str, Any]`

### class `N8NEventMonitor`
- **Inherits from**: DIInitializeMixin

> Records real-time workflow events.

**Methods:**

- `def __init__(self) -> None`
- `def record_event(self, event_type: str, details: Dict[str, Any]) -> None`

### class `N8NValidator`
- **Inherits from**: DIInitializeMixin

> Validates configuration profile URL patterns.

**Methods:**

- `def validate_profile(self, url: str, timeout: int) -> List[str]`

### class `N8NDiagnostics`
- **Inherits from**: DIInitializeMixin

> Diagnoses connection and credential status with actionable remediation steps.

**Methods:**

- `def __init__(self, config_service_or_auth: Any, auth_manager: Optional[N8NAuthenticationManager], session_manager: Optional[N8NSessionManager]) -> None`
- `def run_diagnostics(self) -> Dict[str, Any]`

### class `N8NReportGenerator`
- **Inherits from**: DIInitializeMixin

> Generates markdown reports ONLY inside the workspace docs/n8n/ folder.

**Methods:**

- `def __init__(self, workspace_root: str, health_monitor: N8NHealthMonitor, diagnostics: Optional[N8NDiagnostics]) -> None`
- `def generate_reports(self) -> None`

## Module: core/src/aios/brain/planner.py

### class `BrainPlanner`

**Methods:**

- `def __init__(self, skill_selector: SkillSelector, model_service: ModelService) -> None`
- `def plan(self, objective: str, context: Optional[BrainContext], capability: Optional[str]) -> Workflow`

## Module: core/src/aios/brain/context_manager.py

### class `ContextManager`

**Methods:**

- `def __init__(self, context_service: ContextService, memory_service: MemoryService, project_intel: Optional[ProjectIntelligenceService], dev_workspace: Optional[DeveloperWorkspaceService], personal_service: Optional[PersonalService]) -> None`
- `def assemble_context(self, objective: str) -> BrainContext`

## Module: core/src/aios/brain/models.py

### class `BrainObjective`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `SkillSelection`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ProviderSelection`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `BrainContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `WorkflowStep`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Workflow`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `BrainResponse`
- **Decorators**: `dataclass`
- **Type**: Dataclass

## Module: core/src/aios/brain/brain.py

### class `Brain`

**Methods:**

- `def __init__(self, kernel: Kernel, command_registry: CommandRegistry) -> None`
- `def execute(self, query: str, capability: Optional[str]) -> BrainResponse`
- `def explain(self, query: str, capability: Optional[str]) -> Dict[str, Any]`
  * Simulates planning and routing decisions without executing them.

## Module: core/src/aios/brain/workflow.py

### class `WorkflowExecutor`

**Methods:**

- `def __init__(self, kernel: Any, command_registry: CommandRegistry) -> None`
- `def execute(self, workflow: Workflow) -> bool`
- `def _execute_via_action_engine(self, step: WorkflowStep) -> bool`
- `def _execute_via_command_registry(self, step: WorkflowStep) -> bool`

### def `group_steps_into_levels`
- `def group_steps_into_levels(steps: List[WorkflowStep]) -> List[List[WorkflowStep]]`
> Validates dependencies, checks for circular paths, and groups steps
into execution levels based on their dependency graphs.

### def `visualize_workflow_graph`
- `def visualize_workflow_graph(steps: List[WorkflowStep]) -> str`
> Returns an ASCII graph visualization of the workflow graph levels.

## Module: core/src/aios/brain/skill_selector.py

### class `SkillSelector`

**Methods:**

- `def __init__(self, skill_registry: SkillRegistry) -> None`
- `def select_skills(self, objective: str, capability: Optional[str]) -> List[SkillSelection]`

## Module: core/src/aios/brain/provider_selector.py

### class `ProviderSelector`

**Methods:**

- `def __init__(self, model_service: ModelService) -> None`
- `def select_provider(self, objective: str, context: Optional[BrainContext]) -> ProviderSelection`

## Module: core/src/aios/docgen/ops_main.py

### def `main`
- `def main() -> int`
> CLI entry point for operations guide generator.

## Module: core/src/aios/docgen/models.py

### class `GenerationStatus`
- **Inherits from**: str, Enum
- **Type**: Enum

> Overall outcome of a documentation generation run.

### class `ComponentKind`
- **Inherits from**: str, Enum
- **Type**: Enum

> Category of a discovered component.

### class `ServiceEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a discovered service interface and its concrete implementation.

### class `RepositoryEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a discovered repository class (abstract or concrete).

### class `SkillEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a discovered skill loaded from skill.toml.

### class `ProviderEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a discovered AI provider.

### class `RuntimeComponentEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a discovered runtime component (concrete class registered in bootstrap).

### class `DbModelEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a data model / dataclass / enum discovered in source code.

### class `DIBinding`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A single DI registration: interface → concrete class.

### class `GeneratedFile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Metadata about one generated documentation file.

### class `GenerationResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Summary of a complete documentation generation run.

**Methods:**

- `def total_files(self) -> int`
- `def success(self) -> bool`

## Module: core/src/aios/docgen/cert_engine.py

### class `CertificationEngine`

> Documentation Certification Engine for the Personal AI OS.

Runs all validation analyzers and produces a certification report suite
under docs/certification/.

Design Principles:
- Idempotent: re-running produces identical output given unchanged docs.
- Non-destructive: writes only inside docs/certification/; all other docs untouched.
- No side-effects on the running system: reads source code and docs only.
- Deterministic ordering: all lists are sorted.

**Methods:**

- `def __init__(self, project_root: Optional[Path]) -> None`
- `def run(self) -> CertificationResult`
  * Execute a full documentation certification run.

Returns a CertificationResult summarising all findings,
scores, and generated report files.
- `def _compute_scores(self, result: CertificationResult) -> QualityScore`
  * Build a QualityScore from the raw findings and analyzer outputs.
Preserves coverage score already computed.
- `def output_dir(self) -> Path`
  * Return the configured output directory (docs/certification/).

## Module: core/src/aios/docgen/refgen_models.py

### class `ParameterInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a method parameter with type information.

### class `MethodSignature`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Detailed method signature with parameters, return type, and exceptions.

### class `LifecycleMethod`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Lifecycle method (init_service, cleanup, etc.) with documentation.

### class `ServiceInterface`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Enhanced service interface with full API documentation.

### class `InterfaceImplementationPair`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Pairs an interface with its concrete implementation.

## Module: core/src/aios/docgen/diagram_models.py

### class `ServiceNode`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a service node in the dependency graph.

### class `DIBinding`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a dependency injection binding.

### class `BootstrapStep`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a step in the bootstrap sequence.

### class `LifecyclePhase`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a lifecycle phase.

### class `PersistenceLayer`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a persistence layer (SQLite, PostgreSQL, Redis, Qdrant).

### class `ArchitecturalComponent`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a high-level architectural component.

### class `DiagramGenerationResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Result of diagram generation run.

## Module: core/src/aios/docgen/ops_engine.py

### class `OperationsGeneratorEngine`

> Orchestrates the analysis and generation of operational documentation.

Analyzes deployment requirements, configuration parameters, startup sequences,
OmniRoute provider configuration, and operational procedures to generate
comprehensive operations guides under docs/operations/.

**Methods:**

- `def __init__(self, project_root: Optional[Path]) -> None`
  * Initialize the operations generator engine.

Args:
    project_root: Root directory of the AIOS project. Defaults to cwd.
- `def run(self) -> OperationsGenerationResult`
  * Run the full operations guide generation pipeline.

Returns:
    OperationsGenerationResult with status, timing, and file list.
- `def _analyze_deployments(self)`
  * Analyze service deployment requirements.
- `def _analyze_configuration(self)`
  * Analyze configuration parameters.
- `def _analyze_startup(self)`
  * Analyze startup sequence.
- `def _analyze_backups(self)`
  * Analyze backup requirements.
- `def _analyze_monitoring(self)`
  * Analyze monitoring metrics.
- `def _analyze_troubleshooting(self)`
  * Analyze troubleshooting scenarios.
- `def _analyze_omniroute(self)`
  * Analyze OmniRoute provider configuration.
- `def _render_all(self) -> dict[str, str]`
  * Render all operational guide files.

## Module: core/src/aios/docgen/cert_main.py

### def `main`
- `def main() -> int`
> CLI entry point for documentation certification.

## Module: core/src/aios/docgen/renderers.py

### def `_header`
- `def _header(title: str, description: str) -> str`

### def `_toc`
- `def _toc(items: List[str]) -> str`
> Render a simple Table of Contents from section headings.

### def `_badge`
- `def _badge(label: str, value: str, color: str) -> str`

### def `render_service_catalog`
- `def render_service_catalog(services: List[ServiceEntry]) -> str`
> Produce a Markdown Service Catalog document.

### def `render_repository_catalog`
- `def render_repository_catalog(repositories: List[RepositoryEntry]) -> str`
> Produce a Markdown Repository Catalog document.

### def `render_skill_catalog`
- `def render_skill_catalog(skills: List[SkillEntry]) -> str`
> Produce a Markdown Skill Catalog document.

### def `render_provider_catalog`
- `def render_provider_catalog(providers: List[ProviderEntry]) -> str`
> Produce a Markdown Provider Catalog document.

### def `render_runtime_catalog`
- `def render_runtime_catalog(components: List[RuntimeComponentEntry]) -> str`
> Produce a Markdown Runtime Component Catalog.

### def `render_dependency_graph`
- `def render_dependency_graph(bindings: List[DIBinding]) -> str`
> Produce a Mermaid dependency graph document.

### def `render_db_model_catalog`
- `def render_db_model_catalog(models: List[DbModelEntry]) -> str`
> Produce a Markdown Database Model Catalog.

### def `render_index`
- `def render_index() -> str`
> Produce a top-level index / README for docs/generated/.

## Module: core/src/aios/docgen/diagram_main.py

### def `main`
- `def main() -> int`
> CLI entry point for diagram generator.

## Module: core/src/aios/docgen/refgen_main.py

### def `main`
- `def main() -> int`
> CLI entry point for reference generator.

## Module: core/src/aios/docgen/ops_renderers.py

### def `_banner`
- `def _banner() -> str`
> Generate the auto-generated warning banner.

### def `render_readme_index`
- `def render_readme_index(guide_count: int) -> str`
> Render the README index for operations documentation.

### def `render_local_setup`
- `def render_local_setup(deployments: List[ServiceDeployment]) -> str`
> Render the local development setup guide.

### def `render_configuration`
- `def render_configuration(configs: List[ConfigurationItem], omniroute_providers: List[OmniRouteProvider]) -> str`
> Render the configuration guide.

### def `render_deployment`
- `def render_deployment(deployments: List[ServiceDeployment]) -> str`
> Render the deployment guide.

### def `render_startup`
- `def render_startup(steps: List[StartupStep]) -> str`
> Render the startup sequence guide.

### def `render_monitoring`
- `def render_monitoring(metrics: List[MonitoringMetric]) -> str`
> Render the monitoring guide.

### def `render_backup_restore`
- `def render_backup_restore(targets: List[BackupTarget]) -> str`
> Render the backup and restore guide.

### def `render_troubleshooting`
- `def render_troubleshooting(entries: List[TroubleshootingEntry]) -> str`
> Render the troubleshooting guide.

### def `render_production_checklist`
- `def render_production_checklist() -> str`
> Render the production deployment checklist.

## Module: core/src/aios/docgen/diagram_renderers.py

### def `_banner`
- `def _banner() -> str`
> Generate the auto-generated warning banner.

### def `render_overall_architecture`
- `def render_overall_architecture(components: List[ArchitecturalComponent]) -> str`
> Render the overall AI OS architecture diagram.

### def `render_service_dependency_graph`
- `def render_service_dependency_graph(services: List[ServiceNode]) -> str`
> Render the service dependency graph.

### def `render_di_graph`
- `def render_di_graph(bindings: List[DIBinding]) -> str`
> Render the dependency injection bindings graph.

### def `render_lifecycle_diagram`
- `def render_lifecycle_diagram(phases: List[LifecyclePhase]) -> str`
> Render the runtime lifecycle diagram.

### def `render_bootstrap_sequence`
- `def render_bootstrap_sequence(steps: List[BootstrapStep]) -> str`
> Render the bootstrap sequence diagram.

### def `render_semantic_memory_pipeline`
- `def render_semantic_memory_pipeline() -> str`
> Render the semantic memory pipeline diagram.

### def `render_hybrid_retrieval_pipeline`
- `def render_hybrid_retrieval_pipeline() -> str`
> Render the hybrid retrieval pipeline diagram.

### def `render_persistence_architecture`
- `def render_persistence_architecture(layers: List[PersistenceLayer]) -> str`
> Render the persistence architecture diagram.

### def `render_omniroute_architecture`
- `def render_omniroute_architecture() -> str`
> Render the OmniRoute model selection architecture.

### def `render_agent_interaction_flow`
- `def render_agent_interaction_flow() -> str`
> Render the agent interaction and coordination flow.

### def `render_diagrams_index`
- `def render_diagrams_index(diagram_count: int) -> str`
> Render the README index for diagram documentation.

## Module: core/src/aios/docgen/cert_analyzers.py

### class `MarkdownAnalyzer`

> Validates Markdown formatting across all documentation files.

Checks:
- Each file has exactly one H1 heading
- Heading hierarchy is not skipped (no h1 → h3 without h2)
- No trailing whitespace on headings
- No empty headings
- README navigation links resolve

**Methods:**

- `def analyze(self, docs_root: Path) -> List[Finding]`

### class `MermaidAnalyzer`

> Validates Mermaid diagram syntax in all Markdown documentation files.

Checks:
- All ```mermaid blocks start with a recognised diagram type
- Blocks are not empty
- Basic node definition syntax (no unclosed brackets)

**Methods:**

- `def analyze(self, docs_root: Path) -> List[Finding]`
- `def _check_file(self, rel: str, content: str) -> List[Finding]`
- `def _validate_block(self, rel: str, start_line: int, block: List[str]) -> List[Finding]`

### class `CrossLinkAnalyzer`

> Validates all internal Markdown cross-references.

Checks:
- Relative file links exist on the filesystem
- Anchor links (#section) point to a heading that exists in the target file

Skips:
- file:// absolute-path URIs (IDE deep-links in handwritten docs)
- Legacy numbered doc references (00_*.md) from handwritten docs
- Source-code path examples embedded in documentation prose

**Methods:**

- `def analyze(self, docs_root: Path) -> Tuple[List[BrokenLink], List[Finding]]`
- `def _extract_anchors(content: str) -> Set[str]`
  * GitHub-style anchor generation.

GitHub's algorithm (as of 2024):
  1. Lowercase the heading text
  2. Strip all characters that are NOT alphanumeric, spaces, or hyphens
     (this removes punctuation like &, /, ., etc.)
  3. Replace each remaining space character with a hyphen
     (spaces are replaced individually, NOT collapsed — so 'API & Service'
      becomes 'api  service' after step 2, then 'api--service' after step 3)
  4. Strip leading/trailing hyphens

We generate BOTH the collapsed variant (step 3 with ``\s+`` collapse) AND the
per-space variant so that links using either style are accepted.

### class `OrphanAnalyzer`

> Detects documentation files that are not reachable from any other document.

A file is an orphan if no other Markdown file in the docs tree contains
a link to it (by relative path or basename).

**Methods:**

- `def analyze(self, docs_root: Path) -> List[OrphanDocument]`

### class `CompletenessAnalyzer`

> Validates that all required documentation files and sections are present.

Checks:
- Required files from REQUIRED_FILES exist
- docs/README.md contains all required navigation sections
- Each ops guide contains its required sections

**Methods:**

- `def analyze(self, docs_root: Path, project_root: Path) -> List[Finding]`

### class `DuplicateSectionAnalyzer`

> Detects duplicate headings within a single document.

A heading is considered a duplicate if it appears more than once
at the same nesting level (case-insensitive).

**Methods:**

- `def analyze(self, docs_root: Path) -> List[DuplicateSection]`

### class `CoverageAnalyzer`

> Measures documentation coverage against the source codebase.

Counts:
- Python modules under core/src/aios/
- Modules that appear in at least one generated doc file
- Public symbols (functions / classes) vs documented symbols

**Methods:**

- `def analyze(self, project_root: Path) -> CoverageScore`

### def `_read_text`
- `def _read_text(path: Path) -> str`
> Read a file, returning '' on any error.

### def `_md_files`
- `def _md_files(docs_root: Path, skip_dirs: Set[str]) -> List[Path]`
> Return all .md files under docs_root, skipping excluded directories.

### def `_extract_headings`
- `def _extract_headings(content: str) -> List[Tuple[int, str, int]]`
> Return list of (level, heading_text, line_number) from Markdown content.
Only ATX headings (# Heading) are considered.
Headings inside fenced code blocks (``` or ~~~) are skipped.

### def `_extract_md_links`
- `def _extract_md_links(content: str) -> List[Tuple[str, str, int]]`
> Return list of (link_text, link_target, line_number) for all Markdown links.
Skips http/https/mailto/file:/// absolute-path links.
Skips links inside fenced code blocks (``` or ~~~).
Only relative file paths and anchor-only links are returned.

### def `_resolve_link`
- `def _resolve_link(source: Path, target: str, docs_root: Path) -> Path`
> Resolve a relative Markdown link target relative to its source file.
Strips anchor fragments (#section).

## Module: core/src/aios/docgen/engine.py

### class `DocGeneratorEngine`

> Documentation Generation Engine for the Personal AI OS.

Discovers components through static AST analysis (no runtime imports)
and produces Markdown documentation into docs/generated/.

Design Principles:
- Idempotent: re-running produces identical output given unchanged source.
- Non-destructive: only writes inside docs/generated/; handwritten docs untouched.
- No side-effects on the running system: purely reads source code.
- Deterministic ordering: all lists are sorted alphabetically.

**Methods:**

- `def __init__(self, project_root: Optional[Path]) -> None`
- `def run(self) -> GenerationResult`
  * Execute a full documentation generation run.

Returns a GenerationResult summarising what was produced and any
warnings or errors encountered.
- `def output_dir(self) -> Path`
  * Return the configured output directory (docs/generated/).

## Module: core/src/aios/docgen/discoverers.py

### class `ServiceDiscoverer`

> Discovers service interfaces by scanning for classes that inherit from
ServiceLifecycle and end with 'Service', 'Engine', or 'Resolver'.

Pairs each interface with its implementation (_impl.py counterpart).

**Methods:**

- `def __init__(self, services_root: Path, src_root: Path) -> None`
- `def discover(self) -> List[ServiceEntry]`
- `def _guess_interface(impl_name: str) -> Optional[str]`
  * Strip 'Local', 'Impl', etc. to guess the interface name.

### class `RepositoryDiscoverer`

> Discovers repository abstractions from persistence.py and their
concrete implementations from persistence_impl*.py.

**Methods:**

- `def __init__(self, services_root: Path, src_root: Path) -> None`
- `def discover(self) -> List[RepositoryEntry]`

### class `SkillDiscoverer`

> Discovers skills by scanning directories that contain skill.toml.

**Methods:**

- `def __init__(self, skills_root: Path) -> None`
- `def discover(self) -> List[SkillEntry]`
- `def _load_toml(toml_path: Path) -> Optional[SkillEntry]`
- `def _fallback_parse(toml_path: Path) -> Dict[str, Any]`
  * Minimal key=value TOML parser (no sections).

### class `ProviderDiscoverer`

> Discovers AI providers from the provider registry source code using
AST analysis of register_provider() calls.

**Methods:**

- `def __init__(self, providers_root: Path, src_root: Path) -> None`
- `def discover(self) -> List[ProviderEntry]`
- `def _extract_provider(call_node: ast.Call) -> Optional[ProviderEntry]`
  * Extract ProviderEntry from a ModelInfo(...) AST node.

### class `RuntimeComponentDiscoverer`

> Discovers concrete runtime components by scanning all *_impl.py files under
the services directory (where Local*, PostgreSQL*, Redis*, *Impl classes live).

These are the classes that are wired into the kernel via the Composition Root.

**Methods:**

- `def __init__(self, services_root: Path, src_root: Path) -> None`
- `def discover(self) -> List[RuntimeComponentEntry]`

### class `DbModelDiscoverer`

> Discovers dataclasses, Enums, and plain model classes in the services/
package by scanning for @dataclass decorators, Enum subclasses, and
classes whose names suggest a data model.

**Methods:**

- `def __init__(self, services_root: Path, src_root: Path) -> None`
- `def discover(self) -> List[DbModelEntry]`
- `def _extract_fields(node: ast.ClassDef, kind: str) -> List[str]`
  * Extract field names from a dataclass or enum body.

### class `DIBindingDiscoverer`

> Discovers DI registrations by scanning bootstrap.py for
registry.register(InterfaceType, concrete_instance) calls.

**Methods:**

- `def __init__(self, bootstrap_file: Path) -> None`
- `def discover(self) -> List[DIBinding]`
- `def _name_from_expr(expr: ast.expr) -> Optional[str]`

### def `_read_source`
- `def _read_source(path: Path) -> Optional[str]`
> Return file contents or None on decode error.

### def `_parse_module`
- `def _parse_module(path: Path) -> Optional[ast.Module]`

### def `_get_docstring`
- `def _get_docstring(node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef) -> Optional[str]`
> Extract the first docstring from a class or function node.

### def `_base_names`
- `def _base_names(node: ast.ClassDef) -> List[str]`
> Return the simple names of a class's bases.

### def `_method_names`
- `def _method_names(node: ast.ClassDef) -> List[str]`
> Return all method names defined directly on the class.

### def `_python_files`
- `def _python_files(root: Path, exclude: Optional[List[str]]) -> Iterator[Path]`
> Yield all .py files under *root* that are not in excluded dirs.

### def `_module_name`
- `def _module_name(file_path: Path, src_root: Path) -> str`
> Convert a file path to a dotted Python module name.

## Module: core/src/aios/docgen/cert_models.py

### class `Severity`
- **Inherits from**: str, Enum
- **Type**: Enum

> Severity level of a certification finding.

### class `CertificationStatus`
- **Inherits from**: str, Enum
- **Type**: Enum

> Overall certification outcome.

### class `Finding`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A single validation finding (error, warning, or pass).

### class `BrokenLink`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A broken internal or cross-reference link.

### class `OrphanDocument`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A document that is not referenced from any other document.

### class `DuplicateSection`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A heading that appears more than once within a single document.

### class `CoverageScore`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Documentation Coverage metrics.

**Methods:**

- `def module_coverage(self) -> float`
- `def symbol_coverage(self) -> float`
- `def score(self) -> float`

### class `CrossReferenceScore`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Cross-reference Coverage metrics.

**Methods:**

- `def link_validity_rate(self) -> float`
- `def orphan_rate(self) -> float`
- `def score(self) -> float`

### class `CompletenessScore`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Documentation Completeness metrics.

**Methods:**

- `def section_completeness(self) -> float`
- `def file_completeness(self) -> float`
- `def score(self) -> float`

### class `ConsistencyScore`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Documentation Consistency metrics.

**Methods:**

- `def heading_consistency_rate(self) -> float`
- `def score(self) -> float`
  * Consistency score (0–100).

Uses capped proportional deductions so that structural duplicates in
large auto-generated catalogs (e.g. repeated 'Parameters' headings in
api_reference.md) do not bottom out the score.

Deductions:
  - Each markdown_error:      up to 5 pts (capped at 25 pts total)
  - Each mermaid_error:       up to 5 pts (capped at 25 pts total)
  - Each formatting_warning:  up to 1 pt  (capped at 15 pts total)
  - Duplicate sections:       up to 5 pts per unique file (capped at 20 pts)

### class `QualityScore`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Overall documentation quality score.

**Methods:**

- `def health_score(self) -> float`
  * Weighted composite documentation health score (0–100).
- `def grade(self) -> str`
- `def status(self) -> CertificationStatus`

### class `CertificationResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Complete result of a documentation certification run.

**Methods:**

- `def error_count(self) -> int`
- `def warning_count(self) -> int`
- `def pass_count(self) -> int`

## Module: core/src/aios/docgen/ops_models.py

### class `ServiceDeployment`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents deployment requirements for a service.

### class `ConfigurationItem`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a configuration parameter.

### class `StartupStep`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a step in the startup sequence.

### class `OmniRouteProvider`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents an OmniRoute AI provider.

### class `BackupTarget`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a backup target.

### class `MonitoringMetric`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a monitoring metric.

### class `TroubleshootingEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a troubleshooting scenario.

### class `OperationsGenerationResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Result of operations guide generation.

## Module: core/src/aios/docgen/refgen_renderers.py

### def `_banner`
- `def _banner() -> str`
> Generate the auto-generated warning banner.

### def `_format_parameter`
- `def _format_parameter(param: ParameterInfo) -> str`
> Format a parameter as a string.

### def `_format_signature`
- `def _format_signature(sig: MethodSignature) -> str`
> Format a method signature as a string.

### def `render_services_reference`
- `def render_services_reference(services: List[ServiceInterface]) -> str`
> Render the services.md reference with full API documentation.

### def `render_interfaces_reference`
- `def render_interfaces_reference(services: List[ServiceInterface]) -> str`
> Render the interfaces.md reference showing interface-to-implementation mappings.

### def `render_lifecycle_reference`
- `def render_lifecycle_reference(services: List[ServiceInterface]) -> str`
> Render the lifecycle.md reference documenting lifecycle methods.

### def `render_dependency_injection_reference`
- `def render_dependency_injection_reference(services: List[ServiceInterface]) -> str`
> Render the dependency_injection.md reference documenting DI bindings.

### def `render_api_reference`
- `def render_api_reference(services: List[ServiceInterface]) -> str`
> Render the api_reference.md complete API reference.

### def `render_reference_index`
- `def render_reference_index(services: List[ServiceInterface]) -> str`
> Render the README.md index for the reference documentation.

## Module: core/src/aios/docgen/ops_analyzers.py

### class `ServiceDeploymentAnalyzer`

> Analyzes service deployment requirements.

**Methods:**

- `def analyze(self, project_root: Path) -> List[ServiceDeployment]`
  * Extract service deployment requirements.

### class `ConfigurationAnalyzer`

> Analyzes configuration parameters from the actual implementation.

**Methods:**

- `def analyze(self, project_root: Path) -> List[ConfigurationItem]`
  * Extract configuration parameters aligned with implementation.

### class `StartupSequenceAnalyzer`

> Analyzes service startup order from the bootstrap_kernel composition root.

The bootstrap sequence is derived from:
    core/src/aios/bootstrap_modules/bootstrap_kernel.py

Order:
  1. PostgreSQL   — required by PersistenceBootstrapper (step 3 of bootstrap)
  2. Redis        — required by RedisRuntimeService (step 4 of bootstrap)
  3. Qdrant       — required by QdrantPlatform (step 5 of bootstrap)
  4. DB Migration — run once PostgreSQL is ready (PersistenceBootstrapper.on_ready)
  5. AIOS Core    — starts after all external services (step 6)
  6. n8n          — optional; registered as step 8 of bootstrap

**Methods:**

- `def analyze(self) -> List[StartupStep]`
  * Extract service startup sequence aligned with bootstrap_kernel.py.

### class `OmniRouteAnalyzer`

> Analyzes OmniRoute provider configuration from the providers registry.

**Methods:**

- `def analyze(self) -> List[OmniRouteProvider]`
  * Extract OmniRoute provider configuration.

Derived from:
  - core/src/aios/providers/registry.py
  - core/src/aios/services/model_impl.py
  - config/config.toml

### class `BackupAnalyzer`

> Analyzes backup requirements from the data persistence architecture.

**Methods:**

- `def analyze(self) -> List[BackupTarget]`
  * Extract backup targets.

### class `MonitoringAnalyzer`

> Analyzes monitoring requirements.

**Methods:**

- `def analyze(self) -> List[MonitoringMetric]`
  * Extract monitoring metrics.

### class `TroubleshootingAnalyzer`

> Analyzes common troubleshooting scenarios from known failure modes.

**Methods:**

- `def analyze(self) -> List[TroubleshootingEntry]`
  * Extract troubleshooting scenarios.

## Module: core/src/aios/docgen/__main__.py

### def `main`
- `def main() -> int`

## Module: core/src/aios/docgen/diagram_analyzers.py

### class `ServiceDependencyAnalyzer`

> Analyzes service dependencies for dependency graph generation.

**Methods:**

- `def __init__(self, services_root: Path, src_root: Path)`
- `def analyze(self) -> List[ServiceNode]`
  * Extract service nodes with their dependencies.
- `def _extract_dependencies(self, file_path: str) -> List[str]`
  * Extract service dependencies from __init__ parameters.
- `def _extract_type_name(annotation: ast.expr) -> Optional[str]`
  * Extract type name from annotation.

### class `BootstrapSequenceAnalyzer`

> Analyzes bootstrap sequence from bootstrap.py.

**Methods:**

- `def __init__(self, bootstrap_file: Path)`
- `def analyze(self) -> List[BootstrapStep]`
  * Extract bootstrap initialization sequence.
- `def _extract_init_calls(self, func_node: ast.FunctionDef, base_order: int) -> List[BootstrapStep]`
  * Extract initialization calls from a function.
- `def _get_call_name(call_node: ast.Call) -> Optional[str]`
  * Extract the name from a call node.

### class `LifecycleAnalyzer`

> Analyzes service lifecycle phases.

**Methods:**

- `def __init__(self, services_root: Path, src_root: Path)`
- `def analyze(self) -> List[LifecyclePhase]`
  * Extract lifecycle phases with services.

### class `PersistenceAnalyzer`

> Analyzes persistence architecture.

**Methods:**

- `def analyze(self, project_root: Path) -> List[PersistenceLayer]`
  * Extract persistence layers.
- `def _extract_repository_names(content: str) -> List[str]`
  * Extract repository class names from file content.

### class `ArchitectureComponentAnalyzer`

> Analyzes high-level architectural components.

**Methods:**

- `def analyze(self) -> List[ArchitecturalComponent]`
  * Extract high-level architectural components.

## Module: core/src/aios/docgen/diagram_engine.py

### class `DiagramGeneratorEngine`

> Orchestrates the analysis and generation of architecture diagrams.

Analyzes the codebase to extract architectural information and generates
Mermaid diagrams for visualization in docs/diagrams/.

**Methods:**

- `def __init__(self, project_root: Optional[Path]) -> None`
  * Initialize the diagram generator engine.

Args:
    project_root: Root directory of the AIOS project. Defaults to cwd.
- `def run(self) -> DiagramGenerationResult`
  * Run the full diagram generation pipeline.

Returns:
    DiagramGenerationResult with status, timing, and file list.
- `def _analyze_components(self)`
  * Analyze high-level architectural components.
- `def _analyze_services(self)`
  * Analyze service dependencies.
- `def _analyze_di_bindings(self)`
  * Analyze DI bindings.
- `def _analyze_lifecycle(self)`
  * Analyze lifecycle phases.
- `def _analyze_bootstrap(self)`
  * Analyze bootstrap sequence.
- `def _analyze_persistence(self)`
  * Analyze persistence layers.
- `def _render_all(self) -> dict[str, str]`
  * Render all diagram files.

## Module: core/src/aios/docgen/refgen_engine.py

### class `ReferenceGeneratorEngine`

> Orchestrates the discovery and generation of API & Service reference documentation.

Discovers services with detailed API information (method signatures, parameters,
return types, exceptions, lifecycle methods) and generates comprehensive reference
documentation in docs/reference/.

**Methods:**

- `def __init__(self, project_root: Optional[Path]) -> None`
  * Initialize the reference generator engine.

Args:
    project_root: Root directory of the AIOS project. Defaults to cwd.
- `def run(self) -> ReferenceGenerationResult`
  * Run the full reference generation pipeline.

Returns:
    ReferenceGenerationResult with status, timing, and file list.
- `def _discover_services(self) -> List[ServiceInterface]`
  * Discover services with enhanced API information.
- `def _render_all(self, services: List[ServiceInterface]) -> dict[str, str]`
  * Render all reference documentation files.

### class `ReferenceGenerationResult`

> Result of a reference generation run.

**Methods:**

- `def __init__(self) -> None`

## Module: core/src/aios/docgen/cert_renderers.py

### def `_ts`
- `def _ts(epoch: float) -> str`

### def `_status_badge`
- `def _status_badge(status: CertificationStatus) -> str`

### def `_score_bar`
- `def _score_bar(score: float, width: int) -> str`
> Render a text progress bar for a 0–100 score.

### def `_grade_emoji`
- `def _grade_emoji(grade: str) -> str`

### def `_sev_icon`
- `def _sev_icon(severity: Severity) -> str`

### def `render_certification_readme`
- `def render_certification_readme(result: 'CertificationResult') -> str`

### def `render_certification_report`
- `def render_certification_report(result: 'CertificationResult') -> str`

### def `render_completeness_report`
- `def render_completeness_report(result: 'CertificationResult') -> str`

### def `render_consistency_report`
- `def render_consistency_report(result: 'CertificationResult') -> str`

### def `render_broken_links`
- `def render_broken_links(result: 'CertificationResult') -> str`

### def `render_orphan_documents`
- `def render_orphan_documents(result: 'CertificationResult') -> str`

### def `render_quality_score`
- `def render_quality_score(result: 'CertificationResult') -> str`

## Module: core/src/aios/docgen/refgen_discoverers.py

### class `ServiceReferenceDiscoverer`

> Enhanced service discoverer that extracts detailed API information
including method signatures, parameters, return types, and exceptions.

**Methods:**

- `def __init__(self, services_root: Path, src_root: Path) -> None`
- `def discover(self) -> List[ServiceInterface]`
  * Discover services with detailed API information.
- `def _guess_interface(impl_name: str) -> Optional[str]`
  * Guess the interface name from an implementation name.

### def `_extract_type_annotation`
- `def _extract_type_annotation(node: Optional[ast.expr]) -> Optional[str]`
> Convert an AST type annotation to a string representation.

### def `_extract_default_value`
- `def _extract_default_value(node: Optional[ast.expr]) -> Optional[str]`
> Extract the default value from a parameter node.

### def `_extract_parameters`
- `def _extract_parameters(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[ParameterInfo]`
> Extract parameter information from a function node.

### def `_extract_exceptions`
- `def _extract_exceptions(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]`
> Extract exception types raised by a function.

### def `_extract_method_signature`
- `def _extract_method_signature(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> MethodSignature`
> Extract detailed method signature from a function node.

## Module: core/src/aios/skills/metadata.py

### class `SkillMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

## Module: core/src/aios/skills/registry.py

### class `SkillRegistry`

**Methods:**

- `def __init__(self) -> None`
- `def register(self, skill: BaseSkill) -> None`
- `def unregister(self, skill_id: str) -> None`
- `def get_skill(self, skill_id: str) -> Optional[BaseSkill]`
- `def list_skills(self) -> List[BaseSkill]`

## Module: core/src/aios/skills/installer.py

### class `SkillInstaller`

**Methods:**

- `def __init__(self, manager: SkillManager) -> None`
- `def install(self, source_dir: str) -> bool`

## Module: core/src/aios/skills/loader.py

### class `SkillLoader`

**Methods:**

- `def __init__(self) -> None`
- `def load_skill(self, skill_dir: Path) -> Optional[BaseSkill]`

## Module: core/src/aios/skills/manager.py

### class `SkillManager`

**Methods:**

- `def __init__(self, skills_dir: Path, registry: SkillRegistry) -> None`
- `def load_all_skills(self) -> None`
- `def register_all_commands(self, command_registry: Any, kernel: Any, conv_manager: Any) -> None`
- `def install_skill(self, source_dir: Path) -> bool`
- `def uninstall_skill(self, skill_id: str, command_registry: Any) -> bool`
- `def enable_skill(self, skill_id: str, command_registry: Any, kernel: Any, conv_manager: Any) -> bool`
- `def disable_skill(self, skill_id: str, command_registry: Any) -> bool`
- `def reload_skill(self, skill_id: str, command_registry: Any, kernel: Any, conv_manager: Any) -> bool`

## Module: core/src/aios/skills/base.py

### class `BaseSkill`

**Methods:**

- `def __init__(self, metadata: SkillMetadata, path: str) -> None`
- `def register_commands(self, registry: Any, kernel: Any, conv_manager: Any) -> None`
- `def unregister_commands(self, registry: Any) -> None`

## Module: core/src/aios/services/intent.py

### class `IntentType`
- **Inherits from**: Enum
- **Type**: Enum

### class `Intent`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Strongly typed model representing resolved user intent.

### class `IntentResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Strongly typed model representing the outcome of executing an intent.

### class `IntentResolverService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Interface for translating natural language into structured executing intents.

**Methods:**

- `def resolve(self, text: str) -> Intent`
  * Translates natural language text into a structured Intent.
- `def validate(self, intent: Intent) -> bool`
  * Validates that a resolved Intent is well-formed and executable.
- `def classify(self, text: str) -> IntentType`
  * Classifies natural language text into an IntentType.

## Module: core/src/aios/services/intent_impl.py

### class `LocalIntentResolver`
- **Inherits from**: IntentResolverService

> Rule-based implementation of IntentResolverService for the MVP.

Maps natural language phrases to structured Intents.

**Methods:**

- `def initialize(self) -> None`
- `def classify(self, text: str) -> IntentType`
  * Classifies natural language text into an IntentType based on rules.
- `def resolve(self, text: str) -> Intent`
  * Translates natural language text into a structured Intent.
- `def validate(self, intent: Intent) -> bool`
  * Validates that a resolved Intent is well-formed and executable.

## Module: core/src/aios/services/automation_impl.py

### class `LocalN8NProvider`
- **Inherits from**: N8NProvider

> Concrete provider stub for n8n platform integration.

**Methods:**

- `def provider_id(self) -> str`
- `def validate_definition(self, definition: WorkflowDefinition) -> List[str]`
- `def execute_workflow(self, definition: WorkflowDefinition, session: AutomationSession) -> AutomationResult`

### class `LocalGitHubActionsProvider`
- **Inherits from**: GitHubActionsProvider

> Concrete provider stub for GitHub Actions platform integration.

**Methods:**

- `def provider_id(self) -> str`
- `def validate_definition(self, definition: WorkflowDefinition) -> List[str]`
- `def execute_workflow(self, definition: WorkflowDefinition, session: AutomationSession) -> AutomationResult`

### class `LocalTemporalProvider`
- **Inherits from**: TemporalProvider

> Concrete provider stub for Temporal orchestrator integration.

**Methods:**

- `def provider_id(self) -> str`
- `def validate_definition(self, definition: WorkflowDefinition) -> List[str]`
- `def execute_workflow(self, definition: WorkflowDefinition, session: AutomationSession) -> AutomationResult`

### class `LocalAutomationRegistry`
- **Inherits from**: AutomationRegistry

> Concrete workflow catalog container storing workflow definitions.

**Methods:**

- `def __init__(self, registry: Optional[Any]) -> None`
- `def register_workflow(self, definition: WorkflowDefinition) -> None`
- `def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]`

### class `LocalAutomationValidator`
- **Inherits from**: AutomationValidator

> Performs topological checks (cycles, disconnected nodes, and policy validity).

**Methods:**

- `def validate_workflow(self, definition: WorkflowDefinition) -> List[str]`

### class `LocalAutomationManager`
- **Inherits from**: AutomationManager

> Instantiates automation sessions and delegates executions to provider stubs.

**Methods:**

- `def __init__(self, providers: AutomationProviderRegistry, registry: LocalAutomationRegistry) -> None`
- `def create_session(self, workflow_id: str, workspace_id: str) -> AutomationSession`
- `def execute_session(self, session: AutomationSession, provider_id: str) -> AutomationResult`

### class `LocalAutomationService`
- **Inherits from**: AutomationService

> Central conductor service managing workflows, providers registry, and workspace logging.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def register_provider(self, provider: AutomationProvider) -> None`
- `def run_automation(self, workflow_id: str, workspace_id: str, provider_id: str) -> AutomationSession`
- `def get_session(self, session_id: str) -> Optional[AutomationSession]`
- `def get_history(self, workspace_id: str) -> List[AutomationReport]`
- `def store_automation_summary(self, session_id: str) -> None`
- `def publish_automation_report(self, report: AutomationReport) -> None`

## Module: core/src/aios/services/context_impl.py

### class `LocalContextService`
- **Inherits from**: ContextService

> Concrete implementation of ContextService that resolves environment parameters
and publishes events on context changes.

**Methods:**

- `def __init__(self, event_bus: EventBusService) -> None`
- `def initialize(self) -> None`
- `def detect_context(self) -> WorkspaceContext`
  * Resolves the current execution context.
- `def get_current_context(self) -> WorkspaceContext | None`
- `def build_enriched_context(self, query: str, token_budget: int) -> Dict[str, Any]`
  * Assembles enriched context from various sources.

## Module: core/src/aios/services/workflow_monitoring_impl.py

### class `LocalWorkflowExecutionTracker`
- **Inherits from**: WorkflowExecutionTracker

> Tracks active trace sessions in memory registers.

**Methods:**

- `def __init__(self) -> None`
- `def track_execution(self, record: WorkflowExecutionRecord) -> None`
- `def get_executions(self, workflow_id: str) -> List[WorkflowExecutionRecord]`

### class `LocalWorkflowPerformanceAnalyzer`
- **Inherits from**: WorkflowPerformanceAnalyzer

> Compiles statistics, P95 values, median midpoints, and rates ratios.

**Methods:**

- `def analyze_performance(self, records: List[WorkflowExecutionRecord]) -> WorkflowStatistics`

### class `LocalWorkflowFailureAnalyzer`
- **Inherits from**: WorkflowFailureAnalyzer

> Analyzes failure rates and reports repeating error warnings.

**Methods:**

- `def analyze_failures(self, records: List[WorkflowExecutionRecord]) -> List[str]`

### class `LocalWorkflowRetryAnalyzer`
- **Inherits from**: WorkflowRetryAnalyzer

> Monitors retry trigger trends.

**Methods:**

- `def analyze_retries(self, records: List[WorkflowExecutionRecord]) -> Dict[str, Any]`

### class `LocalWorkflowMonitoringValidator`
- **Inherits from**: WorkflowMonitoringValidator

> Checks sequence trace values for ordering anomalies.

**Methods:**

- `def validate_telemetry(self, records: List[WorkflowExecutionRecord]) -> List[str]`

### class `LocalWorkflowMonitoringService`
- **Inherits from**: WorkflowMonitoringService

> Coordinating service tracking runs, triggers alerts, and publishing telemetry reports.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def record_execution(self, record: WorkflowExecutionRecord) -> None`
- `def get_telemetry_report(self, workspace_id: str) -> WorkflowMonitoringReport`
- `def get_alerts(self, workspace_id: str) -> List[WorkflowAlert]`
- `def get_history(self, workspace_id: str) -> List[WorkflowMonitoringReport]`
- `def store_monitoring_summary(self, workspace_id: str) -> None`
- `def publish_monitoring_report(self, report: WorkflowMonitoringReport) -> None`

## Module: core/src/aios/services/workflow_planning_impl.py

### class `LocalWorkflowIntentAnalyzer`
- **Inherits from**: WorkflowIntentAnalyzer

> Concrete intent analyzer mapping keywords to categories and tags.

**Methods:**

- `def analyze_intent(self, intent: str) -> Dict[str, Any]`

### class `LocalWorkflowDependencyResolver`
- **Inherits from**: WorkflowDependencyResolver

> Topological resolver ordering workflow nodes matching DAG dependencies.

**Methods:**

- `def resolve_dependencies(self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]) -> List[str]`

### class `LocalWorkflowOptimizer`
- **Inherits from**: WorkflowOptimizer

> Topological graph optimizer removing redundant or duplicate nodes.

**Methods:**

- `def optimize_graph(self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]) -> tuple[List[WorkflowNode], List[WorkflowEdge], List[str]]`

### class `LocalWorkflowSuggestionEngine`
- **Inherits from**: WorkflowSuggestionEngine

> Suggests template IDs matching intent tags.

**Methods:**

- `def suggest_templates(self, intent: str, registry: WorkflowTemplateRegistry) -> List[str]`

### class `LocalWorkflowComposer`
- **Inherits from**: WorkflowComposer

> Instantiates template parameters into parameterised WorkflowDefinitions.

**Methods:**

- `def compose_workflow(self, template: WorkflowTemplate, params: Dict[str, Any]) -> WorkflowDefinition`

### class `LocalWorkflowPlanner`
- **Inherits from**: WorkflowPlanner

> Conductor service managing planning pipelines, registry setups, and workspace documents.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def _register_default_templates(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def create_planning_session(self, workspace_id: str, intent: str) -> WorkflowPlanningSession`
- `def generate_plan(self, session: WorkflowPlanningSession) -> WorkflowPlanningReport`
- `def get_session(self, session_id: str) -> Optional[WorkflowPlanningSession]`
- `def get_history(self, workspace_id: str) -> List[WorkflowPlanningReport]`
- `def store_planning_summary(self, session_id: str) -> None`
- `def publish_planning_report(self, report: WorkflowPlanningReport) -> None`

## Module: core/src/aios/services/workflow_versioning_impl.py

### class `LocalWorkflowVersionRegistry`
- **Inherits from**: WorkflowVersionRegistry

> Immutable version catalogs catalog tracking graphs.

**Methods:**

- `def __init__(self, registry: Optional[Any]) -> None`
- `def register_version(self, version: WorkflowVersion) -> None`
- `def get_version(self, version_id: str) -> Optional[WorkflowVersion]`
- `def get_graph(self, workflow_id: str) -> Optional[WorkflowVersionGraph]`

### class `LocalWorkflowCompatibilityAnalyzer`
- **Inherits from**: WorkflowCompatibilityAnalyzer

> Analyzes compatibility status of semantic updates.

**Methods:**

- `def analyze_compatibility(self, from_ver: WorkflowVersion, to_ver: WorkflowVersion) -> Dict[str, Any]`

### class `LocalWorkflowMigrationPlanner`
- **Inherits from**: WorkflowMigrationPlanner

> Assembles migration plans and rollbacks checklists.

**Methods:**

- `def __init__(self) -> None`
- `def create_migration_plan(self, from_ver: WorkflowVersion, to_ver: WorkflowVersion) -> WorkflowEvolutionPlan`
- `def create_rollback_plan(self, from_ver: WorkflowVersion, target_ver: WorkflowVersion) -> WorkflowRollbackPlan`

### class `LocalWorkflowVersionValidator`
- **Inherits from**: WorkflowVersionValidator

> Validates semantic format bounds and author fields completeness.

**Methods:**

- `def validate_version(self, version: WorkflowVersion) -> List[str]`

### class `LocalWorkflowVersionService`
- **Inherits from**: WorkflowVersionService

> Coordinating service generating new version nodes, diff arrays, and Notion reports.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def create_version(self, workflow_id: str, author: str, semver: str, description: str, ir_json: str) -> WorkflowVersion`
- `def get_history(self, workflow_id: str) -> WorkflowVersionHistory`
- `def diff_versions(self, from_version_id: str, to_version_id: str) -> WorkflowVersionDiff`
- `def generate_evolution_plan(self, workflow_id: str, target_semver: str) -> WorkflowEvolutionPlan`
- `def generate_rollback_plan(self, workflow_id: str, target_version_id: str) -> WorkflowRollbackPlan`
- `def generate_version_report(self, workspace_id: str) -> WorkflowVersionReport`
- `def store_version_summary(self, workspace_id: str) -> None`
- `def publish_version_report(self, report: WorkflowVersionReport) -> None`

## Module: core/src/aios/services/file_planner.py

### class `ModificationType`
- **Inherits from**: Enum
- **Type**: Enum

> File modification categories.

### class `AffectedFile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a file impacted by the plan.

### class `AffectedDirectory`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a directory containing impacted files.

### class `ImplementationScope`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidates files and directories within implementation bounds.

### class `PlanningResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Result of intelligent file planning containing dependencies, order, and risks.

### class `FileImpactAnalyzer`
- **Inherits from**: abc.ABC

> Determines exact files and folders impacted by the objective.

**Methods:**

- `def analyze_impact(self, objective: str, code_summary: CodeStructureSummary) -> tuple[List[AffectedFile], List[AffectedDirectory]]`
  * Identifies modification files, target directories, and reasons.

### class `FileDependencyResolver`
- **Inherits from**: abc.ABC

> Resolves direct and indirect dependency chains across code imports.

**Methods:**

- `def resolve_dependencies(self, affected_files: List[AffectedFile], code_summary: CodeStructureSummary) -> tuple[Dict[str, List[str]], Dict[str, List[str]], List[str]]`
  * Resolves direct/indirect imports and flags high-risk paths.

### class `ChangePlanner`
- **Inherits from**: abc.ABC

> Formulates sequence checkpoints, risks, and execution order.

**Methods:**

- `def plan_changes(self, objective: str, scope: ImplementationScope, direct_deps: Dict[str, List[str]], code_summary: CodeStructureSummary) -> PlanningResult`
  * Determines ordered sequence, classification risks, and checkpoints.

### class `FilePlanner`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Primary service coordinating file planning, memory storage, and publishing.

**Methods:**

- `def generate_planning_result(self, workspace_id: str, objective: str, code_summary: CodeStructureSummary) -> PlanningResult`
  * Analyzes a development objective and returns a structured planning result.
- `def store_planning_result(self, result: PlanningResult) -> None`
  * Stores the file planning summary inside Memory Intelligence.
- `def publish_planning_result(self, result: PlanningResult) -> None`
  * Syncs the file planning report with the Knowledge Hub.

## Module: core/src/aios/services/persistence.py

### class `PersistencePolicy`
- **Inherits from**: enum.Enum
- **Type**: Enum

### class `PersistenceStatus`
- **Inherits from**: enum.Enum
- **Type**: Enum

### class `PersistenceResult`

> Explicit database operation result metadata.

**Methods:**

- `def __init__(self, status: PersistenceStatus, message: str, error_code: Optional[str], diagnostics: Optional[Dict[str, Any]], retryable: bool, provider: Optional[str], latency: float, operation_id: Optional[str], timestamp: Optional[float], repository: Optional[str], payload: Optional[Any]) -> None`

### class `PersistenceConfigurationService`
- **Inherits from**: ServiceLifecycle

> Configuration management service for the Persistence Platform.

**Methods:**

- `def __init__(self) -> None`

### class `TransportResult`

> Wrapper encapsulating query execution results, affected rows, and inserted keys.

**Methods:**

- `def __init__(self, rows: List[Dict[str, Any]], last_inserted_id: Optional[Any], rows_affected: int) -> None`

### class `TransportCapabilities`

> Features and capabilities supported by the active database transport.

**Methods:**

- `def __init__(self, support_savepoints: bool, support_json: bool) -> None`

### class `TransportHealth`

> Runtime health status representing connection state, latency, and diagnostics.

**Methods:**

- `def __init__(self, is_alive: bool, latency_ms: float, error_message: Optional[str]) -> None`

### class `TransportConnection`
- **Inherits from**: abc.ABC

> Abstract database connection instance managed by a DatabaseTransport.

**Methods:**

- `def close(self) -> None`
  * Closes the connection instance.
- `def execute(self, query: str, params: Optional[tuple]) -> TransportResult`
  * Executes a query on the connection.

### class `TransportTransaction`
- **Inherits from**: abc.ABC

> Abstract active database transaction scope.

**Methods:**

- `def commit(self) -> None`
  * Commits the transaction.
- `def rollback(self) -> None`
  * Rollbacks the transaction.

### class `DatabaseTransport`
- **Inherits from**: abc.ABC

> Abstract interface exposing the low-level database transport engine.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService) -> None`
- `def connect(self) -> None`
  * Establishes connections or pool resources.
- `def disconnect(self) -> None`
  * Tears down all connections or pools.
- `def execute(self, query: str, params: Optional[tuple]) -> TransportResult`
  * Executes a SQL query and returns result rows.
- `def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]`
  * Executes a bulk batch of SQL queries.
- `def begin_transaction(self) -> TransportTransaction`
  * Begins a database transaction scope.
- `def health(self) -> TransportHealth`
  * Returns health indicators.
- `def capabilities(self) -> TransportCapabilities`
  * Returns provider features capabilities.
- `def validate_configuration(self) -> List[str]`
  * Validates configuration parameters and returns error descriptions.

### class `TransportFactory`

> Factory to discover, validate, and instantiate database transports.

**Methods:**

- `def __init__(self) -> None`
- `def register_transport(self, name: str, transport_cls: Type[DatabaseTransport]) -> None`
  * Registers a DatabaseTransport class under a given name.
- `def create_transport(self, name: str, config: PersistenceConfigurationService) -> DatabaseTransport`
  * Creates an instance of the target DatabaseTransport class.

### class `PersistenceProvider`
- **Inherits from**: abc.ABC

> Abstract interface for database engine providers.

**Methods:**

- `def initialize(self, config: PersistenceConfigurationService) -> None`
  * Initializes the provider with configuration.
- `def connect(self) -> None`
  * Establishes connections/pools to the database.
- `def disconnect(self) -> None`
  * Closes all active connections and pools.
- `def execute(self, query: str, params: Optional[tuple]) -> List[Dict[str, Any]]`
  * Executes a SQL query and returns result rows.
- `def begin_transaction(self) -> None`
  * Begins a database transaction.
- `def commit_transaction(self) -> None`
  * Commits the active transaction.
- `def rollback_transaction(self) -> None`
  * Rollbacks the active transaction.
- `def is_connected(self) -> bool`
  * Returns True if the provider is successfully connected.
- `def get_metrics(self) -> Dict[str, Any]`
  * Returns connection and performance metrics.

### class `PersistenceRegistry`
- **Inherits from**: ServiceLifecycle

> Registry managing pluggable persistence provider engines.

**Methods:**

- `def __init__(self) -> None`
- `def register_provider(self, name: str, provider_cls: Type[PersistenceProvider]) -> None`
  * Registers a PersistenceProvider class.
- `def get_provider_class(self, name: str) -> Type[PersistenceProvider]`
  * Retrieves a registered provider class.

### class `RepositoryRegistry`
- **Inherits from**: ServiceLifecycle

> Registry capable of managing database repositories for future entities.

**Methods:**

- `def __init__(self) -> None`
- `def register_repository(self, name: str, repository_instance: Any) -> None`
  * Registers a concrete repository instance under a given name.
- `def get_repository(self, name: str) -> Any`
  * Retrieves a registered repository instance.

### class `PersistenceService`
- **Inherits from**: ServiceLifecycle

> The central unified service that orchestrates all database interactions.

**Methods:**

- `def execute(self, query: str, params: Optional[tuple]) -> List[Dict[str, Any]]`
  * Executes a database query.
- `def begin_transaction(self) -> PersistenceResult`
  * Starts a transaction scope.
- `def commit(self) -> PersistenceResult`
  * Commits the active transaction scope.
- `def rollback(self) -> PersistenceResult`
  * Rolls back the active transaction scope.
- `def commit_transaction(self) -> PersistenceResult`
  * Commits the active transaction scope.
- `def rollback_transaction(self) -> PersistenceResult`
  * Rolls back the active transaction scope.
- `def save(self, repo_name: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
  * Explicitly saves an entity in the repository.
- `def load(self, repo_name: str, entity_id: str) -> PersistenceResult`
  * Explicitly loads an entity from the repository.
- `def update(self, repo_name: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
  * Explicitly updates an entity in the repository.
- `def delete(self, repo_name: str, entity_id: str) -> PersistenceResult`
  * Explicitly deletes an entity from the repository.

### class `WorkspaceRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workspaces persistence operations.

**Methods:**

- `def save(self, workspace: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a workspace model.
- `def get(self, workspace_id: str) -> Optional[Dict[str, Any]]`
  * Retrieves a workspace model.
- `def delete(self, workspace_id: str) -> PersistenceResult`
  * Deletes a workspace model.
- `def list_all(self) -> List[Dict[str, Any]]`
  * Lists all workspaces in the system.

### class `WorkspaceSessionRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workspace session records.

**Methods:**

- `def save(self, session: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates session records.
- `def get(self, session_id: str) -> Optional[Dict[str, Any]]`
  * Retrieves a session record.
- `def delete(self, session_id: str) -> PersistenceResult`
  * Deletes a session record.
- `def list_all(self) -> List[Dict[str, Any]]`
  * Lists all session records.

### class `ProjectRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing project profiles metadata.

**Methods:**

- `def save(self, project: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates project details.
- `def get(self, project_id: str) -> Optional[Dict[str, Any]]`
  * Retrieves project details.
- `def delete(self, project_id: str) -> PersistenceResult`
  * Deletes project details.

### class `EngineeringProfileRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing engineering configuration profiles.

**Methods:**

- `def save(self, profile: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates engineering profile details.
- `def get(self, profile_id: str) -> Optional[Dict[str, Any]]`
  * Retrieves engineering profile details.
- `def delete(self, profile_id: str) -> PersistenceResult`
  * Deletes engineering profile details.
- `def get_history(self, profile_id: str) -> List[Dict[str, Any]]`
  * Retrieves history of profile modifications.

### class `ConfigurationRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing configuration profile settings.

**Methods:**

- `def save(self, config_profile: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates configuration profiles.
- `def get(self, config_profile_id: str) -> Optional[Dict[str, Any]]`
  * Retrieves configuration profiles.
- `def delete(self, config_profile_id: str) -> PersistenceResult`
  * Deletes configuration profiles.

### class `WorkspacePersistenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service orchestrating durable workspace environments.

**Methods:**

- `def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]`
  * Retrieves targeted workspace.
- `def save_workspace(self, workspace: Dict[str, Any]) -> None`
  * Saves targeted workspace.

### class `EngineeringTaskRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing engineering task persistence.

**Methods:**

- `def save(self, task: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a task.
- `def get(self, task_id: str) -> PersistenceResult`
  * Retrieves a task wrapper.
- `def delete(self, task_id: str) -> PersistenceResult`
  * Deletes a task.
- `def list_all(self) -> PersistenceResult`
  * Lists all tasks.

### class `PlanningRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing development plans and planning sessions.

**Methods:**

- `def save(self, plan: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a planning session.
- `def get(self, plan_id: str) -> PersistenceResult`
  * Retrieves a planning session wrapper.
- `def delete(self, plan_id: str) -> PersistenceResult`
  * Deletes a planning session.

### class `ApprovalRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing quality gate approvals.

**Methods:**

- `def save(self, approval: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates an approval session.
- `def get(self, approval_id: str) -> PersistenceResult`
  * Retrieves an approval session wrapper.
- `def delete(self, approval_id: str) -> PersistenceResult`
  * Deletes an approval session.

### class `ReviewRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing code reviews and transitions.

**Methods:**

- `def save(self, review: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a review session.
- `def get(self, review_id: str) -> PersistenceResult`
  * Retrieves a review session wrapper.
- `def delete(self, review_id: str) -> PersistenceResult`
  * Deletes a review session.

### class `DocumentationMetadataRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing documentation metadata.

**Methods:**

- `def save(self, doc: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates document metadata.
- `def get(self, doc_id: str) -> PersistenceResult`
  * Retrieves document metadata wrapper.
- `def delete(self, doc_id: str) -> PersistenceResult`
  * Deletes document metadata.

### class `TestSessionRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing test execution sessions.

**Methods:**

- `def save(self, session: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a test session.
- `def get(self, session_id: str) -> PersistenceResult`
  * Retrieves a test session wrapper.
- `def delete(self, session_id: str) -> PersistenceResult`
  * Deletes a test session.

### class `TestResultRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing granular test suite results.

**Methods:**

- `def save(self, result: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a test result.
- `def get(self, result_id: str) -> PersistenceResult`
  * Retrieves a test result wrapper.
- `def delete(self, result_id: str) -> PersistenceResult`
  * Deletes a test result.

### class `EngineeringMemoryService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Core coordinating service storing operational engineering metadata.

**Methods:**

- `def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
  * Creates a new durable metadata record.
- `def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
  * Updates an existing durable record.
- `def Archive(self, category: str, entity_id: str) -> PersistenceResult`
  * Archives a durable record.
- `def Restore(self, category: str, entity_id: str) -> PersistenceResult`
  * Restores an archived record.
- `def History(self, category: str, entity_id: str) -> PersistenceResult`
  * Retrieves operational history records.
- `def Statistics(self) -> PersistenceResult`
  * Compiles health metrics statistics.
- `def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`
  * Queries metadata records by attributes.

### class `WorkflowRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workflow definitions persistence operations.

**Methods:**

- `def save(self, workflow: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a workflow definition.
- `def get(self, workflow_id: str) -> PersistenceResult`
  * Retrieves a workflow definition wrapper.
- `def delete(self, workflow_id: str) -> PersistenceResult`
  * Deletes a workflow definition.

### class `WorkflowExecutionRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workflow executions persistence operations.

**Methods:**

- `def save(self, execution: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a workflow execution session.
- `def get(self, execution_id: str) -> PersistenceResult`
  * Retrieves a workflow execution session wrapper.
- `def delete(self, execution_id: str) -> PersistenceResult`
  * Deletes a workflow execution session.

### class `WorkflowMonitoringRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workflow health monitoring persistence operations.

**Methods:**

- `def save(self, monitor_report: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a workflow monitoring report.
- `def get(self, report_id: str) -> PersistenceResult`
  * Retrieves a workflow monitoring report wrapper.
- `def delete(self, report_id: str) -> PersistenceResult`
  * Deletes a workflow monitoring report.

### class `WorkflowOptimizationRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workflow optimizations persistence operations.

**Methods:**

- `def save(self, optimization: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a workflow optimization recommendation.
- `def get(self, optimization_id: str) -> PersistenceResult`
  * Retrieves a workflow optimization recommendation wrapper.
- `def delete(self, optimization_id: str) -> PersistenceResult`
  * Deletes a workflow optimization recommendation.

### class `WorkflowVersionRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workflow versions persistence operations.

**Methods:**

- `def save(self, version: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a workflow version metadata.
- `def get(self, version_id: str) -> PersistenceResult`
  * Retrieves a workflow version metadata wrapper.
- `def delete(self, version_id: str) -> PersistenceResult`
  * Deletes a workflow version metadata.

### class `WorkflowTranslationRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workflow translation metadata persistence operations.

**Methods:**

- `def save(self, translation: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a workflow translation report.
- `def get(self, translation_id: str) -> PersistenceResult`
  * Retrieves a workflow translation report wrapper.
- `def delete(self, translation_id: str) -> PersistenceResult`
  * Deletes a workflow translation report.

### class `WorkflowIntegrationRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing workflow integrations metadata persistence operations.

**Methods:**

- `def save(self, integration: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates a workflow integration config/health.
- `def get(self, integration_id: str) -> PersistenceResult`
  * Retrieves a workflow integration config/health wrapper.
- `def delete(self, integration_id: str) -> PersistenceResult`
  * Deletes a workflow integration config/health.

### class `AutomationTelemetryRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing automation telemetry metrics persistence.

**Methods:**

- `def save(self, telemetry: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates automation telemetry metadata.
- `def get(self, telemetry_id: str) -> PersistenceResult`
  * Retrieves automation telemetry metadata wrapper.
- `def delete(self, telemetry_id: str) -> PersistenceResult`
  * Deletes automation telemetry metadata.

### class `AutomationStatisticsRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Abstract interface managing compiled automation statistics persistence.

**Methods:**

- `def save(self, stats: Dict[str, Any]) -> PersistenceResult`
  * Persists/updates compiled automation statistics.
- `def get(self, stats_id: str) -> PersistenceResult`
  * Retrieves compiled automation statistics wrapper.
- `def delete(self, stats_id: str) -> PersistenceResult`
  * Deletes compiled automation statistics.

### class `AutomationPersistenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Core coordinating service storing operational automation metadata.

**Methods:**

- `def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
  * Creates a new durable automation record.
- `def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
  * Updates an existing durable record.
- `def Archive(self, category: str, entity_id: str) -> PersistenceResult`
  * Archives a durable record.
- `def Restore(self, category: str, entity_id: str) -> PersistenceResult`
  * Restores an archived record.
- `def History(self, category: str, entity_id: str) -> PersistenceResult`
  * Retrieves operational history records.
- `def Statistics(self) -> PersistenceResult`
  * Compiles health metrics statistics.
- `def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`
  * Queries metadata records by attributes.

### class `AIProviderRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, provider: Dict[str, Any]) -> PersistenceResult`
- `def get(self, provider_id: str) -> PersistenceResult`
- `def delete(self, provider_id: str) -> PersistenceResult`

### class `ProviderCapabilityRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, capabilities: Dict[str, Any]) -> PersistenceResult`
- `def get(self, capability_id: str) -> PersistenceResult`
- `def delete(self, capability_id: str) -> PersistenceResult`

### class `ProviderHealthRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, health: Dict[str, Any]) -> PersistenceResult`
- `def get(self, health_id: str) -> PersistenceResult`
- `def delete(self, health_id: str) -> PersistenceResult`

### class `ProviderTelemetryRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, telemetry: Dict[str, Any]) -> PersistenceResult`
- `def get(self, telemetry_id: str) -> PersistenceResult`
- `def delete(self, telemetry_id: str) -> PersistenceResult`

### class `ProviderStatisticsRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, statistics: Dict[str, Any]) -> PersistenceResult`
- `def get(self, statistics_id: str) -> PersistenceResult`
- `def delete(self, statistics_id: str) -> PersistenceResult`

### class `ProviderQuotaRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, quota: Dict[str, Any]) -> PersistenceResult`
- `def get(self, quota_id: str) -> PersistenceResult`
- `def delete(self, quota_id: str) -> PersistenceResult`

### class `ProviderRoutingRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, routing: Dict[str, Any]) -> PersistenceResult`
- `def get(self, routing_id: str) -> PersistenceResult`
- `def delete(self, routing_id: str) -> PersistenceResult`

### class `ProviderSessionRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, session: Dict[str, Any]) -> PersistenceResult`
- `def get(self, session_id: str) -> PersistenceResult`
- `def delete(self, session_id: str) -> PersistenceResult`

### class `ProviderCheckpointRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, checkpoint: Dict[str, Any]) -> PersistenceResult`
- `def get(self, checkpoint_id: str) -> PersistenceResult`
- `def delete(self, checkpoint_id: str) -> PersistenceResult`

### class `ProviderFailoverRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, failover: Dict[str, Any]) -> PersistenceResult`
- `def get(self, failover_id: str) -> PersistenceResult`
- `def delete(self, failover_id: str) -> PersistenceResult`

### class `AIUsageStatisticsRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, usage: Dict[str, Any]) -> PersistenceResult`
- `def get(self, usage_id: str) -> PersistenceResult`
- `def delete(self, usage_id: str) -> PersistenceResult`

### class `AIMemoryRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, memory: Dict[str, Any]) -> PersistenceResult`
- `def get(self, memory_id: str) -> PersistenceResult`
- `def delete(self, memory_id: str) -> PersistenceResult`

### class `AIMemoryPersistenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def Archive(self, category: str, entity_id: str) -> PersistenceResult`
- `def Restore(self, category: str, entity_id: str) -> PersistenceResult`
- `def History(self, category: str, entity_id: str) -> PersistenceResult`
- `def Statistics(self) -> PersistenceResult`
- `def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`

### class `RuntimeIntelligenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def get_telemetry(self) -> Dict[str, Any]`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_recommendations(self) -> List[Dict[str, Any]]`
- `def get_learning_payload(self) -> Dict[str, Any]`
- `def generate_reports(self) -> None`

### class `RedisTransport`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def is_connected(self) -> bool`
- `def execute_command(self, cmd: str) -> Any`

### class `RedisProvider`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get(self, key: str) -> Optional[str]`
- `def set(self, key: str, value: str, ttl: Optional[int]) -> bool`
- `def delete(self, key: str) -> bool`
- `def exists(self, key: str) -> bool`

### class `RedisRuntimeService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def get_telemetry(self) -> Dict[str, Any]`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_recommendations(self) -> List[Dict[str, Any]]`
- `def generate_reports(self) -> None`

### class `CachePolicy`
- **Inherits from**: enum.Enum
- **Type**: Enum

### class `CachePolicyManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_policy(self, subsystem: str) -> CachePolicy`
- `def get_ttl(self, subsystem: str) -> int`
- `def set_policy(self, subsystem: str, policy: CachePolicy) -> None`
- `def set_ttl(self, subsystem: str, ttl: int) -> None`

### class `CacheInvalidationManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def invalidate_key(self, key: str) -> bool`
- `def invalidate_entity(self, subsystem: str, entity_id: str) -> bool`
- `def invalidate_workspace(self, workspace_id: str) -> int`
- `def invalidate_project(self, project_id: str) -> int`
- `def invalidate_provider(self, provider_name: str) -> int`
- `def invalidate_pattern(self, pattern: str) -> int`
- `def invalidate_bulk(self, keys: List[str]) -> int`

### class `CacheWarmupService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def warmup_all_background(self) -> None`
- `def warm_subsystem(self, subsystem: str) -> None`

### class `CacheRebuildService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def trigger_rebuild_background(self) -> None`
- `def rebuild_incremental(self) -> int`

### class `CacheStatisticsCollector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def record_hit(self, subsystem: str, latency_ms: float, correlation_id: Optional[str]) -> None`
- `def record_miss(self, subsystem: str, latency_ms: float, correlation_id: Optional[str]) -> None`
- `def record_expiration(self, key: str) -> None`
- `def record_invalidation(self, count: int) -> None`
- `def record_warmup(self, key_count: int) -> None`
- `def record_rebuild(self, key_count: int) -> None`
- `def record_recommendation(self, rec: Dict[str, Any]) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `CacheHealthMonitor`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def check_health(self) -> Dict[str, Any]`

### class `CacheDiagnostics`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `CacheRecommendationEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `RedisCacheService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get(self, subsystem: str, entity_id: str, fetch_func: Callable[[], Any], policy: Optional[CachePolicy], ttl: Optional[int]) -> Any`
- `def set(self, subsystem: str, entity_id: str, value: Any, policy: Optional[CachePolicy], ttl: Optional[int]) -> bool`
- `def delete(self, subsystem: str, entity_id: str) -> bool`

### class `SessionPolicy`
- **Inherits from**: enum.Enum
- **Type**: Enum

### class `SessionRegistry`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def register_session_type(self, session_type: str, owner_service: str, ttl: float, policy: SessionPolicy, recovery_strategy: str, redis_prefix: str, source_of_truth: Optional[str], heartbeat_required: bool) -> None`
- `def get_configuration(self, session_type: str) -> Dict[str, Any]`
- `def get_all_types(self) -> List[str]`

### class `SessionExpirationManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def check_expirations(self) -> List[str]`
- `def expire_session(self, session_id: str, reason: str) -> None`

### class `SessionRecoveryManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def recover_session(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]`
- `def register_recovery_handler(self, session_type: str, handler: Callable[[str], Optional[Dict[str, Any]]]) -> None`
- `def trigger_rebuild_incremental(self) -> int`

### class `SessionStatisticsCollector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def record_create(self, session_type: str, correlation_id: Optional[str]) -> None`
- `def record_read(self, session_type: str, hit: bool, correlation_id: Optional[str]) -> None`
- `def record_update(self, session_type: str, correlation_id: Optional[str]) -> None`
- `def record_delete(self, session_type: str, correlation_id: Optional[str]) -> None`
- `def record_expire(self, session_type: str, reason: str) -> None`
- `def record_renew(self, session_type: str, correlation_id: Optional[str]) -> None`
- `def record_recovery(self, session_type: str, success: bool) -> None`
- `def record_heartbeat(self, session_type: str) -> None`
- `def record_latency(self, op: str, latency_ms: float) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `SessionHealthMonitor`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def check_health(self) -> Dict[str, Any]`

### class `SessionDiagnostics`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `SessionRecommendationEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `SessionStore`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def create(self, session_type: str, session_id: str, data: Dict[str, Any], workspace_id: Optional[str], project_id: Optional[str]) -> bool`
- `def read(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]`
- `def update(self, session_type: str, session_id: str, data: Dict[str, Any]) -> bool`
- `def delete(self, session_type: str, session_id: str) -> bool`
- `def renew(self, session_type: str, session_id: str) -> bool`
- `def heartbeat(self, session_type: str, session_id: str) -> bool`

### class `SessionManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def create_session(self, session_type: str, session_id: str, data: Dict[str, Any], workspace_id: Optional[str], project_id: Optional[str]) -> bool`
- `def get_session(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]`
- `def update_session(self, session_type: str, session_id: str, data: Dict[str, Any]) -> bool`
- `def delete_session(self, session_type: str, session_id: str) -> bool`
- `def renew_session(self, session_type: str, session_id: str) -> bool`
- `def heartbeat(self, session_type: str, session_id: str) -> bool`

### class `RedisSessionService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_manager(self) -> SessionManager`
- `def get_registry(self) -> SessionRegistry`
- `def get_store(self) -> SessionStore`

### class `LockPolicy`
- **Inherits from**: enum.Enum
- **Type**: Enum

### class `LockRegistry`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def register_lock_type(self, lock_type: str, owner_service: str, redis_prefix: str, lease_duration: float, renewal_strategy: str, timeout: float, recovery_strategy: str, deadlock_rules: Dict[str, Any], retry_policy: Dict[str, Any]) -> None`
- `def get_configuration(self, lock_type: str) -> Dict[str, Any]`
- `def get_all_types(self) -> List[str]`

### class `LockLeaseManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def acquire_lease(self, lock_type: str, lock_id: str, owner_id: str, policy: LockPolicy, lease_duration: Optional[float]) -> bool`
- `def renew_lease(self, lock_type: str, lock_id: str, owner_id: str) -> bool`
- `def release_lease(self, lock_type: str, lock_id: str, owner_id: str) -> bool`
- `def force_release(self, lock_type: str, lock_id: str) -> bool`
- `def verify_ownership(self, lock_type: str, lock_id: str, owner_id: str) -> bool`

### class `LockRecoveryManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def recover_locks(self) -> int`
- `def trigger_lock_rebuild(self) -> None`

### class `DeadlockDetector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def register_wait(self, owner_id: str, lock_id: str, lock_type: str) -> None`
- `def unregister_wait(self, owner_id: str, lock_id: str) -> None`
- `def detect_deadlocks(self) -> List[Dict[str, Any]]`
- `def get_deadlock_recommendations(self) -> List[Dict[str, Any]]`

### class `MutexManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def acquire_mutex(self, lock_type: str, lock_id: str, owner_id: str, timeout: float) -> bool`
- `def release_mutex(self, lock_type: str, lock_id: str, owner_id: str) -> bool`

### class `CoordinationStatisticsCollector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def record_acquisition(self, lock_type: str, policy: LockPolicy, success: bool, wait_time_ms: float) -> None`
- `def record_renewal(self, lock_type: str, success: bool) -> None`
- `def record_release(self, lock_type: str, success: bool) -> None`
- `def record_deadlock(self, cycle: List[str]) -> None`
- `def record_recovery(self, count: int) -> None`
- `def record_latency(self, op: str, latency_ms: float) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `CoordinationHealthMonitor`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def check_health(self) -> Dict[str, Any]`

### class `CoordinationDiagnostics`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `CoordinationRecommendationEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `DistributedLockManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def acquire(self, lock_type: str, lock_id: str, owner_id: str, policy: LockPolicy, lease_duration: Optional[float], timeout: Optional[float]) -> bool`
- `def release(self, lock_type: str, lock_id: str, owner_id: str) -> bool`
- `def renew(self, lock_type: str, lock_id: str, owner_id: str) -> bool`
- `def is_locked(self, lock_type: str, lock_id: str) -> bool`

### class `RedisCoordinationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_lock_manager(self) -> DistributedLockManager`
- `def get_registry(self) -> LockRegistry`
- `def get_lease_manager(self) -> LockLeaseManager`

### class `QueuePriority`
- **Inherits from**: enum.Enum
- **Type**: Enum

### class `QueueRegistry`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def register_queue(self, queue_type: str, owner_service: str, priority: QueuePriority, retry_policy: Dict[str, Any], visibility_timeout: float, retention_policy: float, dlq_name: str, worker_type: str, concurrency_limit: int, recovery_strategy: str) -> None`
- `def get_configuration(self, queue_type: str) -> Dict[str, Any]`
- `def get_all_types(self) -> List[str]`

### class `QueueManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def enqueue(self, queue_type: str, job_id: str, payload: Dict[str, Any], priority: Optional[QueuePriority], delay: float) -> bool`
- `def dequeue(self, queue_type: str, worker_id: str) -> Optional[Dict[str, Any]]`
- `def peek(self, queue_type: str) -> Optional[Dict[str, Any]]`
- `def cancel(self, queue_type: str, job_id: str) -> bool`
- `def acknowledge(self, queue_type: str, job_id: str, worker_id: str) -> bool`
- `def heartbeat(self, queue_type: str, job_id: str, worker_id: str) -> bool`
- `def pause(self, queue_type: str) -> None`
- `def resume(self, queue_type: str) -> None`
- `def purge(self, queue_type: str) -> None`

### class `PriorityQueueManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def sort_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]`

### class `DelayedQueueManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def add_delayed_job(self, job: Dict[str, Any], delay_seconds: float) -> None`
- `def extract_ready_jobs(self) -> List[Dict[str, Any]]`

### class `RetryQueueManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def handle_failure(self, job: Dict[str, Any], error: str) -> bool`

### class `QueueScheduler`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def poll_schedule(self) -> None`

### class `QueueWorkerCoordinator`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def register_worker(self, worker_id: str, worker_type: str) -> None`
- `def get_worker_utilization(self) -> Dict[str, Any]`

### class `QueueRecoveryManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def recover_pending_jobs(self) -> int`

### class `QueueStatisticsCollector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def record_enqueue(self, queue_type: str, priority: QueuePriority) -> None`
- `def record_dequeue(self, queue_type: str, success: bool) -> None`
- `def record_ack(self, queue_type: str) -> None`
- `def record_retry(self, queue_type: str) -> None`
- `def record_dlq(self, queue_type: str) -> None`
- `def record_duration(self, queue_type: str, duration_ms: float) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `QueueHealthMonitor`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def check_health(self) -> Dict[str, Any]`

### class `QueueDiagnostics`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `QueueRecommendationEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `RedisQueueService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_manager(self) -> QueueManager`
- `def get_registry(self) -> QueueRegistry`
- `def get_stats(self) -> QueueStatisticsCollector`

### class `JobState`
- **Inherits from**: enum.Enum
- **Type**: Enum

### class `JobStateMachine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def transition_to(self, job_id: str, new_state: JobState, metadata: Optional[Dict[str, Any]]) -> bool`
- `def get_state(self, job_id: str) -> Optional[JobState]`

### class `QuotaRegistry`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def register_quota(self, quota_type: str, owner_service: str, algorithm: str, capacity: int, refill_rate: float, burst_size: int, window_duration: float, fallback_strategy: str, sync_policy: str) -> None`
- `def get_configuration(self, quota_type: str) -> Dict[str, Any]`
- `def get_all_types(self) -> List[str]`

### class `RateLimitManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def allow_request(self, quota_type: str, resource_id: str, tokens: int) -> bool`
- `def get_quota_status(self, quota_type: str, resource_id: str) -> Dict[str, Any]`

### class `TokenBucketManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def consume(self, key: str, capacity: int, refill_rate: float, tokens: int) -> bool`

### class `SlidingWindowManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def consume(self, key: str, limit: int, window: float, tokens: int) -> bool`

### class `FixedWindowManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def consume(self, key: str, limit: int, window: float, tokens: int) -> bool`

### class `QuotaSynchronizationManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def sync_quota_to_db(self, quota_type: str, resource_id: str, current_usage: int) -> None`

### class `RateLimitRecoveryManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def recover_limits(self) -> int`

### class `RateLimitStatisticsCollector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def record_request(self, quota_type: str, allowed: bool, burst_used: bool) -> None`
- `def record_sync(self) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `RateLimitHealthMonitor`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def check_health(self) -> Dict[str, Any]`

### class `RateLimitDiagnostics`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `RateLimitRecommendationEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `RedisRateLimitService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_manager(self) -> RateLimitManager`
- `def get_registry(self) -> QuotaRegistry`
- `def get_stats(self) -> RateLimitStatisticsCollector`

### class `RedisRuntimeTelemetry`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_telemetry(self) -> Dict[str, Any]`

### class `RedisRuntimeAggregator`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def aggregate_metrics(self) -> Dict[str, Any]`

### class `RedisRuntimeHealthAnalyzer`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def analyze_health(self) -> Dict[str, Any]`

### class `RedisCapacityAnalyzer`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def analyze_capacity(self) -> Dict[str, Any]`

### class `RedisPerformanceAnalyzer`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def analyze_performance(self) -> Dict[str, Any]`

### class `RedisRecommendationEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def generate_recommendations(self) -> List[Dict[str, Any]]`

### class `RedisRuntimeDiagnostics`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `RedisRuntimeStatisticsCollector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_statistics(self) -> Dict[str, Any]`

### class `RedisRuntimeReporter`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def generate_report(self) -> str`

### class `RedisRuntimeValidator`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def validate_telemetry(self, data: Dict[str, Any]) -> bool`

### class `RedisRuntimeIntelligenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_telemetry_service(self) -> RedisRuntimeTelemetry`
- `def get_aggregator(self) -> RedisRuntimeAggregator`
- `def get_health_analyzer(self) -> RedisRuntimeHealthAnalyzer`
- `def get_capacity_analyzer(self) -> RedisCapacityAnalyzer`
- `def get_performance_analyzer(self) -> RedisPerformanceAnalyzer`
- `def get_recommendation_engine(self) -> RedisRecommendationEngine`
- `def get_diagnostics(self) -> RedisRuntimeDiagnostics`
- `def get_stats_collector(self) -> RedisRuntimeStatisticsCollector`
- `def get_reporter(self) -> RedisRuntimeReporter`
- `def get_validator(self) -> RedisRuntimeValidator`

### class `QdrantTransport`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def execute_command(self, cmd: str) -> Any`
- `def is_connected(self) -> bool`
- `def connect(self) -> None`
- `def disconnect(self) -> None`

### class `QdrantProvider`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_transport(self) -> QdrantTransport`
- `def create_collection(self, name: str, vector_size: int, distance: str, on_disk_payload: bool, quantization_config: Optional[Dict[str, Any]]) -> bool`
- `def delete_collection(self, name: str) -> bool`
- `def collection_exists(self, name: str) -> bool`
- `def upsert_points(self, collection: str, points: List[Dict[str, Any]]) -> bool`
- `def delete_points(self, collection: str, point_ids: List[Any]) -> bool`
- `def search_vectors(self, collection: str, vector: List[float], filter_query: Optional[Dict[str, Any]], limit: int, score_threshold: Optional[float]) -> List[Dict[str, Any]]`
- `def get_collection_info(self, name: str) -> Dict[str, Any]`

### class `CollectionManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def create_collection(self, name: str, dimensions: int, distance: str) -> bool`
- `def delete_collection(self, name: str) -> bool`
- `def exists(self, name: str) -> bool`
- `def validate_schema(self, name: str, schema: Dict[str, Any]) -> bool`
- `def create_index(self, collection_name: str, field_name: str, field_type: str) -> bool`
- `def get_statistics(self, name: str) -> Dict[str, Any]`

### class `QdrantRuntimeService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_provider(self) -> QdrantProvider`
- `def get_collection_manager(self) -> CollectionManager`
- `def get_telemetry(self) -> Dict[str, Any]`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, msg: str, severity: str, remediation: str) -> None`

### class `QdrantRuntimeTelemetry`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_telemetry(self) -> Dict[str, Any]`

### class `QdrantHealthAnalyzer`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def analyze_health(self) -> Dict[str, Any]`

### class `QdrantCapacityAnalyzer`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def analyze_capacity(self) -> Dict[str, Any]`

### class `QdrantPerformanceAnalyzer`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def analyze_performance(self) -> Dict[str, Any]`

### class `QdrantRecommendationEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def generate_recommendations(self) -> List[Dict[str, Any]]`

### class `QdrantDiagnosticsEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `QdrantStatisticsCollector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_statistics(self) -> Dict[str, Any]`

### class `QdrantRuntimeReporter`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def generate_report(self) -> str`

### class `QdrantRuntimeValidator`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def validate_telemetry(self, data: Dict[str, Any]) -> bool`

### class `QdrantRuntimeCoordinator`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_telemetry_service(self) -> QdrantRuntimeTelemetry`
- `def get_health_analyzer(self) -> QdrantHealthAnalyzer`
- `def get_capacity_analyzer(self) -> QdrantCapacityAnalyzer`
- `def get_performance_analyzer(self) -> QdrantPerformanceAnalyzer`
- `def get_recommendation_engine(self) -> QdrantRecommendationEngine`
- `def get_diagnostics(self) -> QdrantDiagnosticsEngine`
- `def get_stats_collector(self) -> QdrantStatisticsCollector`
- `def get_reporter(self) -> QdrantRuntimeReporter`
- `def get_validator(self) -> QdrantRuntimeValidator`

### class `EmbeddingMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `EmbeddingBatchRequest`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `EmbeddingBatchResponse`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `EmbeddingProvider`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `EmbeddingService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_provider(self, provider_name: str) -> EmbeddingProvider`
- `def register_provider(self, provider_name: str, provider: EmbeddingProvider) -> None`
- `def embed(self, text: str, provider_name: str) -> List[float]`

### class `EmbeddingVersionManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_active_version(self, collection_name: str) -> str`
- `def set_active_version(self, collection_name: str, version: str) -> None`
- `def requires_migration(self, collection_name: str, current_version: str) -> bool`

### class `EmbeddingCache`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get(self, text: str, version: str) -> Optional[List[float]]`
- `def set(self, text: str, vector: List[float], version: str) -> None`
- `def invalidate(self, text: str, version: str) -> None`
- `def clear(self) -> None`
- `def get_statistics(self) -> Dict[str, Any]`

### class `ChunkMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ChunkStrategy`
- **Inherits from**: enum.Enum
- **Type**: Enum

### class `ChunkResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ChunkingService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def chunk_text(self, text: str, strategy: ChunkStrategy) -> List[ChunkResult]`

### class `ContextCandidate`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ContextRanking`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ContextAssembly`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ContextBuilder`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def rank_candidates(self, candidates: List[ContextCandidate], objective: str) -> List[ContextRanking]`
- `def deduplicate(self, candidates: List[ContextCandidate]) -> List[ContextCandidate]`
- `def assemble_context(self, candidates: List[ContextCandidate], token_budget: int) -> ContextAssembly`

### class `EmbeddingRequest`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `EmbeddingResponse`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `EmbeddingJob`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `EmbeddingEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def embed_text(self, request: EmbeddingRequest) -> EmbeddingResponse`
- `def embed_batch(self, requests: List[EmbeddingRequest]) -> List[EmbeddingResponse]`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`

### class `SemanticQuery`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `SemanticResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `SemanticSearchService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def search(self, query: SemanticQuery) -> List[SemanticResult]`
- `def batch_search(self, queries: List[SemanticQuery]) -> List[List[SemanticResult]]`
- `def cross_collection_search(self, query: SemanticQuery, collections: List[str]) -> List[SemanticResult]`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`

### class `QueryAnalysis`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `QueryAnalysisService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def analyze_query(self, query_text: str, context_metadata: Optional[Dict[str, Any]]) -> QueryAnalysis`
- `def get_supported_intents(self) -> List[str]`

### class `CollectionSelector`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def select_collections(self, analysis: QueryAnalysis) -> Dict[str, float]`

### class `RetrievalCandidate`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `CandidateRanker`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def rank_candidates(self, candidates: List[RetrievalCandidate], weights: Optional[Dict[str, float]]) -> List[RetrievalCandidate]`
- `def get_default_weights(self) -> Dict[str, float]`
- `def set_weights(self, weights: Dict[str, float]) -> None`

### class `ContextAssemblyResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ContextOptimizer`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def optimize_context(self, candidates: List[RetrievalCandidate], token_budget: int) -> ContextAssemblyResult`
- `def merge_overlapping_chunks(self, candidates: List[RetrievalCandidate]) -> List[RetrievalCandidate]`
- `def compress_context(self, text: str, max_tokens: int) -> str`

### class `RetrievalCache`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_query_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]`
- `def set_query_results(self, cache_key: str, results: List[RetrievalCandidate], ttl: int) -> None`
- `def get_candidate_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]`
- `def set_candidate_results(self, cache_key: str, results: List[RetrievalCandidate], ttl: int) -> None`
- `def get_ranking_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]`
- `def set_ranking_results(self, cache_key: str, results: List[RetrievalCandidate], ttl: int) -> None`
- `def get_context_result(self, cache_key: str) -> Optional[str]`
- `def set_context_result(self, cache_key: str, context: str, ttl: int) -> None`
- `def invalidate(self, pattern: str) -> None`
- `def get_statistics(self) -> Dict[str, Any]`

### class `HybridRetrievalService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def retrieve(self, query_text: str, workspace_id: Optional[str], project_id: Optional[str], token_budget: int, filter_query: Optional[Dict[str, Any]]) -> ContextAssemblyResult`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `VectorMemoryRepository`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def save(self, memory_id: str, vector: List[float], payload: Dict[str, Any], retry: bool) -> bool`
- `def upsert(self, memory_id: str, vector: List[float], payload: Dict[str, Any], retry: bool) -> bool`
- `def get(self, memory_id: str) -> Optional[Dict[str, Any]]`
- `def delete(self, memory_id: str) -> bool`
- `def exists(self, memory_id: str) -> bool`
- `def search(self, vector: List[float], filter_query: Optional[Dict[str, Any]], limit: int, score_threshold: Optional[float]) -> List[Dict[str, Any]]`
- `def batch_upsert(self, points: List[Dict[str, Any]], retry: bool) -> bool`
- `def batch_delete(self, memory_ids: List[Any]) -> bool`
- `def count(self) -> int`
- `def clear(self) -> bool`
- `def health(self) -> Dict[str, Any]`
- `def statistics(self) -> Dict[str, Any]`

### class `EngineeringMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `WorkspaceMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `ProjectMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `DocumentationMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `ConversationMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `AutomationMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `ProviderMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `ResearchMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `KnowledgeMemoryRepository`
- **Inherits from**: VectorMemoryRepository, abc.ABC

### class `SemanticMemoryManager`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def index_memory(self, repository_name: str, entity_id: str, text: str, metadata: Dict[str, Any], tags: List[str], importance_override: Optional[float]) -> bool`
- `def retrieve_memories(self, repository_name: str, query_text: str, filter_query: Optional[Dict[str, Any]], limit: int, score_threshold: Optional[float]) -> List[Dict[str, Any]]`
- `def archive_memory(self, repository_name: str, entity_id: str) -> bool`
- `def delete_memory(self, repository_name: str, entity_id: str) -> bool`
- `def reindex_memory(self, repository_name: str, entity_id: str) -> bool`
- `def re_embed_memory(self, repository_name: str, entity_id: str) -> bool`
- `def merge_memories(self, repository_name: str, primary_id: str, secondary_id: str) -> bool`
- `def run_background_cleanup(self, repository_name: str) -> bool`
- `def get_statistics(self) -> Dict[str, Any]`

### class `KnowledgeNode`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Canonical model representing a unit of system knowledge, documentation, or code reference.

**Methods:**

- `def to_dict(self) -> Dict[str, Any]`
  * Converts the KnowledgeNode to a standard Python dictionary.
- `def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeNode'`
  * Instantiates a KnowledgeNode from a dictionary.
- `def to_payload(self) -> Dict[str, Any]`
  * Converts to a dictionary representation suitable for Qdrant payload.
- `def to_json(self) -> str`
  * Serializes the KnowledgeNode to a JSON string.
- `def from_json(cls, json_str: str) -> 'KnowledgeNode'`
  * Deserializes a KnowledgeNode from a JSON string.

## Module: core/src/aios/services/test_coverage.py

### class `CoverageMetrics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidates coverage percentage stats across scopes.

### class `CoveragePolicy`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Enforces target threshold policy mappings.

### class `CoverageSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregates coverage metrics summaries.

### class `CoverageReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Assembled report tracking coverage results and policies.

### class `RegressionRisk`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Details identified regression probability metrics.

### class `ValidationGap`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Highlights validation omissions or insufficient test coverages.

### class `CoverageAnalyzer`
- **Inherits from**: abc.ABC

> Calculates coverage parameters and flags validation gaps.

**Methods:**

- `def analyze_coverage(self, execution_summary: ExecutionSummary, targets: List[CoverageTarget], policy: CoveragePolicy) -> CoverageReport`
  * Determines statement and branch coverages against target policies.

### class `RegressionAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes execution metrics and dependency graphs to isolate regression risks.

**Methods:**

- `def analyze_regression_risks(self, affected_files: List[str], dependency_graph: Dict[str, List[str]], execution_summary: ExecutionSummary) -> RegressionRisk`
  * Computes regression probability index.

### class `AITestCoverageService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service mapping coverage outputs, logging telemetry, and reporting gaps.

**Methods:**

- `def evaluate_validation(self, workspace_id: str, execution_summary: ExecutionSummary, affected_files: List[str], dependency_graph: Dict[str, List[str]], policy: CoveragePolicy) -> Dict[str, Any]`
  * Runs overall coverage & regression analysis validation checks.
- `def store_coverage_summary(self, report: CoverageReport) -> None`
  * Saves coverage and regression summaries inside Memory.
- `def publish_coverage_report(self, report: CoverageReport) -> None`
  * Syncs coverage and regression report with Knowledge Hub.

## Module: core/src/aios/services/documentation_intelligence_impl.py

### class `LocalDocumentationPlanner`
- **Inherits from**: DocumentationPlanner

> Concrete planner assembling document templates structured according to adapter formatting rules.

**Methods:**

- `def plan_documentation(self, session: DocumentationSession, profile_adapter: DocumentationProfileAdapter) -> List[DocumentTemplate]`

### class `LocalDocumentationService`
- **Inherits from**: DocumentationService

> Centralized documentation orchestrator resolving profile configs and tracking registry files.

**Methods:**

- `def __init__(self, memory_service: MemoryService, engineering_profile_service: EngineeringProfileService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[Any], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def _get_policy(self) -> PersistencePolicy`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def create_session(self, workspace: DocumentationWorkspace) -> DocumentationSession`
- `def plan_session(self, session: DocumentationSession) -> List[DocumentTemplate]`
- `def register_artifact(self, artifact: DocumentArtifact) -> None`
- `def get_artifact(self, artifact_id: str) -> Optional[DocumentArtifact]`
- `def store_documentation_summary(self, result: DocumentationResult) -> None`
- `def publish_documentation_summary(self, result: DocumentationResult) -> None`

## Module: core/src/aios/services/reasoning_impl.py

### class `LocalReasoningEvaluator`
- **Inherits from**: ReasoningEvaluator

**Methods:**

- `def evaluate(self, plan: Dict[str, Any], strategy: ReasoningStrategy) -> Dict[str, Any]`

### class `LocalReasoningCritic`
- **Inherits from**: ReasoningCritic

**Methods:**

- `def critique(self, step: ReasoningStep, context: ReasoningContext) -> str`

### class `LocalReasoningService`
- **Inherits from**: ReasoningService

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def create_session(self, objective: str) -> ReasoningSession`
- `def reason(self, objective: str, context: ReasoningContext) -> ReasoningResult`
- `def _select_strategy(self, objective: str) -> ReasoningStrategy`

## Module: core/src/aios/services/test_validation.py

### class `ValidationStatus`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate validation outcomes matching gating thresholds.

### class `ValidationDecision`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate release decision status outcomes.

### class `ValidationFinding`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Detailed diagnostic discovery during validations.

### class `ValidationRecommendation`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Actionable recommendation to address validation findings.

### class `ValidationEvidence`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Supporting telemetry record for validation gates.

### class `ValidationGate`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Validation gate checking rules based on evidence telemetry.

### class `ValidationMetrics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated statistics across test execution runs and coverage targets.

### class `ValidationScore`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Detailed score components including weights and penalty counts.

### class `ValidationSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregated validation statistics summary.

### class `ValidationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Assembled validation report package consumed by future AI OS services.

### class `ValidationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Unified validation compiler synthesizing reports, logging decisions, and publishing summaries.

**Methods:**

- `def synthesize_validation(self, workspace_id: str, execution_summary: ExecutionSummary, coverage_report: CoverageReport, failure_report: FailureAnalysisReport) -> ValidationReport`
  * Assembles authoritative validation report combining executions, coverages, and failure logs.
- `def store_validation_report(self, report: ValidationReport) -> None`
  * Stores validation summary details inside Memory.
- `def publish_validation_report(self, report: ValidationReport) -> None`
  * Syncs validation report with Knowledge Hub.

## Module: core/src/aios/services/agent_impl.py

### class `MockAgent`
- **Inherits from**: Agent

> Mock agent that simulates planning, reasoning, memory retrieval, tool

execution, and returns structured responses.

**Methods:**

- `def __init__(self, memory_service: MemoryService, context_service: ContextService, tool_service: ToolService) -> None`
- `def name(self) -> str`
- `def description(self) -> str`
- `def execute(self, agent_context: AgentContext) -> AgentResult`

### class `DeveloperAgent`
- **Inherits from**: Agent

> Developer Agent that helps develop software by orchestrating context,

memories, tools (git, filesystem, terminal), and querying the LLM adapter.

**Methods:**

- `def __init__(self, memory_service: MemoryService, context_service: ContextService, tool_service: ToolService, model_service: ModelService) -> None`
- `def name(self) -> str`
- `def description(self) -> str`
- `def execute(self, agent_context: AgentContext) -> AgentResult`

### class `CareerAgent`
- **Inherits from**: Agent

> Career Agent to help prepare job applications by analyzing job descriptions,

tailoring resumes, ATS scoring, and generating cover letters.

**Methods:**

- `def __init__(self, memory_service: MemoryService, context_service: ContextService, tool_service: ToolService, model_service: ModelService, github_service: Optional[Any], career_os: Optional[Any], daily_os: Optional[Any]) -> None`
- `def name(self) -> str`
- `def description(self) -> str`
- `def execute(self, agent_context: AgentContext) -> AgentResult`

### class `LocalAgentRuntime`
- **Inherits from**: AgentRuntimeService

> Agent Runtime coordinating memory retrieval, context loading,

and agent execution.

**Methods:**

- `def __init__(self, event_bus: EventBusService, memory_service: MemoryService, context_service: ContextService, tool_service: ToolService, model_service: ModelService) -> None`
- `def initialize(self) -> None`
- `def register_agent(self, agent: Agent) -> None`
- `def unregister_agent(self, name: str) -> None`
- `def execute(self, intent: Intent) -> AgentResult`
- `def interrupt(self) -> None`
- `def cancel(self) -> None`

## Module: core/src/aios/services/developer_workspace_impl.py

### class `LocalDeveloperWorkspace`
- **Inherits from**: DeveloperWorkspaceService

**Methods:**

- `def initialize(self) -> None`
- `def get_workspace_info(self, workspace_root: str) -> DeveloperWorkspaceInfo`
- `def execute_safe_command(self, command: str, args: List[str], workspace_root: str) -> Dict[str, Any]`

## Module: core/src/aios/services/workflow_monitoring.py

### class `WorkflowExecutionState`
- **Inherits from**: str, Enum
- **Type**: Enum

> Workflow execution outcome/running state.

### class `WorkflowExecutionMetrics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Execution timing and metadata telemetries.

### class `WorkflowExecutionRecord`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated telemetry trace describing a single run session.

### class `WorkflowTelemetry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Container grouping execution trace lists by workflow ID.

### class `WorkflowAlert`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Configure-triggered runtime anomaly warning alert.

### class `WorkflowHealthScore`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Workflow structural health evaluation metric.

### class `WorkflowStatistics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Compiled timing and rate metrics detailing workflow run aggregates.

### class `WorkflowMonitoringReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated telemetry summaries payload for syncing or writing.

### class `WorkflowExecutionTracker`
- **Inherits from**: abc.ABC

> Tracks active trace sessions.

**Methods:**

- `def track_execution(self, record: WorkflowExecutionRecord) -> None`
  * Saves run trace.
- `def get_executions(self, workflow_id: str) -> List[WorkflowExecutionRecord]`
  * Retrieves runs traces.

### class `WorkflowPerformanceAnalyzer`
- **Inherits from**: abc.ABC

> Compiles statistics, timing medians, and averages.

**Methods:**

- `def analyze_performance(self, records: List[WorkflowExecutionRecord]) -> WorkflowStatistics`
  * Returns statistics summary object.

### class `WorkflowFailureAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes failure rates and detects repeated blockers.

**Methods:**

- `def analyze_failures(self, records: List[WorkflowExecutionRecord]) -> List[str]`
  * Identifies recurring errors list.

### class `WorkflowRetryAnalyzer`
- **Inherits from**: abc.ABC

> Monitors retry triggers rates and delays.

**Methods:**

- `def analyze_retries(self, records: List[WorkflowExecutionRecord]) -> Dict[str, Any]`
  * Returns retry analysis metrics.

### class `WorkflowMonitoringValidator`
- **Inherits from**: abc.ABC

> Checks timestamps sequencing and integrity validation.

**Methods:**

- `def validate_telemetry(self, records: List[WorkflowExecutionRecord]) -> List[str]`
  * Validates timestamp orders and consistency checks.

### class `WorkflowMonitoringService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Main coordinator tracking executions, generating monitoring reports, and alerts.

**Methods:**

- `def record_execution(self, record: WorkflowExecutionRecord) -> None`
  * Records execution trace and updates active summaries.
- `def get_telemetry_report(self, workspace_id: str) -> WorkflowMonitoringReport`
  * Generates compiled metrics report payload.
- `def get_alerts(self, workspace_id: str) -> List[WorkflowAlert]`
  * Retrieves active alerts list.
- `def get_history(self, workspace_id: str) -> List[WorkflowMonitoringReport]`
  * Retrieves completed reports.
- `def store_monitoring_summary(self, workspace_id: str) -> None`
  * Saves metadata summaries inside memory. Never stores source code/credentials.
- `def publish_monitoring_report(self, report: WorkflowMonitoringReport) -> None`
  * Synchronizes report details to Notion.

## Module: core/src/aios/services/file_planner_impl.py

### class `LocalFileImpactAnalyzer`
- **Inherits from**: FileImpactAnalyzer

> Rule-based impact analyzer mapping files and directories.

**Methods:**

- `def analyze_impact(self, objective: str, code_summary: CodeStructureSummary) -> tuple[List[AffectedFile], List[AffectedDirectory]]`

### class `LocalFileDependencyResolver`
- **Inherits from**: FileDependencyResolver

> Resolves direct and transitive (indirect) dependencies recursively.

**Methods:**

- `def resolve_dependencies(self, affected_files: List[AffectedFile], code_summary: CodeStructureSummary) -> tuple[Dict[str, List[str]], Dict[str, List[str]], List[str]]`

### class `LocalChangePlanner`
- **Inherits from**: ChangePlanner

> Calculates ordered sequences, classifications, and rollback checkpoints.

**Methods:**

- `def plan_changes(self, objective: str, scope: ImplementationScope, direct_deps: Dict[str, List[str]], code_summary: CodeStructureSummary) -> PlanningResult`

### class `LocalFilePlanner`
- **Inherits from**: FilePlanner

> Coordinating File Planner implementation supporting LLM parsing and fallback rules.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_planning_result(self, workspace_id: str, objective: str, code_summary: CodeStructureSummary) -> PlanningResult`
- `def store_planning_result(self, result: PlanningResult) -> None`
- `def publish_planning_result(self, result: PlanningResult) -> None`

## Module: core/src/aios/services/orchestrator_impl.py

### class `DefaultResultAggregator`
- **Inherits from**: ResultAggregator

**Methods:**

- `def aggregate(self, results: Dict[str, Any]) -> str`

### class `LocalOrchestratorService`
- **Inherits from**: OrchestratorService

**Methods:**

- `def __init__(self, command_registry: CommandRegistry) -> None`
- `def initialize(self) -> None`
- `def execute_plan(self, plan: ExecutionPlan, initial_ctx: ExecutionContext) -> Dict[str, Any]`
- `def _group_invocations_into_levels(self, invocations: List[SkillInvocation]) -> List[List[SkillInvocation]]`
- `def _substitute_parameters(self, command: str, variables: Dict[str, Any]) -> str`
- `def _resolve_handler_and_args(self, command_str: str) -> tuple[Any, str]`
- `def _run_handler_capture(self, handler: Any, args: str) -> str`

## Module: core/src/aios/services/memory.py

### class `MemoryType`
- **Inherits from**: Enum
- **Type**: Enum

### class `MemoryCategory`
- **Inherits from**: Enum
- **Type**: Enum

### class `MemoryImportance`
- **Inherits from**: Enum
- **Type**: Enum

### class `RetrievalStrategy`
- **Inherits from**: Enum
- **Type**: Enum

### class `MemoryReference`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `MemoryMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Memory`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `RetrievalContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `MemoryFilter`
- **Inherits from**: abc.ABC

**Methods:**

- `def filter_memories(self, memories: List[Memory], context: RetrievalContext) -> List[Memory]`
  * Filters memories by relevance, recency, importance, and size limits.

### class `MemorySelector`
- **Inherits from**: abc.ABC

**Methods:**

- `def select_memories(self, memories: List[Memory], context: RetrievalContext) -> List[Memory]`
  * Orders and trims memories to the smallest useful set to avoid prompt inflation.

### class `MemoryRetriever`
- **Inherits from**: abc.ABC

**Methods:**

- `def retrieve(self, context: RetrievalContext) -> List[Memory]`
  * Retrieves and filters memories matching a user objective or strategy.

### class `MemoryClassifier`
- **Inherits from**: abc.ABC

**Methods:**

- `def classify_memory(self, content: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`
  * Automatically classifies memory content, extracting category, importance, tags,
related projects, missions, companies, technologies, skills, and files.

### class `MemoryIndexer`
- **Inherits from**: abc.ABC

**Methods:**

- `def index_memory(self, memory: Memory) -> None`
  * Indexes a memory for lookup.
- `def deindex_memory(self, memory_id: str) -> None`
  * Removes a memory from the index.
- `def lookup(self, category: Optional[MemoryCategory], tags: Optional[List[str]], mission: Optional[str], project: Optional[str], company: Optional[str], technology: Optional[str], start_date: Optional[float], end_date: Optional[float]) -> List[Memory]`
  * Retrieves memories matching index constraints.

### class `MemoryService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Interface for loading, updating, committing, and organizing knowledge across sessions.

**Methods:**

- `def classifier(self) -> MemoryClassifier`
- `def indexer(self) -> MemoryIndexer`
- `def retriever(self) -> MemoryRetriever`
- `def add_memory(self, content: str, memory_type: MemoryType, tags: List[str], importance: int, metadata_additional: Dict[str, Any]) -> Memory`
  * Creates and stores a new Memory.
- `def update_memory(self, memory_id: str, content: Optional[str], tags: Optional[List[str]], importance: Optional[int], metadata_additional: Optional[Dict[str, Any]]) -> Memory`
  * Updates an existing Memory.
- `def delete_memory(self, memory_id: str) -> None`
  * Deletes a Memory from the system.
- `def search_memory(self, query: str, memory_type: Optional[MemoryType], tags: Optional[List[str]]) -> List[Memory]`
  * Searches memories by substring content match, type, and/or tags.
- `def get_memory(self, memory_id: str) -> Optional[Memory]`
  * Retrieves a specific memory by ID.
- `def load_workspace_memory(self, workspace_id: str) -> List[Memory]`
  * Loads and returns memories associated with the given workspace ID.
- `def commit(self) -> None`
  * Persists the current memories state to the storage backend.
- `def restore_memory(self, context: dict) -> None`
  * Restores memory relevant to the given context.
- `def observe_event(self, event: dict) -> None`
  * Observes an event for potential memory retention.
- `def commit_memory(self) -> None`
  * Persists the current memory state.
- `def prune_memory(self) -> None`
  * Runs the memory pruning and expiration routines.

## Module: core/src/aios/services/research.py

### class `Source`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Citation`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ResearchResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `SearchProvider`
- **Inherits from**: abc.ABC

**Methods:**

- `def name(self) -> str`
  * Name of the search provider.
- `def search(self, query: str, limit: int) -> List[Source]`
  * Performs a search query and returns list of source results.

### class `ResearchService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def register_provider(self, provider: SearchProvider) -> None`
  * Registers an external or local search provider.
- `def research(self, query: str, limit: int) -> ResearchResult`
  * Decomposes queries, gathers sources, deduplicates/ranks them, and generates a cited report.

## Module: core/src/aios/services/execution_engine.py

### class `ExecutionState`
- **Inherits from**: Enum
- **Type**: Enum

> Lifecycle states of a plan execution session.

### class `ExecutionStep`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents an individual step or action during task execution.

### class `ExecutionCheckpoint`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Saves execution state after a task completes, supporting resume and rollback.

### class `RollbackPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Prepares instructions to revert changes without autonomously performing edits.

### class `ExecutionSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> State tracking for a specific plan execution session.

### class `ExecutionResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Unified result payload for session execution completions or state updates.

### class `ExecutionValidator`
- **Inherits from**: abc.ABC

> Performs pre-flight checks validating repository status, dependencies, and execution orders.

**Methods:**

- `def validate_pre_execution(self, plan: SoftwareEngineeringPlan, task: ImplementationTask, session: ExecutionSession) -> tuple[bool, str]`
  * Validates that a task is safe to execute based on state and dependency availability.

### class `TaskExecutor`
- **Inherits from**: abc.ABC

> Executes a single task, asking for explicit human approval for actions.

**Methods:**

- `def execute_task(self, task: ImplementationTask, session: ExecutionSession, step_approval_callback: Callable[[], bool]) -> tuple[bool, str, List[ExecutionStep]]`
  * Sequentially runs execution actions if human approval callback returns True.

### class `ExecutionReporter`
- **Inherits from**: abc.ABC

> Generates execution summary logs and Markdown reports.

**Methods:**

- `def generate_report(self, session: ExecutionSession, plan: SoftwareEngineeringPlan) -> str`
  * Formulates an execution summary report.

### class `ExecutionEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Central engine orchestration session lifetimes, checkpoints, validations, and rollbacks.

**Methods:**

- `def create_session(self, plan: SoftwareEngineeringPlan) -> ExecutionSession`
  * Initializes a new ExecutionSession tracking a SoftwareEngineeringPlan.
- `def start_execution(self, session_id: str, step_approval_callback: Callable[[], bool]) -> ExecutionResult`
  * Begins executing tasks in a session.
- `def pause_execution(self, session_id: str) -> None`
  * Pauses the execution loop.
- `def resume_execution(self, session_id: str, step_approval_callback: Callable[[], bool]) -> ExecutionResult`
  * Resumes a paused execution session.
- `def cancel_execution(self, session_id: str) -> None`
  * Cancels a running session.
- `def generate_rollback_plan(self, session_id: str) -> RollbackPlan`
  * Generates a rollback report mapping changes back to the start of the session.
- `def store_execution_summary(self, session_id: str) -> None`
  * Saves execution history to Memory Intelligence.
- `def publish_execution_report(self, session_id: str) -> None`
  * Syncs the execution status report with the Knowledge Hub.

## Module: core/src/aios/services/execution_engine_impl.py

### class `LocalExecutionValidator`
- **Inherits from**: ExecutionValidator

> Concrete validator ensuring safety requirements are met before running task.

**Methods:**

- `def validate_pre_execution(self, plan: SoftwareEngineeringPlan, task: ImplementationTask, session: ExecutionSession) -> tuple[bool, str]`

### class `LocalTaskExecutor`
- **Inherits from**: TaskExecutor

> Task Executor that runs with explicit user permission gates.

**Methods:**

- `def execute_task(self, task: ImplementationTask, session: ExecutionSession, step_approval_callback: Callable[[], bool]) -> tuple[bool, str, List[ExecutionStep]]`

### class `LocalExecutionReporter`
- **Inherits from**: ExecutionReporter

> Constructs Markdown summaries of Execution Sessions.

**Methods:**

- `def generate_report(self, session: ExecutionSession, plan: SoftwareEngineeringPlan) -> str`

### class `LocalExecutionEngine`
- **Inherits from**: ExecutionEngine

> Main Execution Engine managing sessions, checkpoints, validation, and rollbacks.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def create_session(self, plan: SoftwareEngineeringPlan) -> ExecutionSession`
- `def start_execution(self, session_id: str, step_approval_callback: Callable[[], bool]) -> ExecutionResult`
- `def pause_execution(self, session_id: str) -> None`
- `def resume_execution(self, session_id: str, step_approval_callback: Callable[[], bool]) -> ExecutionResult`
- `def cancel_execution(self, session_id: str) -> None`
- `def generate_rollback_plan(self, session_id: str) -> RollbackPlan`
- `def store_execution_summary(self, session_id: str) -> None`
- `def publish_execution_report(self, session_id: str) -> None`

## Module: core/src/aios/services/engineering_profile_impl.py

### class `LocalProfileSerializer`
- **Inherits from**: ProfileSerializer

> Concrete profile serializer mapping dict structures to dataclasses.

**Methods:**

- `def serialize(self, profile: EngineeringProfile) -> Dict[str, Any]`
- `def deserialize(self, data: Dict[str, Any]) -> EngineeringProfile`

### class `LocalProfileLoader`
- **Inherits from**: ProfileLoader

> Loads profiles from JSON files on local disk paths.

**Methods:**

- `def load_from_file(self, file_path: str) -> Dict[str, Any]`

### class `LocalProfileManager`
- **Inherits from**: ProfileManager

> Deep merges profile structures and runs basic validations checks.

**Methods:**

- `def merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]`
- `def validate(self, profile: EngineeringProfile) -> List[str]`

### class `LocalEngineeringProfileService`
- **Inherits from**: EngineeringProfileService

> Concrete profile service orchestrating database persistence and verification checks.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[Any], registry: Optional[Any], profile_repo: Optional[EngineeringProfileRepository]) -> None`
- `def _get_policy(self) -> PersistencePolicy`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_profile(self, profile_id: str) -> Optional[EngineeringProfile]`
- `def save_profile(self, profile: EngineeringProfile) -> None`
- `def delete_profile(self, profile_id: str) -> None`
- `def get_profile_history(self, profile_id: str) -> List[Dict[str, Any]]`
- `def rollback_profile(self, profile_id: str, version: int) -> None`
- `def store_profile_summary(self, profile: EngineeringProfile) -> None`
- `def publish_profile_summary(self, profile: EngineeringProfile) -> None`

## Module: core/src/aios/services/n8n_translation_impl.py

### class `LocalN8NNodeMapper`
- **Inherits from**: N8NNodeMapper

> Concrete node mapper converting IR nodes into n8n native node schemas.

**Methods:**

- `def map_node(self, node: Dict[str, Any], context: TranslationContext) -> Dict[str, Any]`

### class `LocalTranslationValidator`
- **Inherits from**: TranslationValidator

> Integrity checking validator validating JSON schemas and edge connection links.

**Methods:**

- `def validate_translation(self, ir: WorkflowIR, n8n_json: Dict[str, Any]) -> List[str]`

### class `LocalWorkflowCompiler`
- **Inherits from**: WorkflowCompiler

> Compiles WorkflowDefinitions into intermediate canonical IR maps.

**Methods:**

- `def compile_definition_to_ir(self, definition: WorkflowDefinition) -> WorkflowIR`

### class `LocalWorkflowSerializer`
- **Inherits from**: WorkflowSerializer

> Pretty prints output JSON to file buffers.

**Methods:**

- `def serialize_to_json_string(self, n8n_json: Dict[str, Any]) -> str`

### class `LocalN8NTranslationEngine`
- **Inherits from**: N8NTranslationEngine

> Drives node translations and connections mappings.

**Methods:**

- `def __init__(self) -> None`
- `def translate_ir(self, ir: WorkflowIR, context: TranslationContext) -> Dict[str, Any]`

### class `LocalWorkflowTranslator`
- **Inherits from**: WorkflowTranslator

> Coordinating gateway compiling definitions and storing execution logs.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def translate_workflow(self, definition: WorkflowDefinition, workspace_id: str) -> TranslationReport`
- `def get_history(self, workspace_id: str) -> List[TranslationReport]`
- `def store_translation_summary(self, report_id: str) -> None`
- `def publish_translation_report(self, report: TranslationReport) -> None`

## Module: core/src/aios/services/patch_generation_impl.py

### class `LocalDiffGenerator`
- **Inherits from**: DiffGenerator

> Generates unified diff representation using Python difflib standard library.

**Methods:**

- `def generate_diff(self, original_content: str, modified_content: str, file_path: str) -> str`

### class `LocalPatchGenerator`
- **Inherits from**: PatchGenerator

> Computes unified diffs and metadata across files in workspace and repo root.

**Methods:**

- `def __init__(self, diff_generator: DiffGenerator) -> None`
- `def generate_patch_bundle(self, workspace_root: str, original_repo_root: str, affected_files: List[str]) -> PatchBundle`

### class `LocalPatchValidator`
- **Inherits from**: PatchValidator

> Enforces syntax check and checksum compatibility for patches.

**Methods:**

- `def validate_patch_bundle(self, bundle: PatchBundle, workspace_root: str) -> tuple[bool, str]`

### class `LocalConflictDetector`
- **Inherits from**: ConflictDetector

> Detects merge collisions between workspace and origin repository roots.

**Methods:**

- `def detect_conflicts(self, bundle: PatchBundle, original_repo_root: str) -> tuple[List[str], List[str]]`

### class `LocalPatchSerializer`
- **Inherits from**: PatchSerializer

> Converts patch objects to/from JSON.

**Methods:**

- `def serialize_bundle(self, bundle: PatchBundle) -> str`
- `def deserialize_bundle(self, content: str) -> PatchBundle`

### class `LocalPatchGenerationService`
- **Inherits from**: PatchGenerationService

> Coordinates reviews packaging, stats caching, and publication.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def create_review_package(self, workspace_id: str, original_repo_root: str, workspace_root: str, affected_files: List[str]) -> ReviewPackage`
- `def store_patch_summary(self, review_package: ReviewPackage) -> None`
- `def publish_patch_report(self, review_package: ReviewPackage) -> None`

## Module: core/src/aios/services/knowledge_hub_impl.py

### class `NotionProvider`
- **Inherits from**: KnowledgeProvider

**Methods:**

- `def __init__(self, config: NotionConfig) -> None`
- `def get_name(self) -> str`
- `def authenticate(self) -> bool`
- `def discover_databases(self) -> List[Dict[str, Any]]`
- `def discover_pages(self) -> List[KnowledgePage]`
- `def search(self, query: str) -> List[KnowledgePage]`
- `def read_page(self, page_id: str) -> Optional[KnowledgePage]`
- `def create_page(self, parent_id: str, title: str, content: str, properties: Optional[Dict[str, Any]]) -> Optional[KnowledgePage]`
- `def update_page(self, page_id: str, title: Optional[str], content: Optional[str], properties: Optional[Dict[str, Any]]) -> Optional[KnowledgePage]`
- `def _post(self, path: str, payload: dict) -> dict`
- `def _get(self, path: str) -> dict`
- `def _patch(self, path: str, payload: dict) -> dict`
- `def _delete(self, path: str) -> dict`
- `def _request(self, path: str, payload: Optional[dict], method: str) -> dict`
- `def _markdown_to_blocks(self, content: str) -> List[dict]`
- `def _create_block(self, type_: str, text: str) -> dict`
- `def _get_title(self, page_or_db: dict) -> str`
- `def _extract_rich_text(self, rich_texts: List[dict]) -> str`

### class `LocalKnowledgeHub`
- **Inherits from**: KnowledgeHubService

**Methods:**

- `def __init__(self, config: NotionConfig, personal_service: PersonalService) -> None`
- `def initialize(self) -> None`
- `def register_provider(self, provider: KnowledgeProvider) -> None`
- `def get_provider(self, name: str) -> Optional[KnowledgeProvider]`
- `def sync_document(self, doc: KnowledgeDocument, provider_name: str) -> KnowledgeSyncResult`
- `def get_sync_status(self, document_id: str) -> Optional[KnowledgeMetadata]`
- `def _load_sync_registry(self) -> None`
- `def _save_sync_registry(self) -> None`

## Module: core/src/aios/services/career_impl.py

### class `LocalCareerProfileManager`
- **Inherits from**: CareerProfileManager

**Methods:**

- `def __init__(self, personal_service: PersonalService) -> None`
- `def get_career_profile(self) -> Optional[CareerProfile]`
- `def update_career_profile(self, profile: CareerProfile) -> None`

### class `LocalJobAnalyzer`
- **Inherits from**: JobAnalyzer

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService) -> None`
- `def analyze_job(self, job_description: str) -> Dict[str, Any]`

### class `LocalResumeOptimizer`
- **Inherits from**: ResumeOptimizer

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService) -> None`
- `def tailor_resume(self, resume: Resume, job_description: str) -> ResumeVersion`
- `def optimize_ats(self, resume_version: ResumeVersion, keywords: List[str]) -> ResumeVersion`

### class `LocalATSAnalyzer`
- **Inherits from**: ATSAnalyzer

**Methods:**

- `def __init__(self, model_service: ModelService) -> None`
- `def score_resume_against_job(self, resume_version: ResumeVersion, job_description: str) -> Dict[str, Any]`

### class `LocalCoverLetterGenerator`
- **Inherits from**: CoverLetterGenerator

**Methods:**

- `def __init__(self, model_service: ModelService) -> None`
- `def generate_cover_letter(self, resume_version: ResumeVersion, job_description: str) -> str`

### class `LocalPortfolioAnalyzer`
- **Inherits from**: PortfolioAnalyzer

**Methods:**

- `def __init__(self, model_service: ModelService, github_service: GitHubService) -> None`
- `def analyze_portfolio(self, username: str) -> Dict[str, Any]`

### class `LocalApplicationTracker`
- **Inherits from**: ApplicationTracker

**Methods:**

- `def __init__(self, personal_service: PersonalService) -> None`
- `def _get_applications(self) -> List[JobApplication]`
- `def _save_applications(self, apps: List[JobApplication]) -> None`
- `def add_application(self, app: JobApplication) -> None`
- `def update_application_status(self, app_id: str, status: str) -> None`
- `def list_applications(self) -> List[JobApplication]`

### class `LocalInterviewCoach`
- **Inherits from**: InterviewCoach

**Methods:**

- `def __init__(self, model_service: ModelService) -> None`
- `def prepare_interview(self, company: str, role: str) -> Dict[str, Any]`
- `def generate_questions(self, role: str, category: str) -> List[str]`

### class `LocalCareerPlanner`
- **Inherits from**: CareerPlanner

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService, registry: Optional[Any]) -> None`
- `def generate_plan(self) -> Dict[str, Any]`

### class `LocalJobMatcher`
- **Inherits from**: JobMatcher

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService) -> None`
- `def match_jobs(self, jobs: List[str]) -> List[Dict[str, Any]]`

### class `LocalCareerOSService`
- **Inherits from**: CareerOSService

> Unified service implementation coordinating all Career OS modules.

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService, github_service: GitHubService, project_intel: Optional[ProjectIntelligenceService], n8n_service: Optional[N8NService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def profile_manager(self) -> CareerProfileManager`
- `def job_analyzer(self) -> JobAnalyzer`
- `def resume_optimizer(self) -> ResumeOptimizer`
- `def ats_analyzer(self) -> ATSAnalyzer`
- `def cover_letter_generator(self) -> CoverLetterGenerator`
- `def portfolio_analyzer(self) -> PortfolioAnalyzer`
- `def application_tracker(self) -> ApplicationTracker`
- `def interview_coach(self) -> InterviewCoach`
- `def career_planner(self) -> CareerPlanner`
- `def job_matcher(self) -> JobMatcher`

## Module: core/src/aios/services/memory_impl.py

### class `LocalMemoryClassifier`
- **Inherits from**: MemoryClassifier

**Methods:**

- `def __init__(self, memory_service: 'LocalMemoryService') -> None`
- `def classify_memory(self, content: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]`

### class `LocalMemoryIndexer`
- **Inherits from**: MemoryIndexer

**Methods:**

- `def __init__(self, memory_service: 'LocalMemoryService') -> None`
- `def index_memory(self, memory: Memory) -> None`
- `def deindex_memory(self, memory_id: str) -> None`
- `def lookup(self, category: Optional[MemoryCategory], tags: Optional[List[str]], mission: Optional[str], project: Optional[str], company: Optional[str], technology: Optional[str], start_date: Optional[float], end_date: Optional[float]) -> List[Memory]`

### class `LocalMemoryFilter`
- **Inherits from**: MemoryFilter

**Methods:**

- `def filter_memories(self, memories: List[Memory], context: RetrievalContext) -> List[Memory]`

### class `LocalMemorySelector`
- **Inherits from**: MemorySelector

**Methods:**

- `def select_memories(self, memories: List[Memory], context: RetrievalContext) -> List[Memory]`

### class `LocalMemoryRetriever`
- **Inherits from**: MemoryRetriever

**Methods:**

- `def __init__(self, memory_service: 'LocalMemoryService', filter_component: MemoryFilter, selector_component: MemorySelector) -> None`
- `def retrieve(self, context: RetrievalContext) -> List[Memory]`

### class `LocalMemoryService`
- **Inherits from**: MemoryService

> Concrete implementation of MemoryService utilizing a configurable local storage backend.

**Methods:**

- `def __init__(self, event_bus: EventBusService, storage: Optional[MemoryStorage]) -> None`
- `def set_model_service(self, model_service: ModelService) -> None`
- `def model_service(self) -> Optional[ModelService]`
- `def classifier(self) -> MemoryClassifier`
- `def indexer(self) -> MemoryIndexer`
- `def retriever(self) -> MemoryRetriever`
- `def initialize(self) -> None`
- `def _on_context_loaded(self, event: ContextLoadedEvent) -> None`
- `def _on_session_started(self, event: SessionStartedEvent) -> None`
- `def _on_session_ended(self, event: SessionEndedEvent) -> None`
- `def add_memory(self, content: str, memory_type: MemoryType, tags: List[str], importance: int, metadata_additional: Dict[str, Any]) -> Memory`
- `def update_memory(self, memory_id: str, content: Optional[str], tags: Optional[List[str]], importance: Optional[int], metadata_additional: Optional[Dict[str, Any]]) -> Memory`
- `def delete_memory(self, memory_id: str) -> None`
- `def search_memory(self, query: str, memory_type: Optional[MemoryType], tags: Optional[List[str]]) -> List[Memory]`
- `def get_memory(self, memory_id: str) -> Optional[Memory]`
- `def load_workspace_memory(self, workspace_id: str) -> List[Memory]`
- `def commit(self) -> None`
- `def restore_memory(self, context: dict) -> None`
- `def observe_event(self, event: dict) -> None`
- `def commit_memory(self) -> None`
- `def prune_memory(self) -> None`

## Module: core/src/aios/services/engineering_documentation.py

### class `DecisionRecord`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> An individual ADR specification.

### class `ImplementationSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Summary of features and timelines.

### class `EngineeringTimeline`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Timeline details mapping milestone timings.

### class `ChangeSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Summary metrics of modified codebase lines.

### class `ValidationSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Summary mapping test executions results.

### class `RiskSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Risk tiers assessments tags.

### class `EngineeringDocumentArtifact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Output artifact documentation container.

### class `EngineeringDocumentationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Executive engineering metrics report.

### class `ADRGenerator`
- **Inherits from**: abc.ABC

> Formats DecisionRecord specs into single Markdown outputs.

**Methods:**

- `def generate_adr(self, record: DecisionRecord) -> str`
  * Outputs Markdown representations.

### class `EngineeringReportGenerator`
- **Inherits from**: abc.ABC

> Combines metrics datasets into comprehensive reports.

**Methods:**

- `def generate_engineering_report(self, summary: ImplementationSummary, validation: ValidationSummary, risk: RiskSummary) -> str`
  * Assembles Markdown content.

### class `EngineeringDocumentPlanner`
- **Inherits from**: abc.ABC

> Plans layout structure matching target style rules.

**Methods:**

- `def plan_engineering_documents(self, workspace_id: str) -> List[DecisionRecord]`
  * Assembles list of decisions requiring documenting.

### class `EngineeringDocumentValidator`
- **Inherits from**: abc.ABC

> Validates markdown structure completeness or duplicate ADR indexes.

**Methods:**

- `def validate_engineering_document(self, artifact: EngineeringDocumentArtifact) -> List[str]`
  * Returns validation error list.

### class `EngineeringDocumentationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service planning timelines summaries and publishing metrics.

**Methods:**

- `def create_adr_document(self, workspace_id: str, record: DecisionRecord) -> EngineeringDocumentArtifact`
  * Builds an ADR document artifact.
- `def create_engineering_report(self, workspace_id: str, summary: ImplementationSummary, validation: ValidationSummary, risk: RiskSummary) -> EngineeringDocumentArtifact`
  * Builds an engineering report artifact.
- `def store_engineering_summary(self, artifact: EngineeringDocumentArtifact) -> None`
  * Logs summaries metadata in Memory.
- `def publish_engineering_report(self, report: EngineeringDocumentationReport) -> None`
  * Pushes updates to Knowledge Hub Notion pages.

## Module: core/src/aios/services/test_generation_impl.py

### class `LocalTestPatternAnalyzer`
- **Inherits from**: TestPatternAnalyzer

> Analyzes folders to parse naming style and fixtures conventions.

**Methods:**

- `def analyze_patterns(self, existing_tests_dir: str) -> str`

### class `LocalTestTemplateEngine`
- **Inherits from**: TestTemplateEngine

> Formats Python test suite structures using standard templating.

**Methods:**

- `def render_template(self, template_name: str, context: Dict[str, Any]) -> str`

### class `LocalTestCaseBuilder`
- **Inherits from**: TestCaseBuilder

> Structures step-by-step target execution cases.

**Methods:**

- `def build_cases(self, objective: str, patterns: str) -> List[Dict[str, Any]]`

### class `LocalAssertionGenerator`
- **Inherits from**: AssertionGenerator

> Generates standard asserts.

**Methods:**

- `def generate_assertions(self, target_symbol: str) -> List[str]`

### class `LocalFixtureGenerator`
- **Inherits from**: FixtureGenerator

> Creates Pytest fixture setup functions.

**Methods:**

- `def generate_fixtures(self, target_symbol: str) -> List[str]`

### class `LocalMockGenerator`
- **Inherits from**: MockGenerator

> Creates MagicMock return handlers.

**Methods:**

- `def generate_mocks(self, target_symbol: str) -> List[str]`

### class `LocalEdgeCaseGenerator`
- **Inherits from**: EdgeCaseGenerator

> Creates exception boundaries block tests.

**Methods:**

- `def generate_edge_cases(self, target_symbol: str) -> List[str]`

### class `LocalRegressionTestGenerator`
- **Inherits from**: RegressionTestGenerator

> Creates regression verification tests.

**Methods:**

- `def generate_regression_tests(self, target_symbol: str) -> List[str]`

### class `LocalTestGenerator`
- **Inherits from**: TestGenerator

> Assembles fixtures, mocks, asserts, and edge cases to write unit tests.

**Methods:**

- `def __init__(self) -> None`
- `def generate_test_suite(self, workspace_root: str, target_file: str, patterns: str, code_summary: CodeStructureSummary) -> GeneratedTestArtifact`

### class `LocalTestGenerationService`
- **Inherits from**: TestGenerationService

> Coordinating Test Generation Service utilizing Model Service routing layers.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_workspace_tests(self, workspace_id: str, objective: str, workspace_root: str, target_files: List[str], code_summary: CodeStructureSummary) -> TestGenerationReport`
- `def store_generation_report(self, report: TestGenerationReport) -> None`
- `def publish_generation_report(self, report: TestGenerationReport) -> None`

## Module: core/src/aios/services/session_impl.py

### class `LocalSessionService`
- **Inherits from**: SessionService

> Concrete implementation of SessionService that manages the lifecycle of sessions
and publishes events on session start and end.

**Methods:**

- `def __init__(self, event_bus: EventBusService) -> None`
- `def initialize(self) -> None`
- `def start_session(self, workspace_path: str, session_id: Optional[str]) -> Session`
  * Starts a new session for the given workspace path and publishes SessionStartedEvent.
- `def end_session(self) -> None`
  * Ends the active session and publishes SessionEndedEvent.
- `def get_current_session(self) -> Optional[Session]`
  * Returns the currently active session, if any.
- `def create_session(self, workspace_path: str) -> str`
  * Launches a new session and returns the session ID.
- `def save_session(self, session_id: str) -> None`
  * Persists the active session state.
- `def get_active_session_id(self) -> Optional[str]`
  * Returns the current active session ID, if any.

## Module: core/src/aios/services/workspace_intelligence.py

### class `RepositoryHealth`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents health metrics of the repository.

### class `RepositorySummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Contains full high-level and detailed analysis of a code repository.

### class `RepositoryAnalyzer`
- **Inherits from**: abc.ABC

> Component to inspect files, structures, configuration, CI/CD, and Docker files.

**Methods:**

- `def analyze(self, workspace_root: str) -> Dict[str, Any]`
  * Scans the repository structure, config files, and build pipelines.

### class `ArchitectureAnalyzer`
- **Inherits from**: abc.ABC

> Component to evaluate high-level layout, components, and execution paths.

**Methods:**

- `def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]`
  * Identifies architectural layout, key components, entrypoints, and observations.

### class `DependencyAnalyzer`
- **Inherits from**: abc.ABC

> Component to map imports, packages, and dependency relations.

**Methods:**

- `def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, List[str]]`
  * Extracts dependency relationships between components and modules.

### class `TechnologyAnalyzer`
- **Inherits from**: abc.ABC

> Component to identify languages, databases, linters, frameworks, and deployment options.

**Methods:**

- `def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]`
  * Identifies frameworks, database adapters, test configurations, linters, and clouds.

### class `DocumentationAnalyzer`
- **Inherits from**: abc.ABC

> Component to analyze documentation files, README completeness, and ADR counts.

**Methods:**

- `def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]`
  * Measures documentation coverage, ADR counts, and README files quality details.

### class `WorkspaceIntelligenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Unified service representing primary repository analysis and project health verification.

**Methods:**

- `def analyze_repository(self, workspace_root: str) -> RepositorySummary`
  * Executes full repository analyzers, maps dependencies, and generates summary metrics.
- `def store_summary_in_memory(self, summary: RepositorySummary) -> None`
  * Stores the structured summary and health metrics inside the memory service.
- `def publish_to_knowledge_hub(self, summary: RepositorySummary) -> None`
  * Publishes the repository summary report to the Knowledge Hub.

### class `SymbolReference`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a code symbol (class, function, method, interface, enum) extracted via AST.

### class `CodeStructureSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Unified code structure representation containing symbol indexes and call/dependency graphs.

### class `LanguageASTParser`
- **Inherits from**: abc.ABC

> Interface for language-specific AST parsers.

**Methods:**

- `def can_parse(self, file_extension: str) -> bool`
  * Returns True if this parser can handle the given file extension.
- `def parse(self, file_path: str, content: str) -> List[SymbolReference]`
  * Parses the content of a source file and returns extracted symbols.

### class `ASTAnalyzer`
- **Inherits from**: abc.ABC

> Component responsible for parsing source code into syntax symbols.

**Methods:**

- `def parse_file(self, file_path: str, content: str) -> List[SymbolReference]`
  * Parses source file content into a list of syntax symbols.

### class `SymbolIndexer`
- **Inherits from**: abc.ABC

> Component maintaining code symbols lookup maps.

**Methods:**

- `def index_symbols(self, symbols: List[SymbolReference]) -> None`
  * Indexes symbols for fast lookup.
- `def lookup_symbol(self, name: str) -> Optional[SymbolReference]`
  * Looks up a symbol by its name.
- `def list_symbols(self) -> List[SymbolReference]`
  * Returns all indexed symbols.

### class `DependencyGraphBuilder`
- **Inherits from**: abc.ABC

> Component constructing module import and inheritance graphs.

**Methods:**

- `def build_graph(self, file_paths: List[str], symbols: List[SymbolReference]) -> Dict[str, List[str]]`
  * Maps imports and module-level dependency relationships.

### class `CallGraphBuilder`
- **Inherits from**: abc.ABC

> Component constructing function call dependency graphs.

**Methods:**

- `def build_call_graph(self, symbols: List[SymbolReference]) -> Dict[str, List[str]]`
  * Builds a map representing function call references.

### class `CodeIntelligenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Unified service representing code-level understanding and AST analyses.

**Methods:**

- `def analyze_codebase(self, workspace_root: str) -> CodeStructureSummary`
  * Triggers complete source files AST parsing and graph builders.
- `def store_code_summary(self, summary: CodeStructureSummary) -> None`
  * Stores structural summaries inside Memory Intelligence without saving source content.
- `def publish_code_report(self, summary: CodeStructureSummary) -> None`
  * Publishes the code structure summary report to the Knowledge Hub.

## Module: core/src/aios/services/automation.py

### class `WorkflowNode`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Graph node representing an operation or decision element.

### class `WorkflowEdge`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Directed graph edge representing execution transitions routes.

### class `WorkflowGraph`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Directed graph container organizing nodes and edge links.

### class `WorkflowTrigger`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Trigger conditions prompting execution flow runs.

### class `WorkflowAction`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Concrete workflow action executing system operations.

### class `WorkflowCondition`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Conditional evaluation expression.

### class `WorkflowVariable`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Variable container declaring schema types and defaults.

### class `WorkflowCredentialReference`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Credential metadata index referencing system vaults securely.

### class `WorkflowExecutionPolicy`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Configurable execution constraints matching runtime policies.

### class `WorkflowMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Metadata tag indicators detailing descriptions and dependencies.

### class `WorkflowArtifact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Output artifacts resulting from workflow execution loops.

### class `WorkflowDefinition`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Unified container representing a platform-independent workflow graph.

### class `AutomationSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Lifecycle tracking for an active execution flow session.

### class `AutomationResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated outcome metrics from workflow executions.

### class `AutomationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Report compiled for external Knowledge Hub updates.

### class `AutomationProvider`
- **Inherits from**: abc.ABC

> Abstract interface for execution providers.

**Methods:**

- `def provider_id(self) -> str`
  * Returns unique identifier for provider.
- `def validate_definition(self, definition: WorkflowDefinition) -> List[str]`
  * Validates if provider supports the workflow structures.
- `def execute_workflow(self, definition: WorkflowDefinition, session: AutomationSession) -> AutomationResult`
  * Runs the workflow using provider execution engines.

### class `N8NProvider`
- **Inherits from**: AutomationProvider, abc.ABC

> Abstract provider structure for n8n platform integration.

### class `GitHubActionsProvider`
- **Inherits from**: AutomationProvider, abc.ABC

> Abstract provider structure for GitHub Actions integration.

### class `TemporalProvider`
- **Inherits from**: AutomationProvider, abc.ABC

> Abstract provider structure for Temporal orchestrators integration.

### class `AutomationProviderRegistry`

> Container registry holding registered automation providers.

**Methods:**

- `def __init__(self) -> None`
- `def register(self, provider: AutomationProvider) -> None`
- `def get(self, provider_id: str) -> Optional[AutomationProvider]`
- `def list_providers(self) -> List[str]`

### class `AutomationRegistry`
- **Inherits from**: abc.ABC

> Workflow catalog manager saving platform-independent workflow definitions.

**Methods:**

- `def register_workflow(self, definition: WorkflowDefinition) -> None`
  * Registers definition template.
- `def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]`
  * Retrieves definition template by ID.

### class `AutomationValidator`
- **Inherits from**: abc.ABC

> Enforces graph structures completeness, loop preventions, and credential checks.

**Methods:**

- `def validate_workflow(self, definition: WorkflowDefinition) -> List[str]`
  * Validates graph connectivity and variables consistency.

### class `AutomationManager`
- **Inherits from**: abc.ABC

> Orchestrates session creation and runner hand-offs.

**Methods:**

- `def create_session(self, workflow_id: str, workspace_id: str) -> AutomationSession`
  * Instantiates session for run.
- `def execute_session(self, session: AutomationSession, provider_id: str) -> AutomationResult`
  * Delegates execution loop to targeted provider.

### class `AutomationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Conductor service managing runs, providers, history logs, and Notion reporting.

**Methods:**

- `def register_provider(self, provider: AutomationProvider) -> None`
  * Registers third-party executor runner.
- `def run_automation(self, workflow_id: str, workspace_id: str, provider_id: str) -> AutomationSession`
  * Submits task, validation checks, and triggers runner loops.
- `def get_session(self, session_id: str) -> Optional[AutomationSession]`
  * Retrieves current session tracking details.
- `def get_history(self, workspace_id: str) -> List[AutomationReport]`
  * Retrieves completed history logs for workspace.
- `def store_automation_summary(self, session_id: str) -> None`
  * Caches summary metrics in Memory. Never saves source code/credentials.
- `def publish_automation_report(self, report: AutomationReport) -> None`
  * Synchronizes report page to Notion.

## Module: core/src/aios/services/review_impl.py

### class `LocalReviewAnalyzer`
- **Inherits from**: ReviewAnalyzer

> Concrete review analyzer generating findings from Approval Package details.

**Methods:**

- `def analyze_package(self, workspace_id: str, package: ApprovalPackage) -> tuple[ReviewSummary, List[ReviewFinding]]`

### class `LocalReviewValidator`
- **Inherits from**: ReviewValidator

> Concrete validator flagging duplicate findings, evidence issues, and inconsistency gates.

**Methods:**

- `def validate_review(self, report: ReviewReport) -> List[str]`

### class `LocalReviewEngine`
- **Inherits from**: ReviewEngine

> Central orchestrator managing automated review runs, memory logging, Notion syncs.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def run_review(self, workspace_id: str, package: ApprovalPackage) -> ReviewSession`
- `def get_session(self, session_id: str) -> Optional[ReviewSession]`
- `def get_history(self, workspace_id: str) -> List[ReviewSummary]`
- `def store_review_summary(self, session: ReviewSession) -> None`
- `def publish_review_report(self, report: ReviewReport) -> None`

## Module: core/src/aios/services/security.py

### def `validate_workspace_path`
- `def validate_workspace_path(path_str: str, workspace_root: str) -> Path`
> Validates that the given target path is strictly within the active workspace root.
Resolves symbolic links and normalizes the path to prevent directory traversal.

Raises:
    PermissionError: If the resolved path escapes the workspace root.
    ValueError: If the path is invalid.

## Module: core/src/aios/services/n8n.py

### class `InternalNode`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `InternalConnection`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `InternalWorkflow`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ExecutionMetrics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ConnectionHealth`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `N8NService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def create_workflow(self, workflow: InternalWorkflow) -> InternalWorkflow`
  * Saves/deploys the internal workflow representation.
- `def update_workflow(self, workflow_id: str, workflow: InternalWorkflow) -> InternalWorkflow`
  * Updates an existing workflow.
- `def delete_workflow(self, workflow_id: str) -> bool`
  * Deletes an existing workflow by its identifier.
- `def get_workflow(self, workflow_id: str) -> Optional[InternalWorkflow]`
  * Retrieves a workflow by its identifier.
- `def list_workflows(self) -> List[InternalWorkflow]`
  * Lists all deployed workflows.
- `def validate_workflow(self, workflow: InternalWorkflow) -> Dict[str, Any]`
  * Runs graph diagnostics: detects loops, unreachable nodes, missing credentials.
- `def generate_workflow_from_natural_language(self, description: str) -> InternalWorkflow`
  * Uses ModelService to plan and construct a valid InternalWorkflow from plain text.
- `def execute_workflow(self, workflow_id: str) -> bool`
  * Starts/triggers execution of a workflow.
- `def stop_workflow(self, workflow_id: str) -> bool`
  * Halts running execution of a workflow.
- `def get_execution_metrics(self, workflow_id: str) -> Optional[ExecutionMetrics]`
  * Retrieves running metrics and log streams.
- `def check_health(self) -> ConnectionHealth`
  * Checks API connectivity to the local/remote n8n engine.

## Module: core/src/aios/services/test_engineer.py

### class `TestCategory`
- **Inherits from**: Enum
- **Type**: Enum

> Supported testing disciplines.

### class `TestPriority`
- **Inherits from**: Enum
- **Type**: Enum

> Gauges prioritization sequence weights.

### class `TestStrategy`
- **Inherits from**: Enum
- **Type**: Enum

> Refers to validation depth bounds.

### class `TestRequirement`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Requirement criteria for satisfying validation targets.

### class `TestTarget`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Specific code target (file path or symbol class/function).

### class `TestScope`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Encloses target lists, goals, and risk levels.

### class `TestSuite`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Packaged collection of test definitions targeting specific modules.

### class `TestPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Complete testing plan specification.

### class `TestPlanningResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Ordered result sequence of test planner run.

### class `TestPlanner`
- **Inherits from**: abc.ABC

> Core logic engine mapping changes to testing strategies and prioritization queues.

**Methods:**

- `def plan_tests(self, objective: str, affected_files: List[str], code_summary: CodeStructureSummary) -> TestPlanningResult`
  * Determines strategies, scopes, suites, prioritization order, and estimated timelines.

### class `AITestEngineerService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Central service managing test planning, memory storage, and reports syncing.

**Methods:**

- `def generate_test_plan(self, workspace_id: str, objective: str, affected_files: List[str], code_summary: CodeStructureSummary) -> TestPlanningResult`
  * Orchestrates test planning result generation.
- `def store_test_plan(self, result: TestPlanningResult) -> None`
  * Stores the testing plan summary inside Memory Intelligence.
- `def publish_test_plan(self, result: TestPlanningResult) -> None`
  * Syncs the testing plan report with the Knowledge Hub.

## Module: core/src/aios/services/runtime_impl.py

### class `LocalEventDispatcher`
- **Inherits from**: EventDispatcher

**Methods:**

- `def __init__(self) -> None`
- `def dispatch(self, event_name: str, payload: Dict[str, Any]) -> None`
- `def subscribe(self, event_name: str, callback: Callable[[Dict[str, Any]], None]) -> None`

### class `LocalHealthMonitor`
- **Inherits from**: HealthMonitor

**Methods:**

- `def __init__(self, runtime) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `BackgroundTaskManager`

**Methods:**

- `def __init__(self) -> None`
- `def submit(self, task: BackgroundTask) -> None`
- `def tick(self) -> None`

### class `WatcherManager`

**Methods:**

- `def __init__(self) -> None`
- `def register(self, watcher: Watcher) -> None`
- `def stop_all(self) -> None`

### class `NotificationManager`

**Methods:**

- `def __init__(self, dispatcher: EventDispatcher) -> None`
- `def notify(self, message: str) -> None`

### class `BaseSystemWatcher`
- **Inherits from**: Watcher

**Methods:**

- `def __init__(self, name: str) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def name(self) -> str`

### class `WorkspaceWatcher`
- **Inherits from**: BaseSystemWatcher

**Methods:**

- `def __init__(self) -> None`

### class `GitWatcher`
- **Inherits from**: BaseSystemWatcher

**Methods:**

- `def __init__(self) -> None`

### class `MissionWatcher`
- **Inherits from**: BaseSystemWatcher

**Methods:**

- `def __init__(self) -> None`

### class `WorkflowWatcher`
- **Inherits from**: BaseSystemWatcher

**Methods:**

- `def __init__(self) -> None`

### class `ProviderWatcher`
- **Inherits from**: BaseSystemWatcher

**Methods:**

- `def __init__(self) -> None`

### class `MemoryWatcher`
- **Inherits from**: BaseSystemWatcher

**Methods:**

- `def __init__(self) -> None`

### class `LocalRuntime`
- **Inherits from**: RuntimeService

**Methods:**

- `def __init__(self, kernel) -> None`
- `def state(self) -> RuntimeState`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def register_watcher(self, watcher: Watcher) -> None`
- `def submit_task(self, task: BackgroundTask) -> None`
- `def get_session(self) -> Optional[RuntimeSession]`

## Module: core/src/aios/services/approval_impl.py

### class `MinValidationScoreRule`
- **Inherits from**: ApprovalRule

> Ensures validation overall score meets targeted gating value.

**Methods:**

- `def __init__(self, min_score: float) -> None`
- `def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]`

### class `RequiredCoverageRule`
- **Inherits from**: ApprovalRule

> Ensures test statement coverage matches minimum thresholds.

**Methods:**

- `def __init__(self, min_coverage: float) -> None`
- `def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]`

### class `MaxRiskLevelRule`
- **Inherits from**: ApprovalRule

> Enforces safety constraints by bounding implementation risks level.

**Methods:**

- `def __init__(self, max_allowed_level: str) -> None`
- `def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]`

### class `DocumentationCompletenessRule`
- **Inherits from**: ApprovalRule

> Validates that documentation files exist or are fully complete.

**Methods:**

- `def __init__(self) -> None`
- `def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]`

### class `CriticalFailureThresholdRule`
- **Inherits from**: ApprovalRule

> Guards execution pathways from running when critical bugs/failures exist.

**Methods:**

- `def __init__(self, max_failures: int) -> None`
- `def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]`

### class `EngineeringProfileRequirementsRule`
- **Inherits from**: ApprovalRule

> Verifies alignment between targets and global profile standards.

**Methods:**

- `def __init__(self, target_language: str) -> None`
- `def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]`

### class `LocalApprovalValidator`
- **Inherits from**: ApprovalValidator

> Verifies that approval packages are complete and consistent.

**Methods:**

- `def validate_package(self, package: ApprovalPackage) -> List[str]`
- `def check_duplicate_request(self, request: ApprovalRequest, history: List[ApprovalSummary]) -> bool`

### class `LocalApprovalManager`
- **Inherits from**: ApprovalManager

> Concrete compiler and policy evaluation controller.

**Methods:**

- `def create_session(self, request: ApprovalRequest) -> ApprovalSession`
- `def compile_package(self, session: ApprovalSession) -> ApprovalPackage`
- `def evaluate_policy(self, package: ApprovalPackage) -> ApprovalDecision`

### class `LocalApprovalEngineService`
- **Inherits from**: ApprovalEngineService

> Central orchestrator managing approval sessions, storage in memory, and reporting.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def _get_policy(self) -> PersistencePolicy`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def request_approval(self, request: ApprovalRequest) -> ApprovalSession`
- `def get_session(self, session_id: str) -> Optional[ApprovalSession]`
- `def get_history(self, workspace_id: str) -> ApprovalHistory`
- `def store_approval_summary(self, session: ApprovalSession) -> None`
- `def publish_approval_report(self, report: ApprovalReport) -> None`

## Module: core/src/aios/services/session.py

### class `Session`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Strongly typed representation of a user session.

### class `SessionStartedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published immediately after a session is successfully started.

### class `SessionEndedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published immediately after a session is successfully ended.

### class `SessionService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Interface for managing the lifecycle and persistence of interactive sessions.

**Methods:**

- `def start_session(self, workspace_path: str, session_id: Optional[str]) -> Session`
  * Starts a new session for the given workspace path and publishes SessionStartedEvent.
- `def end_session(self) -> None`
  * Ends the active session and publishes SessionEndedEvent.
- `def get_current_session(self) -> Optional[Session]`
  * Returns the currently active session, if any.
- `def create_session(self, workspace_path: str) -> str`
  * Launches a new session and returns the session ID.
- `def save_session(self, session_id: str) -> None`
  * Persists the active session state.
- `def get_active_session_id(self) -> Optional[str]`
  * Returns the current active session ID, if any.

## Module: core/src/aios/services/memory_storage.py

### class `MemoryStorage`
- **Inherits from**: abc.ABC

> Interface for memory storage engines.

**Methods:**

- `def save_memory(self, memory: Memory) -> None`
  * Saves or updates a memory in the storage backend.
- `def get_memory(self, memory_id: str) -> Optional[Memory]`
  * Retrieves a memory from the storage backend.
- `def delete_memory(self, memory_id: str) -> None`
  * Deletes a memory from the storage backend.
- `def load_all_memories(self) -> List[Memory]`
  * Loads and returns all memories from the storage backend.
- `def commit(self) -> None`
  * Persists any pending changes to the storage backend.

## Module: core/src/aios/services/intent_engine.py

### class `IntentContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Tracks variables, context information, and retrieved memories.

### class `IntentPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a structured execution graph generated by the Intent Engine.

### class `IntentResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents the output of the Intent Engine analysis and planning step.

### class `IntentClassifier`
- **Inherits from**: abc.ABC

> Classifies user queries into one or more system categories.

**Methods:**

- `def classify(self, text: str) -> List[str]`
  * Classifies text into categories: Career, Project, Research, Learning, Automation, Planning, Coding, GitHub, Knowledge, Mission, Daily, Conversation, Hybrid.

### class `IntentAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes context dependencies and requirements for a set of categories.

**Methods:**

- `def analyze(self, text: str, context: IntentContext) -> Dict[str, Any]`
  * Analyzes context requirements, dependencies, and expected outputs for categories.

### class `IntentResolver`
- **Inherits from**: abc.ABC

> Resolves natural language objectives into structured IntentPlans.

**Methods:**

- `def resolve_plan(self, text: str, context: IntentContext) -> IntentPlan`
  * Translates a user objective and context into a structured IntentPlan execution graph.

### class `IntentEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

> The conductor service determining which capabilities participate to achieve the objective.

**Methods:**

- `def process_objective(self, objective: str) -> IntentResult`
  * Processes the objective, retrieves memories, plans service orchestration, and evaluates safety.

## Module: core/src/aios/services/code_generation.py

### class `GenerationPolicy`
- **Inherits from**: Enum
- **Type**: Enum

> Policies dictating structural refactoring permissibility levels.

### class `GeneratedArtifact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a generated code file artifact target.

### class `GenerationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Final code generation execution telemetry report.

### class `GenerationSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Active code generation session lifecycle tracker.

### class `CodePlanner`
- **Inherits from**: abc.ABC

> Formulates multi-step generation execution schedules.

**Methods:**

- `def plan_generation_steps(self, objective: str, policy: GenerationPolicy) -> List[Dict[str, Any]]`
  * Determines ordered files target steps and actions.

### class `ContextAssembler`
- **Inherits from**: abc.ABC

> Assembles minimalist relevant file context without bloated prompts.

**Methods:**

- `def assemble_context(self, file_path: str, code_summary: CodeStructureSummary) -> str`
  * Aggregates direct imports, interfaces, and minimal code snippets.

### class `PromptBuilder`
- **Inherits from**: abc.ABC

> Formats system instructions, metadata, and task scopes.

**Methods:**

- `def build_prompt(self, objective: str, target_file: str, context: str, policy: GenerationPolicy) -> LLMRequest`
  * Packages LLMRequest with category, priority, and JSON schemas.

### class `FileGenerator`
- **Inherits from**: abc.ABC

> Handles file creations within the isolated sandboxes.

**Methods:**

- `def create_file(self, workspace_root: str, file_path: str, content: str) -> GeneratedArtifact`
  * Writes new file to workspace directory.

### class `FileEditor`
- **Inherits from**: abc.ABC

> Applies modifications, appends, and replacements inside sandboxes.

**Methods:**

- `def edit_file(self, workspace_root: str, file_path: str, edits: str) -> GeneratedArtifact`
  * Modifies existing sandbox files.

### class `SyntaxValidator`
- **Inherits from**: abc.ABC

> Runs compiler checks and ast validation (e.g. compile() in python).

**Methods:**

- `def validate_syntax(self, content: str, file_path: str) -> tuple[bool, str]`
  * Validates that syntax parses cleanly without syntax errors.

### class `StyleValidator`
- **Inherits from**: abc.ABC

> Checks basic layout, spacing, and convention compliance.

**Methods:**

- `def validate_style(self, content: str, file_path: str) -> tuple[bool, str]`
  * Validates standard rules formatting and conventions.

### class `ImportValidator`
- **Inherits from**: abc.ABC

> Verifies referenced packages/modules exist in target workspace.

**Methods:**

- `def validate_imports(self, content: str, file_path: str, code_summary: CodeStructureSummary) -> tuple[bool, str]`
  * Verifies that imports align with code summary dependencies.

### class `GenerationValidator`
- **Inherits from**: abc.ABC

> Orchestrates comprehensive validation pipelines.

**Methods:**

- `def validate_artifact(self, artifact: GeneratedArtifact, code_summary: CodeStructureSummary) -> tuple[bool, List[str]]`
  * Aggregates syntax, style, and import verifications.

### class `CodeGenerationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service orchestrating code planning, generation sessions, and reviews.

**Methods:**

- `def start_session(self, workspace_id: str, policy: GenerationPolicy) -> GenerationSession`
  * Starts a tracked generation session.
- `def generate_code(self, session: GenerationSession, target_file: str, objective: str, workspace_root: str, code_summary: CodeStructureSummary) -> GenerationReport`
  * Executes Code Generation workflow using the ModelService.
- `def store_generation_summary(self, report: GenerationReport) -> None`
  * Stores code generation session stats inside Memory.
- `def publish_generation_report(self, report: GenerationReport) -> None`
  * Syncs the code generation report with the Knowledge Hub.

## Module: core/src/aios/services/n8n_integration_impl.py

### class `LocalN8NClient`
- **Inherits from**: N8NClient

> Concrete client executing real REST calls to self-hosted n8n, falling back to mock when offline.

**Methods:**

- `def __init__(self) -> None`
- `def upload_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]`
- `def update_workflow(self, workflow_id: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]`
- `def delete_workflow(self, workflow_id: str) -> bool`
- `def list_workflows(self) -> List[Dict[str, Any]]`
- `def get_workflow(self, workflow_id: str) -> Dict[str, Any]`
- `def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]`
- `def get_execution(self, execution_id: str) -> Dict[str, Any]`
- `def list_executions(self, workflow_id: str) -> List[Dict[str, Any]]`
- `def activate_workflow(self, workflow_id: str) -> bool`
- `def deactivate_workflow(self, workflow_id: str) -> bool`

### class `LocalN8NWorkflowRepository`
- **Inherits from**: N8NWorkflowRepository

> Workflow metadata catalog.

**Methods:**

- `def __init__(self, registry: Optional[Any]) -> None`
- `def save_workflow_metadata(self, workflow_id: str, metadata: Dict[str, Any]) -> None`
- `def get_workflow_metadata(self, workflow_id: str) -> Optional[Dict[str, Any]]`

### class `LocalN8NExecutionRepository`
- **Inherits from**: N8NExecutionRepository

> Executions metadata catalog.

**Methods:**

- `def __init__(self, registry: Optional[Any]) -> None`
- `def save_execution_metadata(self, execution_id: str, metadata: Dict[str, Any]) -> None`

### class `LocalN8NCredentialRepository`
- **Inherits from**: N8NCredentialRepository

> Credential vault indexing references.

**Methods:**

- `def __init__(self) -> None`
- `def register_credential_reference(self, name: str, value: str) -> None`

### class `LocalN8NHealthMonitor`
- **Inherits from**: N8NHealthMonitor

> Ping endpoints returning low latency and capabilities list, falling back to mock when offline.

**Methods:**

- `def __init__(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `LocalN8NWorkspaceMapper`
- **Inherits from**: N8NWorkspaceMapper

> Maps workflows ownership IDs to workspaces identifiers.

**Methods:**

- `def __init__(self) -> None`
- `def map_workflow_to_workspace(self, workflow_id: str, workspace_id: str) -> None`
- `def get_workspace_for_workflow(self, workflow_id: str) -> Optional[str]`

### class `LocalN8NValidator`
- **Inherits from**: N8NValidator

> Checks URL patterns and basic connections profiles parameters.

**Methods:**

- `def validate_server_config(self, profile: N8NConnectionProfile) -> List[str]`

### class `LocalN8NIntegrationService`
- **Inherits from**: N8NIntegrationService

> Conductor service managing client uploads, health checks, report generators, and Notion report syncing.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def upload_workflow_json(self, workspace_id: str, workflow_json: Dict[str, Any]) -> str`
- `def trigger_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]`
- `def get_health_status(self) -> N8NIntegrationReport`
- `def get_history(self, workspace_id: str) -> List[N8NIntegrationReport]`
- `def store_integration_summary(self, report_id: str) -> None`
- `def publish_integration_report(self, report: N8NIntegrationReport) -> None`

## Module: core/src/aios/services/code_generation_impl.py

### class `LocalCodePlanner`
- **Inherits from**: CodePlanner

> Generates sequential change tasks based on targeted policies.

**Methods:**

- `def plan_generation_steps(self, objective: str, policy: GenerationPolicy) -> List[Dict[str, Any]]`

### class `LocalContextAssembler`
- **Inherits from**: ContextAssembler

> Extracts direct imports and interface summaries to minimize prompt sizes.

**Methods:**

- `def assemble_context(self, file_path: str, code_summary: CodeStructureSummary) -> str`

### class `LocalPromptBuilder`
- **Inherits from**: PromptBuilder

> Builds clean, structured instruction templates incorporating policy constraints.

**Methods:**

- `def build_prompt(self, objective: str, target_file: str, context: str, policy: GenerationPolicy) -> LLMRequest`

### class `LocalFileGenerator`
- **Inherits from**: FileGenerator

> Handles workspace file creation operations.

**Methods:**

- `def create_file(self, workspace_root: str, file_path: str, content: str) -> GeneratedArtifact`

### class `LocalFileEditor`
- **Inherits from**: FileEditor

> Handles workspace file edit operations.

**Methods:**

- `def edit_file(self, workspace_root: str, file_path: str, edits: str) -> GeneratedArtifact`

### class `LocalSyntaxValidator`
- **Inherits from**: SyntaxValidator

> Validates code compilation using standard compile() function.

**Methods:**

- `def validate_syntax(self, content: str, file_path: str) -> tuple[bool, str]`

### class `LocalStyleValidator`
- **Inherits from**: StyleValidator

> Enforces basic spacing, line lengths, and convention checks.

**Methods:**

- `def validate_style(self, content: str, file_path: str) -> tuple[bool, str]`

### class `LocalImportValidator`
- **Inherits from**: ImportValidator

> Parses AST to verify imported dependencies are registered.

**Methods:**

- `def validate_imports(self, content: str, file_path: str, code_summary: CodeStructureSummary) -> tuple[bool, str]`

### class `LocalGenerationValidator`
- **Inherits from**: GenerationValidator

> Aggregates syntax, style, and import validations.

**Methods:**

- `def __init__(self) -> None`
- `def validate_artifact(self, artifact: GeneratedArtifact, code_summary: CodeStructureSummary) -> tuple[bool, List[str]]`

### class `LocalCodeGenerationService`
- **Inherits from**: CodeGenerationService

> Coordinating service utilizing LLM model routing to write safe workspace files.

**Methods:**

- `def __init__(self, memory_service: MemoryService, model_service: ModelService, knowledge_hub: Optional[KnowledgeHubService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def start_session(self, workspace_id: str, policy: GenerationPolicy) -> GenerationSession`
- `def generate_code(self, session: GenerationSession, target_file: str, objective: str, workspace_root: str, code_summary: CodeStructureSummary) -> GenerationReport`
- `def store_generation_summary(self, report: GenerationReport) -> None`
- `def publish_generation_report(self, report: GenerationReport) -> None`

## Module: core/src/aios/services/test_impact.py

### class `ImpactNode`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a codebase node within an impact map graph.

### class `ImpactEdge`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents dependency/call relationships between impact nodes.

### class `ImpactGraph`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated graph structure representing codebase changes propagation paths.

### class `AffectedComponent`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a component impacted directly or indirectly by modifications.

### class `AffectedTestSuite`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents an existing test suite impacted by codebase changes.

### class `RegressionCandidate`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a codebase module prone to regressions.

### class `RiskAssessment`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Assesses change risk ratings across architectural borders.

### class `CoverageTarget`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Testing coverage goal for a specific file target.

### class `ImpactAnalysisResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Final outcome bundle of a change impact analyzer execution.

### class `ChangeImpactAnalyzer`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Primary service coordinating testing impact calculations, memory persistency, and syncing.

**Methods:**

- `def analyze_change_impact(self, workspace_id: str, objective: str, affected_files: List[str], code_summary: CodeStructureSummary) -> ImpactAnalysisResult`
  * Determines impacted interfaces, database nodes, regression risks, and coverage targets.
- `def store_impact_result(self, result: ImpactAnalysisResult) -> None`
  * Stores change impact summaries inside Memory.
- `def publish_impact_report(self, result: ImpactAnalysisResult) -> None`
  * Syncs change impact report with the Knowledge Hub.

## Module: core/src/aios/services/readme_intelligence_impl.py

### class `LocalREADMEAnalyzer`
- **Inherits from**: READMEAnalyzer

> Concrete analyzer identifying missing standard README sections.

**Methods:**

- `def analyze_readme(self, existing_content: str, workspace_metadata: Dict[str, Any]) -> READMEReport`

### class `LocalREADMEPlanner`
- **Inherits from**: READMEPlanner

> Concrete sections planner generating content template placeholders.

**Methods:**

- `def plan_sections(self, report: READMEReport, template: READMETemplate) -> List[READMESection]`

### class `LocalREADMEValidator`
- **Inherits from**: READMEValidator

> Concrete validator flagging link errors or duplicate headers.

**Methods:**

- `def validate_readme(self, content: str) -> List[str]`

### class `LocalREADMEGenerator`
- **Inherits from**: READMEGenerator

> Formats list of sections into single markdown string.

**Methods:**

- `def generate_readme(self, workspace_id: str, sections: List[READMESection]) -> READMEArtifact`

### class `LocalREADMEUpdater`
- **Inherits from**: READMEUpdater

> Updates targeted sections in existing files by heading keys.

**Methods:**

- `def update_readme(self, existing: READMEArtifact, changes: List[READMESection]) -> READMEArtifact`

### class `LocalREADMEIntelligenceService`
- **Inherits from**: READMEIntelligenceService

> Coordinating README configuration manager routing LLM refinements and caching metadata.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_and_generate(self, workspace_id: str, existing_content: str, workspace_metadata: Dict[str, Any], template: READMETemplate) -> READMEArtifact`
- `def store_readme_summary(self, summary: READMESummary) -> None`
- `def publish_readme_report(self, report: READMEReport) -> None`

## Module: core/src/aios/services/test_impact_impl.py

### class `LocalChangeImpactAnalyzer`
- **Inherits from**: ChangeImpactAnalyzer

> Calculates propagation maps, runs risks assessments, and determines coverage scopes.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_change_impact(self, workspace_id: str, objective: str, affected_files: List[str], code_summary: CodeStructureSummary) -> ImpactAnalysisResult`
- `def store_impact_result(self, result: ImpactAnalysisResult) -> None`
- `def publish_impact_report(self, result: ImpactAnalysisResult) -> None`

## Module: core/src/aios/services/review.py

### class `ReviewCategory`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate review domains evaluated by the Review Engine.

### class `ReviewSeverity`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate finding impact levels.

### class `ReviewEvidence`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregated evidence details backing a review finding.

### class `ReviewRecommendation`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Actionable remediation steps addressing review finding diagnostics.

### class `ReviewFinding`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Diagnostic discover details compiled during code review.

### class `ReviewSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Executive metrics summary detailing overall review outcomes.

### class `ReviewReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregated code review outcome report payload.

### class `ReviewSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Lifecycle tracking for an active code review evaluation run.

### class `ReviewAnalyzer`
- **Inherits from**: abc.ABC

> Core review analyzer engine auditing packages to discover findings.

**Methods:**

- `def analyze_package(self, workspace_id: str, package: Any) -> tuple[ReviewSummary, List[ReviewFinding]]`
  * Scans the package components and returns compiled summary and findings list.

### class `ReviewValidator`
- **Inherits from**: abc.ABC

> Enforces integrity, completeness, and consistency checks on review findings.

**Methods:**

- `def validate_review(self, report: ReviewReport) -> List[str]`
  * Validates consistency and returns warnings list.

### class `ReviewEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Primary service coordinating reviews, workspace persistence, memory stores, and reports syncs.

**Methods:**

- `def run_review(self, workspace_id: str, package: Any) -> ReviewSession`
  * Executes full automated analysis on approval package.
- `def get_session(self, session_id: str) -> Optional[ReviewSession]`
  * Retrieves session details by id.
- `def get_history(self, workspace_id: str) -> List[ReviewSummary]`
  * Retrieves past review summary history for workspace.
- `def store_review_summary(self, session: ReviewSession) -> None`
  * Saves severity statistics and summary in memory. Never saves source code.
- `def publish_review_report(self, report: ReviewReport) -> None`
  * Publishes sync report to Knowledge Hub on demand.

## Module: core/src/aios/services/runtime.py

### class `RuntimeState`
- **Inherits from**: Enum
- **Type**: Enum

### class `RuntimeSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `RuntimeConfiguration`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `BackgroundTask`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Watcher`
- **Inherits from**: abc.ABC

**Methods:**

- `def start(self) -> None`
  * Starts monitoring the target resource.
- `def stop(self) -> None`
  * Stops monitoring the target resource.
- `def name(self) -> str`
  * Returns the name of the watcher.

### class `EventDispatcher`
- **Inherits from**: abc.ABC

**Methods:**

- `def dispatch(self, event_name: str, payload: Dict[str, Any]) -> None`
  * Publishes strongly typed runtime events to listeners.
- `def subscribe(self, event_name: str, callback: Callable[[Dict[str, Any]], None]) -> None`
  * Subscribes a callback listener to specific event types.

### class `HealthMonitor`
- **Inherits from**: abc.ABC

**Methods:**

- `def check_health(self) -> Dict[str, Any]`
  * Audits status checks across all registered core services.

### class `RuntimeService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def state(self) -> RuntimeState`
  * Returns the active state of the runtime engine.
- `def start(self) -> None`
  * Executes startup sequence, loading configurations and loading services.
- `def stop(self) -> None`
  * Gracefully shuts down running watchers and background threads.
- `def register_watcher(self, watcher: Watcher) -> None`
  * Adds and starts a system watcher.
- `def submit_task(self, task: BackgroundTask) -> None`
  * Submits a delayed or recurring task to the background pool.
- `def get_session(self) -> Optional[RuntimeSession]`
  * Returns the current active session.

## Module: core/src/aios/services/project_intelligence_impl.py

### class `LocalProjectIntelligence`
- **Inherits from**: ProjectIntelligenceService

**Methods:**

- `def __init__(self, cache_filename: str) -> None`
- `def initialize(self) -> None`
- `def analyze_workspace(self, workspace_root: str) -> ProjectContext`
- `def _load_gitignore_rules(self, root_path: Path) -> List[str]`
- `def _is_ignored(self, path_str: str, rules: List[str]) -> bool`
- `def _analyze_file(self, file_path: Path, rel_file_str: str) -> tuple[List[Dict[str, Any]], int]`
- `def _detect_project_configs(self, root_path: Path, package_managers: List[str], frameworks: List[str], dependencies: List[str]) -> None`
- `def _get_git_metadata(self, workspace_root: str) -> tuple[Optional[str], List[str]]`

## Module: core/src/aios/services/model.py

### class `LLMRequest`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `LLMResponse`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ModelService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def execute_prompt(self, prompt: str, system_instruction: Optional[str]) -> str`
- `def execute_request(self, request: LLMRequest) -> LLMResponse`
- `def execute_stream(self, request: LLMRequest) -> Iterator[LLMResponse]`

## Module: core/src/aios/services/developer_workspace.py

### class `DeveloperWorkspaceInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `DeveloperWorkspaceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_workspace_info(self, workspace_root: str) -> DeveloperWorkspaceInfo`
  * Retrieves structured information about the active git state, tests, and configuration.
- `def execute_safe_command(self, command: str, args: List[str], workspace_root: str) -> Dict[str, Any]`
  * Executes a development command (like tests or linting) safely, validating parameters.

## Module: core/src/aios/services/event_bus.py

### class `Event`
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Base class for all strongly typed events in the system.

### class `EventBusService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Interface for synchronous event registration, subscription, and publishing.

**Methods:**

- `def register_event_type(self, event_type: Type[Event]) -> None`
  * Registers a strongly typed event class with the bus.
- `def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None`
  * Subscribes an isolated handler to a specific Event type.
- `def unsubscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None`
  * Unsubscribes a handler from a specific Event type.
- `def publish(self, event: Event) -> None`
  * Publishes an event synchronously to all registered subscribers.

### class `KernelStartedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Event published when the Kernel has successfully booted and transitioned to READY.

## Module: core/src/aios/services/ai_workspace_impl.py

### class `LocalWorkspaceValidator`
- **Inherits from**: WorkspaceValidator

> Verifies directory structures and session ownership details.

**Methods:**

- `def validate_workspace(self, workspace_root: str) -> tuple[bool, str]`
- `def validate_snapshot(self, snapshot: WorkspaceSnapshot) -> tuple[bool, str]`
- `def validate_session(self, session: WorkspaceSession) -> tuple[bool, str]`

### class `LocalWorkspaceCleaner`
- **Inherits from**: WorkspaceCleaner

> Safely cleans temp files and purges obsolete workspaces recursively.

**Methods:**

- `def cleanup_temp_files(self, workspace_root: str) -> int`
- `def purge_workspace(self, workspace_root: str) -> None`

### class `LocalAIWorkspaceService`
- **Inherits from**: AIWorkspaceService

> Orchestrates workspace lifecycles, files copies, and snapshot rollbacks.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def _get_policy(self) -> PersistencePolicy`
- `def _get_workspace_meta(self, workspace_id: str) -> Optional[WorkspaceMetadata]`
- `def _get_session(self, workspace_id: str) -> Optional[WorkspaceSession]`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def create_workspace(self, original_repo_root: str) -> WorkspaceSession`
- `def validate_workspace(self, workspace_id: str) -> tuple[bool, str]`
- `def open_workspace(self, workspace_id: str) -> WorkspaceSession`
- `def close_workspace(self, workspace_id: str) -> None`
- `def cleanup_workspace(self, workspace_id: str) -> int`
- `def archive_workspace(self, workspace_id: str) -> str`
- `def restore_workspace(self, archive_path: str) -> WorkspaceSession`
- `def destroy_workspace(self, workspace_id: str) -> None`
- `def create_snapshot(self, workspace_id: str, description: str) -> WorkspaceSnapshot`
- `def restore_snapshot(self, workspace_id: str, snapshot_id: str) -> WorkspaceRecovery`
- `def track_change(self, workspace_id: str, change: WorkspaceChange) -> None`
- `def get_changes(self, workspace_id: str) -> List[WorkspaceChange]`
- `def store_workspace_summary(self, workspace_id: str) -> None`
- `def publish_workspace_report(self, workspace_id: str) -> None`

## Module: core/src/aios/services/architecture_documentation.py

### class `ArchitectureComponent`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A distinct structural part of the system (e.g. Service, Controller).

### class `ArchitectureLayer`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> An architectural division containing components (e.g., Kernel Layer).

### class `ArchitectureRelationship`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> System dependency coupling between two components.

### class `ArchitectureDiagram`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Mermaid diagram output code string.

### class `ArchitectureDecision`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> An Architecture Decision Record (ADR) reference.

### class `ArchitectureSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Summary metrics of components and active layers counts.

### class `ArchitectureReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Architecture health audit detailing layers violations or unused parts.

### class `ArchitectureAnalyzer`
- **Inherits from**: abc.ABC

> Compares codebase layouts to find circular dependencies or structural violations.

**Methods:**

- `def analyze_architecture(self, code_structure: Dict[str, Any], existing_docs: str) -> ArchitectureReport`
  * Finds violations and logs metrics.

### class `ArchitectureDocumentPlanner`
- **Inherits from**: abc.ABC

> Plans structure layout matching formatting rules.

**Methods:**

- `def plan_architecture_documentation(self, report: ArchitectureReport) -> List[ArchitectureComponent]`
  * Assembles list of components requiring documentation.

### class `ArchitectureValidator`
- **Inherits from**: abc.ABC

> Checks Mermaid diagram consistency or broken references.

**Methods:**

- `def validate_architecture_document(self, diagram: ArchitectureDiagram, registry: 'ArchitectureRegistry') -> List[str]`
  * Returns validation errors list.

### class `ArchitectureRegistry`

> Thread-safe index cataloging components and decisions.

**Methods:**

- `def __init__(self) -> None`
- `def register_component(self, component: ArchitectureComponent) -> None`
- `def get_component(self, name: str) -> Optional[ArchitectureComponent]`
- `def register_layer(self, layer: ArchitectureLayer) -> None`
- `def get_layer(self, name: str) -> Optional[ArchitectureLayer]`
- `def add_relationship(self, rel: ArchitectureRelationship) -> None`
- `def list_relationships(self) -> List[ArchitectureRelationship]`
- `def register_decision(self, decision: ArchitectureDecision) -> None`
- `def get_decision(self, decision_id: str) -> Optional[ArchitectureDecision]`

### class `ArchitectureDocumentationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service generating architecture structures, diagram layouts, and memory logs.

**Methods:**

- `def generate_architecture_documentation(self, workspace_id: str, code_structure: Dict[str, Any], existing_docs: str) -> ArchitectureDiagram`
  * Assembles Mermaid diagram layouts.
- `def store_architecture_summary(self, summary: ArchitectureSummary) -> None`
  * Logs summaries records in Memory.
- `def publish_architecture_report(self, report: ArchitectureReport) -> None`
  * Pushes reports updates to Knowledge Hub.

## Module: core/src/aios/services/event_bus_impl.py

### class `LocalEventBus`
- **Inherits from**: EventBusService

> A lightweight, synchronous, in-memory event bus.
Enforces strong event typing, registration, and isolated handler execution.

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def shutdown(self) -> None`
- `def register_event_type(self, event_type: Type[Event]) -> None`
  * Registers a strongly typed event class with the bus.
- `def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None`
  * Subscribes an isolated handler to a specific Event type.
- `def unsubscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None`
  * Unsubscribes a handler from a specific Event type.
- `def publish(self, event: Event) -> None`
  * Publishes an event synchronously to all registered subscribers.

## Module: core/src/aios/services/approval_history_impl.py

### class `LocalApprovalHistoryValidator`
- **Inherits from**: ApprovalHistoryValidator

> Enforces state transition rules, schema checks, and statistics limits.

**Methods:**

- `def validate_transition(self, from_state: ApprovalState, to_state: ApprovalState) -> bool`
- `def validate_report(self, report: ApprovalHistoryReport) -> List[str]`

### class `LocalApprovalHistoryAnalyzer`
- **Inherits from**: ApprovalHistoryAnalyzer

> Calculates aggregates, computes trend slopes, and identifies recurring pattern gaps.

**Methods:**

- `def compile_statistics(self, records: List[ApprovalDecisionRecord]) -> ApprovalStatistics`
- `def analyze_trends(self, records: List[ApprovalDecisionRecord]) -> List[ApprovalTrend]`
- `def discover_patterns(self, entries: List[ApprovalHistoryEntry], records: List[ApprovalDecisionRecord]) -> List[ApprovalPattern]`

### class `LocalApprovalHistoryService`
- **Inherits from**: ApprovalHistoryService

> Central manager coordinating transitions log, stats compiles, and report generation.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def _get_policy(self) -> PersistencePolicy`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def create_history_entry(self, workspace_id: str, session_id: str, initial_state: ApprovalState, actor: str) -> ApprovalHistoryEntry`
- `def transition_state(self, workspace_id: str, session_id: str, target_state: ApprovalState, actor: str, reason: str) -> ApprovalHistoryEntry`
- `def record_decision(self, record: ApprovalDecisionRecord) -> None`
- `def get_history_entry(self, session_id: str) -> Optional[ApprovalHistoryEntry]`
- `def get_decision_records(self, workspace_id: str) -> List[ApprovalDecisionRecord]`
- `def run_history_analysis(self, workspace_id: str) -> ApprovalHistoryReport`
- `def store_history_summary(self, workspace_id: str) -> None`
- `def publish_history_report(self, report: ApprovalHistoryReport) -> None`

## Module: core/src/aios/services/test_engineer_impl.py

### class `LocalTestPlanner`
- **Inherits from**: TestPlanner

> Rule-based test planning logic to evaluate impact and strategies.

**Methods:**

- `def plan_tests(self, objective: str, affected_files: List[str], code_summary: CodeStructureSummary) -> TestPlanningResult`

### class `LocalAITestEngineerService`
- **Inherits from**: AITestEngineerService

> Primary Test Engineer coordinating plans, caching results, and publishing reports.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_test_plan(self, workspace_id: str, objective: str, affected_files: List[str], code_summary: CodeStructureSummary) -> TestPlanningResult`
- `def store_test_plan(self, result: TestPlanningResult) -> None`
- `def publish_test_plan(self, result: TestPlanningResult) -> None`

## Module: core/src/aios/services/personal_impl.py

### class `LocalPersonalService`
- **Inherits from**: PersonalService

**Methods:**

- `def __init__(self, cache_filename: str, workspace_root: str) -> None`
- `def initialize(self) -> None`
- `def get_profile(self, profile_id: str) -> Optional[PersonalProfile]`
- `def create_profile(self, profile: PersonalProfile) -> PersonalProfile`
- `def update_profile(self, profile_id: str, profile: PersonalProfile) -> PersonalProfile`
- `def delete_profile(self, profile_id: str) -> bool`
- `def switch_active_profile(self, profile_id: str) -> bool`
- `def get_active_profile(self) -> Optional[PersonalProfile]`
- `def list_profiles(self) -> List[str]`
- `def get_relevant_context(self, objective: str) -> Dict[str, Any]`
- `def _save_cache(self) -> None`
- `def _serialize_profile(self, p: PersonalProfile) -> Dict[str, Any]`
- `def _serialize_resume(self, r: Resume) -> Dict[str, Any]`
- `def _deserialize_profile(self, data: Dict[str, Any]) -> PersonalProfile`

## Module: core/src/aios/services/stubs.py

### class `StubContextService`
- **Inherits from**: ContextService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def detect_context(self) -> WorkspaceContext`
- `def get_current_context(self) -> WorkspaceContext | None`

### class `StubMemoryService`
- **Inherits from**: MemoryService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def add_memory(self, content: str, memory_type: MemoryType, tags: list[str], importance: int, metadata_additional: dict) -> Memory`
- `def update_memory(self, memory_id: str, content: Optional[str], tags: Optional[list[str]], importance: Optional[int], metadata_additional: Optional[dict]) -> Memory`
- `def delete_memory(self, memory_id: str) -> None`
- `def search_memory(self, query: str, memory_type: Optional[MemoryType], tags: Optional[list[str]]) -> list[Memory]`
- `def get_memory(self, memory_id: str) -> Optional[Memory]`
- `def load_workspace_memory(self, workspace_id: str) -> list[Memory]`
- `def commit(self) -> None`
- `def restore_memory(self, context: dict) -> None`
- `def observe_event(self, event: dict) -> None`
- `def commit_memory(self) -> None`
- `def prune_memory(self) -> None`

### class `StubSessionService`
- **Inherits from**: SessionService

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def start_session(self, workspace_path: str, session_id: Optional[str]) -> Session`
- `def end_session(self) -> None`
- `def get_current_session(self) -> Optional[Session]`
- `def create_session(self, workspace_path: str) -> str`
- `def save_session(self, session_id: str) -> None`
- `def get_active_session_id(self) -> Optional[str]`

### class `StubModelService`
- **Inherits from**: ModelService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def execute_prompt(self, prompt: str, system_instruction: str | None) -> str`
- `def execute_request(self, request: LLMRequest) -> LLMResponse`
- `def execute_stream(self, request: LLMRequest) -> Iterator[LLMResponse]`

### class `StubToolService`
- **Inherits from**: ToolService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def register_tool(self, tool: Tool) -> None`
- `def unregister_tool(self, name: str) -> None`
- `def list_tools(self) -> list[ToolMetadata]`
- `def execute_tool(self, name: str, arguments: dict) -> ToolResult`
- `def validate_tool(self, name: str, arguments: dict) -> bool`
- `def invoke_tool(self, name: str, arguments: dict) -> dict`

### class `StubEventBusService`
- **Inherits from**: EventBusService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def register_event_type(self, event_type: Type[Event]) -> None`
- `def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None`
- `def unsubscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None`
- `def publish(self, event: Event) -> None`

### class `StubIntentResolverService`
- **Inherits from**: IntentResolverService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def resolve(self, text: str) -> Intent`
- `def validate(self, intent: Intent) -> bool`
- `def classify(self, text: str) -> IntentType`

### class `StubAgentRuntimeService`
- **Inherits from**: AgentRuntimeService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def register_agent(self, agent: Agent) -> None`
- `def unregister_agent(self, name: str) -> None`
- `def execute(self, intent: Intent) -> AgentResult`
- `def interrupt(self) -> None`
- `def cancel(self) -> None`

## Module: core/src/aios/services/test_failure_impl.py

### class `LocalFailureAnalyzer`
- **Inherits from**: FailureAnalyzer

> Classifies traceback signatures and groups exceptions into clusters.

**Methods:**

- `def classify_failure(self, raw_output: str) -> FailurePattern`
- `def cluster_failures(self, signatures: List[FailureSignature]) -> List[FailureCluster]`

### class `LocalRootCauseAnalyzer`
- **Inherits from**: RootCauseAnalyzer

> Correlates call structures and execution timelines to isolate origin failure components.

**Methods:**

- `def analyze_root_cause(self, execution_summary: ExecutionSummary, code_summary: CodeStructureSummary) -> Dict[str, Any]`

### class `LocalFailureAnalysisService`
- **Inherits from**: FailureAnalysisService

> Coordinating diagnosis service utilizing Model Service routing layers for failure refinements.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def diagnose_failures(self, workspace_id: str, execution_summary: ExecutionSummary, code_summary: CodeStructureSummary) -> FailureAnalysisReport`
- `def store_failure_report(self, report: FailureAnalysisReport) -> None`
- `def publish_failure_report(self, report: FailureAnalysisReport) -> None`

## Module: core/src/aios/services/test_execution.py

### class `ExecutionTarget`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a test file, class, or method target for execution.

### class `ExecutionLog`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a log line captured during execution.

### class `ExecutionMetrics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidates execution test count totals.

### class `ExecutionResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Assembled execution metrics outcome for a single test target execution.

### class `ExecutionSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregated execution details for all execution targets run.

### class `ExecutionSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Tracks active execution session state details.

### class `TestFrameworkAdapter`
- **Inherits from**: abc.ABC

> Abstract interface defining framework-specific adapters.

**Methods:**

- `def framework_name(self) -> str`
  * Returns adapter framework name identifier.
- `def execute_tests(self, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionResult`
  * Runs test execution using framework specific process invocation.

### class `TestRunner`
- **Inherits from**: abc.ABC

> Standard execution runner orchestrating sessions.

**Methods:**

- `def run_session(self, session: ExecutionSession, workspace_root: str) -> ExecutionSummary`
  * Executes targeted session within the workspace.

### class `TestExecutor`
- **Inherits from**: abc.ABC

> Primary logic engine managing runner instances.

**Methods:**

- `def execute(self, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionSummary`
  * Triggers execution over target list.

### class `TestExecutionService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service triggering execution runs, caching summaries, and publishing reports.

**Methods:**

- `def execute_workspace_tests(self, workspace_id: str, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionSummary`
  * Triggers targeted execution flow inside workspace.
- `def store_execution_summary(self, summary: ExecutionSummary) -> None`
  * Saves execution statistics inside Memory.
- `def publish_execution_report(self, summary: ExecutionSummary) -> None`
  * Syncs execution summary reports with Knowledge Hub.

## Module: core/src/aios/services/mission_impl.py

### class `LocalMissionPlanner`
- **Inherits from**: MissionPlanner

**Methods:**

- `def plan_mission(self, objective: str, context: MissionContext) -> Mission`

### class `LocalMissionExecutor`
- **Inherits from**: MissionExecutor

**Methods:**

- `def __init__(self, agent_runtime: AgentRuntimeService) -> None`
- `def cancel(self, mission_id: str) -> None`
- `def execute_mission(self, mission: Mission, context: MissionContext) -> bool`

### class `LocalMissionRepository`
- **Inherits from**: MissionRepository

**Methods:**

- `def __init__(self, cache_filename: str, workspace_root: str) -> None`
- `def initialize(self) -> None`
- `def save_mission(self, mission: Mission) -> None`
- `def load_mission(self, mission_id: str) -> Optional[Mission]`
- `def list_missions(self) -> List[Mission]`
- `def _save_cache(self) -> None`
- `def _serialize_mission(self, m: Mission) -> Dict[str, Any]`
- `def _deserialize_mission(self, data: Dict[str, Any]) -> Mission`

### class `LocalMissionEngine`
- **Inherits from**: MissionEngine

**Methods:**

- `def __init__(self, agent_runtime: AgentRuntimeService, workspace_root: str, registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def create_mission(self, title: str, objective: str) -> Mission`
- `def start_mission(self, mission_id: str) -> bool`
- `def cancel_mission(self, mission_id: str) -> bool`
- `def get_mission(self, mission_id: str) -> Optional[Mission]`

## Module: core/src/aios/services/approval_history.py

### class `ApprovalState`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate states of the approval gating workflow state machine.

### class `ApprovalStateTransition`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Immutable transition details tracking state progression.

### class `ApprovalHistoryEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Immutable entry containing a session's workflow state transitions list.

### class `ApprovalDecisionRecord`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated telemetry record for a completed approval session.

### class `ApprovalStatistics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Statistical summary metrics derived from historical records.

### class `ApprovalTrend`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Temporal progression trend metrics details.

### class `ApprovalPattern`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Identified recurring pattern or blocker discovered from histories.

### class `ApprovalRecommendationHistory`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Historical recommendation compiled from quality patterns audits.

### class `ApprovalHistoryReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated report encapsulating statistics, trends, and pattern recommendations.

### class `ApprovalHistoryValidator`
- **Inherits from**: abc.ABC

> Enforces state transition rules, consistency metrics, and schema integrity.

**Methods:**

- `def validate_transition(self, from_state: ApprovalState, to_state: ApprovalState) -> bool`
  * Returns True if transition is valid.
- `def validate_report(self, report: ApprovalHistoryReport) -> List[str]`
  * Returns validation error list.

### class `ApprovalHistoryAnalyzer`
- **Inherits from**: abc.ABC

> Audits past decision records to extrapolate statistics, trends, and patterns.

**Methods:**

- `def compile_statistics(self, records: List[ApprovalDecisionRecord]) -> ApprovalStatistics`
  * Aggregates decision records into stats metrics.
- `def analyze_trends(self, records: List[ApprovalDecisionRecord]) -> List[ApprovalTrend]`
  * Computes metric directions over time.
- `def discover_patterns(self, entries: List[ApprovalHistoryEntry], records: List[ApprovalDecisionRecord]) -> List[ApprovalPattern]`
  * Identifies recurring blocker patterns and gaps.

### class `ApprovalHistoryService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Primary service coordinating state transitions, history logs, analytics, and reporting.

**Methods:**

- `def create_history_entry(self, workspace_id: str, session_id: str, initial_state: ApprovalState, actor: str) -> ApprovalHistoryEntry`
  * Instantiates a new state-machine history log tracker for a session.
- `def transition_state(self, workspace_id: str, session_id: str, target_state: ApprovalState, actor: str, reason: str) -> ApprovalHistoryEntry`
  * Transitions state, validating transition guidelines and appending transitions log.
- `def record_decision(self, record: ApprovalDecisionRecord) -> None`
  * Records a completed session telemetry summary.
- `def get_history_entry(self, session_id: str) -> Optional[ApprovalHistoryEntry]`
  * Retrieves history transitions for a session.
- `def get_decision_records(self, workspace_id: str) -> List[ApprovalDecisionRecord]`
  * Retrieves recorded decisions for workspace.
- `def run_history_analysis(self, workspace_id: str) -> ApprovalHistoryReport`
  * Runs analyzer queries and compiles statistics, trends, and patterns reports.
- `def store_history_summary(self, workspace_id: str) -> None`
  * Saves metadata trend and statistics to memory. Never stores source code.
- `def publish_history_report(self, report: ApprovalHistoryReport) -> None`
  * Publishes history report to Knowledge Hub Notion database on demand.

## Module: core/src/aios/services/context.py

### class `WorkspaceContext`
- **Decorators**: `dataclass(frozen=True)`
- **Type**: Dataclass

> Strongly typed representation of the active workspace context.

### class `ContextLoadedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published immediately after workspace context is successfully detected.

### class `ContextChangedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published when the active workspace context changes.

### class `ContextService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Interface for detecting, resolving, and refreshing workspace context.

**Methods:**

- `def detect_context(self) -> WorkspaceContext`
  * Inspects the workspace and resolves context signals.
- `def get_current_context(self) -> WorkspaceContext | None`
  * Returns the currently active workspace context.
- `def build_enriched_context(self, query: str, token_budget: int) -> Dict[str, Any]`
  * Assembles enriched context from runtime, workspace, conversation,

engineering, research, documentation memories, and recent retrievals.

## Module: core/src/aios/services/ai_workspace.py

### class `WorkspaceMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Tracks isolated directory configuration and metadata.

### class `WorkspaceFile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a file cloned or tracked inside the workspace.

### class `WorkspaceChange`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Tracks a metadata file operation without generating patches/diffs.

### class `WorkspaceSnapshot`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Tracks workspace file states at a given moment for rollback/recovery.

### class `WorkspaceRecovery`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Details a snapshot or workspace recovery event outcome.

### class `WorkspaceSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Lifecycle tracking for an active workspace engineering context.

### class `WorkspaceSandbox`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Manages disk allocations and directory targets for the workspace.

### class `WorkspaceValidator`
- **Inherits from**: abc.ABC

> Enforces constraints verifying structural layout and integrity.

**Methods:**

- `def validate_workspace(self, workspace_root: str) -> tuple[bool, str]`
  * Validates directories structure and layout constraints.
- `def validate_snapshot(self, snapshot: WorkspaceSnapshot) -> tuple[bool, str]`
  * Validates snapshot integrity and file lists compatibility.
- `def validate_session(self, session: WorkspaceSession) -> tuple[bool, str]`
  * Validates active ownership and access rules.

### class `WorkspaceCleaner`
- **Inherits from**: abc.ABC

> Purges temporary directories and cleans up obsolete workspaces.

**Methods:**

- `def cleanup_temp_files(self, workspace_root: str) -> int`
  * Deletes temporary files in the workspace and returns the count.
- `def purge_workspace(self, workspace_root: str) -> None`
  * Deletes all files and directories in the workspace path recursively.

### class `AIWorkspaceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Central service interface managing isolated workspace sandboxes and sessions.

**Methods:**

- `def create_workspace(self, original_repo_root: str) -> WorkspaceSession`
  * Initializes directories, clones workspace files, and registers session.
- `def validate_workspace(self, workspace_id: str) -> tuple[bool, str]`
  * Runs integrity and structural checks on the workspace.
- `def open_workspace(self, workspace_id: str) -> WorkspaceSession`
  * Opens/activates an existing closed workspace.
- `def close_workspace(self, workspace_id: str) -> None`
  * Marks workspace session as closed.
- `def cleanup_workspace(self, workspace_id: str) -> int`
  * Cleans temporary files and logs in the workspace directory.
- `def archive_workspace(self, workspace_id: str) -> str`
  * Compresses the workspace directory to an archive and returns its file path.
- `def restore_workspace(self, archive_path: str) -> WorkspaceSession`
  * Restores a workspace directory from an archive.
- `def destroy_workspace(self, workspace_id: str) -> None`
  * Permanently deletes the workspace directories and data.
- `def create_snapshot(self, workspace_id: str, description: str) -> WorkspaceSnapshot`
  * Saves current state and returns snapshot metadata.
- `def restore_snapshot(self, workspace_id: str, snapshot_id: str) -> WorkspaceRecovery`
  * Restores file configurations to match a saved snapshot.
- `def track_change(self, workspace_id: str, change: WorkspaceChange) -> None`
  * Registers a change event in the session log.
- `def get_changes(self, workspace_id: str) -> List[WorkspaceChange]`
  * Retrieves registered workspace changes.
- `def store_workspace_summary(self, workspace_id: str) -> None`
  * Stores the workspace session summary in Memory Intelligence.
- `def publish_workspace_report(self, workspace_id: str) -> None`
  * Publishes the workspace engineering report to the Knowledge Hub.

## Module: core/src/aios/services/workflow_optimization_impl.py

### class `LocalWorkflowCostAnalyzer`
- **Inherits from**: WorkflowCostAnalyzer

> Analyzes cloud billing and token usage metrics.

**Methods:**

- `def analyze_cost(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `LocalWorkflowLatencyAnalyzer`
- **Inherits from**: WorkflowLatencyAnalyzer

> Analyzes execution durations to clear delay bottlenecks.

**Methods:**

- `def analyze_latency(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `LocalWorkflowParallelizationAnalyzer`
- **Inherits from**: WorkflowParallelizationAnalyzer

> Detects sequential nodes eligible for concurrent execution.

**Methods:**

- `def analyze_parallelization(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `LocalWorkflowRedundancyAnalyzer`
- **Inherits from**: WorkflowRedundancyAnalyzer

> Flags duplicated tasks or duplicate API requests.

**Methods:**

- `def analyze_redundancy(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `LocalWorkflowSchedulingAnalyzer`
- **Inherits from**: WorkflowSchedulingAnalyzer

> Analyzes cron intervals to trim scheduler collisions.

**Methods:**

- `def analyze_scheduling(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `LocalWorkflowResourceAnalyzer`
- **Inherits from**: WorkflowResourceAnalyzer

> Trims high resource bounds.

**Methods:**

- `def analyze_resources(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `LocalWorkflowComplexityAnalyzer`
- **Inherits from**: WorkflowComplexityAnalyzer

> Measures graph complexity and maintains metric scores.

**Methods:**

- `def analyze_complexity(self, workflow_graph: Any) -> Dict[str, float]`

### class `LocalWorkflowOptimizationValidator`
- **Inherits from**: WorkflowOptimizationValidator

> Validates duplicate recommendation IDs and confidence bounds.

**Methods:**

- `def __init__(self, kb: WorkflowOptimizationKnowledgeBase) -> None`
- `def validate_plan(self, plan: WorkflowOptimizationPlan) -> List[str]`

### class `LocalWorkflowOptimizationAnalyzer`
- **Inherits from**: WorkflowOptimizationAnalyzer

> Aggregates separate analyzers and compiles optimization recommendations.

**Methods:**

- `def __init__(self) -> None`
- `def run_analysis(self, workflow_id: str, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `LocalWorkflowOptimizationPlanner`
- **Inherits from**: WorkflowOptimizationPlanner

> Central planner coordinating sub-analyzers to construct plans.

**Methods:**

- `def __init__(self) -> None`
- `def construct_optimization_plan(self, workflow_id: str, workflow_graph: Any, telemetry: List[Any]) -> WorkflowOptimizationPlan`

### class `LocalWorkflowOptimizationService`
- **Inherits from**: WorkflowOptimizationService

> Coordinates optimization runs, writes workspace plans reports, and posts to Notion database.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def generate_optimization_report(self, workspace_id: str) -> WorkflowOptimizationReport`
- `def get_latest_report(self, workspace_id: str) -> Optional[WorkflowOptimizationReport]`
- `def get_history(self, workspace_id: str) -> List[WorkflowOptimizationReport]`
- `def store_optimization_summary(self, workspace_id: str) -> None`
- `def publish_optimization_report(self, report: WorkflowOptimizationReport) -> None`

## Module: core/src/aios/services/orchestrator.py

### class `SkillInvocation`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ExecutionPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ExecutionContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ResultAggregator`
- **Inherits from**: abc.ABC

**Methods:**

- `def aggregate(self, results: Dict[str, Any]) -> str`
  * Aggregates multiple step outputs into a single consolidated report.

### class `OrchestratorService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def execute_plan(self, plan: ExecutionPlan, initial_ctx: ExecutionContext) -> Dict[str, Any]`
  * Executes a multi-skill execution plan in dependency order, passing outputs.

## Module: core/src/aios/services/workflow_planning.py

### class `WorkflowTemplate`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Parameterized workflow template ready for composition instantiation.

### class `WorkflowConstraint`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Pre-conditions or post-conditions validation gating rule.

### class `WorkflowPlanningSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Lifecycle tracking for an active workflow planning session.

### class `WorkflowPlanningReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Report compiled for external Knowledge Hub Notion syncing.

### class `WorkflowIntentAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes intent texts to detect targets, tags, and matching templates.

**Methods:**

- `def analyze_intent(self, intent: str) -> Dict[str, Any]`
  * Parses raw text into structural properties dict.

### class `WorkflowTemplateRegistry`

> Registry holding reusable and parameterized workflow templates.

**Methods:**

- `def __init__(self) -> None`
- `def register_template(self, template: WorkflowTemplate) -> None`
  * Saves template in registry.
- `def get_template(self, template_id: str) -> Optional[WorkflowTemplate]`
  * Retrieves template by ID.
- `def list_templates(self) -> List[str]`
  * Lists registered template IDs.

### class `WorkflowDependencyResolver`
- **Inherits from**: abc.ABC

> Orders nodes to satisfy execution dependency bounds.

**Methods:**

- `def resolve_dependencies(self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]) -> List[str]`
  * Returns ordered node IDs conforming to DAG execution routes.

### class `WorkflowOptimizer`
- **Inherits from**: abc.ABC

> Performs planning-time graph structural optimizations.

**Methods:**

- `def optimize_graph(self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]) -> tuple[List[WorkflowNode], List[WorkflowEdge], List[str]]`
  * Returns (optimized_nodes, optimized_edges, optimizations_done).

### class `WorkflowSuggestionEngine`
- **Inherits from**: abc.ABC

> Suggests relevant template IDs matching analyzed intents.

**Methods:**

- `def suggest_templates(self, intent: str, registry: WorkflowTemplateRegistry) -> List[str]`
  * Returns matched template IDs.

### class `WorkflowComposer`
- **Inherits from**: abc.ABC

> Hydrates templates parameters to compose concrete WorkflowDefinitions.

**Methods:**

- `def compose_workflow(self, template: WorkflowTemplate, params: Dict[str, Any]) -> WorkflowDefinition`
  * Returns parameterized workflow definition.

### class `WorkflowPlanner`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Conductor service managing planning sessions, optimizations, registry, and reporting.

**Methods:**

- `def create_planning_session(self, workspace_id: str, intent: str) -> WorkflowPlanningSession`
  * Creates session to initiate plan.
- `def generate_plan(self, session: WorkflowPlanningSession) -> WorkflowPlanningReport`
  * Processes intent, resolves graphs, optimizes structure, and logs report.
- `def get_session(self, session_id: str) -> Optional[WorkflowPlanningSession]`
  * Retrieves session details.
- `def get_history(self, workspace_id: str) -> List[WorkflowPlanningReport]`
  * Retrieves past plans for workspace.
- `def store_planning_summary(self, session_id: str) -> None`
  * Caches stats in Memory. Never saves source code/credentials.
- `def publish_planning_report(self, report: WorkflowPlanningReport) -> None`
  * Pushes report metadata to Notion.

## Module: core/src/aios/services/documentation_intelligence.py

### class `DocumentCategory`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate documentation category classifications.

### class `DocumentSource`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate artifact inputs source components.

### class `DocumentMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated metadata tagging a single document.

### class `DocumentTemplate`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Document template settings outlining target headings structure.

### class `DocumentArtifact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a generated/registered documentation artifact.

### class `DocumentationWorkspace`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Active repository directory mapping configuration settings.

### class `DocumentationSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Telemetry record tracking documentation generation sessions lifecycle.

### class `DocumentationResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregates documentation generation results.

### class `DocumentationProfileAdapter`

> Adapts engineering configurations to documentation-specific parameters.

**Methods:**

- `def __init__(self, profile: DocumentationProfile) -> None`
- `def get_format(self) -> str`
- `def should_generate_api(self) -> bool`
- `def get_style_rules(self) -> Dict[str, Any]`

### class `DocumentationPlanner`
- **Inherits from**: abc.ABC

> Plans template layouts based on target project profiles.

**Methods:**

- `def plan_documentation(self, session: DocumentationSession, profile_adapter: DocumentationProfileAdapter) -> List[DocumentTemplate]`
  * Assembles recommended lists of doc templates.

### class `DocumentationRegistry`

> Thread-safe registry caching documents and layout templates.

**Methods:**

- `def __init__(self) -> None`
- `def register_artifact(self, artifact: DocumentArtifact) -> None`
- `def get_artifact(self, artifact_id: str) -> Optional[DocumentArtifact]`
- `def register_template(self, template: DocumentTemplate) -> None`
- `def get_template(self, template_id: str) -> Optional[DocumentTemplate]`

### class `DocumentationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service organizing document plans and registers.

**Methods:**

- `def create_session(self, workspace: DocumentationWorkspace) -> DocumentationSession`
  * Initializes a new documentation tracking session.
- `def plan_session(self, session: DocumentationSession) -> List[DocumentTemplate]`
  * Compiles structure template lists matching target settings.
- `def register_artifact(self, artifact: DocumentArtifact) -> None`
  * Saves generated doc artifacts inside index registry.
- `def get_artifact(self, artifact_id: str) -> Optional[DocumentArtifact]`
  * Fetches registered documentation artifact.
- `def store_documentation_summary(self, result: DocumentationResult) -> None`
  * Stores summaries configurations in Memory.
- `def publish_documentation_summary(self, result: DocumentationResult) -> None`
  * Syncs documentation summaries with Knowledge Hub.

## Module: core/src/aios/services/collaboration.py

### class `ReviewerRole`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate configurable human reviewer roles.

### class `ReviewAction`
- **Inherits from**: Enum
- **Type**: Enum

> Immutable log actions for collaborative reviews.

### class `Reviewer`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Configurable reviewer profile details containing permissions.

### class `ReviewComment`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Individual human review comment linked to structural items.

### class `ReviewThread`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Thread grouping root comments and nested replies.

### class `ReviewVote`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Reviewer decision vote capturing rationale details.

### class `ReviewAuditLog`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Single immutable audit log entry details.

### class `ReviewTimeline`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Immutable chronological review timeline containing audit items.

### class `ReviewCheckpoint`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> State snapshot of active voting and comment statistics.

### class `ReviewResolution`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Official gate review decision and outcome details.

### class `ReviewFeedback`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Post-gate reviewer ratings and feedback notes.

### class `ReviewCollaborationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Outcome report detailing thread states, timelines, and audit traces.

### class `ReviewCollaborationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Primary service coordinating human feedback, threads, votes, and workspace logging.

**Methods:**

- `def create_thread(self, workspace_id: str, session_id: str, comment: ReviewComment) -> ReviewThread`
  * Instantiates a new discussion thread.
- `def reply_to_comment(self, workspace_id: str, thread_id: str, comment_id: str, reply: ReviewComment) -> ReviewComment`
  * Appends nested comment reply inside an active discussion thread.
- `def resolve_thread(self, workspace_id: str, thread_id: str, resolver: str) -> None`
  * Resolves discussion thread marking resolved status.
- `def reopen_thread(self, workspace_id: str, thread_id: str, reopener: str) -> None`
  * Reopens discussion thread marking open status.
- `def cast_vote(self, workspace_id: str, session_id: str, vote: ReviewVote) -> None`
  * Casts vote outcome for active session.
- `def get_threads(self, workspace_id: str, session_id: str) -> List[ReviewThread]`
  * Retrieves active threads list for active session.
- `def get_timeline(self, workspace_id: str, session_id: str) -> ReviewTimeline`
  * Retrieves immutable execution timeline for session.
- `def get_audit_log(self, workspace_id: str, session_id: str) -> List[ReviewAuditLog]`
  * Retrieves append-only audit entries for session.
- `def store_collaboration_summary(self, workspace_id: str, session_id: str) -> None`
  * Caches metadata and statistics in memory. Never stores source code.
- `def publish_collaboration_report(self, report: ReviewCollaborationReport) -> None`
  * Publishes details to Notion database on demand.

## Module: core/src/aios/services/model_impl.py

### class `LocalModelService`
- **Inherits from**: ModelService

**Methods:**

- `def __init__(self, default_model: str, config_path: str, registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`
- `def execute_prompt(self, prompt: str, system_instruction: Optional[str]) -> str`
- `def execute_request(self, request: LLMRequest) -> LLMResponse`
- `def execute_stream(self, request: LLMRequest) -> Iterator[LLMResponse]`

### def `_resolve_provider_for_model`
- `def _resolve_provider_for_model(configured_provider: Optional[str]) -> Optional[str]`
> Return the name of the best registered provider to serve an unrecognised model.

Resolution order (first match wins):
  1. The provider named in ``config.llm.provider``, if it is already registered.
     This lets config.toml express an explicit preference without hardcoding anything
     in application code.
  2. The first registered provider that has at least one model with
     ``supports_coding=True``.  Capable inference providers (e.g. NVIDIA) are
     naturally preferred over stub/mock providers this way.
  3. The first registered non-mock provider.
  4. Whatever was registered first (last-resort fallback so routing stays alive).

No provider names are hardcoded here; the ladder is driven entirely by the
current state of the registries at call time.

## Module: core/src/aios/services/engineering_intelligence_impl.py

### class `LocalChangeImpactAnalyzer`
- **Inherits from**: ChangeImpactAnalyzer

> Rule-based change impact analyzer used as fallback.

**Methods:**

- `def analyze_impact(self, workspace_root: str, objective: str, code_summary: CodeStructureSummary) -> tuple[List[AffectedFile], List[AffectedComponent]]`

### class `LocalComplexityEstimator`
- **Inherits from**: ComplexityEstimator

> Rule-based complexity estimator used as fallback.

**Methods:**

- `def estimate_complexity(self, affected_files: List[AffectedFile], affected_components: List[AffectedComponent], code_summary: CodeStructureSummary) -> tuple[str, float]`

### class `LocalRiskAnalyzer`
- **Inherits from**: RiskAnalyzer

> Rule-based risk analyzer used as fallback.

**Methods:**

- `def analyze_risks(self, objective: str, affected_files: List[AffectedFile], affected_components: List[AffectedComponent], code_summary: CodeStructureSummary) -> List[str]`

### class `LocalImplementationPlanner`
- **Inherits from**: ImplementationPlanner

> Rule-based implementation planner used as fallback.

**Methods:**

- `def generate_plan(self, objective: str, affected_files: List[AffectedFile], affected_components: List[AffectedComponent], complexity: str, risks: List[str], code_summary: CodeStructureSummary) -> EngineeringPlan`

### class `LocalEngineeringAnalyzer`
- **Inherits from**: EngineeringAnalyzer

> Main Engineering Analyzer orchestrating LLM queries and fallbacks.

**Methods:**

- `def __init__(self, code_intel: CodeIntelligenceService, model_service: Optional[ModelService]) -> None`
- `def analyze_engineering(self, workspace_root: str, objective: str) -> EngineeringReport`

### class `LocalEngineeringIntelligenceService`
- **Inherits from**: EngineeringIntelligenceService

> Concrete Engineering Intelligence service implementation.

**Methods:**

- `def __init__(self, code_intel: CodeIntelligenceService, workspace_intel: WorkspaceIntelligenceService, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_report(self, workspace_root: str, objective: str) -> EngineeringReport`
- `def store_report(self, report: EngineeringReport) -> None`
- `def publish_report(self, report: EngineeringReport) -> None`

## Module: core/src/aios/services/intent_engine_impl.py

### class `LocalIntentClassifier`
- **Inherits from**: IntentClassifier

**Methods:**

- `def __init__(self, model_service: Optional[ModelService]) -> None`
- `def classify(self, text: str) -> List[str]`

### class `LocalIntentAnalyzer`
- **Inherits from**: IntentAnalyzer

**Methods:**

- `def analyze(self, text: str, context: IntentContext) -> Dict[str, Any]`

### class `LocalIntentResolver`
- **Inherits from**: IntentResolver

**Methods:**

- `def __init__(self, classifier: IntentClassifier, analyzer: IntentAnalyzer) -> None`
- `def resolve_plan(self, text: str, context: IntentContext) -> IntentPlan`

### class `LocalIntentEngine`
- **Inherits from**: IntentEngine

**Methods:**

- `def __init__(self, memory_service: MemoryService, reasoning_service: ReasoningService, model_service: Optional[ModelService]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def process_objective(self, objective: str) -> IntentResult`

## Module: core/src/aios/services/release_documentation.py

### class `ReleaseSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated metrics summary of a software version release.

### class `ReleaseArtifact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Output artifact documentation container (Notes, Changelogs, Guides).

### class `ReleaseDocumentationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Release validation health check report.

### class `ReleaseNotesGenerator`
- **Inherits from**: abc.ABC

> Formats ReleaseSummary details into standard Markdown Release Notes.

**Methods:**

- `def generate_release_notes(self, summary: ReleaseSummary, details: Dict[str, Any]) -> str`
  * Assembles Markdown content.

### class `ChangelogGenerator`
- **Inherits from**: abc.ABC

> Formats commits lists into Keep a Changelog standard format.

**Methods:**

- `def generate_changelog(self, summary: ReleaseSummary, commits: List[Dict[str, Any]]) -> str`
  * Assembles Markdown content.

### class `MigrationGuideGenerator`
- **Inherits from**: abc.ABC

> Formats breaking changes instructions into a clean step-by-step migration layout.

**Methods:**

- `def generate_migration_guide(self, version_from: str, version_to: str, instructions: List[str]) -> str`
  * Assembles Markdown content.

### class `UpgradeGuideGenerator`
- **Inherits from**: abc.ABC

> Formats deployment steps checklist into standard upgrade guides.

**Methods:**

- `def generate_upgrade_guide(self, target_version: str, checklist: List[str]) -> str`
  * Assembles Markdown content.

### class `ReleaseValidator`
- **Inherits from**: abc.ABC

> Validates markdown structure, semantic versioning formats, and duplicate releases entries.

**Methods:**

- `def validate_release_document(self, artifact: ReleaseArtifact) -> List[str]`
  * Returns validation error list.

### class `ReleaseDocumentPlanner`
- **Inherits from**: abc.ABC

> Plans release summaries depending on target workspaces and metadata versions.

**Methods:**

- `def plan_release_documentation(self, workspace_id: str, target_version: str) -> ReleaseSummary`
  * Compiles target release scope metrics.

### class `ReleaseDocumentationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service executing generators, validators, and memory summaries stores.

**Methods:**

- `def create_release_notes(self, workspace_id: str, summary: ReleaseSummary, details: Dict[str, Any]) -> ReleaseArtifact`
  * Builds a Release Notes artifact.
- `def create_changelog(self, workspace_id: str, summary: ReleaseSummary, commits: List[Dict[str, Any]]) -> ReleaseArtifact`
  * Builds a Changelog artifact.
- `def create_migration_guide(self, workspace_id: str, version_from: str, version_to: str, instructions: List[str]) -> ReleaseArtifact`
  * Builds a Migration Guide artifact.
- `def create_upgrade_guide(self, workspace_id: str, target_version: str, checklist: List[str]) -> ReleaseArtifact`
  * Builds an Upgrade Guide artifact.
- `def store_release_summary(self, artifact: ReleaseArtifact) -> None`
  * Logs summaries metadata in Memory.
- `def publish_release_report(self, report: ReleaseDocumentationReport) -> None`
  * Pushes updates to Knowledge Hub Notion pages.

## Module: core/src/aios/services/agent.py

### class `AgentLifecycle`
- **Inherits from**: Enum
- **Type**: Enum

### class `AgentCapability`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `AgentTask`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `AgentExecutionPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `AgentContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> The execution context provided to an Agent during invocation.

### class `AgentResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> The structured result returned from an Agent execution.

### class `Agent`
- **Inherits from**: abc.ABC

> Base class for all Agents in the system.

**Methods:**

- `def name(self) -> str`
  * Returns the name of the agent.
- `def description(self) -> str`
  * Returns the description of the agent.
- `def execute(self, agent_context: AgentContext) -> AgentResult`
  * Executes the agent logic with the provided context.

### class `AgentRegistry`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def register(self, agent: Agent) -> None`
- `def unregister(self, name: str) -> None`
- `def get_agent(self, name: str) -> Optional[Agent]`
- `def list_agents(self) -> List[Agent]`

### class `AgentFactory`

> Factory to instantiate core agents.

**Methods:**

- `def create_agent(agent_type: str) -> Agent`

### class `LocalAgentManager`
- **Inherits from**: ServiceLifecycle

> Coordinates agents, workflows, and multi-skill orchestrator plans.

**Methods:**

- `def __init__(self, registry: AgentRegistry, orchestrator: Any) -> None`
- `def initialize(self) -> None`

### class `AgentStartedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published when an agent runtime execution starts.

### class `AgentCompletedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published when an agent execution completes successfully.

### class `AgentFailedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published when an agent execution fails.

### class `AgentRuntimeService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Interface for managing agents and dispatching intent executions.

**Methods:**

- `def register_agent(self, agent: Agent) -> None`
  * Registers an agent with the runtime registry.
- `def unregister_agent(self, name: str) -> None`
  * Unregisters an agent by name.
- `def execute(self, intent: Intent) -> AgentResult`
  * Runs the active agent against the given Intent, resolving dependencies.
- `def interrupt(self) -> None`
  * Interrupts the active agent execution.
- `def cancel(self) -> None`
  * Cancels the active agent execution.

## Module: core/src/aios/services/approval.py

### class `ApprovalStatus`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate approval outcomes matching gating criteria.

### class `ApprovalDecision`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Approval decision outcome featuring reasoning and reviewer details.

### class `ApprovalEvidence`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregated engineering evidence from systems components.

### class `ApprovalRule`
- **Inherits from**: abc.ABC
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Abstract rule interface evaluating approval package inputs.

**Methods:**

- `def evaluate(self, package: 'ApprovalPackage') -> tuple[bool, str]`
  * Evaluates compliance, returning (passed, reason).

### class `ApprovalPolicy`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Configurable collection of validation and risk rules.

### class `ApprovalPackage`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Unified container encapsulating all aggregated evidence and summaries.

### class `ApprovalRequest`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Client request initiating a validation gate review process.

### class `ApprovalSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Lifecycle tracking for an active approval evaluation session.

### class `ApprovalSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregated approval summary details stored inside Memory.

### class `ApprovalHistory`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Chronological execution logs trace tracking approval decisions.

### class `ApprovalReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Report compiled for external Knowledge Hub syncs.

### class `ApprovalValidator`
- **Inherits from**: abc.ABC

> Enforces structural completeness and compliance constraints.

**Methods:**

- `def validate_package(self, package: ApprovalPackage) -> List[str]`
  * Returns validation error list.
- `def check_duplicate_request(self, request: ApprovalRequest, history: List[ApprovalSummary]) -> bool`
  * Returns True if the request is a duplicate.

### class `ApprovalManager`
- **Inherits from**: abc.ABC

> Orchestrates session creation, packages compiling, and policies evaluation.

**Methods:**

- `def create_session(self, request: ApprovalRequest) -> ApprovalSession`
  * Creates a new approval session.
- `def compile_package(self, session: ApprovalSession) -> ApprovalPackage`
  * Aggregates evidence and compiles the approval package.
- `def evaluate_policy(self, package: ApprovalPackage) -> ApprovalDecision`
  * Evaluates policy rules and produces an approval decision.

### class `ApprovalEngineService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Conductor service managing requests, histories, memory stores, and reports syncs.

**Methods:**

- `def request_approval(self, request: ApprovalRequest) -> ApprovalSession`
  * Submits an approval request and runs the full evaluation loop.
- `def get_session(self, session_id: str) -> Optional[ApprovalSession]`
  * Retrieves an active or completed session.
- `def get_history(self, workspace_id: str) -> Optional[ApprovalHistory]`
  * Retrieves history of approval runs for a workspace.
- `def store_approval_summary(self, session: ApprovalSession) -> None`
  * Saves metadata-only approval logs in Memory. Never saves source code.
- `def publish_approval_report(self, report: ApprovalReport) -> None`
  * Synchronizes report summaries on Notion.

## Module: core/src/aios/services/mission.py

### class `MissionStatus`
- **Inherits from**: Enum
- **Type**: Enum

### class `MissionTask`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `MissionMilestone`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Mission`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `MissionGoal`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `MissionContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `MissionPlanner`
- **Inherits from**: abc.ABC

**Methods:**

- `def plan_mission(self, objective: str, context: MissionContext) -> Mission`
  * Decomposes a long-term goal objective into structured milestones and tasks.

### class `MissionExecutor`
- **Inherits from**: abc.ABC

**Methods:**

- `def execute_mission(self, mission: Mission, context: MissionContext) -> bool`
  * Executes milestones sequentially, delegating tasks to agents.

### class `MissionRepository`
- **Inherits from**: abc.ABC

**Methods:**

- `def save_mission(self, mission: Mission) -> None`
  * Persists a mission state.
- `def load_mission(self, mission_id: str) -> Optional[Mission]`
  * Loads a persisted mission.
- `def list_missions(self) -> List[Mission]`
  * Lists all missions.

### class `MissionEngine`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def create_mission(self, title: str, objective: str) -> Mission`
  * Creates and registers a new mission.
- `def start_mission(self, mission_id: str) -> bool`
  * Initiates execution of a registered mission.
- `def cancel_mission(self, mission_id: str) -> bool`
  * Cancels a running mission.
- `def get_mission(self, mission_id: str) -> Optional[Mission]`
  * Retrieves a mission state.

## Module: core/src/aios/services/test_failure.py

### class `FailureSeverity`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate failure severity classifications.

### class `FailureConfidence`
- **Inherits from**: Enum
- **Type**: Enum

> Enumerate failure confidence classifications.

### class `FailureSignature`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a unique trace of a test execution failure.

### class `FailurePattern`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Standard pattern classifying a failure family class.

### class `FailureCluster`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Groups of similar failures based on pattern classification.

### class `FailureRecommendation`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Actionable recommendation to address identified execution failures.

### class `FailureAnalysisReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Assembled report containing clustered failure diagnoses.

### class `RootCauseAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes workspace dependencies and logs to isolate failure originations.

**Methods:**

- `def analyze_root_cause(self, execution_summary: ExecutionSummary, code_summary: CodeStructureSummary) -> Dict[str, Any]`
  * Correlates call graphs and log histories to map origin paths.

### class `FailureAnalyzer`
- **Inherits from**: abc.ABC

> Identifies patterns, exception classes, and stacks signatures.

**Methods:**

- `def classify_failure(self, raw_output: str) -> FailurePattern`
  * Parses stdout trace logs to classify failure types.
- `def cluster_failures(self, signatures: List[FailureSignature]) -> List[FailureCluster]`
  * Groups matching traces into signature clusters.

### class `FailureAnalysisService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating diagnosis service executing failure analyses, caching outcomes, and publishing reports.

**Methods:**

- `def diagnose_failures(self, workspace_id: str, execution_summary: ExecutionSummary, code_summary: CodeStructureSummary) -> FailureAnalysisReport`
  * Runs overall failure analysis diagnostic routines.
- `def store_failure_report(self, report: FailureAnalysisReport) -> None`
  * Saves failure reports summaries inside Memory.
- `def publish_failure_report(self, report: FailureAnalysisReport) -> None`
  * Syncs failure report with Knowledge Hub.

## Module: core/src/aios/services/patch_generation.py

### class `PatchMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Tracks patch metadata, identifiers, and validations.

### class `PatchStatistics`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidates modification metrics across code patches.

### class `PatchPreview`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Human-readable preview of planned code alterations.

### class `PatchBundle`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Aggregates multiple file diffs and metadata.

### class `ReviewPackage`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated package for developer code review before merge approval.

### class `DiffGenerator`
- **Inherits from**: abc.ABC

> Generates standard unified diff format strings.

**Methods:**

- `def generate_diff(self, original_content: str, modified_content: str, file_path: str) -> str`
  * Returns standard unified diff comparison output.

### class `PatchGenerator`
- **Inherits from**: abc.ABC

> Orchestrates patch bundle creation across isolated workspaces.

**Methods:**

- `def generate_patch_bundle(self, workspace_root: str, original_repo_root: str, affected_files: List[str]) -> PatchBundle`
  * Generates a PatchBundle containing all changed file diffs.

### class `PatchValidator`
- **Inherits from**: abc.ABC

> Verifies lines offsets, checksums, and syntax integrity.

**Methods:**

- `def validate_patch_bundle(self, bundle: PatchBundle, workspace_root: str) -> tuple[bool, str]`
  * Validates patch formatting, line mappings, and syntax validity.

### class `ConflictDetector`
- **Inherits from**: abc.ABC

> Checks for concurrent modifications and dependency mismatches.

**Methods:**

- `def detect_conflicts(self, bundle: PatchBundle, original_repo_root: str) -> tuple[List[str], List[str]]`
  * Checks for merge conflicts and planning inconsistencies.

### class `PatchSerializer`
- **Inherits from**: abc.ABC

> Serializes patch bundles to/from standardized file systems representations.

**Methods:**

- `def serialize_bundle(self, bundle: PatchBundle) -> str`
  * Serializes bundle to a structured string.
- `def deserialize_bundle(self, content: str) -> PatchBundle`
  * Deserializes bundle from a structured string.

### class `PatchGenerationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Primary service managing unified diff generation, validations, and review packaging.

**Methods:**

- `def create_review_package(self, workspace_id: str, original_repo_root: str, workspace_root: str, affected_files: List[str]) -> ReviewPackage`
  * Assembles a full review package containing preview, stats, and conflict checks.
- `def store_patch_summary(self, review_package: ReviewPackage) -> None`
  * Persists the patch execution summary in Memory Intelligence.
- `def publish_patch_report(self, review_package: ReviewPackage) -> None`
  * Publishes the patch review report to the Knowledge Hub.

## Module: core/src/aios/services/reasoning.py

### class `ReasoningStrategy`
- **Inherits from**: Enum
- **Type**: Enum

### class `ReasoningStep`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ReasoningChain`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ReasoningContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ReasoningMemory`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ReasoningResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ReasoningSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ReasoningEvaluator`
- **Inherits from**: abc.ABC

**Methods:**

- `def evaluate(self, plan: Dict[str, Any], strategy: ReasoningStrategy) -> Dict[str, Any]`
  * Evaluates completeness, safety, complexity, and maintainability of the plan.

### class `ReasoningCritic`
- **Inherits from**: abc.ABC

**Methods:**

- `def critique(self, step: ReasoningStep, context: ReasoningContext) -> str`
  * Evaluates a single reasoning step thought and suggests criticisms or flags risks.

### class `ReasoningService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def reason(self, objective: str, context: ReasoningContext) -> ReasoningResult`
  * Processes the objective through the goal analysis, strategy matching, and self critique loop.
- `def create_session(self, objective: str) -> ReasoningSession`
  * Initializes a reasoning session.

## Module: core/src/aios/services/api_documentation.py

### class `APIParameter`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A query or path parameter detail.

### class `APISchema`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Data object definition for requests and responses.

### class `APIExample`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Mock example request and response payload JSONs.

### class `APIResponse`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> An HTTP response specification.

### class `APIEndpoint`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A single REST/GraphQL/RPC API endpoint.

### class `APIDocumentArtifact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Constructed API documentation output.

### class `APIReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Discrepancy report detailing gaps in current API docs.

### class `APIAnalyzer`
- **Inherits from**: abc.ABC

> Parses AST structures to discover endpoints and compare current documentation.

**Methods:**

- `def analyze_api(self, code_structure: Dict[str, Any], existing_docs: str) -> APIReport`
  * Flags missing parameters or outdated schemas.

### class `APIDocumentationPlanner`
- **Inherits from**: abc.ABC

> Plans layout structure matching target formatting style rules.

**Methods:**

- `def plan_api_documentation(self, report: APIReport) -> List[APIEndpoint]`
  * Assembles list of endpoints requiring documentation additions.

### class `APIDocumentValidator`
- **Inherits from**: abc.ABC

> Validates markdown formatting and OpenAPI compatibility of generated specs.

**Methods:**

- `def validate_api_document(self, artifact: APIDocumentArtifact) -> List[str]`
  * Returns validation error list.

### class `APIRegistry`

> Thread-safe registry caching discovered endpoint specifications.

**Methods:**

- `def __init__(self) -> None`
- `def register_endpoint(self, endpoint: APIEndpoint) -> None`
- `def get_endpoint(self, method: str, path: str) -> Optional[APIEndpoint]`
- `def list_endpoints(self) -> List[APIEndpoint]`

### class `APIDocumentationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service executing discovers, validates, and syncs summaries.

**Methods:**

- `def generate_api_documentation(self, workspace_id: str, code_structure: Dict[str, Any], existing_docs: str) -> APIDocumentArtifact`
  * Runs discovery and formats API schemas.
- `def store_api_summary(self, artifact: APIDocumentArtifact) -> None`
  * Stores API summaries in Memory.
- `def publish_api_report(self, report: APIReport) -> None`
  * Syncs API reports with Knowledge Hub.

## Module: core/src/aios/services/project_intelligence.py

### class `ProjectContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ProjectIntelligenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def analyze_workspace(self, workspace_root: str) -> ProjectContext`
  * Analyzes the workspace, respects gitignore and build targets,
uses incremental caching for fast rescans, and returns a unified ProjectContext.

## Module: core/src/aios/services/daily.py

### class `DailyTask`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ScheduleItem`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `DailySchedule`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `WorkSession`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `DailyReviewSummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `DailyPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `PriorityCalculator`
- **Inherits from**: abc.ABC

**Methods:**

- `def calculate_priority(self, task: DailyTask) -> str`
  * Determines the final priority level (Critical, High, Medium, Low) of a task.

### class `WorkloadEstimator`
- **Inherits from**: abc.ABC

**Methods:**

- `def estimate_workload(self, tasks: List[DailyTask]) -> Dict[str, Any]`
  * Calculates total hours, overloaded schedule detection, remaining work, and capacity.

### class `ScheduleOptimizer`
- **Inherits from**: abc.ABC

**Methods:**

- `def optimize_schedule(self, tasks: List[DailyTask]) -> DailySchedule`
  * Orders tasks, groups similar work, reduces context switching, and recommends focus/break periods.

### class `TaskPrioritizer`
- **Inherits from**: abc.ABC

**Methods:**

- `def prioritize_tasks(self, tasks: List[DailyTask]) -> List[DailyTask]`
  * Calculates priorities and updates task models.

### class `ProgressTracker`
- **Inherits from**: abc.ABC

**Methods:**

- `def update_task_status(self, task_id: str, status: str, completion_percentage: float) -> DailyTask`
  * Updates task execution status and start/finish timestamps.
- `def get_task(self, task_id: str) -> Optional[DailyTask]`
  * Retrieves a single task status.
- `def list_tasks(self) -> List[DailyTask]`
  * Lists active tasks.

### class `SessionRecorder`
- **Inherits from**: abc.ABC

**Methods:**

- `def start_session(self, task_id: str, mission_id: str, category: str, notes: str) -> WorkSession`
  * Logs start of a work session associated with a task/mission.
- `def end_session(self, session_id: str, notes: str) -> WorkSession`
  * Logs end of a work session and calculates duration.
- `def list_sessions(self, task_id: Optional[str]) -> List[WorkSession]`
  * Lists logged work sessions.

### class `DailyReview`
- **Inherits from**: abc.ABC

**Methods:**

- `def generate_review(self) -> DailyReviewSummary`
  * Generates an intelligent end-of-day summary using current tasks, commits, and goals.

### class `ProductivityAnalyzer`
- **Inherits from**: abc.ABC

**Methods:**

- `def analyze_productivity(self) -> Dict[str, Any]`
  * Calculates performance indicators like completion rate, focus time, and planning accuracy.

### class `DailyPlanner`
- **Inherits from**: abc.ABC

**Methods:**

- `def plan_day(self) -> DailyPlan`
  * Automatically generates a prioritized daily plan using missions, goals, tasks, and code metrics.

### class `DailyOSService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Unified service interface coordinating Daily OS components.

**Methods:**

- `def planner(self) -> DailyPlanner`
- `def prioritizer(self) -> TaskPrioritizer`
- `def priority_calculator(self) -> PriorityCalculator`
- `def workload_estimator(self) -> WorkloadEstimator`
- `def schedule_optimizer(self) -> ScheduleOptimizer`
- `def progress_tracker(self) -> ProgressTracker`
- `def session_recorder(self) -> SessionRecorder`
- `def daily_review(self) -> DailyReview`
- `def productivity_analyzer(self) -> ProductivityAnalyzer`

## Module: core/src/aios/services/workflow_versioning.py

### class `WorkflowVersionMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Version metadata carrying author, tags, and semantic versions.

### class `WorkflowVersion`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Immutable workflow version object mapping telemetry, IR, and translations references.

### class `WorkflowVersionGraph`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> DAG graph structure tracking parent-child branches of version histories.

### class `WorkflowVersionHistory`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Timeline catalog ordering run versions chronologically.

### class `WorkflowVersionDiff`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Immutable difference payload outlining changes between two version states.

### class `WorkflowSnapshot`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Immutable full workflow snapshot.

### class `WorkflowEvolutionPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Plan detailing upgrade sequence path recommendations.

### class `WorkflowRollbackPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Plan detailing rollback path steps. Never executed by this subsystem.

### class `WorkflowVersionReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated summary report describing workspace versioning updates.

### class `WorkflowVersionRegistry`
- **Inherits from**: abc.ABC

> Immutable version catalogs catalog.

**Methods:**

- `def register_version(self, version: WorkflowVersion) -> None`
  * Saves immutable version structure.
- `def get_version(self, version_id: str) -> Optional[WorkflowVersion]`
  * Retrieves immutable version structure by ID.
- `def get_graph(self, workflow_id: str) -> Optional[WorkflowVersionGraph]`
  * Retrieves versions DAG graph for a workflow.

### class `WorkflowCompatibilityAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes semver bounds, parameters updates, and breaking changes.

**Methods:**

- `def analyze_compatibility(self, from_ver: WorkflowVersion, to_ver: WorkflowVersion) -> Dict[str, Any]`
  * Returns upgrade compatibility results.

### class `WorkflowMigrationPlanner`
- **Inherits from**: abc.ABC

> Assembles migration plans and rollbacks checklists.

**Methods:**

- `def create_migration_plan(self, from_ver: WorkflowVersion, to_ver: WorkflowVersion) -> WorkflowEvolutionPlan`
  * Returns upgrade migration plan.
- `def create_rollback_plan(self, from_ver: WorkflowVersion, target_ver: WorkflowVersion) -> WorkflowRollbackPlan`
  * Returns target rollback path checklist plan.

### class `WorkflowVersionValidator`
- **Inherits from**: abc.ABC

> Validates parameters, author definitions, and version formats.

**Methods:**

- `def validate_version(self, version: WorkflowVersion) -> List[str]`
  * Validates formatting and references validations.

### class `WorkflowVersionService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Orchestrates workflows version registry, diff executions, and migration plans.

**Methods:**

- `def create_version(self, workflow_id: str, author: str, semver: str, description: str, ir_json: str) -> WorkflowVersion`
  * Registers a new workflow version node.
- `def get_history(self, workflow_id: str) -> WorkflowVersionHistory`
  * Retrieves chronological run history timeline.
- `def diff_versions(self, from_version_id: str, to_version_id: str) -> WorkflowVersionDiff`
  * Generates immutable difference between two version nodes.
- `def generate_evolution_plan(self, workflow_id: str, target_semver: str) -> WorkflowEvolutionPlan`
  * Compiles upgrade migration steps.
- `def generate_rollback_plan(self, workflow_id: str, target_version_id: str) -> WorkflowRollbackPlan`
  * Compiles target rollback target checklist.
- `def generate_version_report(self, workspace_id: str) -> WorkflowVersionReport`
  * Assembles workspace versioning summary report.
- `def store_version_summary(self, workspace_id: str) -> None`
  * Saves metadata summaries inside memory. Never stores source code/credentials.
- `def publish_version_report(self, report: WorkflowVersionReport) -> None`
  * Synchronizes report details to Notion on-demand.

## Module: core/src/aios/services/test_execution_impl.py

### class `PytestAdapter`
- **Inherits from**: TestFrameworkAdapter

> Pytest framework adapter executing tests in the workspace sandbox.

**Methods:**

- `def framework_name(self) -> str`
- `def execute_tests(self, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionResult`

### class `LocalTestRunner`
- **Inherits from**: TestRunner

> Executes target sessions using registered framework adapters.

**Methods:**

- `def __init__(self) -> None`
- `def run_session(self, session: ExecutionSession, workspace_root: str) -> ExecutionSummary`

### class `LocalTestExecutor`
- **Inherits from**: TestExecutor

> Executes and monitors test target lists.

**Methods:**

- `def __init__(self) -> None`
- `def execute(self, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionSummary`

### class `LocalTestExecutionService`
- **Inherits from**: TestExecutionService

> Coordinating service orchestrating execution, memory logging, and report syncing.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[Any], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def _get_policy(self) -> PersistencePolicy`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def execute_workspace_tests(self, workspace_id: str, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionSummary`
- `def store_execution_summary(self, summary: ExecutionSummary) -> None`
- `def publish_execution_report(self, summary: ExecutionSummary) -> None`

## Module: core/src/aios/services/n8n_translation.py

### class `WorkflowIR`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Canonical Intermediate Representation (IR) of a workflow.

### class `TranslationContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Carries local session state variables, configurations and validation errors.

### class `TranslationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Outcome report describing compiles count, warnings, and path targets.

### class `N8NNodeMapper`
- **Inherits from**: abc.ABC

> Maps custom node configurations to native n8n schema specifications.

**Methods:**

- `def map_node(self, node: Dict[str, Any], context: TranslationContext) -> Dict[str, Any]`
  * Translates node parameters to n8n parameters format.

### class `N8NConnectionMapper`

> Compiles workflow edges into main execution connection structures.

**Methods:**

- `def map_connections(self, edges: List[Dict[str, Any]], context: TranslationContext) -> Dict[str, Any]`

### class `N8NExpressionBuilder`

> Parses expressions into evaluation parameters.

**Methods:**

- `def build_expression(self, expression: str, context: TranslationContext) -> str`

### class `N8NCredentialMapper`

> Associates credential vault pointers to secure nodes properties.

**Methods:**

- `def map_credential(self, cred_ref: Dict[str, Any], context: TranslationContext) -> Dict[str, Any]`

### class `N8NWorkflowBuilder`

> Constructs final JSON payloads compliant with n8n schema standards.

**Methods:**

- `def build_workflow_json(self, ir: WorkflowIR, nodes: List[Dict[str, Any]], connections: Dict[str, Any], context: TranslationContext) -> Dict[str, Any]`

### class `TranslationValidator`
- **Inherits from**: abc.ABC

> Verifies generated JSON integrity, schemas, and missing nodes mappings.

**Methods:**

- `def validate_translation(self, ir: WorkflowIR, n8n_json: Dict[str, Any]) -> List[str]`
  * Runs checks against connections, duplicate node mappings, and n8n JSON formats.

### class `WorkflowCompiler`
- **Inherits from**: abc.ABC

> Compiles high-level WorkflowDefinitions into intermediate canonical IR.

**Methods:**

- `def compile_definition_to_ir(self, definition: WorkflowDefinition) -> WorkflowIR`
  * Translates workflow template configuration definition to IR.

### class `WorkflowSerializer`
- **Inherits from**: abc.ABC

> Serializes execution payloads.

**Methods:**

- `def serialize_to_json_string(self, n8n_json: Dict[str, Any]) -> str`
  * Returns pretty JSON output format.

### class `N8NTranslationEngine`
- **Inherits from**: abc.ABC

> Translates canonical WorkflowIR components using registers node mappers.

**Methods:**

- `def translate_ir(self, ir: WorkflowIR, context: TranslationContext) -> Dict[str, Any]`
  * Produces n8n execution diagram JSON.

### class `WorkflowTranslator`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Main gateway coordinating translation runs, memory stores, and reports updates.

**Methods:**

- `def translate_workflow(self, definition: WorkflowDefinition, workspace_id: str) -> TranslationReport`
  * Executes full translation compiler pipeline, writes workspace reports and json target.
- `def get_history(self, workspace_id: str) -> List[TranslationReport]`
  * Retrieves history runs reports.
- `def store_translation_summary(self, report_id: str) -> None`
  * Saves metadata statistics inside memory. Never stores source code/credentials.
- `def publish_translation_report(self, report: TranslationReport) -> None`
  * Synchronizes report page details to Notion on-demand.

## Module: core/src/aios/services/architecture_documentation_impl.py

### class `LocalArchitectureAnalyzer`
- **Inherits from**: ArchitectureAnalyzer

> Concrete analyzer discovering layers decoupling rules violations.

**Methods:**

- `def analyze_architecture(self, code_structure: Dict[str, Any], existing_docs: str) -> ArchitectureReport`

### class `LocalArchitectureDocumentPlanner`
- **Inherits from**: ArchitectureDocumentPlanner

> Concrete planner mapping codebase reports to target component structures.

**Methods:**

- `def plan_architecture_documentation(self, report: ArchitectureReport) -> List[ArchitectureComponent]`

### class `LocalArchitectureValidator`
- **Inherits from**: ArchitectureValidator

> Concrete validator flagging unknown node connection references.

**Methods:**

- `def validate_architecture_document(self, diagram: ArchitectureDiagram, registry: ArchitectureRegistry) -> List[str]`

### class `LocalArchitectureDocumentationService`
- **Inherits from**: ArchitectureDocumentationService

> Coordinating Architecture service formatting diagram representations and pushing logs.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_architecture_documentation(self, workspace_id: str, code_structure: Dict[str, Any], existing_docs: str) -> ArchitectureDiagram`
- `def store_architecture_summary(self, summary: ArchitectureSummary) -> None`
- `def publish_architecture_report(self, report: ArchitectureReport) -> None`

## Module: core/src/aios/services/github.py

### class `GitHubAuthentication`
- **Decorators**: `dataclass`
- **Type**: Dataclass

**Methods:**

- `def get_headers(self) -> Dict[str, str]`

### class `GitHubCache`

**Methods:**

- `def __init__(self) -> None`
- `def get(self, key: str) -> Optional[Any]`
- `def set(self, key: str, value: Any) -> None`
- `def clear(self) -> None`

### class `GitHubRepository`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubPullRequest`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubIssue`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubCommit`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubBranch`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubRelease`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubWorkflow`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubContext`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Unified service interface for GitHub Intelligence.

**Methods:**

- `def inspect_repository(self, repo_name: str) -> GitHubRepository`
  * Fetch details of a repository.
- `def list_branches(self, repo_name: str) -> List[GitHubBranch]`
  * List all branches in a repository.
- `def create_branch(self, repo_name: str, branch_name: str, target_sha: str) -> GitHubBranch`
  * Create a new branch in a repository.
- `def inspect_pull_request(self, repo_name: str, pr_number: int) -> GitHubPullRequest`
  * Inspect details of a pull request.
- `def inspect_issue(self, repo_name: str, issue_number: int) -> GitHubIssue`
  * Inspect details of an issue.
- `def get_commit_history(self, repo_name: str, branch: Optional[str]) -> List[GitHubCommit]`
  * Fetch commit history for a repository.
- `def get_release_history(self, repo_name: str) -> List[GitHubRelease]`
  * Fetch release history for a repository.
- `def get_workflow_status(self, repo_name: str) -> List[GitHubWorkflow]`
  * Fetch GitHub Action workflows status.
- `def get_repository_stats(self, repo_name: str) -> Dict[str, Any]`
  * Fetch repository statistics (stars, forks, open issues).
- `def search_repositories(self, query: str) -> List[GitHubRepository]`
  * Search GitHub for repositories matching a query.
- `def get_repository_metadata(self, repo_name: str) -> Dict[str, Any]`
  * Fetch full repository metadata.
- `def get_diff(self, repo_name: str, base: str, head: str) -> str`
  * Get code diff between base and head branches/commits.
- `def get_file(self, repo_name: str, path: str, ref: Optional[str]) -> str`
  * Retrieve file content from repository.
- `def get_readme(self, repo_name: str) -> str`
  * Retrieve README.md content from repository.
- `def get_contributors(self, repo_name: str) -> List[Dict[str, Any]]`
  * Get repository contributors list.
- `def get_labels(self, repo_name: str) -> List[str]`
  * Get repository issue/PR labels.
- `def get_milestones(self, repo_name: str) -> List[Dict[str, Any]]`
  * Get repository milestones.
- `def review_repository(self, repo_name: str) -> str`
  * Deep architectural review of the repository using LLM.
- `def review_pr(self, repo_name: str, pr_number: int) -> str`
  * AI code review of a pull request.
- `def explain_commit_history(self, repo_name: str, branch: Optional[str]) -> str`
  * Analyze and cluster commit history, identifying refactors and milestones.

## Module: core/src/aios/services/test_validation_impl.py

### class `LocalValidationService`
- **Inherits from**: ValidationService

> Unified validation manager compiling executing metrics, coverage goals, and diagnostics reports.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def synthesize_validation(self, workspace_id: str, execution_summary: ExecutionSummary, coverage_report: CoverageReport, failure_report: FailureAnalysisReport) -> ValidationReport`
- `def store_validation_report(self, report: ValidationReport) -> None`
- `def publish_validation_report(self, report: ValidationReport) -> None`

## Module: core/src/aios/services/career.py

### class `JobApplication`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `CareerProfileManager`
- **Inherits from**: abc.ABC

**Methods:**

- `def get_career_profile(self) -> Optional[CareerProfile]`
  * Get the user's active career profile details.
- `def update_career_profile(self, profile: CareerProfile) -> None`
  * Update active career profile settings.

### class `JobAnalyzer`
- **Inherits from**: abc.ABC

**Methods:**

- `def analyze_job(self, job_description: str) -> Dict[str, Any]`
  * Extract requirements, required skills, preferred technologies, and ATS keywords.

### class `ResumeOptimizer`
- **Inherits from**: abc.ABC

**Methods:**

- `def tailor_resume(self, resume: Resume, job_description: str) -> ResumeVersion`
  * Create a tailored ResumeVersion for a target job description.
- `def optimize_ats(self, resume_version: ResumeVersion, keywords: List[str]) -> ResumeVersion`
  * Optimize ResumeVersion bullet points and keywords for target ATS list.

### class `ATSAnalyzer`
- **Inherits from**: abc.ABC

**Methods:**

- `def score_resume_against_job(self, resume_version: ResumeVersion, job_description: str) -> Dict[str, Any]`
  * Evaluate match score, list found/missing keywords, and suggest improvements.

### class `CoverLetterGenerator`
- **Inherits from**: abc.ABC

**Methods:**

- `def generate_cover_letter(self, resume_version: ResumeVersion, job_description: str) -> str`
  * Generate a cover letter tailored to a target job and resume version.

### class `PortfolioAnalyzer`
- **Inherits from**: abc.ABC

**Methods:**

- `def analyze_portfolio(self, username: str) -> Dict[str, Any]`
  * Rank projects, recommend featured projects, and suggest documentation/README improvements.

### class `ApplicationTracker`
- **Inherits from**: abc.ABC

**Methods:**

- `def add_application(self, app: JobApplication) -> None`
  * Add a job application to tracking history.
- `def update_application_status(self, app_id: str, status: str) -> None`
  * Update status of a tracked job application.
- `def list_applications(self) -> List[JobApplication]`
  * List all tracked job applications.

### class `InterviewCoach`
- **Inherits from**: abc.ABC

**Methods:**

- `def prepare_interview(self, company: str, role: str) -> Dict[str, Any]`
  * Generate company prep materials, system design preparation, and weakness analysis.
- `def generate_questions(self, role: str, category: str) -> List[str]`
  * Generate technical, behavioral, system design, or coding questions.

### class `CareerPlanner`
- **Inherits from**: abc.ABC

**Methods:**

- `def generate_plan(self) -> Dict[str, Any]`
  * Analyze goals, missing skills, alternative career paths, and estimate impact.

### class `JobMatcher`
- **Inherits from**: abc.ABC

**Methods:**

- `def match_jobs(self, jobs: List[str]) -> List[Dict[str, Any]]`
  * Score multiple job descriptions against profile and recommend improvements.

### class `CareerOSService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Unified service interface coordinating Career OS components.

**Methods:**

- `def profile_manager(self) -> CareerProfileManager`
- `def job_analyzer(self) -> JobAnalyzer`
- `def resume_optimizer(self) -> ResumeOptimizer`
- `def ats_analyzer(self) -> ATSAnalyzer`
- `def cover_letter_generator(self) -> CoverLetterGenerator`
- `def portfolio_analyzer(self) -> PortfolioAnalyzer`
- `def application_tracker(self) -> ApplicationTracker`
- `def interview_coach(self) -> InterviewCoach`
- `def career_planner(self) -> CareerPlanner`
- `def job_matcher(self) -> JobMatcher`

## Module: core/src/aios/services/engineering_profile.py

### class `ProjectProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Project-specific metadata parameters.

### class `CodingProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Language and coding standard definitions.

### class `TestingProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Testing frameworks configurations and target policies.

### class `ExecutionProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Execution sandbox environments preferences.

### class `DocumentationProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Docs formats and generation preferences.

### class `GitHubProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Repository organization details.

### class `ReleaseProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Versioning methods and auto-release policies.

### class `AutomationProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Task automations and retry settings.

### class `WorkspaceProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Sandbox workspaces limits and exclusions.

### class `EngineeringProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Consolidated profile representing engineering configurations.

### class `ProfileSerializer`
- **Inherits from**: abc.ABC

> Serializes profile models to/from JSON or dictionaries.

**Methods:**

- `def serialize(self, profile: EngineeringProfile) -> Dict[str, Any]`
  * Converts model to dictionary format.
- `def deserialize(self, data: Dict[str, Any]) -> EngineeringProfile`
  * Converts dictionary to strongly-typed profile.

### class `ProfileLoader`
- **Inherits from**: abc.ABC

> Retrieves profile files from disk or environmental configs.

**Methods:**

- `def load_from_file(self, file_path: str) -> Dict[str, Any]`
  * Loads configuration dictionary from path.

### class `ProfileManager`
- **Inherits from**: abc.ABC

> Merges and validates multiple profiles using precedence matrices.

**Methods:**

- `def merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]`
  * Performs deep merges over profiles configs.
- `def validate(self, profile: EngineeringProfile) -> List[str]`
  * Runs validation checks, returning list of validation errors.

### class `ProfileRegistry`

> Thread-safe registry cache for loaded engineering profiles.

**Methods:**

- `def __init__(self) -> None`
- `def register(self, profile_id: str, profile: EngineeringProfile) -> None`
- `def get(self, profile_id: str) -> Optional[EngineeringProfile]`

### class `EngineeringProfileService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating configurations service managing engineering profiles.

**Methods:**

- `def get_profile(self, profile_id: str) -> Optional[EngineeringProfile]`
  * Retrieves targeted engineering profile configuration.
- `def save_profile(self, profile: EngineeringProfile) -> None`
  * Caches engineering profile instance.
- `def store_profile_summary(self, profile: EngineeringProfile) -> None`
  * Saves profile metadata configuration in Memory.
- `def publish_profile_summary(self, profile: EngineeringProfile) -> None`
  * Syncs profile specifications with Knowledge Hub.

## Module: core/src/aios/services/knowledge_hub.py

### class `KnowledgeOperation`
- **Inherits from**: Enum
- **Type**: Enum

### class `KnowledgeSyncPolicy`
- **Inherits from**: Enum
- **Type**: Enum

### class `KnowledgeMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `KnowledgeReference`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `KnowledgeDocument`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `KnowledgePage`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `KnowledgeSyncResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `KnowledgeProvider`
- **Inherits from**: abc.ABC

**Methods:**

- `def get_name(self) -> str`
  * Returns the provider name (e.g. 'notion').
- `def authenticate(self) -> bool`
  * Verifies authentication credentials with the external system.
- `def discover_databases(self) -> List[Dict[str, Any]]`
  * Discovers accessible databases.
- `def discover_pages(self) -> List[KnowledgePage]`
  * Discovers accessible root pages.
- `def search(self, query: str) -> List[KnowledgePage]`
  * Searches the provider for matching pages.
- `def read_page(self, page_id: str) -> Optional[KnowledgePage]`
  * Reads a specific page from the provider.
- `def create_page(self, parent_id: str, title: str, content: str, properties: Optional[Dict[str, Any]]) -> Optional[KnowledgePage]`
  * Creates a page under a parent page or inside a database.
- `def update_page(self, page_id: str, title: Optional[str], content: Optional[str], properties: Optional[Dict[str, Any]]) -> Optional[KnowledgePage]`
  * Updates an existing page's title, content, or properties.

### class `KnowledgeHubService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def register_provider(self, provider: KnowledgeProvider) -> None`
  * Registers a knowledge sync provider.
- `def get_provider(self, name: str) -> Optional[KnowledgeProvider]`
  * Retrieves a registered provider by name.
- `def sync_document(self, doc: KnowledgeDocument, provider_name: str) -> KnowledgeSyncResult`
  * Synchronizes a KnowledgeDocument with an external provider.
- `def get_sync_status(self, document_id: str) -> Optional[KnowledgeMetadata]`
  * Gets the sync metadata for a specific document.

## Module: core/src/aios/services/engineering_intelligence.py

### class `AffectedFile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a source file likely to be affected by the engineering change.

### class `AffectedComponent`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents an architectural component/symbol affected by the change.

### class `ChangeRecommendation`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A recommended structural modification for a specific target.

### class `EngineeringPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Structured implementation plan generated for a software change objective.

### class `EngineeringReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Full engineering analysis report including impact, complexity, risks, and plans.

### class `ChangeImpactAnalyzer`
- **Inherits from**: abc.ABC

> Responsible for determining affected modules, services, interfaces, files, and docs.

**Methods:**

- `def analyze_impact(self, workspace_root: str, objective: str, code_summary: CodeStructureSummary) -> tuple[List[AffectedFile], List[AffectedComponent]]`
  * Identifies files, classes, methods, and interfaces affected by the change objective.

### class `ComplexityEstimator`
- **Inherits from**: abc.ABC

> Responsible for estimating implementation complexity and effort based on architectural impact.

**Methods:**

- `def estimate_complexity(self, affected_files: List[AffectedFile], affected_components: List[AffectedComponent], code_summary: CodeStructureSummary) -> tuple[str, float]`
  * Returns complexity classification (Low/Medium/High/Very High) and estimated effort in hours.

### class `RiskAnalyzer`
- **Inherits from**: abc.ABC

> Responsible for identifying architectural risks (breaking APIs, circular deps, violations).

**Methods:**

- `def analyze_risks(self, objective: str, affected_files: List[AffectedFile], affected_components: List[AffectedComponent], code_summary: CodeStructureSummary) -> List[str]`
  * Identifies risk indicators like high coupling, circular dependencies, and API breakages.

### class `ImplementationPlanner`
- **Inherits from**: abc.ABC

> Responsible for generating step-by-step engineering plans, execution orders, and validation plans.

**Methods:**

- `def generate_plan(self, objective: str, affected_files: List[AffectedFile], affected_components: List[AffectedComponent], complexity: str, risks: List[str], code_summary: CodeStructureSummary) -> EngineeringPlan`
  * Constructs an ordered implementation plan with validation strategies and dependencies.

### class `EngineeringAnalyzer`
- **Inherits from**: abc.ABC

> Unified coordinator component executing impact, complexity, risk, and plan assessments.

**Methods:**

- `def analyze_engineering(self, workspace_root: str, objective: str) -> EngineeringReport`
  * Executes full analysis pipeline and generates a complete Engineering Report.

### class `EngineeringIntelligenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Primary service interface exposing engineering analysis, storage, and publishing.

**Methods:**

- `def generate_report(self, workspace_root: str, objective: str) -> EngineeringReport`
  * Analyzes a change objective and constructs a complete EngineeringReport.
- `def store_report(self, report: EngineeringReport) -> None`
  * Stores the engineering plan and summary inside Memory Intelligence.
- `def publish_report(self, report: EngineeringReport) -> None`
  * Publishes the engineering report to the Knowledge Hub.

## Module: core/src/aios/services/software_engineer_impl.py

### class `LocalFeaturePlanner`
- **Inherits from**: FeaturePlanner

> Rule-based feature planner fallback.

**Methods:**

- `def plan_features(self, objective: str, engineering_report: EngineeringReport) -> List[DevelopmentPhase]`

### class `LocalTaskDecomposer`
- **Inherits from**: TaskDecomposer

> Rule-based task decomposer fallback.

**Methods:**

- `def decompose_tasks(self, objective: str, engineering_report: EngineeringReport) -> List[ImplementationTask]`

### class `LocalExecutionPlanner`
- **Inherits from**: ExecutionPlanner

> Rule-based execution planner fallback.

**Methods:**

- `def plan_execution(self, tasks: List[ImplementationTask]) -> tuple[List[str], Dict[str, List[str]], str]`

### class `LocalFilePlanner`
- **Inherits from**: FilePlanner

> Rule-based file planner fallback.

**Methods:**

- `def plan_files(self, objective: str, engineering_report: EngineeringReport) -> tuple[List[str], List[str]]`

### class `LocalTestingPlanner`
- **Inherits from**: TestingPlanner

> Rule-based testing planner fallback.

**Methods:**

- `def plan_testing(self, objective: str, engineering_report: EngineeringReport) -> tuple[List[str], str, str]`

### class `LocalDocumentationPlanner`
- **Inherits from**: DocumentationPlanner

> Rule-based documentation planner fallback.

**Methods:**

- `def plan_documentation(self, objective: str, engineering_report: EngineeringReport) -> List[str]`

### class `LocalImplementationPlanner`
- **Inherits from**: ImplementationPlanner

> Main implementation planner orchestrating LLM execution and rule fallbacks.

**Methods:**

- `def __init__(self, model_service: Optional[ModelService]) -> None`
- `def plan_implementation(self, objective: str, engineering_report: EngineeringReport) -> SoftwareEngineeringPlan`

### class `LocalSoftwareEngineerService`
- **Inherits from**: SoftwareEngineerService

> Concrete implementation of SoftwareEngineerService.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def _get_policy(self) -> PersistencePolicy`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def create_development_plan(self, objective: str, engineering_report: EngineeringReport) -> SoftwareEngineeringPlan`
- `def store_development_plan(self, plan: SoftwareEngineeringPlan) -> None`
- `def publish_development_plan(self, plan: SoftwareEngineeringPlan) -> None`

## Module: core/src/aios/services/tool_impl.py

### class `FilesystemTool`
- **Inherits from**: Tool

> Tool for safe local filesystem operations.

**Methods:**

- `def metadata(self) -> ToolMetadata`
- `def __init__(self, workspace_root_provider) -> None`
- `def execute(self, arguments: Dict[str, Any]) -> ToolResult`

### class `GitTool`
- **Inherits from**: Tool

> Tool for running local git commands safely.

**Methods:**

- `def metadata(self) -> ToolMetadata`
- `def execute(self, arguments: Dict[str, Any]) -> ToolResult`

### class `TerminalTool`
- **Inherits from**: Tool

> Tool for safe local command execution in the shell.

**Methods:**

- `def metadata(self) -> ToolMetadata`
- `def execute(self, arguments: Dict[str, Any]) -> ToolResult`

### class `LocalToolManager`
- **Inherits from**: ToolService

> Concrete implementation of ToolService.

Manages the tool registry, performs schema validation, executes tools,
and publishes status events to the event bus.

**Methods:**

- `def __init__(self, event_bus: EventBusService) -> None`
- `def initialize(self) -> None`
- `def _on_context_loaded(self, event) -> None`
- `def _on_session_started(self, event) -> None`
- `def register_tool(self, tool: Tool) -> None`
  * Registers a tool with the engine.
- `def unregister_tool(self, name: str) -> None`
  * Unregisters a tool by name.
- `def list_tools(self) -> List[ToolMetadata]`
  * Lists metadata of all registered tools.
- `def validate_tool(self, name: str, arguments: Dict[str, Any]) -> bool`
  * Validates tool arguments against its input schema.
- `def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult`
  * Executes a registered tool by name with the given arguments.
- `def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`
  * Invokes a registered tool by name and returns output dict (backward compatibility).

## Module: core/src/aios/services/collaboration_impl.py

### class `LocalReviewCollaborationService`
- **Inherits from**: ReviewCollaborationService

> Concrete collaboration coordinator managing reviewer feedback and immutable audit traces.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str`
- `def _get_audit_log_list(self, session_id: str) -> List[ReviewAuditLog]`
- `def _add_audit_log(self, session_id: str, action: ReviewAction, actor: str, details: str) -> None`
- `def create_thread(self, workspace_id: str, session_id: str, comment: ReviewComment) -> ReviewThread`
- `def reply_to_comment(self, workspace_id: str, thread_id: str, comment_id: str, reply: ReviewComment) -> ReviewComment`
- `def resolve_thread(self, workspace_id: str, thread_id: str, resolver: str) -> None`
- `def reopen_thread(self, workspace_id: str, thread_id: str, reopener: str) -> None`
- `def cast_vote(self, workspace_id: str, session_id: str, vote: ReviewVote) -> None`
- `def get_threads(self, workspace_id: str, session_id: str) -> List[ReviewThread]`
- `def get_timeline(self, workspace_id: str, session_id: str) -> ReviewTimeline`
- `def get_audit_log(self, workspace_id: str, session_id: str) -> List[ReviewAuditLog]`
- `def store_collaboration_summary(self, workspace_id: str, session_id: str) -> None`
- `def compile_collaboration_report(self, workspace_id: str, session_id: str) -> ReviewCollaborationReport`
- `def publish_collaboration_report(self, report: ReviewCollaborationReport) -> None`

## Module: core/src/aios/services/workflow_optimization.py

### class `WorkflowOptimizationCategory`
- **Inherits from**: str, Enum
- **Type**: Enum

> Optimization category tags.

### class `WorkflowOptimizationPriority`
- **Inherits from**: str, Enum
- **Type**: Enum

> Priority levels.

### class `WorkflowOptimizationImpact`
- **Inherits from**: str, Enum
- **Type**: Enum

> Impact levels.

### class `WorkflowOptimizationPattern`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Pre-defined knowledge pattern definition.

### class `WorkflowOptimizationRecommendation`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Detailed recommendation details.

### class `WorkflowOptimizationPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Immutable optimization plan container.

### class `WorkflowOptimizationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Immutable optimization report output containing all generated plans.

### class `WorkflowOptimizationKnowledgeBase`

> Catalog of pre-defined reusable optimization patterns.

**Methods:**

- `def __init__(self) -> None`
- `def _bootstrap_patterns(self) -> None`
- `def get_pattern(self, pattern_id: str) -> Optional[WorkflowOptimizationPattern]`
  * Retrieves pattern metadata by ID.
- `def get_all_patterns(self) -> List[WorkflowOptimizationPattern]`
  * Lists all registered patterns.

### class `WorkflowCostAnalyzer`
- **Inherits from**: abc.ABC

> Trims token/API billing bounds.

**Methods:**

- `def analyze_cost(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `WorkflowLatencyAnalyzer`
- **Inherits from**: abc.ABC

> Trims runtime latency path bottlenecks.

**Methods:**

- `def analyze_latency(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `WorkflowParallelizationAnalyzer`
- **Inherits from**: abc.ABC

> Suggests concurrent executions on independent branches.

**Methods:**

- `def analyze_parallelization(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `WorkflowRedundancyAnalyzer`
- **Inherits from**: abc.ABC

> Finds duplicate nodes/conditions.

**Methods:**

- `def analyze_redundancy(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `WorkflowSchedulingAnalyzer`
- **Inherits from**: abc.ABC

> Optimizes cron schedulers intervals.

**Methods:**

- `def analyze_scheduling(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `WorkflowResourceAnalyzer`
- **Inherits from**: abc.ABC

> Trims memory/CPU usage spikes.

**Methods:**

- `def analyze_resources(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `WorkflowComplexityAnalyzer`
- **Inherits from**: abc.ABC

> Measures graph complexity and maintains metric scores.

**Methods:**

- `def analyze_complexity(self, workflow_graph: Any) -> Dict[str, float]`

### class `WorkflowOptimizationValidator`
- **Inherits from**: abc.ABC

> Validates plan integrity constraints, confidence bounds, and patterns references.

**Methods:**

- `def validate_plan(self, plan: WorkflowOptimizationPlan) -> List[str]`

### class `WorkflowOptimizationAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes telemetry and graphs using sub-analyzers.

**Methods:**

- `def run_analysis(self, workflow_id: str, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]`

### class `WorkflowOptimizationPlanner`
- **Inherits from**: abc.ABC

> Central planner coordinating sub-analyzers to construct plans.

**Methods:**

- `def construct_optimization_plan(self, workflow_id: str, workflow_graph: Any, telemetry: List[Any]) -> WorkflowOptimizationPlan`

### class `WorkflowOptimizationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Conductor orchestration optimizing workflows, writing reports, and syncing databases.

**Methods:**

- `def generate_optimization_report(self, workspace_id: str) -> WorkflowOptimizationReport`
  * Assembles optimization report for a workspace.
- `def get_latest_report(self, workspace_id: str) -> Optional[WorkflowOptimizationReport]`
  * Retrieves the latest generated report.
- `def get_history(self, workspace_id: str) -> List[WorkflowOptimizationReport]`
  * Retrieves completed reports history.
- `def store_optimization_summary(self, workspace_id: str) -> None`
  * Saves metadata summaries inside memory. Never stores source code/credentials.
- `def publish_optimization_report(self, report: WorkflowOptimizationReport) -> None`
  * Synchronizes report details to Notion on-demand.

## Module: core/src/aios/services/test_coverage_impl.py

### class `LocalCoverageAnalyzer`
- **Inherits from**: CoverageAnalyzer

> Concrete coverage evaluator simulating statement, branch, and configuration coverages.

**Methods:**

- `def analyze_coverage(self, execution_summary: ExecutionSummary, targets: List[CoverageTarget], policy: CoveragePolicy) -> CoverageReport`

### class `LocalRegressionAnalyzer`
- **Inherits from**: RegressionAnalyzer

> Concrete regression risk evaluator checking dependency chains.

**Methods:**

- `def analyze_regression_risks(self, affected_files: List[str], dependency_graph: Dict[str, List[str]], execution_summary: ExecutionSummary) -> RegressionRisk`

### class `LocalAITestCoverageService`
- **Inherits from**: AITestCoverageService

> Coordinating service evaluates test validations, caches metrics, and publishes Notion summaries.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[Any], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def evaluate_validation(self, workspace_id: str, execution_summary: ExecutionSummary, affected_files: List[str], dependency_graph: Dict[str, List[str]], policy: CoveragePolicy) -> Dict[str, Any]`
- `def store_coverage_summary(self, report: CoverageReport) -> None`
- `def publish_coverage_report(self, report: CoverageReport) -> None`

## Module: core/src/aios/services/readme_intelligence.py

### class `READMESection`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> A single header section content in a README file.

### class `READMETemplate`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Target sections sequencing and design rules.

### class `READMEArtifact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a generated/updated README artifact.

### class `READMESummary`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Metadata summary statistics for a README file.

### class `READMEReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Comprehensive report analyzing discrepancies in an existing README.

### class `READMEAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes workspace structures and current documentation to find gaps.

**Methods:**

- `def analyze_readme(self, existing_content: str, workspace_metadata: Dict[str, Any]) -> READMEReport`
  * Compares current content to metadata targets to log missing headers.

### class `READMEPlanner`
- **Inherits from**: abc.ABC

> Plans README sections order matching style conventions.

**Methods:**

- `def plan_sections(self, report: READMEReport, template: READMETemplate) -> List[READMESection]`
  * Assembles list of sections with target heading priorities.

### class `READMEValidator`
- **Inherits from**: abc.ABC

> Validates structural formatting and broken links inside markdown files.

**Methods:**

- `def validate_readme(self, content: str) -> List[str]`
  * Returns validation error logs list.

### class `READMEGenerator`
- **Inherits from**: abc.ABC

> Formats planning sections list into a single markdown string.

**Methods:**

- `def generate_readme(self, workspace_id: str, sections: List[READMESection]) -> READMEArtifact`
  * Assembles Markdown content.

### class `READMEUpdater`
- **Inherits from**: abc.ABC

> Updates targeted sections without overwriting custom modifications.

**Methods:**

- `def update_readme(self, existing: READMEArtifact, changes: List[READMESection]) -> READMEArtifact`
  * Merges new section changes into an existing artifact.

### class `READMEIntelligenceService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service executing analyses, updates, and memory synchronizations.

**Methods:**

- `def analyze_and_generate(self, workspace_id: str, existing_content: str, workspace_metadata: Dict[str, Any], template: READMETemplate) -> READMEArtifact`
  * Analyzes gaps and generates an updated README artifact.
- `def store_readme_summary(self, summary: READMESummary) -> None`
  * Stores README summaries inside Memory.
- `def publish_readme_report(self, report: READMEReport) -> None`
  * Syncs README analysis records with Knowledge Hub.

## Module: core/src/aios/services/tool.py

### class `ToolMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Metadata describing a tool's capability and interface.

### class `ToolResult`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> The result returned from executing a tool.

### class `Tool`
- **Inherits from**: abc.ABC

> Base class for all tools in the system.

**Methods:**

- `def metadata(self) -> ToolMetadata`
  * Returns the metadata of the tool.
- `def execute(self, arguments: Dict[str, Any]) -> ToolResult`
  * Executes the tool with the given arguments.

### class `ToolStartedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published when a tool execution is started.

### class `ToolCompletedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published when a tool execution completes successfully.

### class `ToolFailedEvent`
- **Inherits from**: Event
- **Decorators**: `dataclass(frozen=True, kw_only=True)`
- **Type**: Dataclass

> Published when a tool execution fails.

### class `ToolService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Interface for managing the registration and execution of safe tools.

**Methods:**

- `def register_tool(self, tool: Tool) -> None`
  * Registers a tool with the engine.
- `def unregister_tool(self, name: str) -> None`
  * Unregisters a tool by name.
- `def list_tools(self) -> List[ToolMetadata]`
  * Lists metadata of all registered tools.
- `def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult`
  * Executes a registered tool by name with the given arguments.
- `def validate_tool(self, name: str, arguments: Dict[str, Any]) -> bool`
  * Validates tool arguments against its input schema.
- `def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`
  * Invokes a registered tool by name and returns output dict.

## Module: core/src/aios/services/api_documentation_impl.py

### class `LocalAPIAnalyzer`
- **Inherits from**: APIAnalyzer

> Concrete analyzer scanning code structures for REST routes.

**Methods:**

- `def analyze_api(self, code_structure: Dict[str, Any], existing_docs: str) -> APIReport`

### class `LocalAPIDocumentationPlanner`
- **Inherits from**: APIDocumentationPlanner

> Concrete planner mapping discovered endpoints to schemas configurations.

**Methods:**

- `def plan_api_documentation(self, report: APIReport) -> List[APIEndpoint]`

### class `LocalAPIDocumentValidator`
- **Inherits from**: APIDocumentValidator

> Concrete validator flagging OpenAPI duplicate routes or empty schemas.

**Methods:**

- `def validate_api_document(self, artifact: APIDocumentArtifact) -> List[str]`

### class `LocalAPIDocumentationService`
- **Inherits from**: APIDocumentationService

> Coordinating API service cataloging schemas and pushing summaries to Notion.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_api_documentation(self, workspace_id: str, code_structure: Dict[str, Any], existing_docs: str) -> APIDocumentArtifact`
- `def store_api_summary(self, artifact: APIDocumentArtifact) -> None`
- `def publish_api_report(self, report: APIReport) -> None`

## Module: core/src/aios/services/workspace_intelligence_impl.py

### class `LocalRepositoryAnalyzer`
- **Inherits from**: RepositoryAnalyzer

**Methods:**

- `def __init__(self, project_intel: ProjectIntelligenceService) -> None`
- `def analyze(self, workspace_root: str) -> Dict[str, Any]`

### class `LocalArchitectureAnalyzer`
- **Inherits from**: ArchitectureAnalyzer

**Methods:**

- `def __init__(self, model_service: Optional[ModelService]) -> None`
- `def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]`

### class `LocalDependencyAnalyzer`
- **Inherits from**: DependencyAnalyzer

**Methods:**

- `def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, List[str]]`

### class `LocalTechnologyAnalyzer`
- **Inherits from**: TechnologyAnalyzer

**Methods:**

- `def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]`

### class `LocalDocumentationAnalyzer`
- **Inherits from**: DocumentationAnalyzer

**Methods:**

- `def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]`

### class `LocalWorkspaceIntelligenceService`
- **Inherits from**: WorkspaceIntelligenceService

**Methods:**

- `def __init__(self, project_intel: ProjectIntelligenceService, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_repository(self, workspace_root: str) -> RepositorySummary`
- `def store_summary_in_memory(self, summary: RepositorySummary) -> None`
- `def publish_to_knowledge_hub(self, summary: RepositorySummary) -> None`

### class `PythonSymbolVisitor`
- **Inherits from**: ast.NodeVisitor

**Methods:**

- `def __init__(self, file_path: str) -> None`
- `def _get_decorator_name(self, node: ast.AST) -> str`
- `def _get_base_name(self, node: ast.AST) -> str`
- `def visit_ClassDef(self, node: ast.ClassDef) -> None`
- `def visit_FunctionDef(self, node: ast.FunctionDef) -> None`
- `def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None`
- `def _visit_func(self, node: Any) -> None`
- `def visit_Import(self, node: ast.Import) -> None`
- `def visit_ImportFrom(self, node: ast.ImportFrom) -> None`

### class `PythonASTParser`
- **Inherits from**: LanguageASTParser

**Methods:**

- `def can_parse(self, file_extension: str) -> bool`
- `def parse(self, file_path: str, content: str) -> List[SymbolReference]`

### class `TypeScriptASTParser`
- **Inherits from**: LanguageASTParser

**Methods:**

- `def can_parse(self, file_extension: str) -> bool`
- `def parse(self, file_path: str, content: str) -> List[SymbolReference]`
- `def _clean_source(self, content: str) -> str`

### class `LocalASTAnalyzer`
- **Inherits from**: ASTAnalyzer

**Methods:**

- `def __init__(self) -> None`
- `def register_parser(self, parser: LanguageASTParser) -> None`
- `def parse_file(self, file_path: str, content: str) -> List[SymbolReference]`

### class `LocalSymbolIndexer`
- **Inherits from**: SymbolIndexer

**Methods:**

- `def __init__(self) -> None`
- `def index_symbols(self, symbols: List[SymbolReference]) -> None`
- `def lookup_symbol(self, name: str) -> Optional[SymbolReference]`
- `def list_symbols(self) -> List[SymbolReference]`

### class `LocalDependencyGraphBuilder`
- **Inherits from**: DependencyGraphBuilder

**Methods:**

- `def build_graph(self, file_paths: List[str], symbols: List[SymbolReference]) -> Dict[str, List[str]]`

### class `LocalCallGraphBuilder`
- **Inherits from**: CallGraphBuilder

**Methods:**

- `def build_call_graph(self, symbols: List[SymbolReference]) -> Dict[str, List[str]]`

### class `LocalCodeIntelligenceService`
- **Inherits from**: CodeIntelligenceService

**Methods:**

- `def __init__(self, project_intel: ProjectIntelligenceService, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_codebase(self, workspace_root: str) -> CodeStructureSummary`
- `def store_code_summary(self, summary: CodeStructureSummary) -> None`
- `def publish_code_report(self, summary: CodeStructureSummary) -> None`

## Module: core/src/aios/services/research_impl.py

### class `MockSearchProvider`
- **Inherits from**: SearchProvider

**Methods:**

- `def name(self) -> str`
- `def search(self, query: str, limit: int) -> List[Source]`

### class `LocalResearchService`
- **Inherits from**: ResearchService

**Methods:**

- `def __init__(self, model_service: ModelService, cache_filename: str, workspace_root: str, registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def register_provider(self, provider: SearchProvider) -> None`
- `def research(self, query: str, limit: int) -> ResearchResult`
- `def _plan_queries(self, query: str) -> List[str]`
- `def _rank_sources(self, sources: List[Source], query: str) -> List[Source]`

## Module: core/src/aios/services/github_impl.py

### class `LocalGitHubService`
- **Inherits from**: GitHubService

> Concrete implementation of GitHubService providing repository metadata and AI analyses.

**Methods:**

- `def __init__(self, model_service: ModelService, project_intel: Optional[ProjectIntelligenceService], dev_workspace: Optional[DeveloperWorkspaceService], token: Optional[str], base_url: str, timeout: int, max_retries: int, rate_limit_per_min: int, cache_enabled: bool, offline_mode: bool) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _parse_repo_name(self, repo_name: str) -> tuple[str, str]`
  * Normalize repo name from potential URLs or full paths.
- `def _request(self, method: str, path: str, params: Optional[dict], json_data: Optional[dict]) -> Any`
- `def inspect_repository(self, repo_name: str) -> GitHubRepository`
- `def list_branches(self, repo_name: str) -> List[GitHubBranch]`
- `def create_branch(self, repo_name: str, branch_name: str, target_sha: str) -> GitHubBranch`
- `def inspect_pull_request(self, repo_name: str, pr_number: int) -> GitHubPullRequest`
- `def inspect_issue(self, repo_name: str, issue_number: int) -> GitHubIssue`
- `def get_commit_history(self, repo_name: str, branch: Optional[str]) -> List[GitHubCommit]`
- `def get_release_history(self, repo_name: str) -> List[GitHubRelease]`
- `def get_workflow_status(self, repo_name: str) -> List[GitHubWorkflow]`
- `def get_repository_stats(self, repo_name: str) -> Dict[str, Any]`
- `def search_repositories(self, query: str) -> List[GitHubRepository]`
- `def get_repository_metadata(self, repo_name: str) -> Dict[str, Any]`
- `def get_diff(self, repo_name: str, base: str, head: str) -> str`
- `def get_file(self, repo_name: str, path: str, ref: Optional[str]) -> str`
- `def get_readme(self, repo_name: str) -> str`
- `def get_contributors(self, repo_name: str) -> List[Dict[str, Any]]`
- `def get_labels(self, repo_name: str) -> List[str]`
- `def get_milestones(self, repo_name: str) -> List[Dict[str, Any]]`
- `def review_repository(self, repo_name: str) -> str`
- `def review_pr(self, repo_name: str, pr_number: int) -> str`
- `def explain_commit_history(self, repo_name: str, branch: Optional[str]) -> str`

## Module: core/src/aios/services/base.py

### class `ServiceLifecycle`

> Defines the contract for core service lifecycles.
Each service transitions through these stages:
initialize -> start -> ready -> shutdown.

**Methods:**

- `def __init_subclass__(cls)`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def ready(self) -> bool`
- `def shutdown(self) -> None`

## Module: core/src/aios/services/n8n_impl.py

### class `LocalN8NService`
- **Inherits from**: N8NService

**Methods:**

- `def __init__(self, model_service: ModelService, cache_filename: str, workspace_root: str) -> None`
- `def initialize(self) -> None`
- `def create_workflow(self, workflow: InternalWorkflow) -> InternalWorkflow`
- `def update_workflow(self, workflow_id: str, workflow: InternalWorkflow) -> InternalWorkflow`
- `def delete_workflow(self, workflow_id: str) -> bool`
- `def get_workflow(self, workflow_id: str) -> Optional[InternalWorkflow]`
- `def list_workflows(self) -> List[InternalWorkflow]`
- `def validate_workflow(self, workflow: InternalWorkflow) -> Dict[str, Any]`
- `def generate_workflow_from_natural_language(self, description: str) -> InternalWorkflow`
- `def execute_workflow(self, workflow_id: str) -> bool`
- `def stop_workflow(self, workflow_id: str) -> bool`
- `def get_execution_metrics(self, workflow_id: str) -> Optional[ExecutionMetrics]`
- `def check_health(self) -> ConnectionHealth`
- `def internal_to_n8n(self, wf: InternalWorkflow) -> Dict[str, Any]`
- `def n8n_to_internal(self, data: Dict[str, Any]) -> InternalWorkflow`
- `def _save_cache(self) -> None`
- `def _serialize_workflow(self, wf: InternalWorkflow) -> Dict[str, Any]`
- `def _deserialize_workflow(self, data: Dict[str, Any]) -> InternalWorkflow`

## Module: core/src/aios/services/n8n_integration.py

### class `N8NServerInformation`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Carries version numbers, instance ID mappings and capability lists.

### class `N8NConnectionProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Connection profile containing target URL, auth types and timeouts.

### class `N8NIntegrationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Report compiled for external Knowledge Hub Notion syncing.

### class `N8NAuthenticationProvider`
- **Inherits from**: abc.ABC

> Abstract authentication header generator.

**Methods:**

- `def get_auth_headers(self) -> Dict[str, str]`
  * Returns auth header parameters.

### class `APIKeyAuthenticationProvider`
- **Inherits from**: N8NAuthenticationProvider

> API Key authentications helper.

**Methods:**

- `def __init__(self, api_key: str) -> None`
- `def get_auth_headers(self) -> Dict[str, str]`

### class `BearerTokenAuthenticationProvider`
- **Inherits from**: N8NAuthenticationProvider

> Bearer Token authentications helper.

**Methods:**

- `def __init__(self, token: str) -> None`
- `def get_auth_headers(self) -> Dict[str, str]`

### class `N8NConnectionManager`

> Manages active connection headers.

**Methods:**

- `def __init__(self, profile: N8NConnectionProfile, auth_provider: N8NAuthenticationProvider) -> None`
- `def get_headers(self) -> Dict[str, str]`

### class `N8NClient`
- **Inherits from**: abc.ABC

> Abstract HTTP client executing API calls.

**Methods:**

- `def upload_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]`
  * Uploads workflow JSON.
- `def update_workflow(self, workflow_id: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]`
  * Updates workflow JSON.
- `def delete_workflow(self, workflow_id: str) -> bool`
  * Deletes workflow.
- `def list_workflows(self) -> List[Dict[str, Any]]`
  * Lists uploaded workflows.
- `def get_workflow(self, workflow_id: str) -> Dict[str, Any]`
  * Retrieves workflow by ID.
- `def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]`
  * Triggers execution.
- `def get_execution(self, execution_id: str) -> Dict[str, Any]`
  * Retrieves execution status logs.
- `def list_executions(self, workflow_id: str) -> List[Dict[str, Any]]`
  * Lists executions logs.
- `def activate_workflow(self, workflow_id: str) -> bool`
  * Activates workflow triggers.
- `def deactivate_workflow(self, workflow_id: str) -> bool`
  * Deactivates workflow triggers.

### class `N8NWorkflowRepository`
- **Inherits from**: abc.ABC

> Metadata repository saving mappings for local workflows.

**Methods:**

- `def save_workflow_metadata(self, workflow_id: str, metadata: Dict[str, Any]) -> None`
  * Saves metadata map.
- `def get_workflow_metadata(self, workflow_id: str) -> Optional[Dict[str, Any]]`
  * Retrieves metadata map.

### class `N8NExecutionRepository`
- **Inherits from**: abc.ABC

> Metadata repository saving executions summaries.

**Methods:**

- `def save_execution_metadata(self, execution_id: str, metadata: Dict[str, Any]) -> None`
  * Saves metadata map.

### class `N8NCredentialRepository`
- **Inherits from**: abc.ABC

> Associates credential vault pointers.

**Methods:**

- `def register_credential_reference(self, name: str, value: str) -> None`
  * Saves reference to credential lookup.

### class `N8NHealthMonitor`
- **Inherits from**: abc.ABC

> Executes server status, version and connectivity latency checks.

**Methods:**

- `def check_health(self) -> Dict[str, Any]`
  * Returns health diagnostics metrics.

### class `N8NWorkspaceMapper`
- **Inherits from**: abc.ABC

> Maps workflows ownership to specific workspace sessions.

**Methods:**

- `def map_workflow_to_workspace(self, workflow_id: str, workspace_id: str) -> None`
  * Registers workspace mapping.
- `def get_workspace_for_workflow(self, workflow_id: str) -> Optional[str]`
  * Retrieves mapping value.

### class `N8NValidator`
- **Inherits from**: abc.ABC

> Validates configuration parameters and connection profile endpoints.

**Methods:**

- `def validate_server_config(self, profile: N8NConnectionProfile) -> List[str]`
  * Validates configuration settings.

### class `N8NIntegrationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Central conductor interface managing health checks, workflows uploads, and executions.

**Methods:**

- `def upload_workflow_json(self, workspace_id: str, workflow_json: Dict[str, Any]) -> str`
  * Uploads workflow JSON.
- `def trigger_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]`
  * Executes active workflow.
- `def get_health_status(self) -> N8NIntegrationReport`
  * Returns current integration diagnostics report.
- `def get_history(self, workspace_id: str) -> List[N8NIntegrationReport]`
  * Retrieves history runs reports.
- `def store_integration_summary(self, report_id: str) -> None`
  * Saves metadata statistics inside memory. Never stores source code/credentials.
- `def publish_integration_report(self, report: N8NIntegrationReport) -> None`
  * Synchronizes report page details to Notion on-demand.

## Module: core/src/aios/services/release_documentation_impl.py

### class `LocalReleaseNotesGenerator`
- **Inherits from**: ReleaseNotesGenerator

> Formats ReleaseSummary details and additional release facets into standard Markdown Release Notes.

**Methods:**

- `def generate_release_notes(self, summary: ReleaseSummary, details: Dict[str, Any]) -> str`

### class `LocalChangelogGenerator`
- **Inherits from**: ChangelogGenerator

> Formats commits lists into Keep a Changelog standard format.

**Methods:**

- `def generate_changelog(self, summary: ReleaseSummary, commits: List[Dict[str, Any]]) -> str`

### class `LocalMigrationGuideGenerator`
- **Inherits from**: MigrationGuideGenerator

> Formats breaking changes instructions into a clean step-by-step migration layout.

**Methods:**

- `def generate_migration_guide(self, version_from: str, version_to: str, instructions: List[str]) -> str`

### class `LocalUpgradeGuideGenerator`
- **Inherits from**: UpgradeGuideGenerator

> Formats deployment steps checklist into standard upgrade guides.

**Methods:**

- `def generate_upgrade_guide(self, target_version: str, checklist: List[str]) -> str`

### class `LocalReleaseValidator`
- **Inherits from**: ReleaseValidator

> Validates markdown structure, semantic versioning formats, and duplicate releases entries.

**Methods:**

- `def __init__(self, memory_service: MemoryService) -> None`
- `def validate_release_document(self, artifact: ReleaseArtifact) -> List[str]`

### class `LocalReleaseDocumentPlanner`
- **Inherits from**: ReleaseDocumentPlanner

> Plans release summaries depending on target workspaces and metadata versions.

**Methods:**

- `def __init__(self, registry: Optional[Any]) -> None`
- `def plan_release_documentation(self, workspace_id: str, target_version: str) -> ReleaseSummary`

### class `LocalReleaseDocumentationService`
- **Inherits from**: ReleaseDocumentationService

> Coordinating service executing generators, validators, and memory summaries stores.

**Methods:**

- `def __init__(self, memory_service: MemoryService, profile_service: EngineeringProfileService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _write_to_workspace(self, workspace_id: str, filename_template: str, content: str) -> str`
- `def _get_profile_preferences(self) -> Dict[str, Any]`
- `def create_release_notes(self, workspace_id: str, summary: ReleaseSummary, details: Dict[str, Any]) -> ReleaseArtifact`
- `def create_changelog(self, workspace_id: str, summary: ReleaseSummary, commits: List[Dict[str, Any]]) -> ReleaseArtifact`
- `def create_migration_guide(self, workspace_id: str, version_from: str, version_to: str, instructions: List[str]) -> ReleaseArtifact`
- `def create_upgrade_guide(self, workspace_id: str, target_version: str, checklist: List[str]) -> ReleaseArtifact`
- `def store_release_summary(self, artifact: ReleaseArtifact) -> None`
- `def publish_release_report(self, report: ReleaseDocumentationReport) -> None`

## Module: core/src/aios/services/personal.py

### class `Contact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `SocialProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Experience`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Education`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `SkillProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ProjectReference`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ResumeVersion`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Resume`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `PortfolioProject`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `CareerProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Goal`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `LearningItem`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Certificate`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Achievement`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Preference`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `Template`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `KnowledgeEntry`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `DocumentReference`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `PersonalProfile`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `PersonalService`
- **Inherits from**: ServiceLifecycle, abc.ABC

**Methods:**

- `def get_profile(self, profile_id: str) -> Optional[PersonalProfile]`
  * Retrieves a specific personal profile.
- `def create_profile(self, profile: PersonalProfile) -> PersonalProfile`
  * Creates and persists a new personal profile.
- `def update_profile(self, profile_id: str, profile: PersonalProfile) -> PersonalProfile`
  * Updates and increments the version of an existing profile.
- `def delete_profile(self, profile_id: str) -> bool`
  * Deletes a personal profile.
- `def switch_active_profile(self, profile_id: str) -> bool`
  * Switches the active profile used for context injection.
- `def get_active_profile(self) -> Optional[PersonalProfile]`
  * Returns the currently active profile.
- `def list_profiles(self) -> List[str]`
  * Lists all registered profile identifiers.
- `def get_relevant_context(self, objective: str) -> Dict[str, Any]`
  * Performs intelligent context selection based on the objective query.

## Module: core/src/aios/services/daily_impl.py

### class `LocalPriorityCalculator`
- **Inherits from**: PriorityCalculator

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService, career_os: Optional[CareerOSService], registry: Any, project_intel: ProjectIntelligenceService) -> None`
- `def calculate_priority(self, task: DailyTask) -> str`

### class `LocalWorkloadEstimator`
- **Inherits from**: WorkloadEstimator

**Methods:**

- `def estimate_workload(self, tasks: List[DailyTask]) -> Dict[str, Any]`

### class `LocalScheduleOptimizer`
- **Inherits from**: ScheduleOptimizer

**Methods:**

- `def __init__(self, model_service: ModelService) -> None`
- `def optimize_schedule(self, tasks: List[DailyTask]) -> DailySchedule`

### class `LocalTaskPrioritizer`
- **Inherits from**: TaskPrioritizer

**Methods:**

- `def __init__(self, priority_calculator: PriorityCalculator) -> None`
- `def prioritize_tasks(self, tasks: List[DailyTask]) -> List[DailyTask]`

### class `LocalProgressTracker`
- **Inherits from**: ProgressTracker

**Methods:**

- `def __init__(self, personal_service: PersonalService) -> None`
- `def _get_tasks(self) -> List[DailyTask]`
- `def _save_tasks(self, tasks: List[DailyTask]) -> None`
- `def update_task_status(self, task_id: str, status: str, completion_percentage: float) -> DailyTask`
- `def get_task(self, task_id: str) -> Optional[DailyTask]`
- `def list_tasks(self) -> List[DailyTask]`

### class `LocalSessionRecorder`
- **Inherits from**: SessionRecorder

**Methods:**

- `def __init__(self, personal_service: PersonalService) -> None`
- `def _get_sessions(self) -> List[WorkSession]`
- `def _save_sessions(self, sessions: List[WorkSession]) -> None`
- `def start_session(self, task_id: str, mission_id: str, category: str, notes: str) -> WorkSession`
- `def end_session(self, session_id: str, notes: str) -> WorkSession`
- `def list_sessions(self, task_id: Optional[str]) -> List[WorkSession]`

### class `LocalDailyReview`
- **Inherits from**: DailyReview

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService, career_os: Optional[CareerOSService], registry: Any, project_intel: ProjectIntelligenceService, github_service: GitHubService) -> None`
- `def generate_review(self) -> DailyReviewSummary`
- `def _persist_review(self, summary: DailyReviewSummary) -> None`

### class `LocalProductivityAnalyzer`
- **Inherits from**: ProductivityAnalyzer

**Methods:**

- `def __init__(self, personal_service: PersonalService, registry: Any) -> None`
- `def analyze_productivity(self) -> Dict[str, Any]`

### class `LocalDailyPlanner`
- **Inherits from**: DailyPlanner

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService, github_service: GitHubService, project_intel: ProjectIntelligenceService, career_os: Optional[CareerOSService], registry: Any) -> None`
- `def plan_day(self) -> DailyPlan`

### class `LocalDailyOSService`
- **Inherits from**: DailyOSService

> Unified service implementation coordinating all Daily OS modules.

**Methods:**

- `def __init__(self, model_service: ModelService, personal_service: PersonalService, github_service: GitHubService, project_intel: ProjectIntelligenceService, career_os: Optional[CareerOSService], registry: Any) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def planner(self) -> DailyPlanner`
- `def prioritizer(self) -> TaskPrioritizer`
- `def priority_calculator(self) -> PriorityCalculator`
- `def workload_estimator(self) -> WorkloadEstimator`
- `def schedule_optimizer(self) -> ScheduleOptimizer`
- `def progress_tracker(self) -> ProgressTracker`
- `def session_recorder(self) -> SessionRecorder`
- `def daily_review(self) -> DailyReview`
- `def productivity_analyzer(self) -> ProductivityAnalyzer`

## Module: core/src/aios/services/test_generation.py

### class `GeneratedTestArtifact`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a generated test file artifact target.

### class `TestGenerationReport`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Final outcome report detailing generated test telemetry.

### class `TestPatternAnalyzer`
- **Inherits from**: abc.ABC

> Analyzes existing tests to identify naming, fixture, and assertion styles.

**Methods:**

- `def analyze_patterns(self, existing_tests_dir: str) -> str`
  * Returns structured patterns description summary.

### class `TestTemplateEngine`
- **Inherits from**: abc.ABC

> Renders test mock skeletons using style guides.

**Methods:**

- `def render_template(self, template_name: str, context: Dict[str, Any]) -> str`
  * Renders test code templates.

### class `TestCaseBuilder`
- **Inherits from**: abc.ABC

> Structures test parameters, steps, and targets.

**Methods:**

- `def build_cases(self, objective: str, patterns: str) -> List[Dict[str, Any]]`
  * Determines target cases to create.

### class `AssertionGenerator`
- **Inherits from**: abc.ABC

> Generates standard target assertions.

**Methods:**

- `def generate_assertions(self, target_symbol: str) -> List[str]`
  * Returns assert snippets.

### class `FixtureGenerator`
- **Inherits from**: abc.ABC

> Generates testing fixtures mapping setups.

**Methods:**

- `def generate_fixtures(self, target_symbol: str) -> List[str]`
  * Returns pytest fixtures declarations.

### class `MockGenerator`
- **Inherits from**: abc.ABC

> Generates service mock parameters.

**Methods:**

- `def generate_mocks(self, target_symbol: str) -> List[str]`
  * Returns mock definitions.

### class `EdgeCaseGenerator`
- **Inherits from**: abc.ABC

> Generates exception boundaries and edge cases parameters.

**Methods:**

- `def generate_edge_cases(self, target_symbol: str) -> List[str]`
  * Returns exception test blocks.

### class `RegressionTestGenerator`
- **Inherits from**: abc.ABC

> Generates regression-specific test targets.

**Methods:**

- `def generate_regression_tests(self, target_symbol: str) -> List[str]`
  * Returns regression validation snippets.

### class `TestGenerator`
- **Inherits from**: abc.ABC

> Primary engine executing generation of single test files.

**Methods:**

- `def generate_test_suite(self, workspace_root: str, target_file: str, patterns: str, code_summary: CodeStructureSummary) -> GeneratedTestArtifact`
  * Writes and returns test target artifacts.

### class `TestGenerationService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Coordinating service executing test planning, context generation, and reviews packaging.

**Methods:**

- `def generate_workspace_tests(self, workspace_id: str, objective: str, workspace_root: str, target_files: List[str], code_summary: CodeStructureSummary) -> TestGenerationReport`
  * Executes test generation pipeline using the ModelService.
- `def store_generation_report(self, report: TestGenerationReport) -> None`
  * Stores test generation report inside Memory.
- `def publish_generation_report(self, report: TestGenerationReport) -> None`
  * Syncs test generation report with the Knowledge Hub.

## Module: core/src/aios/services/software_engineer.py

### class `ImplementationTask`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a discrete unit of development work.

### class `ValidationStep`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a test or verification check.

### class `DevelopmentPhase`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Represents a high-level stage in the feature implementation lifecycle.

### class `SoftwareEngineeringPlan`
- **Decorators**: `dataclass`
- **Type**: Dataclass

> Detailed development plan translating architectural goals to implementation steps.

### class `FeaturePlanner`
- **Inherits from**: abc.ABC

> Generates high-level development phases and validation tasks for a feature.

**Methods:**

- `def plan_features(self, objective: str, engineering_report: EngineeringReport) -> List[DevelopmentPhase]`
  * Maps an engineering report into a set of development phases with validation tasks.

### class `TaskDecomposer`
- **Inherits from**: abc.ABC

> Decomposes a major feature objective into structured implementation tasks.

**Methods:**

- `def decompose_tasks(self, objective: str, engineering_report: EngineeringReport) -> List[ImplementationTask]`
  * Breaks down a feature into discrete, validated, dependency-tracked tasks.

### class `ExecutionPlanner`
- **Inherits from**: abc.ABC

> Plans low-risk execution order, dependency mapping, and rollback strategies.

**Methods:**

- `def plan_execution(self, tasks: List[ImplementationTask]) -> tuple[List[str], Dict[str, List[str]], str]`
  * Returns safest execution order, task dependencies, and rollback strategy.

### class `FilePlanner`
- **Inherits from**: abc.ABC

> Identifies required files, creation targets, and migration requirements.

**Methods:**

- `def plan_files(self, objective: str, engineering_report: EngineeringReport) -> tuple[List[str], List[str]]`
  * Identifies target files to change and any migration/setup requirements.

### class `TestingPlanner`
- **Inherits from**: abc.ABC

> Plans testing strategies, validation steps, and required tests.

**Methods:**

- `def plan_testing(self, objective: str, engineering_report: EngineeringReport) -> tuple[List[str], str, str]`
  * Determines required tests, validation strategy, and general testing strategy.

### class `DocumentationPlanner`
- **Inherits from**: abc.ABC

> Identifies documentation and architecture guide updates.

**Methods:**

- `def plan_documentation(self, objective: str, engineering_report: EngineeringReport) -> List[str]`
  * Identifies which READMEs, guides, or KB files require updating.

### class `ImplementationPlanner`
- **Inherits from**: abc.ABC

> Orchestrator producing complete, structured SoftwareEngineeringPlans.

**Methods:**

- `def plan_implementation(self, objective: str, engineering_report: EngineeringReport) -> SoftwareEngineeringPlan`
  * Constructs a comprehensive, validated SoftwareEngineeringPlan.

### class `SoftwareEngineerService`
- **Inherits from**: ServiceLifecycle, abc.ABC

> Unified service for creating, storing, and publishing development plans.

**Methods:**

- `def create_development_plan(self, objective: str, engineering_report: EngineeringReport) -> SoftwareEngineeringPlan`
  * Generates a complete SoftwareEngineeringPlan based on an EngineeringReport.
- `def store_development_plan(self, plan: SoftwareEngineeringPlan) -> None`
  * Stores the development plan inside Memory Intelligence.
- `def publish_development_plan(self, plan: SoftwareEngineeringPlan) -> None`
  * Publishes the development plan to the Knowledge Hub.

## Module: core/src/aios/services/engineering_documentation_impl.py

### class `LocalADRGenerator`
- **Inherits from**: ADRGenerator

> Concrete generator assembling ADR Markdown layouts.

**Methods:**

- `def generate_adr(self, record: DecisionRecord) -> str`

### class `LocalEngineeringReportGenerator`
- **Inherits from**: EngineeringReportGenerator

> Concrete generator compiling metrics summaries into Markdown reports.

**Methods:**

- `def generate_engineering_report(self, summary: ImplementationSummary, validation: ValidationSummary, risk: RiskSummary) -> str`

### class `LocalEngineeringDocumentPlanner`
- **Inherits from**: EngineeringDocumentPlanner

> Concrete planner mapping decisions lists requiring documenting.

**Methods:**

- `def plan_engineering_documents(self, workspace_id: str) -> List[DecisionRecord]`

### class `LocalEngineeringDocumentValidator`
- **Inherits from**: EngineeringDocumentValidator

> Concrete validator flagging duplicate ADRs or empty sections.

**Methods:**

- `def validate_engineering_document(self, artifact: EngineeringDocumentArtifact) -> List[str]`

### class `LocalEngineeringDocumentationService`
- **Inherits from**: EngineeringDocumentationService

> Coordinating service executing generators and memory synchronizations.

**Methods:**

- `def __init__(self, memory_service: MemoryService, knowledge_hub: Optional[KnowledgeHubService], model_service: Optional[ModelService], registry: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def create_adr_document(self, workspace_id: str, record: DecisionRecord) -> EngineeringDocumentArtifact`
- `def create_engineering_report(self, workspace_id: str, summary: ImplementationSummary, validation: ValidationSummary, risk: RiskSummary) -> EngineeringDocumentArtifact`
- `def store_engineering_summary(self, artifact: EngineeringDocumentArtifact) -> None`
- `def publish_engineering_report(self, report: EngineeringDocumentationReport) -> None`

## Module: core/src/aios/services/memory_storage_impl.py

### class `LocalJSONMemoryStorage`
- **Inherits from**: MemoryStorage

> Local JSON file implementation of MemoryStorage.

**Methods:**

- `def __init__(self, file_path: Optional[Path]) -> None`
- `def _load_from_file(self) -> None`
- `def save_memory(self, memory: Memory) -> None`
- `def get_memory(self, memory_id: str) -> Optional[Memory]`
- `def delete_memory(self, memory_id: str) -> None`
- `def load_all_memories(self) -> List[Memory]`
- `def commit(self) -> None`

## Module: core/src/aios/services/developer/scanner.py

### class `RepositoryScanner`

**Methods:**

- `def __init__(self, workspace_root: str) -> None`
- `def scan(self, max_depth: int) -> Dict[str, Any]`
- `def _get_git_diff(self) -> Optional[str]`
- `def _get_git_diff_cached(self) -> Optional[str]`
- `def _get_git_branch(self) -> Optional[str]`
- `def _get_git_status(self) -> Optional[str]`
- `def _get_git_commits(self) -> List[str]`
- `def _get_dir_tree(self, path: Path, current_depth: int, max_depth: int) -> str`
- `def _get_readme(self) -> Optional[str]`
- `def _get_important_configs(self) -> List[Path]`
- `def _detect_languages(self) -> List[str]`
- `def _detect_ecosystem(self, configs: List[Path]) -> tuple[Optional[str], List[str], Optional[str], Optional[str]]`

## Module: core/src/aios/services/developer/index.py

### class `CodeIndex`

**Methods:**

- `def __init__(self, workspace_root: str) -> None`
- `def index(self) -> Dict[str, Any]`
- `def _find_directories(self, candidates: List[str]) -> List[str]`
- `def _find_entry_points(self) -> List[str]`
- `def _find_configs(self) -> List[str]`
- `def _find_docs(self) -> List[str]`
- `def _find_largest_files(self) -> List[Dict[str, Any]]`
- `def _find_todos_and_fixmes(self) -> List[Dict[str, Any]]`

## Module: core/src/aios/services/developer/summary.py

### class `WorkspaceSummary`

**Methods:**

- `def __init__(self, scan_results: Dict[str, Any], index_results: Dict[str, Any]) -> None`
- `def generate(self) -> Dict[str, Any]`
  * Synthesizes scanner and indexer results into a clean, structured WorkspaceSummary.

## Module: core/src/aios/services/intelligence/tool_selector.py

### class `ToolSelector`

**Methods:**

- `def __init__(self) -> None`
- `def select_tools(self, intent: Intent) -> List[str]`

## Module: core/src/aios/services/intelligence/reasoning_context.py

### class `ReasoningContext`

**Methods:**

- `def __init__(self, intent: Intent, repository_analysis: Dict[str, Any], conversation_summary: str, conversation_history: str, memories: List[Any], workspace: Dict[str, Any], selected_tools: List[str], expanded_query: str) -> None`

## Module: core/src/aios/services/intelligence/intent_expander.py

### class `IntentExpander`

**Methods:**

- `def __init__(self) -> None`
- `def expand(self, intent: Intent) -> str`

## Module: core/src/aios/services/intelligence/memory_ranker.py

### class `MemoryRanker`

**Methods:**

- `def __init__(self, memories: List[Any]) -> None`
- `def rank(self, query: str, active_workspace: str, limit: int) -> List[Any]`

## Module: core/src/aios/services/intelligence/context_ranker.py

### class `ContextRanker`

**Methods:**

- `def __init__(self) -> None`
- `def select_context(self, action: str, query: str, full_analysis: Dict[str, Any]) -> Dict[str, Any]`

## Module: core/src/aios/services/intelligence/repository_analyzer.py

### class `RepositoryAnalysis`

**Methods:**

- `def __init__(self, data: Dict[str, Any]) -> None`

### class `RepositoryAnalyzer`

**Methods:**

- `def __init__(self, scanner_results: Dict[str, Any], index_results: Dict[str, Any]) -> None`
- `def analyze(self) -> RepositoryAnalysis`

## Module: core/src/aios/services/docintel/scanner.py

### class `RepositoryScanner`

> Scans the AI OS codebase to identify packages, services, and configs.

**Methods:**

- `def __init__(self, root_dir: str, exclude_patterns: Optional[List[str]]) -> None`
- `def scan(self) -> Dict[str, Any]`
  * Scans the repository and returns structural metadata.

## Module: core/src/aios/services/docintel/graph.py

### class `DependencyGraphBuilder`

> Builds module, package, and service dependency graphs and generates Mermaid flowcharts.

**Methods:**

- `def _get_module_name(self, filepath: str) -> str`
  * Converts file path to python dot-separated module name.
- `def build_dependency_graph(self, scan_results: Dict[str, Any], index_data: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]`
  * Constructs an adjacency list of module relationships based on imports.
- `def build_package_graph(self, scan_results: Dict[str, Any], dep_graph: Dict[str, List[str]]) -> Dict[str, List[str]]`
  * Constructs an adjacency list of package-level dependencies.
- `def build_service_graph(self, scan_results: Dict[str, Any], dep_graph: Dict[str, List[str]]) -> Dict[str, List[str]]`
  * Extracts the dependency graph filtered for services, providers, and registries.
- `def generate_mermaid(self, graph: Dict[str, List[str]], title: str) -> str`
  * Converts adjacency lists to a Mermaid flowchart diagram.

## Module: core/src/aios/services/docintel/intelligence.py

### class `DocumentationIntelligenceEngine`

> Analyzes documentation completeness and scans inline TODOs/FIXMEs.

**Methods:**

- `def analyze(self, index_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]`
- `def _scan_todos_fixmes(self, file_path: str, report: Dict[str, Any]) -> None`

## Module: core/src/aios/services/docintel/generator.py

### class `MarkdownGenerator`

> Formats scan indices and dependency graphs into Markdown documents inside /docs.

**Methods:**

- `def __init__(self, output_dir: str) -> None`
- `def generate(self, scan_results: Dict[str, Any], index_data: Dict[str, Dict[str, Any]], intel_report: Dict[str, Any], dep_mermaid: str, pkg_mermaid: str, svc_mermaid: str) -> None`
  * Saves target markdown folders and files in the destination directory.
- `def _write_readme(self, scan_results: Dict[str, Any]) -> None`
- `def _write_architecture(self, pkg_mermaid: str, svc_mermaid: str) -> None`
- `def _write_services(self, scan_results: Dict[str, Any]) -> None`
- `def _write_providers(self, scan_results: Dict[str, Any]) -> None`
- `def _write_api(self, index_data: Dict[str, Dict[str, Any]]) -> None`
- `def _write_dependency_graph(self, dep_mermaid: str) -> None`
- `def _write_reports(self, intel_report: Dict[str, Any]) -> None`
- `def _save_file(self, subpath: str, content: str) -> None`

## Module: core/src/aios/services/docintel/indexer.py

### class `DocumentationIndexer`

> Parses Python source files using AST to extract detailed metadata.

**Methods:**

- `def parse_file(self, filepath: str) -> Dict[str, Any]`
  * Parses a single file and extracts detailed structural metadata.
- `def _parse_class(self, node: ast.ClassDef) -> Dict[str, Any]`
- `def _parse_function(self, node: ast.FunctionDef) -> Dict[str, Any]`
- `def _parse_imports(self, node: Any) -> List[str]`
- `def _get_source_segment(self, node: Any) -> str`
  * Fallback to unparse or name extraction for type annotations/bases.
- `def _estimate_complexity(self, node: ast.FunctionDef) -> int`
  * Estimates cyclomatic complexity based on branch nodes in AST.

## Module: core/src/aios/services/action/planner.py

### class `ActionPlanner`

**Methods:**

- `def __init__(self, model_service: Optional[ModelService]) -> None`
- `def plan(self, objective: str) -> ActionPlan`

## Module: core/src/aios/services/action/models.py

### class `ActionType`
- **Inherits from**: Enum
- **Type**: Enum

### class `RiskLevel`
- **Inherits from**: Enum
- **Type**: Enum

### class `ActionStep`

**Methods:**

- `def __init__(self, description: str, action_type: ActionType, risk_level: RiskLevel, tool_name: str, tool_args: Dict[str, Any], is_reversible: bool, undo_args: Optional[Dict[str, Any]]) -> None`
- `def to_dict(self) -> Dict[str, Any]`
- `def from_dict(cls, data: Dict[str, Any]) -> 'ActionStep'`

### class `ActionPlan`

**Methods:**

- `def __init__(self, objective: str, steps: Optional[List[ActionStep]], id: Optional[str], status: str, created_at: Optional[float], updated_at: Optional[float]) -> None`
- `def to_dict(self) -> Dict[str, Any]`
- `def from_dict(cls, data: Dict[str, Any]) -> 'ActionPlan'`

## Module: core/src/aios/services/action/rollback.py

### class `RollbackCoordinator`

**Methods:**

- `def __init__(self, tool_service: Any) -> None`
- `def rollback_step(self, step: ActionStep) -> bool`

## Module: core/src/aios/services/action/approval.py

### class `ApprovalManager`

**Methods:**

- `def __init__(self) -> None`
- `def display_plan(self, plan: ActionPlan) -> None`
- `def approve_plan(self, plan: ActionPlan) -> None`
- `def reject_plan(self, plan: ActionPlan) -> None`

## Module: core/src/aios/services/action/report.py

### class `ActionReportGenerator`

**Methods:**

- `def __init__(self) -> None`
- `def generate(self, plan: ActionPlan, start_time: float) -> str`

## Module: core/src/aios/services/action/executor.py

### class `ActionExecutor`

**Methods:**

- `def __init__(self, tool_service: Any) -> None`
- `def execute_step(self, step: ActionStep) -> bool`
- `def execute_plan(self, plan: ActionPlan) -> str`

## Module: core/src/aios/services/action/history.py

### class `ActionHistory`

**Methods:**

- `def __init__(self, storage_dir: Path) -> None`
- `def _get_path(self, plan_id: str) -> Path`
- `def save_plan(self, plan: ActionPlan) -> None`
- `def set_active_plan(self, plan: ActionPlan) -> None`
- `def get_active_plan(self) -> Optional[ActionPlan]`
- `def clear_active_plan(self) -> None`
- `def load_plan(self, plan_id: str) -> Optional[ActionPlan]`
- `def list_plans(self) -> List[ActionPlan]`

## Module: core/src/aios/services/persistence_impl_modules/postgresql.py

### class `PostgreSQLTransport`
- **Inherits from**: DatabaseTransport

> Production runtime database transport utilizing PostgreSQL psycopg2 driver.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService) -> None`
- `def validate_configuration(self) -> List[str]`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute(self, query: str, params: Optional[tuple]) -> TransportResult`
- `def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]`
- `def begin_transaction(self) -> TransportTransaction`
- `def health(self) -> TransportHealth`
- `def capabilities(self) -> TransportCapabilities`

### class `PostgreSQLProvider`
- **Inherits from**: PersistenceProvider

> PostgreSQL database engine provider wrapping a DatabaseTransport.

**Methods:**

- `def __init__(self, transport: Optional[DatabaseTransport]) -> None`
- `def initialize(self, config: PersistenceConfigurationService) -> None`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute(self, query: str, params: Optional[tuple]) -> List[Dict[str, Any]]`
- `def begin_transaction(self) -> None`
- `def commit_transaction(self) -> None`
- `def rollback_transaction(self) -> None`
- `def is_connected(self) -> bool`
- `def get_metrics(self) -> Dict[str, Any]`

## Module: core/src/aios/services/persistence_impl_modules/core_persistence.py

### class `PersistenceServiceImpl`
- **Inherits from**: PersistenceService

> Unified service exposing SQL execution and transactional operations.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService, registry: PersistenceRegistry, repos: RepositoryRegistry) -> None`
- `def initialize(self) -> None`
- `def fallback_to_sqlite(self) -> None`
- `def start(self) -> None`
- `def shutdown(self) -> None`
- `def check_status(self, repository: Optional[str], operation: Optional[str]) -> PersistenceResult`
- `def get_diagnostics_for_error(self, e: Exception) -> Dict[str, Any]`
- `def execute(self, query: str, params: Optional[tuple]) -> List[Dict[str, Any]]`
- `def begin_transaction(self) -> PersistenceResult`
- `def commit(self) -> PersistenceResult`
- `def rollback(self) -> PersistenceResult`
- `def commit_transaction(self) -> PersistenceResult`
- `def rollback_transaction(self) -> PersistenceResult`
- `def save(self, repo_name: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def load(self, repo_name: str, entity_id: str) -> PersistenceResult`
- `def update(self, repo_name: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def delete(self, repo_name: str, entity_id: str) -> PersistenceResult`

### class `PersistenceHealthMonitor`
- **Inherits from**: ServiceLifecycle

> Tracks latency averages, P95 values, transaction metrics, and pool status.

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `PersistenceDiagnostics`
- **Inherits from**: ServiceLifecycle

> Diagnoses persistence platform issues and provides remediations.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService, service: PersistenceService) -> None`
- `def run_diagnostics(self) -> Dict[str, Any]`

### class `PersistenceValidator`
- **Inherits from**: ServiceLifecycle

> Validates configuration parameters.

**Methods:**

- `def validate_config(self, host: str, port: int) -> List[str]`

### class `PersistenceReportGenerator`
- **Inherits from**: ServiceLifecycle

> Generates persistence telemetry reports inside docs/persistence/.

**Methods:**

- `def __init__(self, workspace_root: str, health_monitor: PersistenceHealthMonitor, diagnostics: PersistenceDiagnostics) -> None`
- `def generate_reports(self) -> None`

### class `PersistenceBootstrapper`
- **Inherits from**: ServiceLifecycle

> Bootstrapper executing database schema migrations.

**Methods:**

- `def __init__(self, persistence_service: PersistenceService) -> None`
- `def start(self) -> None`

## Module: core/src/aios/services/persistence_impl_modules/repo_base.py

### class `_RepositoryMixin`

> Internal mixin providing shared CRUD helper utilities and no-op lifecycle
stubs for repository implementations whose operations all return
``PersistenceResult``.

Concrete classes gain four benefits:
  1. ``initialize() / start() / stop()`` are inherited as no-ops.
  2. Status-guard logic is de-duplicated via ``_guard_status()``.
  3. Write, fetch-one, and fetch-all boilerplate is de-duplicated via
     ``_write()``, ``_fetch_one()``, and ``_fetch_all()``.
  4. Cache-aware write and fetch helpers are de-duplicated via
     ``_write_with_cache()`` and ``_fetch_one_with_cache()``.

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _guard_status(self, table: str, operation: str) -> Optional[PersistenceResult]`
  * Check service readiness for *table*/*operation*.

Returns the failed ``PersistenceResult`` when the service is not ready;
returns ``None`` when the service is healthy and ready to proceed.
Raises ``RuntimeError`` immediately when STRICT policy is active.
- `def _write(self, table: str, query: str, params: Tuple[Any, ...], success_msg: str) -> PersistenceResult`
  * Execute a write SQL statement (INSERT / UPDATE / DELETE) and wrap the
outcome in a ``PersistenceResult``.

On success returns ``PersistenceStatus.SUCCESS``.
On failure returns ``PersistenceStatus.UNKNOWN_FAILURE`` (or raises
``RuntimeError`` when STRICT policy is active).
- `def _fetch_one(self, table: str, query: str, params: Tuple[Any, ...], entity_id: str, parse_fn: Callable[[Dict[str, Any]], Dict[str, Any]], success_msg: str) -> PersistenceResult`
  * SELECT a single row by id and wrap it in a ``PersistenceResult``.

Returns ``PersistenceStatus.UNKNOWN_FAILURE`` (or raises in STRICT mode)
when no row is found.
- `def _fetch_all(self, table: str, query: str, parse_fn: Callable[[Dict[str, Any]], Dict[str, Any]], success_msg: str) -> PersistenceResult`
  * SELECT all rows from *table* and wrap in a ``PersistenceResult`` whose
``payload`` is a list of parsed row dicts.
- `def _resolve_cache_services()`
  * Attempt to resolve RedisCacheService and CachePolicyManager from the
global ServiceRegistry.  Returns ``(cache_svc, policy_mgr)`` where
either may be ``None`` when the services are unavailable.

The import is deferred to avoid circular-import issues at module load
time and to keep the mixin usable without Redis being present.
- `def _resolve_cache_svc()`
  * Attempt to resolve only RedisCacheService.  Returns ``cache_svc`` or
``None`` when unavailable.
- `def _write_with_cache(self, table: str, query: str, params: Tuple[Any, ...], success_msg: str, cache_namespace: str, entity_id: str) -> PersistenceResult`
  * Execute a write SQL statement then apply Redis cache policy.

After a successful write the method:
- On ``WRITE_THROUGH`` policy: calls ``cache_payload_fn()`` to obtain
  the cache payload and stores a ``PersistenceResult`` in the cache.
- On any other policy (except ``NO_CACHE``): invalidates the entry.

Parameters
----------
table:
    SQL table name used for the ``PersistenceResult.repository`` field
    and the status guard.
query:
    INSERT / UPDATE / DELETE SQL string.
params:
    Positional parameters for the query.
success_msg:
    Human-readable message on success.
cache_namespace:
    Logical Redis namespace (e.g. ``"provider_capabilities"``).
entity_id:
    Primary key of the entity being written.
cache_payload_fn:
    Optional zero-argument callable returning the dict to cache.
    Only called on ``WRITE_THROUGH``.
retrieve_msg:
    Message used in the cached ``PersistenceResult`` payload.
- `def _delete_with_cache(self, table: str, query: str, params: Tuple[Any, ...], success_msg: str, cache_namespace: str, entity_id: str) -> PersistenceResult`
  * Execute a DELETE SQL statement then invalidate the Redis cache entry.

Equivalent to ``_write_with_cache`` but always invalidates (no
write-through path needed for deletes).
- `def _fetch_one_with_cache(self, table: str, query: str, params: Tuple[Any, ...], entity_id: str, parse_fn: Callable[[Dict[str, Any]], Dict[str, Any]], success_msg: str, not_found_msg: str, cache_namespace: str) -> PersistenceResult`
  * Fetch a single row through Redis cache when available, falling back to
a direct SQL query.

The cache is expected to store a ``PersistenceResult`` (as set by
``_write_with_cache`` on WRITE_THROUGH).  If the cache returns a
``PersistenceResult`` it is returned directly; otherwise the fallback
SQL fetch is executed and wrapped in a new ``PersistenceResult``.

## Module: core/src/aios/services/persistence_impl_modules/embedding.py

### class `MockEmbeddingProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self, model_name: str, dimensions: int) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `EmbeddingServiceImpl`
- **Inherits from**: EmbeddingService

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_provider(self, provider_name: str) -> EmbeddingProvider`
- `def register_provider(self, provider_name: str, provider: EmbeddingProvider) -> None`
- `def embed(self, text: str, provider_name: str) -> List[float]`

### class `EmbeddingVersionManagerImpl`
- **Inherits from**: EmbeddingVersionManager

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_active_version(self, collection_name: str) -> str`
- `def set_active_version(self, collection_name: str, version: str) -> None`
- `def requires_migration(self, collection_name: str, current_version: str) -> bool`

### class `EmbeddingCacheImpl`
- **Inherits from**: EmbeddingCache

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _get_key(self, text: str, version: str) -> str`
- `def get(self, text: str, version: str) -> Optional[List[float]]`
- `def set(self, text: str, vector: List[float], version: str) -> None`
- `def invalidate(self, text: str, version: str) -> None`
- `def clear(self) -> None`
- `def get_statistics(self) -> Dict[str, Any]`

### class `ChunkingServiceImpl`
- **Inherits from**: ChunkingService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def chunk_text(self, text: str, strategy: ChunkStrategy) -> List[ChunkResult]`

### class `ContextBuilderImpl`
- **Inherits from**: ContextBuilder

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def rank_candidates(self, candidates: List[ContextCandidate], objective: str) -> List[ContextRanking]`
- `def deduplicate(self, candidates: List[ContextCandidate]) -> List[ContextCandidate]`
- `def assemble_context(self, candidates: List[ContextCandidate], token_budget: int) -> ContextAssembly`

### class `SentenceTransformerProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self, model_name: str, dimensions: int) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `OpenAIProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self, model_name: str, dimensions: int) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `GeminiProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self, model_name: str, dimensions: int) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `OllamaProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self, model_name: str, dimensions: int) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `EmbeddingEngineImpl`
- **Inherits from**: EmbeddingEngine

**Methods:**

- `def __init__(self, embedding_service: EmbeddingService, cache: EmbeddingCache) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def shutdown(self) -> None`
- `def _retry_worker(self) -> None`
- `def _should_retry(self, attempts: int, last_attempted: float, base_backoff: float) -> bool`
- `def run_retry_cycle(self) -> None`
- `def _persist_failed_job(self, text: str, provider_name: str, collection_name: Optional[str]) -> None`
- `def embed_text(self, request: EmbeddingRequest, retry: bool) -> EmbeddingResponse`
- `def embed_batch(self, requests: List[EmbeddingRequest], retry: bool) -> List[EmbeddingResponse]`
- `def _validate_vector(self, vector: List[float], expected_dims: int) -> None`
- `def _log_err(self, msg: str) -> None`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`

### class `SemanticSearchServiceImpl`
- **Inherits from**: SemanticSearchService

**Methods:**

- `def __init__(self, embed_engine: EmbeddingEngine) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _get_query_cache_key(self, query: SemanticQuery) -> str`
- `def search(self, query: SemanticQuery) -> List[SemanticResult]`
- `def batch_search(self, queries: List[SemanticQuery]) -> List[List[SemanticResult]]`
- `def cross_collection_search(self, query: SemanticQuery, collections: List[str]) -> List[SemanticResult]`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`

### class `QueryAnalysisServiceImpl`
- **Inherits from**: QueryAnalysisService

> Comprehensive query analysis service for Hybrid Retrieval platform.

Classifies 9 intent types: question, documentation, code_search, engineering,
research, conversation_history, automation_workflow, configuration, general_knowledge.
Detects workspace/project scope, collection candidates, and retrieval strategy.
Supports future extensibility via configurable rules.

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def shutdown(self) -> None`
- `def load_config_file(self, config_path: Path) -> None`
  * Load intent rules from configuration file (dynamic runtime config).
- `def get_supported_intents(self) -> List[str]`
- `def register_custom_rule(self, intent: str, domains: List[str], trigger_words: List[str], confidence_boost: float, scope: str) -> None`
  * Register a custom intent rule for future extensibility.
- `def analyze_query(self, query_text: str, context_metadata: Optional[Dict[str, Any]]) -> QueryAnalysis`

### class `CollectionSelectorImpl`
- **Inherits from**: CollectionSelector

> Intelligent collection routing with weighted scoring and configurable priorities.

Supports:
- Single collection routing
- Multi-collection weighted routing
- Workspace/project-scoped filtering
- Configurable collection priorities
- Future plugin support via domain_map extension

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def shutdown(self) -> None`
- `def load_config_file(self, config_path: Path) -> None`
  * Load intent-based collection routing weights from configuration file.
- `def set_collection_priority(self, collection: str, weight: float) -> None`
  * Override collection priority weight at runtime.
- `def register_domain(self, domain: str, collection: str) -> None`
  * Register a new domain -> collection mapping (plugin support).
- `def select_collections(self, analysis: QueryAnalysis) -> Dict[str, float]`
  * Select collections with weighted routing.

Uses intent-based weights when available, falls back to domain-based
with equal weighting. Applies runtime overrides on top.
Returns: Dict[collection_name -> weight (0.0-1.0)]

### class `CandidateRankerImpl`
- **Inherits from**: CandidateRanker

> Configurable multi-signal candidate ranker.

Ranking signals (all configurable via set_weights):
1. semantic_similarity  - raw Qdrant similarity score
2. importance           - domain importance from metadata
3. freshness            - exponential time decay
4. workspace_relevance  - workspace match bonus
5. project_relevance    - project match bonus
6. source_quality       - collection quality tier
7. engineering_priority - engineering collection boost
8. metadata_confidence  - metadata completeness
9. duplicate_penalty    - penalize near-duplicates

No hardcoded constants - all weights are configurable.

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def shutdown(self) -> None`
- `def get_default_weights(self) -> Dict[str, float]`
- `def set_weights(self, weights: Dict[str, float]) -> None`
  * Override ranking weights at runtime. Only provided keys are updated.
- `def rank_candidates(self, candidates: List[RetrievalCandidate], weights: Optional[Dict[str, float]]) -> List[RetrievalCandidate]`
- `def get_statistics(self) -> Dict[str, Any]`

### class `ContextOptimizerImpl`
- **Inherits from**: ContextOptimizer

> Context optimizer that removes duplicates, merges overlapping chunks,
compresses context, preserves citations, respects token budgets,
prioritizes high-value content, and preserves ordering.

No LLM calls - all operations are deterministic.

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def shutdown(self) -> None`
- `def get_statistics(self) -> Dict[str, Any]`
- `def _estimate_tokens(self, text: str) -> int`
  * Estimate token count: approx 4 chars per token.
- `def _text_similarity(self, a: str, b: str) -> float`
  * Simple overlap-based similarity without NLP library.
- `def merge_overlapping_chunks(self, candidates: List[RetrievalCandidate]) -> List[RetrievalCandidate]`
  * Merge candidates with high text overlap (>70% Jaccard similarity).
Preserves the higher-scoring candidate when merging.
- `def compress_context(self, text: str, max_tokens: int) -> str`
  * Compress text to fit within token budget by truncating sentences.
Preserves leading sentences (most important content first).
No LLM calls.
- `def optimize_context(self, candidates: List[RetrievalCandidate], token_budget: int) -> ContextAssemblyResult`
  * Full context optimization pipeline:
1. Deduplicate by exact text match
2. Merge overlapping chunks
3. Respect token budget
4. Prioritize high-value content (by score)
5. Preserve citations (source_collection + id headers)
6. Preserve ordering (already sorted by ranker)

### class `RetrievalCacheImpl`
- **Inherits from**: RetrievalCache

> Multi-tier retrieval cache with Redis integration and memory fallback.

Cache tiers:
- Query cache: full query -> ranked result list
- Candidate cache: collection search results
- Ranking cache: post-ranking results
- Context cache: optimized context strings

Each tier has independent TTL configuration.
Gracefully degrades to in-memory cache when Redis unavailable.
No request fails due to cache unavailability.

**Methods:**

- `def __init__(self, redis_service: Optional[Any]) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def shutdown(self) -> None`
- `def _redis_available(self) -> bool`
- `def _redis_get(self, key: str) -> Optional[str]`
- `def _redis_setex(self, key: str, ttl: int, value: str) -> None`
- `def _redis_delete_pattern(self, pattern: str) -> None`
- `def _serialize_candidates(self, results: List[RetrievalCandidate]) -> str`
- `def _deserialize_candidates(self, raw: str) -> List[RetrievalCandidate]`
- `def _local_set(self, store: Dict[str, Any], key: str, val: Any, ttl: int, tier: str, increment_sets: bool) -> None`
- `def _get_tier_entry(self, store: Dict[str, Any], cache_key: str, redis_key: str, tier: str) -> Optional[Any]`
- `def get_query_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]`
- `def set_query_results(self, cache_key: str, results: List[RetrievalCandidate], ttl: int) -> None`
- `def get_candidate_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]`
- `def set_candidate_results(self, cache_key: str, results: List[RetrievalCandidate], ttl: int) -> None`
- `def get_ranking_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]`
- `def set_ranking_results(self, cache_key: str, results: List[RetrievalCandidate], ttl: int) -> None`
- `def get_context_result(self, cache_key: str) -> Optional[str]`
- `def set_context_result(self, cache_key: str, context: str, ttl: int) -> None`
- `def invalidate(self, pattern: str) -> None`
  * Invalidate all cache tiers matching pattern.
- `def get_statistics(self) -> Dict[str, Any]`

### class `HybridRetrievalServiceImpl`
- **Inherits from**: HybridRetrievalService

**Methods:**

- `def __init__(self, query_analyzer: QueryAnalysisService, selector: CollectionSelector, search_service: SemanticSearchService, ranker: CandidateRanker, optimizer: ContextOptimizer, cache: RetrievalCache) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def shutdown(self) -> None`
- `def retrieve(self, query_text: str, workspace_id: Optional[str], project_id: Optional[str], token_budget: int, filter_query: Optional[Dict[str, Any]]) -> ContextAssemblyResult`
- `def get_recommendations(self) -> List[Dict[str, Any]]`
  * Dynamically generate refinement recommendations based on cache/latency metrics.
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`

## Module: core/src/aios/services/persistence_impl_modules/qdrant.py

### class `QdrantConfigurationService`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`

### class `QdrantConnectionManager`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, config: QdrantConfigurationService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def is_connected(self) -> bool`
- `def get_client(self) -> Any`

### class `QdrantTransportImpl`
- **Inherits from**: QdrantTransport

**Methods:**

- `def __init__(self, config: QdrantConfigurationService, connection_manager: QdrantConnectionManager) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def is_connected(self) -> bool`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute_command(self, cmd: str) -> Any`

### class `QdrantProviderImpl`
- **Inherits from**: QdrantProvider

**Methods:**

- `def __init__(self, transport: QdrantTransport) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_transport(self) -> QdrantTransport`
- `def create_collection(self, name: str, vector_size: int, distance: str, on_disk_payload: bool, quantization_config: Optional[Dict[str, Any]]) -> bool`
- `def delete_collection(self, name: str) -> bool`
- `def collection_exists(self, name: str) -> bool`
- `def upsert_points(self, collection: str, points: List[Dict[str, Any]]) -> bool`
- `def delete_points(self, collection: str, point_ids: List[Any]) -> bool`
- `def search_vectors(self, collection: str, vector: List[float], filter_query: Optional[Dict[str, Any]], limit: int, score_threshold: Optional[float]) -> List[Dict[str, Any]]`
- `def get_collection_info(self, name: str) -> Dict[str, Any]`

### class `CollectionManagerImpl`
- **Inherits from**: CollectionManager

**Methods:**

- `def __init__(self, provider: QdrantProvider, config: QdrantConfigurationService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def create_collection(self, name: str, dimensions: int, distance: str) -> bool`
- `def delete_collection(self, name: str) -> bool`
- `def exists(self, name: str) -> bool`
- `def validate_schema(self, name: str, schema: Dict[str, Any]) -> bool`
- `def create_index(self, collection_name: str, field_name: str, field_type: str) -> bool`
- `def get_statistics(self, name: str) -> Dict[str, Any]`

### class `QdrantRuntimeServiceImpl`
- **Inherits from**: QdrantRuntimeService

**Methods:**

- `def __init__(self, provider: QdrantProvider, collection_manager: CollectionManager, config: QdrantConfigurationService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_provider(self) -> QdrantProvider`
- `def get_collection_manager(self) -> CollectionManager`
- `def get_telemetry(self) -> Dict[str, Any]`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, msg: str, severity: str, remediation: str) -> None`

### class `MockEmbeddingProvider`
- **Inherits from**: EmbeddingProvider

**Methods:**

- `def __init__(self, model_name: str, dimensions: int) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def embed_text(self, text: str) -> List[float]`
- `def embed_batch(self, texts: List[str]) -> List[List[float]]`
- `def get_metadata(self) -> EmbeddingMetadata`

### class `EmbeddingServiceImpl`
- **Inherits from**: EmbeddingService

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_provider(self, provider_name: str) -> EmbeddingProvider`
- `def register_provider(self, provider_name: str, provider: EmbeddingProvider) -> None`
- `def embed(self, text: str, provider_name: str) -> List[float]`

### class `EmbeddingVersionManagerImpl`
- **Inherits from**: EmbeddingVersionManager

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_active_version(self, collection_name: str) -> str`
- `def set_active_version(self, collection_name: str, version: str) -> None`
- `def requires_migration(self, collection_name: str, current_version: str) -> bool`

### class `EmbeddingCacheImpl`
- **Inherits from**: EmbeddingCache

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _get_key(self, text: str, version: str) -> str`
- `def get(self, text: str, version: str) -> Optional[List[float]]`
- `def set(self, text: str, vector: List[float], version: str) -> None`
- `def invalidate(self, text: str, version: str) -> None`
- `def clear(self) -> None`
- `def get_statistics(self) -> Dict[str, Any]`

### class `ChunkingServiceImpl`
- **Inherits from**: ChunkingService

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def chunk_text(self, text: str, strategy: ChunkStrategy) -> List[ChunkResult]`

### class `ContextBuilderImpl`
- **Inherits from**: ContextBuilder

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def rank_candidates(self, candidates: List[ContextCandidate], objective: str) -> List[ContextRanking]`
- `def deduplicate(self, candidates: List[ContextCandidate]) -> List[ContextCandidate]`
- `def assemble_context(self, candidates: List[ContextCandidate], token_budget: int) -> ContextAssembly`

### class `QdrantRepositoryImpl`
- **Inherits from**: VectorMemoryRepository

**Methods:**

- `def __init__(self, collection_name: str, provider: QdrantProvider, col_manager: CollectionManager, dimensions: int, distance: str) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _record_op(self, op: str, latency_ms: float) -> None`
- `def _insert_pending_indexing_job(self, memory_id: str, vector: List[float], payload: Dict[str, Any], operation: str, failure_reason: str) -> None`
  * Auto-insert a pending_indexing_jobs record when Qdrant write fails.

This ensures no data is lost when Qdrant is temporarily unavailable.
The retry daemon (EmbeddingEngineImpl._retry_worker) will automatically
reprocess these records and re-index them once Qdrant recovers.
- `def save(self, memory_id: str, vector: List[float], payload: Dict[str, Any], retry: bool) -> bool`
- `def upsert(self, memory_id: str, vector: List[float], payload: Dict[str, Any], retry: bool) -> bool`
- `def get(self, memory_id: str) -> Optional[Dict[str, Any]]`
- `def delete(self, memory_id: str) -> bool`
- `def exists(self, memory_id: str) -> bool`
- `def search(self, vector: List[float], filter_query: Optional[Dict[str, Any]], limit: int, score_threshold: Optional[float]) -> List[Dict[str, Any]]`
- `def batch_upsert(self, points: List[Dict[str, Any]], retry: bool) -> bool`
- `def batch_delete(self, memory_ids: List[Any]) -> bool`
- `def count(self) -> int`
- `def clear(self) -> bool`
- `def health(self) -> Dict[str, Any]`
- `def statistics(self) -> Dict[str, Any]`

### class `EngineeringMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, EngineeringMemoryRepository

### class `WorkspaceMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, WorkspaceMemoryRepository

### class `ProjectMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, ProjectMemoryRepository

### class `DocumentationMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, DocumentationMemoryRepository

### class `ConversationMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, ConversationMemoryRepository

### class `AutomationMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, AutomationMemoryRepository

### class `ProviderMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, ProviderMemoryRepository

### class `ResearchMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, ResearchMemoryRepository

### class `KnowledgeMemoryRepositoryImpl`
- **Inherits from**: QdrantRepositoryImpl, KnowledgeMemoryRepository

### class `QdrantRuntimeTelemetryImpl`
- **Inherits from**: QdrantRuntimeTelemetry

**Methods:**

- `def __init__(self, registry: Any) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_telemetry(self) -> Dict[str, Any]`

### class `QdrantHealthAnalyzerImpl`
- **Inherits from**: QdrantHealthAnalyzer

**Methods:**

- `def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_health(self) -> Dict[str, Any]`

### class `QdrantCapacityAnalyzerImpl`
- **Inherits from**: QdrantCapacityAnalyzer

**Methods:**

- `def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_capacity(self) -> Dict[str, Any]`

### class `QdrantPerformanceAnalyzerImpl`
- **Inherits from**: QdrantPerformanceAnalyzer

**Methods:**

- `def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _calculate_p50_p95_p99(self, values: List[float]) -> Dict[str, float]`
- `def analyze_performance(self) -> Dict[str, Any]`

### class `QdrantDiagnosticsEngineImpl`
- **Inherits from**: QdrantDiagnosticsEngine

**Methods:**

- `def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`

### class `QdrantRecommendationEngineImpl`
- **Inherits from**: QdrantRecommendationEngine

**Methods:**

- `def __init__(self, diagnostics_engine: QdrantDiagnosticsEngine, capacity_analyzer: QdrantCapacityAnalyzer, performance_analyzer: QdrantPerformanceAnalyzer) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_recommendations(self) -> List[Dict[str, Any]]`

### class `QdrantStatisticsCollectorImpl`
- **Inherits from**: QdrantStatisticsCollector

**Methods:**

- `def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_statistics(self) -> Dict[str, Any]`

### class `QdrantRuntimeReporterImpl`
- **Inherits from**: QdrantRuntimeReporter

**Methods:**

- `def __init__(self, coordinator: QdrantRuntimeCoordinator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_report(self) -> str`

### class `QdrantRuntimeValidatorImpl`
- **Inherits from**: QdrantRuntimeValidator

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def validate_telemetry(self, data: Dict[str, Any]) -> bool`

### class `QdrantRuntimeCoordinatorImpl`
- **Inherits from**: QdrantRuntimeCoordinator

**Methods:**

- `def __init__(self, telemetry_service: QdrantRuntimeTelemetry, health_analyzer: QdrantHealthAnalyzer, capacity_analyzer: QdrantCapacityAnalyzer, performance_analyzer: QdrantPerformanceAnalyzer, recommendation_engine: QdrantRecommendationEngine, diagnostics: QdrantDiagnosticsEngine, stats_collector: QdrantStatisticsCollector, reporter: QdrantRuntimeReporter, validator: QdrantRuntimeValidator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def shutdown(self) -> None`
- `def get_telemetry_service(self) -> QdrantRuntimeTelemetry`
- `def get_health_analyzer(self) -> QdrantHealthAnalyzer`
- `def get_capacity_analyzer(self) -> QdrantCapacityAnalyzer`
- `def get_performance_analyzer(self) -> QdrantPerformanceAnalyzer`
- `def get_recommendation_engine(self) -> QdrantRecommendationEngine`
- `def get_diagnostics(self) -> QdrantDiagnosticsEngine`
- `def get_stats_collector(self) -> QdrantStatisticsCollector`
- `def get_reporter(self) -> QdrantRuntimeReporter`
- `def get_validator(self) -> QdrantRuntimeValidator`

### class `SemanticMemoryManagerImpl`
- **Inherits from**: SemanticMemoryManager

**Methods:**

- `def __init__(self, registry: Any) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def calculate_hash(self, text: str) -> str`
- `def _get_repository(self, repository_name: str) -> Optional[Any]`
- `def calculate_importance(self, text: str, tags: List[str], metadata: Dict[str, Any]) -> float`
- `def index_memory(self, repository_name: str, entity_id: str, text: str, metadata: Dict[str, Any], tags: List[str], importance_override: Optional[float]) -> bool`
- `def retrieve_memories(self, repository_name: str, query_text: str, filter_query: Optional[Dict[str, Any]], limit: int, score_threshold: Optional[float]) -> List[Dict[str, Any]]`
- `def archive_memory(self, repository_name: str, entity_id: str) -> bool`
- `def delete_memory(self, repository_name: str, entity_id: str) -> bool`
- `def reindex_memory(self, repository_name: str, entity_id: str) -> bool`
- `def re_embed_memory(self, repository_name: str, entity_id: str) -> bool`
- `def merge_memories(self, repository_name: str, primary_id: str, secondary_id: str) -> bool`
- `def run_background_cleanup(self, repository_name: str) -> bool`
- `def get_statistics(self) -> Dict[str, Any]`

## Module: core/src/aios/services/persistence_impl_modules/transactions.py

### class `TransactionStackManager`

> Manages transactional savepoints stacks on top of raw transport transactions.

**Methods:**

- `def __init__(self, transport: DatabaseTransport) -> None`
- `def begin(self) -> None`
- `def commit(self) -> None`
- `def rollback(self) -> None`

## Module: core/src/aios/services/persistence_impl_modules/intelligence.py

### class `AIUsageStatisticsRepositoryImpl`
- **Inherits from**: AIUsageStatisticsRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def save(self, usage: Dict[str, Any]) -> PersistenceResult`
- `def get(self, usage_id: str) -> PersistenceResult`
- `def delete(self, usage_id: str) -> PersistenceResult`

### class `AIMemoryRepositoryImpl`
- **Inherits from**: AIMemoryRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def save(self, memory: Dict[str, Any]) -> PersistenceResult`
- `def get(self, memory_id: str) -> PersistenceResult`
- `def delete(self, memory_id: str) -> PersistenceResult`

### class `AIMemoryValidator`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def validate_provider(self, data: Dict[str, Any]) -> List[str]`
- `def validate_capabilities(self, data: Dict[str, Any]) -> List[str]`
- `def validate_health(self, data: Dict[str, Any]) -> List[str]`
- `def validate_telemetry(self, data: Dict[str, Any]) -> List[str]`
- `def validate_statistics(self, data: Dict[str, Any]) -> List[str]`
- `def validate_quota(self, data: Dict[str, Any]) -> List[str]`
- `def validate_routing(self, data: Dict[str, Any]) -> List[str]`
- `def validate_session(self, data: Dict[str, Any]) -> List[str]`
- `def validate_checkpoint(self, data: Dict[str, Any]) -> List[str]`
- `def validate_failover(self, data: Dict[str, Any]) -> List[str]`
- `def validate_usage(self, data: Dict[str, Any]) -> List[str]`
- `def validate_memory(self, data: Dict[str, Any]) -> List[str]`

### class `AIMemoryTelemetry`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_query(self, latency_ms: float, success: bool) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `AIMemoryStatistics`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def compile_statistics(self) -> Dict[str, Any]`

### class `AIMemoryHealthMonitor`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, service: PersistenceService, telemetry: AIMemoryTelemetry, stats: AIMemoryStatistics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `AIMemoryReportGenerator`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, working_dir: str, health_monitor: AIMemoryHealthMonitor) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_health_report(self) -> str`

### class `AIMemoryPersistenceServiceImpl`
- **Inherits from**: AIMemoryPersistenceService

**Methods:**

- `def __init__(self, service: PersistenceService, provider_repo: AIProviderRepository, capability_repo: ProviderCapabilityRepository, health_repo: ProviderHealthRepository, telemetry_repo: ProviderTelemetryRepository, statistics_repo: ProviderStatisticsRepository, quota_repo: ProviderQuotaRepository, routing_repo: ProviderRoutingRepository, session_repo: ProviderSessionRepository, checkpoint_repo: ProviderCheckpointRepository, failover_repo: ProviderFailoverRepository, usage_repo: AIUsageStatisticsRepository, memory_repo: AIMemoryRepository, validator: AIMemoryValidator, telemetry: AIMemoryTelemetry, stats_compiler: AIMemoryStatistics, health_monitor: AIMemoryHealthMonitor, report_generator: AIMemoryReportGenerator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _get_repo(self, category: str) -> Optional[Any]`
- `def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def Archive(self, category: str, entity_id: str) -> PersistenceResult`
- `def archive(self, category: str, entity_id: str) -> PersistenceResult`
- `def Restore(self, category: str, entity_id: str) -> PersistenceResult`
- `def History(self, category: str, entity_id: str) -> PersistenceResult`
- `def Statistics(self) -> PersistenceResult`
- `def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`
- `def search_metadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`

### class `RuntimeCorrelationManager`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def set_context(cls, workspace_id: Optional[str], project_id: Optional[str], repository: Optional[str], operation: Optional[str]) -> str`
- `def get_context(cls) -> Dict[str, Any]`
- `def clear(cls) -> None`

### class `RuntimeTelemetryCollector`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_query(self, latency_ms: float, success: bool) -> None`
- `def record_retry(self) -> None`
- `def record_connection_status(self, active: int, idle: int, failures: int) -> None`

### class `RuntimePerformanceAnalyzer`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, telemetry: RuntimeTelemetryCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_percentile(self, pct: float) -> float`
- `def get_performance_metrics(self) -> Dict[str, float]`

### class `RuntimeStatisticsEngine`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_operation(self, success: bool, policy: str) -> None`
- `def record_cache(self, hit: bool, is_read: bool) -> None`
- `def get_statistics(self) -> Dict[str, Any]`

### class `RuntimeDiagnosticsEngine`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`

### class `RuntimeCapacityAnalyzer`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, telemetry: RuntimeTelemetryCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_capacity_status(self) -> Dict[str, Any]`

### class `RuntimeQueryProfiler`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def profile_query(self, query: str, duration_ms: float) -> None`
- `def get_slow_queries(self) -> List[Dict[str, Any]]`

### class `RuntimeTransactionProfiler`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_transaction(self, duration_ms: float, nested: bool) -> None`
- `def get_transaction_metrics(self) -> Dict[str, Any]`

### class `RuntimeRepositoryProfiler`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_call(self, repo: str, operation: str, duration_ms: float) -> None`
- `def get_utilization(self) -> Dict[str, Any]`

### class `RuntimeLifecycleMonitor`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_boot(self, duration_s: float) -> None`
- `def record_swap(self) -> None`
- `def record_migrations(self, count: int) -> None`
- `def get_lifecycle_status(self) -> Dict[str, Any]`

### class `RuntimeRecommendationEngine`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, telemetry: RuntimeTelemetryCollector, perf: RuntimePerformanceAnalyzer, capacity: RuntimeCapacityAnalyzer, query_prof: RuntimeQueryProfiler, tx_prof: RuntimeTransactionProfiler, repo_prof: RuntimeRepositoryProfiler) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_recommendations(self) -> List[Dict[str, Any]]`

### class `RuntimeHealthMonitor`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, service: PersistenceService, telemetry: RuntimeTelemetryCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `RuntimeReportGenerator`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, working_dir: str, intelligence: Any) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_reports(self) -> None`

### class `RuntimeIntelligenceServiceImpl`
- **Inherits from**: RuntimeIntelligenceService, ServiceLifecycle

**Methods:**

- `def __init__(self, health_monitor: RuntimeHealthMonitor, telemetry: RuntimeTelemetryCollector, stats_engine: RuntimeStatisticsEngine, diag_engine: RuntimeDiagnosticsEngine, capacity: RuntimeCapacityAnalyzer, recommend: RuntimeRecommendationEngine, perf: RuntimePerformanceAnalyzer, query_prof: RuntimeQueryProfiler, tx_prof: RuntimeTransactionProfiler, repo_prof: RuntimeRepositoryProfiler, lifecycle: RuntimeLifecycleMonitor, report_gen: RuntimeReportGenerator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def get_telemetry(self) -> Dict[str, Any]`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_recommendations(self) -> List[Dict[str, Any]]`
- `def get_learning_payload(self) -> Dict[str, Any]`
- `def generate_reports(self) -> None`

### def `get_unified_ri`
- `def get_unified_ri() -> Optional[Any]`

## Module: core/src/aios/services/persistence_impl_modules/sqlite.py

### class `SQLiteTransport`
- **Inherits from**: DatabaseTransport

> Production runtime database transport utilizing local SQLite.

**Methods:**

- `def __init__(self, config: PersistenceConfigurationService) -> None`
- `def active_conn(self) -> Optional[sqlite3.Connection]`
- `def active_conn(self, val: Optional[sqlite3.Connection]) -> None`
- `def tx_depth(self) -> int`
- `def tx_depth(self, val: int) -> None`
- `def validate_configuration(self) -> List[str]`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute(self, query: str, params: Optional[tuple]) -> TransportResult`
- `def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]`
- `def begin_transaction(self) -> TransportTransaction`
- `def health(self) -> TransportHealth`
- `def capabilities(self) -> TransportCapabilities`

### class `SQLiteProvider`
- **Inherits from**: PersistenceProvider

> SQLite engine provider wrapping a SQLiteTransport.

**Methods:**

- `def __init__(self, transport: Optional[DatabaseTransport]) -> None`
- `def initialize(self, config: PersistenceConfigurationService) -> None`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def execute(self, query: str, params: Optional[tuple]) -> List[Dict[str, Any]]`
- `def begin_transaction(self) -> None`
- `def commit_transaction(self) -> None`
- `def rollback_transaction(self) -> None`
- `def is_connected(self) -> bool`
- `def get_metrics(self) -> Dict[str, Any]`

## Module: core/src/aios/services/persistence_impl_modules/migrations.py

### class `Migration`

> Migration definition model.

**Methods:**

- `def __init__(self, version: int, name: str, up_sql: str) -> None`

### class `MigrationManager`

> Discovers, validates, and executes migrations.

**Methods:**

- `def __init__(self, provider: PersistenceProvider) -> None`
- `def register_migration(self, version: int, name: str, up_sql: str) -> None`
- `def initialize_history_table(self) -> None`
- `def get_applied_versions(self) -> List[int]`
- `def get_pending_migrations(self) -> List[Migration]`
- `def validate_migrations(self) -> List[str]`
- `def execute_migrations(self) -> int`

## Module: core/src/aios/services/persistence_impl_modules/repositories.py

### class `WorkspaceRepositoryImpl`
- **Inherits from**: WorkspaceRepository

> Concrete repository mapping workspaces configuration schemas to SQLite/PostgreSQL.

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, workspace: Dict[str, Any]) -> PersistenceResult`
- `def get(self, workspace_id: str) -> Optional[Dict[str, Any]]`
- `def delete(self, workspace_id: str) -> PersistenceResult`
- `def list_all(self) -> List[Dict[str, Any]]`

### class `WorkspaceSessionRepositoryImpl`
- **Inherits from**: WorkspaceSessionRepository

> Concrete repository mapping session lifecycles durability.

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, session: Dict[str, Any]) -> PersistenceResult`
- `def get(self, session_id: str) -> Optional[Dict[str, Any]]`
- `def delete(self, session_id: str) -> PersistenceResult`
- `def list_all(self) -> List[Dict[str, Any]]`

### class `ProjectRepositoryImpl`
- **Inherits from**: ProjectRepository

> Concrete repository mapping projects models.

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, project: Dict[str, Any]) -> PersistenceResult`
- `def get(self, project_id: str) -> Optional[Dict[str, Any]]`
- `def delete(self, project_id: str) -> PersistenceResult`

### class `EngineeringProfileRepositoryImpl`
- **Inherits from**: EngineeringProfileRepository

> Concrete repository mapping engineering configurations and historical versions.

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, profile: Dict[str, Any]) -> PersistenceResult`
- `def get(self, profile_id: str) -> Optional[Dict[str, Any]]`
- `def delete(self, profile_id: str) -> PersistenceResult`
- `def get_history(self, profile_id: str) -> List[Dict[str, Any]]`

### class `ConfigurationRepositoryImpl`
- **Inherits from**: ConfigurationRepository

> Concrete repository mapping configuration profile references.

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, config_profile: Dict[str, Any]) -> PersistenceResult`
- `def get(self, config_profile_id: str) -> Optional[Dict[str, Any]]`
- `def delete(self, config_profile_id: str) -> PersistenceResult`

### class `WorkspacePersistenceValidator`
- **Inherits from**: ServiceLifecycle

> Validator checking configuration inconsistencies.

**Methods:**

- `def validate_workspace(self, workspace: Dict[str, Any]) -> List[str]`

### class `WorkspacePersistenceTelemetry`
- **Inherits from**: ServiceLifecycle

> Tracks query latency statistics and database rollbacks.

**Methods:**

- `def __init__(self) -> None`
- `def record_rollback(self) -> None`
- `def record_failure(self, repo_name: str) -> None`
- `def record_latency(self, latency_ms: float) -> None`
- `def get_telemetry(self) -> Dict[str, Any]`

### class `WorkspacePersistenceStatistics`
- **Inherits from**: ServiceLifecycle

> Compiles statistics summaries from tables.

**Methods:**

- `def __init__(self, workspace_repo: WorkspaceRepository, session_repo: WorkspaceSessionRepository) -> None`
- `def get_stats(self) -> Dict[str, Any]`

### class `WorkspacePersistenceServiceImpl`
- **Inherits from**: WorkspacePersistenceService

> Concrete coordinating service executing operations across durable workspaces.

**Methods:**

- `def __init__(self, workspace_repo: WorkspaceRepository, session_repo: WorkspaceSessionRepository, project_repo: ProjectRepository, profile_repo: EngineeringProfileRepository, config_repo: ConfigurationRepository, validator: WorkspacePersistenceValidator, telemetry: WorkspacePersistenceTelemetry, statistics: WorkspacePersistenceStatistics) -> None`
- `def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]`
- `def save_workspace(self, workspace: Dict[str, Any]) -> None`

### class `WorkspacePersistenceReportGenerator`
- **Inherits from**: ServiceLifecycle

> Compiles metrics, registries, status, and health indicators into markdown reports.

**Methods:**

- `def __init__(self, workspace_root: str, service: WorkspacePersistenceService, diagnostics: PersistenceDiagnostics, telemetry: WorkspacePersistenceTelemetry, statistics: WorkspacePersistenceStatistics, registry: RepositoryRegistry) -> None`
- `def generate_reports(self) -> None`

### class `EngineeringTaskRepositoryImpl`
- **Inherits from**: _RepositoryMixin, EngineeringTaskRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, task: Dict[str, Any]) -> PersistenceResult`
- `def get(self, task_id: str) -> PersistenceResult`
- `def delete(self, task_id: str) -> PersistenceResult`
- `def list_all(self) -> PersistenceResult`

### class `PlanningRepositoryImpl`
- **Inherits from**: _RepositoryMixin, PlanningRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, plan: Dict[str, Any]) -> PersistenceResult`
- `def get(self, plan_id: str) -> PersistenceResult`
- `def delete(self, plan_id: str) -> PersistenceResult`

### class `ApprovalRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ApprovalRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, approval: Dict[str, Any]) -> PersistenceResult`
- `def get(self, approval_id: str) -> PersistenceResult`
- `def delete(self, approval_id: str) -> PersistenceResult`

### class `ReviewRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ReviewRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, review: Dict[str, Any]) -> PersistenceResult`
- `def get(self, review_id: str) -> PersistenceResult`
- `def delete(self, review_id: str) -> PersistenceResult`

### class `DocumentationMetadataRepositoryImpl`
- **Inherits from**: _RepositoryMixin, DocumentationMetadataRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, doc: Dict[str, Any]) -> PersistenceResult`
- `def get(self, doc_id: str) -> PersistenceResult`
- `def delete(self, doc_id: str) -> PersistenceResult`

### class `TestSessionRepositoryImpl`
- **Inherits from**: _RepositoryMixin, TestSessionRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, session: Dict[str, Any]) -> PersistenceResult`
- `def get(self, session_id: str) -> PersistenceResult`
- `def delete(self, session_id: str) -> PersistenceResult`

### class `TestResultRepositoryImpl`
- **Inherits from**: _RepositoryMixin, TestResultRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, result: Dict[str, Any]) -> PersistenceResult`
- `def get(self, result_id: str) -> PersistenceResult`
- `def delete(self, result_id: str) -> PersistenceResult`

### class `EngineeringMemoryValidator`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def validate_task(self, data: Dict[str, Any]) -> List[str]`
- `def validate_plan(self, data: Dict[str, Any]) -> List[str]`
- `def validate_approval(self, data: Dict[str, Any]) -> List[str]`
- `def validate_review(self, data: Dict[str, Any]) -> List[str]`
- `def validate_doc(self, data: Dict[str, Any]) -> List[str]`
- `def validate_test_session(self, data: Dict[str, Any]) -> List[str]`
- `def validate_test_result(self, data: Dict[str, Any]) -> List[str]`

### class `EngineeringMemoryTelemetry`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_query(self, latency_ms: float, success: bool) -> None`
- `def get_average_latency(self) -> float`
- `def get_p95_latency(self) -> float`

### class `EngineeringMemoryStatistics`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def compile_statistics(self) -> Dict[str, Any]`

### class `EngineeringMemoryHealthMonitor`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, service: PersistenceService, telemetry: EngineeringMemoryTelemetry, stats_compiler: EngineeringMemoryStatistics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `EngineeringMemoryReportGenerator`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, workspace_root: str, health_monitor: EngineeringMemoryHealthMonitor) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_reports(self) -> None`

### class `EngineeringMemoryServiceImpl`
- **Inherits from**: EngineeringMemoryService

**Methods:**

- `def __init__(self, service: PersistenceService, task_repo: EngineeringTaskRepository, planning_repo: PlanningRepository, approval_repo: ApprovalRepository, review_repo: ReviewRepository, doc_repo: DocumentationMetadataRepository, test_session_repo: TestSessionRepository, test_result_repo: TestResultRepository, validator: EngineeringMemoryValidator, telemetry: EngineeringMemoryTelemetry, stats_compiler: EngineeringMemoryStatistics, health_monitor: EngineeringMemoryHealthMonitor, report_generator: EngineeringMemoryReportGenerator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _get_repo(self, category: str) -> Optional[Any]`
- `def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def Archive(self, category: str, entity_id: str) -> PersistenceResult`
- `def archive(self, category: str, entity_id: str) -> PersistenceResult`
- `def Restore(self, category: str, entity_id: str) -> PersistenceResult`
- `def restore(self, category: str, entity_id: str) -> PersistenceResult`
- `def History(self, category: str, entity_id: str) -> PersistenceResult`
- `def history(self, category: str, entity_id: str) -> PersistenceResult`
- `def Statistics(self) -> PersistenceResult`
- `def statistics(self) -> PersistenceResult`
- `def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`
- `def search_metadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`

### class `WorkflowRepositoryImpl`
- **Inherits from**: _RepositoryMixin, WorkflowRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, workflow: Dict[str, Any]) -> PersistenceResult`
- `def get(self, workflow_id: str) -> PersistenceResult`
- `def delete(self, workflow_id: str) -> PersistenceResult`

### class `WorkflowExecutionRepositoryImpl`
- **Inherits from**: _RepositoryMixin, WorkflowExecutionRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, execution: Dict[str, Any]) -> PersistenceResult`
- `def get(self, execution_id: str) -> PersistenceResult`
- `def delete(self, execution_id: str) -> PersistenceResult`

### class `WorkflowMonitoringRepositoryImpl`
- **Inherits from**: _RepositoryMixin, WorkflowMonitoringRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, monitor_report: Dict[str, Any]) -> PersistenceResult`
- `def get(self, report_id: str) -> PersistenceResult`
- `def delete(self, report_id: str) -> PersistenceResult`

### class `WorkflowOptimizationRepositoryImpl`
- **Inherits from**: _RepositoryMixin, WorkflowOptimizationRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, optimization: Dict[str, Any]) -> PersistenceResult`
- `def get(self, optimization_id: str) -> PersistenceResult`
- `def delete(self, optimization_id: str) -> PersistenceResult`

### class `WorkflowVersionRepositoryImpl`
- **Inherits from**: _RepositoryMixin, WorkflowVersionRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, version: Dict[str, Any]) -> PersistenceResult`
- `def get(self, version_id: str) -> PersistenceResult`
- `def delete(self, version_id: str) -> PersistenceResult`

### class `WorkflowTranslationRepositoryImpl`
- **Inherits from**: _RepositoryMixin, WorkflowTranslationRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, translation: Dict[str, Any]) -> PersistenceResult`
- `def get(self, translation_id: str) -> PersistenceResult`
- `def delete(self, translation_id: str) -> PersistenceResult`

### class `WorkflowIntegrationRepositoryImpl`
- **Inherits from**: _RepositoryMixin, WorkflowIntegrationRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, integration: Dict[str, Any]) -> PersistenceResult`
- `def get(self, integration_id: str) -> PersistenceResult`
- `def delete(self, integration_id: str) -> PersistenceResult`

### class `AutomationTelemetryRepositoryImpl`
- **Inherits from**: _RepositoryMixin, AutomationTelemetryRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, telemetry: Dict[str, Any]) -> PersistenceResult`
- `def get(self, telemetry_id: str) -> PersistenceResult`
- `def delete(self, telemetry_id: str) -> PersistenceResult`

### class `AutomationStatisticsRepositoryImpl`
- **Inherits from**: _RepositoryMixin, AutomationStatisticsRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, stats: Dict[str, Any]) -> PersistenceResult`
- `def get(self, stats_id: str) -> PersistenceResult`
- `def delete(self, stats_id: str) -> PersistenceResult`

### class `AutomationPersistenceValidator`
- **Inherits from**: ServiceLifecycle

> Validates Automation entity schemas and structures.

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def validate_workflow(self, data: Dict[str, Any]) -> List[str]`
- `def validate_execution(self, data: Dict[str, Any]) -> List[str]`
- `def validate_monitor(self, data: Dict[str, Any]) -> List[str]`
- `def validate_optimization(self, data: Dict[str, Any]) -> List[str]`
- `def validate_version(self, data: Dict[str, Any]) -> List[str]`
- `def validate_translation(self, data: Dict[str, Any]) -> List[str]`
- `def validate_integration(self, data: Dict[str, Any]) -> List[str]`
- `def validate_telemetry(self, data: Dict[str, Any]) -> List[str]`
- `def validate_statistics(self, data: Dict[str, Any]) -> List[str]`

### class `AutomationPersistenceTelemetry`
- **Inherits from**: ServiceLifecycle

> Monitors queries latencies and failures for Automation Persistence Service.

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_query(self, latency: float, success: bool) -> None`
- `def get_average_latency(self) -> float`
- `def get_p95_latency(self) -> float`

### class `AutomationPersistenceStatistics`
- **Inherits from**: ServiceLifecycle

> Compiles statistics across Automation tables.

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def compile_statistics(self) -> Dict[str, Any]`

### class `AutomationPersistenceHealthMonitor`
- **Inherits from**: ServiceLifecycle

> Validates connectivity and schema consistency for automation persistence.

**Methods:**

- `def __init__(self, service: PersistenceService, telemetry: AutomationPersistenceTelemetry, stats: AutomationPersistenceStatistics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `AutomationPersistenceReportGenerator`
- **Inherits from**: ServiceLifecycle

> Outputs status, diagnostics, and metrics summaries for M4.

**Methods:**

- `def __init__(self, workspace_root: str, health_monitor: AutomationPersistenceHealthMonitor) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_health_report(self) -> str`

### class `AutomationPersistenceServiceImpl`
- **Inherits from**: AutomationPersistenceService

> Implementation of AutomationPersistenceService coordinator.

**Methods:**

- `def __init__(self, service: PersistenceService, workflow_repo: WorkflowRepository, execution_repo: WorkflowExecutionRepository, monitor_repo: WorkflowMonitoringRepository, optimization_repo: WorkflowOptimizationRepository, version_repo: WorkflowVersionRepository, translation_repo: WorkflowTranslationRepository, integration_repo: WorkflowIntegrationRepository, telemetry_repo: AutomationTelemetryRepository, stats_repo: AutomationStatisticsRepository, validator: AutomationPersistenceValidator, telemetry: AutomationPersistenceTelemetry, stats_compiler: AutomationPersistenceStatistics, health_monitor: AutomationPersistenceHealthMonitor, report_generator: AutomationPersistenceReportGenerator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def _get_repo(self, category: str) -> Optional[Any]`
- `def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult`
- `def Archive(self, category: str, entity_id: str) -> PersistenceResult`
- `def archive(self, category: str, entity_id: str) -> PersistenceResult`
- `def Restore(self, category: str, entity_id: str) -> PersistenceResult`
- `def restore(self, category: str, entity_id: str) -> PersistenceResult`
- `def History(self, category: str, entity_id: str) -> PersistenceResult`
- `def history(self, category: str, entity_id: str) -> PersistenceResult`
- `def Statistics(self) -> PersistenceResult`
- `def statistics(self) -> PersistenceResult`
- `def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`
- `def search_metadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult`

### class `AIProviderRepositoryImpl`
- **Inherits from**: _RepositoryMixin, AIProviderRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, provider: Dict[str, Any]) -> PersistenceResult`
- `def get(self, provider_id: str) -> PersistenceResult`
- `def delete(self, provider_id: str) -> PersistenceResult`

### class `ProviderCapabilityRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderCapabilityRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, capabilities: Dict[str, Any]) -> PersistenceResult`
- `def get(self, capability_id: str) -> PersistenceResult`
- `def delete(self, capability_id: str) -> PersistenceResult`

### class `ProviderHealthRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderHealthRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, health: Dict[str, Any]) -> PersistenceResult`
- `def get(self, health_id: str) -> PersistenceResult`
- `def delete(self, health_id: str) -> PersistenceResult`

### class `ProviderTelemetryRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderTelemetryRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, telemetry: Dict[str, Any]) -> PersistenceResult`
- `def get(self, telemetry_id: str) -> PersistenceResult`
- `def delete(self, telemetry_id: str) -> PersistenceResult`

### class `ProviderStatisticsRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderStatisticsRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, statistics: Dict[str, Any]) -> PersistenceResult`
- `def get(self, statistics_id: str) -> PersistenceResult`
- `def delete(self, statistics_id: str) -> PersistenceResult`

### class `ProviderQuotaRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderQuotaRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, quota: Dict[str, Any]) -> PersistenceResult`
- `def get(self, quota_id: str) -> PersistenceResult`
- `def delete(self, quota_id: str) -> PersistenceResult`

### class `ProviderRoutingRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderRoutingRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, routing: Dict[str, Any]) -> PersistenceResult`
- `def get(self, routing_id: str) -> PersistenceResult`
- `def delete(self, routing_id: str) -> PersistenceResult`

### class `ProviderSessionRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderSessionRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, session: Dict[str, Any]) -> PersistenceResult`
- `def get(self, session_id: str) -> PersistenceResult`
- `def delete(self, session_id: str) -> PersistenceResult`

### class `ProviderCheckpointRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderCheckpointRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, checkpoint: Dict[str, Any]) -> PersistenceResult`
- `def get(self, checkpoint_id: str) -> PersistenceResult`
- `def delete(self, checkpoint_id: str) -> PersistenceResult`

### class `ProviderFailoverRepositoryImpl`
- **Inherits from**: _RepositoryMixin, ProviderFailoverRepository

**Methods:**

- `def __init__(self, service: PersistenceService) -> None`
- `def save(self, failover: Dict[str, Any]) -> PersistenceResult`
- `def get(self, failover_id: str) -> PersistenceResult`
- `def delete(self, failover_id: str) -> PersistenceResult`

## Module: core/src/aios/services/persistence_impl_modules/utilities.py

### def `format_query`
- `def format_query(query: str, provider_name: str) -> str`
> Helper to convert SQL query positional markers to Postgres formats dynamically.

### def `serialize_val`
- `def serialize_val(val: Any) -> str`

### def `deserialize_val`
- `def deserialize_val(s: str) -> Any`

### def `build_qdrant_filter`
- `def build_qdrant_filter(filter_dict: Dict[str, Any]) -> Any`

## Module: core/src/aios/services/persistence_impl_modules/redis/sessions.py

### class `SessionRegistryImpl`
- **Inherits from**: SessionRegistry

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def register_session_type(self, session_type: str, owner_service: str, ttl: float, policy: SessionPolicy, recovery_strategy: str, redis_prefix: str, source_of_truth: Optional[str], heartbeat_required: bool) -> None`
- `def get_configuration(self, session_type: str) -> Dict[str, Any]`
- `def get_all_types(self) -> List[str]`

### class `SessionStatisticsCollectorImpl`
- **Inherits from**: SessionStatisticsCollector

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_create(self, session_type: str, correlation_id: Optional[str]) -> None`
- `def record_read(self, session_type: str, hit: bool, correlation_id: Optional[str]) -> None`
- `def record_update(self, session_type: str, correlation_id: Optional[str]) -> None`
- `def record_delete(self, session_type: str, correlation_id: Optional[str]) -> None`
- `def record_expire(self, session_type: str, reason: str) -> None`
- `def record_renew(self, session_type: str, correlation_id: Optional[str]) -> None`
- `def record_recovery(self, session_type: str, success: bool) -> None`
- `def record_heartbeat(self, session_type: str) -> None`
- `def record_latency(self, op: str, latency_ms: float) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `SessionDiagnosticsImpl`
- **Inherits from**: SessionDiagnostics

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `SessionHealthMonitorImpl`
- **Inherits from**: SessionHealthMonitor

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `SessionRecommendationEngineImpl`
- **Inherits from**: SessionRecommendationEngine

**Methods:**

- `def __init__(self, stats: SessionStatisticsCollector, diag: SessionDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `SessionStoreImpl`
- **Inherits from**: SessionStore

**Methods:**

- `def __init__(self, provider: RedisProvider, registry: SessionRegistry, stats: SessionStatisticsCollector, diag: SessionDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def make_key(self, workspace_id: Optional[str], project_id: Optional[str], session_type: str, session_id: str) -> str`
- `def create(self, session_type: str, session_id: str, data: Dict[str, Any], workspace_id: Optional[str], project_id: Optional[str]) -> bool`
- `def read(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]`
- `def update(self, session_type: str, session_id: str, data: Dict[str, Any]) -> bool`
- `def delete(self, session_type: str, session_id: str) -> bool`
- `def renew(self, session_type: str, session_id: str) -> bool`
- `def heartbeat(self, session_type: str, session_id: str) -> bool`

### class `SessionExpirationManagerImpl`
- **Inherits from**: SessionExpirationManager

**Methods:**

- `def __init__(self, store: SessionStore, registry: SessionRegistry) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_expirations(self) -> List[str]`
- `def expire_session(self, session_id: str, reason: str) -> None`

### class `SessionRecoveryManagerImpl`
- **Inherits from**: SessionRecoveryManager

**Methods:**

- `def __init__(self, p_service: PersistenceService, provider: RedisProvider, stats: SessionStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def register_recovery_handler(self, session_type: str, handler: Callable[[str], Optional[Dict[str, Any]]]) -> None`
- `def recover_session(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]`
- `def trigger_rebuild_incremental(self) -> int`

### class `SessionManagerImpl`
- **Inherits from**: SessionManager

**Methods:**

- `def __init__(self, store: SessionStore, recovery: SessionRecoveryManager, registry: SessionRegistry, stats: SessionStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def create_session(self, session_type: str, session_id: str, data: Dict[str, Any], workspace_id: Optional[str], project_id: Optional[str]) -> bool`
- `def get_session(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]`
- `def update_session(self, session_type: str, session_id: str, data: Dict[str, Any]) -> bool`
- `def delete_session(self, session_type: str, session_id: str) -> bool`
- `def renew_session(self, session_type: str, session_id: str) -> bool`
- `def heartbeat(self, session_type: str, session_id: str) -> bool`

### class `RedisSessionServiceImpl`
- **Inherits from**: RedisSessionService

**Methods:**

- `def __init__(self, provider: RedisProvider, registry: SessionRegistry, store: SessionStore, manager: SessionManager, stats: SessionStatisticsCollector, diag: SessionDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_manager(self) -> SessionManager`
- `def get_registry(self) -> SessionRegistry`
- `def get_store(self) -> SessionStore`

## Module: core/src/aios/services/persistence_impl_modules/redis/queues.py

### class `QueueRegistryImpl`
- **Inherits from**: QueueRegistry

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def register_queue(self, queue_type: str, owner_service: str, priority: QueuePriority, retry_policy: Dict[str, Any], visibility_timeout: float, retention_policy: float, dlq_name: str, worker_type: str, concurrency_limit: int, recovery_strategy: str) -> None`
- `def get_configuration(self, queue_type: str) -> Dict[str, Any]`
- `def get_all_types(self) -> List[str]`

### class `QueueStatisticsCollectorImpl`
- **Inherits from**: QueueStatisticsCollector

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_enqueue(self, queue_type: str, priority: QueuePriority) -> None`
- `def record_dequeue(self, queue_type: str, success: bool) -> None`
- `def record_ack(self, queue_type: str) -> None`
- `def record_retry(self, queue_type: str) -> None`
- `def record_dlq(self, queue_type: str) -> None`
- `def record_duration(self, queue_type: str, duration_ms: float) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `QueueDiagnosticsImpl`
- **Inherits from**: QueueDiagnostics

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `QueueHealthMonitorImpl`
- **Inherits from**: QueueHealthMonitor

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `QueueRecommendationEngineImpl`
- **Inherits from**: QueueRecommendationEngine

**Methods:**

- `def __init__(self, stats: QueueStatisticsCollector, diag: QueueDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `PriorityQueueManagerImpl`
- **Inherits from**: PriorityQueueManager

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def sort_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]`

### class `DelayedQueueManagerImpl`
- **Inherits from**: DelayedQueueManager

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def add_delayed_job(self, job: Dict[str, Any], delay_seconds: float) -> None`
- `def extract_ready_jobs(self) -> List[Dict[str, Any]]`

### class `RetryQueueManagerImpl`
- **Inherits from**: RetryQueueManager

**Methods:**

- `def __init__(self, registry: QueueRegistry, stats: QueueStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def handle_failure(self, job: Dict[str, Any], error: str) -> bool`

### class `QueueSchedulerImpl`
- **Inherits from**: QueueScheduler

**Methods:**

- `def __init__(self, manager: QueueManager) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def poll_schedule(self) -> None`

### class `QueueWorkerCoordinatorImpl`
- **Inherits from**: QueueWorkerCoordinator

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def register_worker(self, worker_id: str, worker_type: str) -> None`
- `def get_worker_utilization(self) -> Dict[str, Any]`

### class `QueueRecoveryManagerImpl`
- **Inherits from**: QueueRecoveryManager

**Methods:**

- `def __init__(self, stats: QueueStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def recover_pending_jobs(self) -> int`

### class `QueueManagerImpl`
- **Inherits from**: QueueManager

**Methods:**

- `def __init__(self, provider: RedisProvider, registry: QueueRegistry, priority_mgr: PriorityQueueManager, delayed_mgr: DelayedQueueManager, retry_mgr: RetryQueueManager, stats: QueueStatisticsCollector, diag: QueueDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def make_key(self, queue_type: str, job_id: str) -> str`
- `def enqueue(self, queue_type: str, job_id: str, payload: Dict[str, Any], priority: Optional[QueuePriority], delay: float) -> bool`
- `def dequeue(self, queue_type: str, worker_id: str) -> Optional[Dict[str, Any]]`
- `def peek(self, queue_type: str) -> Optional[Dict[str, Any]]`
- `def cancel(self, queue_type: str, job_id: str) -> bool`
- `def acknowledge(self, queue_type: str, job_id: str, worker_id: str) -> bool`
- `def heartbeat(self, queue_type: str, job_id: str, worker_id: str) -> bool`
- `def pause(self, queue_type: str) -> None`
- `def resume(self, queue_type: str) -> None`
- `def purge(self, queue_type: str) -> None`

### class `RedisQueueServiceImpl`
- **Inherits from**: RedisQueueService

**Methods:**

- `def __init__(self, provider: RedisProvider, registry: QueueRegistry, manager: QueueManager, stats: QueueStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_manager(self) -> QueueManager`
- `def get_registry(self) -> QueueRegistry`
- `def get_stats(self) -> QueueStatisticsCollector`

### class `JobStateMachineImpl`
- **Inherits from**: JobStateMachine

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def transition_to(self, job_id: str, new_state: JobState, metadata: Optional[Dict[str, Any]]) -> bool`
- `def get_state(self, job_id: str) -> Optional[JobState]`

## Module: core/src/aios/services/persistence_impl_modules/redis/rate_limiting.py

### class `QuotaRegistryImpl`
- **Inherits from**: QuotaRegistry

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def register_quota(self, quota_type: str, owner_service: str, algorithm: str, capacity: int, refill_rate: float, burst_size: int, window_duration: float, fallback_strategy: str, sync_policy: str) -> None`
- `def get_configuration(self, quota_type: str) -> Dict[str, Any]`
- `def get_all_types(self) -> List[str]`

### class `TokenBucketManagerImpl`
- **Inherits from**: TokenBucketManager

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def consume(self, key: str, capacity: int, refill_rate: float, tokens: int) -> bool`

### class `SlidingWindowManagerImpl`
- **Inherits from**: SlidingWindowManager

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def consume(self, key: str, limit: int, window: float, tokens: int) -> bool`

### class `FixedWindowManagerImpl`
- **Inherits from**: FixedWindowManager

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def consume(self, key: str, limit: int, window: float, tokens: int) -> bool`

### class `QuotaSynchronizationManagerImpl`
- **Inherits from**: QuotaSynchronizationManager

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def sync_quota_to_db(self, quota_type: str, resource_id: str, current_usage: int) -> None`

### class `RateLimitRecoveryManagerImpl`
- **Inherits from**: RateLimitRecoveryManager

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def recover_limits(self) -> int`

### class `RateLimitStatisticsCollectorImpl`
- **Inherits from**: RateLimitStatisticsCollector

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_request(self, quota_type: str, allowed: bool, burst_used: bool) -> None`
- `def record_sync(self) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `RateLimitDiagnosticsImpl`
- **Inherits from**: RateLimitDiagnostics

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `RateLimitHealthMonitorImpl`
- **Inherits from**: RateLimitHealthMonitor

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `RateLimitRecommendationEngineImpl`
- **Inherits from**: RateLimitRecommendationEngine

**Methods:**

- `def __init__(self, stats: RateLimitStatisticsCollector, diag: RateLimitDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `RateLimitManagerImpl`
- **Inherits from**: RateLimitManager

**Methods:**

- `def __init__(self, provider: RedisProvider, registry: QuotaRegistry, token_bucket: TokenBucketManager, sliding_window: SlidingWindowManager, fixed_window: FixedWindowManager, sync_mgr: QuotaSynchronizationManager, recovery_mgr: RateLimitRecoveryManager, stats: RateLimitStatisticsCollector, diag: RateLimitDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def make_key(self, quota_type: str, resource_id: str) -> str`
- `def allow_request(self, quota_type: str, resource_id: str, tokens: int) -> bool`
- `def _local_consume(self, key: str, algo: str, capacity: int, refill_rate: float, window: float, tokens: int) -> bool`
- `def get_quota_status(self, quota_type: str, resource_id: str) -> Dict[str, Any]`

### class `RedisRateLimitServiceImpl`
- **Inherits from**: RedisRateLimitService

**Methods:**

- `def __init__(self, provider: RedisProvider, registry: QuotaRegistry, manager: RateLimitManager, stats: RateLimitStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_manager(self) -> RateLimitManager`
- `def get_registry(self) -> QuotaRegistry`
- `def get_stats(self) -> RateLimitStatisticsCollector`

## Module: core/src/aios/services/persistence_impl_modules/redis/locks.py

### class `LockRegistryImpl`
- **Inherits from**: LockRegistry

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def register_lock_type(self, lock_type: str, owner_service: str, redis_prefix: str, lease_duration: float, renewal_strategy: str, timeout: float, recovery_strategy: str, deadlock_rules: Dict[str, Any], retry_policy: Dict[str, Any]) -> None`
- `def get_configuration(self, lock_type: str) -> Dict[str, Any]`
- `def get_all_types(self) -> List[str]`

### class `LockLeaseManagerImpl`
- **Inherits from**: LockLeaseManager

**Methods:**

- `def __init__(self, provider: RedisProvider, registry: LockRegistry, deadlock: DeadlockDetector, stats: CoordinationStatisticsCollector, diag: CoordinationDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def make_key(self, lock_type: str, lock_id: str) -> str`
- `def acquire_lease(self, lock_type: str, lock_id: str, owner_id: str, policy: LockPolicy, lease_duration: Optional[float]) -> bool`
- `def renew_lease(self, lock_type: str, lock_id: str, owner_id: str) -> bool`
- `def release_lease(self, lock_type: str, lock_id: str, owner_id: str) -> bool`
- `def force_release(self, lock_type: str, lock_id: str) -> bool`
- `def verify_ownership(self, lock_type: str, lock_id: str, owner_id: str) -> bool`

### class `LockRecoveryManagerImpl`
- **Inherits from**: LockRecoveryManager

**Methods:**

- `def __init__(self, stats: CoordinationStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def recover_locks(self) -> int`
- `def trigger_lock_rebuild(self) -> None`

### class `MutexManagerImpl`
- **Inherits from**: MutexManager

**Methods:**

- `def __init__(self, lease_manager: LockLeaseManager, stats: CoordinationStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def acquire_mutex(self, lock_type: str, lock_id: str, owner_id: str, timeout: float) -> bool`
- `def release_mutex(self, lock_type: str, lock_id: str, owner_id: str) -> bool`

### class `DistributedLockManagerImpl`
- **Inherits from**: DistributedLockManager

**Methods:**

- `def __init__(self, lease_manager: LockLeaseManager, deadlock: DeadlockDetector, stats: CoordinationStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def acquire(self, lock_type: str, lock_id: str, owner_id: str, policy: LockPolicy, lease_duration: Optional[float], timeout: Optional[float]) -> bool`
- `def release(self, lock_type: str, lock_id: str, owner_id: str) -> bool`
- `def renew(self, lock_type: str, lock_id: str, owner_id: str) -> bool`
- `def is_locked(self, lock_type: str, lock_id: str) -> bool`

## Module: core/src/aios/services/persistence_impl_modules/redis/cache.py

### class `CachePolicyManagerImpl`
- **Inherits from**: CachePolicyManager

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_policy(self, subsystem: str) -> CachePolicy`
- `def get_ttl(self, subsystem: str) -> int`
- `def set_policy(self, subsystem: str, policy: CachePolicy) -> None`
- `def set_ttl(self, subsystem: str, ttl: int) -> None`

### class `CacheStatisticsCollectorImpl`
- **Inherits from**: CacheStatisticsCollector

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_hit(self, subsystem: str, latency_ms: float, correlation_id: Optional[str]) -> None`
- `def record_miss(self, subsystem: str, latency_ms: float, correlation_id: Optional[str]) -> None`
- `def record_expiration(self, key: str) -> None`
- `def record_invalidation(self, count: int) -> None`
- `def record_warmup(self, key_count: int) -> None`
- `def record_rebuild(self, key_count: int) -> None`
- `def record_recommendation(self, rec: Dict[str, Any]) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `CacheDiagnosticsImpl`
- **Inherits from**: CacheDiagnostics

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`

### class `CacheHealthMonitorImpl`
- **Inherits from**: CacheHealthMonitor

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `CacheRecommendationEngineImpl`
- **Inherits from**: CacheRecommendationEngine

**Methods:**

- `def __init__(self, stats: CacheStatisticsCollector, diag: CacheDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `CacheInvalidationManagerImpl`
- **Inherits from**: CacheInvalidationManager

**Methods:**

- `def __init__(self, provider: RedisProvider, stats: CacheStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def make_key(self, subsystem: str, entity_id: str) -> str`
- `def invalidate_key(self, key: str) -> bool`
- `def invalidate_entity(self, subsystem: str, entity_id: str) -> bool`
- `def invalidate_workspace(self, workspace_id: str) -> int`
- `def invalidate_project(self, project_id: str) -> int`
- `def invalidate_provider(self, provider_name: str) -> int`
- `def invalidate_pattern(self, pattern: str) -> int`
- `def invalidate_bulk(self, keys: List[str]) -> int`

### class `CacheWarmupServiceImpl`
- **Inherits from**: CacheWarmupService

**Methods:**

- `def __init__(self, service: PersistenceService, cache_service: RedisCacheService, stats: CacheStatisticsCollector) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def warmup_all_background(self) -> None`
- `def _run_warmup(self) -> None`
- `def warm_subsystem(self, subsystem: str) -> None`

### class `CacheRebuildServiceImpl`
- **Inherits from**: CacheRebuildService

**Methods:**

- `def __init__(self, service: PersistenceService, provider: RedisProvider, stats: CacheStatisticsCollector, warmup_svc: CacheWarmupService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def trigger_rebuild_background(self) -> None`
- `def _run_rebuild(self) -> None`
- `def rebuild_incremental(self) -> int`

### class `RedisCacheServiceImpl`
- **Inherits from**: RedisCacheService

**Methods:**

- `def __init__(self, provider: RedisProvider, policy_mgr: CachePolicyManager, stats: CacheStatisticsCollector, diag: CacheDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def make_key(self, subsystem: str, entity_id: str) -> str`
- `def get(self, subsystem: str, entity_id: str, fetch_func: Callable[[], Any], policy: Optional[CachePolicy], ttl: Optional[int]) -> Any`
- `def set(self, subsystem: str, entity_id: str, value: Any, policy: Optional[CachePolicy], ttl: Optional[int]) -> bool`
- `def delete(self, subsystem: str, entity_id: str) -> bool`

## Module: core/src/aios/services/persistence_impl_modules/redis/telemetry.py

### class `RedisTelemetry`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_query(self, latency_ms: float, success: bool) -> None`

### class `RedisStatistics`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, telemetry: RedisTelemetry) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `RedisDiagnostics`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, conn_manager: RedisConnectionManager) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`

### class `RedisHealthMonitor`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, transport: RedisTransport) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `RedisValidator`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def validate_key(self, key: str) -> List[str]`

### class `RedisReportGenerator`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, working_dir: str, runtime_service: Any) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_reports(self) -> None`

### class `RedisRuntimeTelemetryImpl`
- **Inherits from**: RedisRuntimeTelemetry

**Methods:**

- `def __init__(self, aggregator: RedisRuntimeAggregator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_telemetry(self) -> Dict[str, Any]`

### class `RedisRuntimeAggregatorImpl`
- **Inherits from**: RedisRuntimeAggregator

**Methods:**

- `def __init__(self, cache_stats: CacheStatisticsCollector, session_stats: SessionStatisticsCollector, coord_stats: CoordinationStatisticsCollector, queue_stats: QueueStatisticsCollector, rate_limit_stats: RateLimitStatisticsCollector, connection: RedisConnectionManager) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def aggregate_metrics(self) -> Dict[str, Any]`

### class `RedisRuntimeHealthAnalyzerImpl`
- **Inherits from**: RedisRuntimeHealthAnalyzer

**Methods:**

- `def __init__(self, cache_health: CacheHealthMonitor, session_health: SessionHealthMonitor, coord_health: CoordinationHealthMonitor, queue_health: QueueHealthMonitor, rate_limit_health: RateLimitHealthMonitor) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_health(self) -> Dict[str, Any]`

### class `RedisCapacityAnalyzerImpl`
- **Inherits from**: RedisCapacityAnalyzer

**Methods:**

- `def __init__(self, aggregator: RedisRuntimeAggregator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_capacity(self) -> Dict[str, Any]`

### class `RedisPerformanceAnalyzerImpl`
- **Inherits from**: RedisPerformanceAnalyzer

**Methods:**

- `def __init__(self, aggregator: RedisRuntimeAggregator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def analyze_performance(self) -> Dict[str, Any]`

### class `RedisRecommendationEngineImpl`
- **Inherits from**: RedisRecommendationEngine

**Methods:**

- `def __init__(self, cache_rec: CacheRecommendationEngine, session_rec: SessionRecommendationEngine, coord_rec: CoordinationRecommendationEngine, queue_rec: QueueRecommendationEngine, rate_limit_rec: RateLimitRecommendationEngine) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_recommendations(self) -> List[Dict[str, Any]]`

### class `RedisRuntimeDiagnosticsImpl`
- **Inherits from**: RedisRuntimeDiagnostics

**Methods:**

- `def __init__(self, cache_diag: CacheDiagnostics, session_diag: SessionDiagnostics, coord_diag: CoordinationDiagnostics, queue_diag: QueueDiagnostics, rate_limit_diag: RateLimitDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `RedisRuntimeStatisticsCollectorImpl`
- **Inherits from**: RedisRuntimeStatisticsCollector

**Methods:**

- `def __init__(self, aggregator: RedisRuntimeAggregator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_statistics(self) -> Dict[str, Any]`

### class `RedisRuntimeReporterImpl`
- **Inherits from**: RedisRuntimeReporter

**Methods:**

- `def __init__(self, aggregator: RedisRuntimeAggregator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def generate_report(self) -> str`

### class `RedisRuntimeValidatorImpl`
- **Inherits from**: RedisRuntimeValidator

**Methods:**

- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def validate_telemetry(self, data: Dict[str, Any]) -> bool`

### class `RedisRuntimeIntelligenceServiceImpl`
- **Inherits from**: RedisRuntimeIntelligenceService

**Methods:**

- `def __init__(self, telemetry_service: RedisRuntimeTelemetry, aggregator: RedisRuntimeAggregator, health_analyzer: RedisRuntimeHealthAnalyzer, capacity_analyzer: RedisCapacityAnalyzer, performance_analyzer: RedisPerformanceAnalyzer, recommendation_engine: RedisRecommendationEngine, diagnostics: RedisRuntimeDiagnostics, stats_collector: RedisRuntimeStatisticsCollector, reporter: RedisRuntimeReporter, validator: RedisRuntimeValidator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_telemetry_service(self) -> RedisRuntimeTelemetry`
- `def get_aggregator(self) -> RedisRuntimeAggregator`
- `def get_health_analyzer(self) -> RedisRuntimeHealthAnalyzer`
- `def get_capacity_analyzer(self) -> RedisCapacityAnalyzer`
- `def get_performance_analyzer(self) -> RedisPerformanceAnalyzer`
- `def get_recommendation_engine(self) -> RedisRecommendationEngine`
- `def get_diagnostics(self) -> RedisRuntimeDiagnostics`
- `def get_stats_collector(self) -> RedisRuntimeStatisticsCollector`
- `def get_reporter(self) -> RedisRuntimeReporter`
- `def get_validator(self) -> RedisRuntimeValidator`

## Module: core/src/aios/services/persistence_impl_modules/redis/redis_client.py

### class `RedisConfigurationService`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`

### class `FakeRedisClient`

> Thread-safe in-process Redis stub used when Redis is unavailable.

**Methods:**

- `def __init__(self) -> None`
- `def ping(self) -> bool`
- `def get(self, key: str) -> Optional[str]`
- `def set(self, key: str, value: str, ex: Optional[int]) -> bool`
- `def delete(self, key: str) -> bool`
- `def exists(self, key: str) -> bool`
- `def keys(self, pattern: str) -> List[str]`

### class `RedisConnectionManager`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self, config: RedisConfigurationService) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def connect(self) -> Any`

### class `RedisTransportImpl`
- **Inherits from**: RedisTransport

**Methods:**

- `def __init__(self, config: RedisConfigurationService, conn_manager: RedisConnectionManager) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def connect(self) -> None`
- `def disconnect(self) -> None`
- `def is_connected(self) -> bool`
- `def execute_command(self, cmd: str) -> Any`

### class `RedisProviderImpl`
- **Inherits from**: RedisProvider

**Methods:**

- `def __init__(self, transport: RedisTransport) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get(self, key: str) -> Optional[str]`
- `def set(self, key: str, value: str, ttl: Optional[int]) -> bool`
- `def delete(self, key: str) -> bool`
- `def exists(self, key: str) -> bool`

### class `RedisRuntimeServiceImpl`
- **Inherits from**: RedisRuntimeService, ServiceLifecycle

**Methods:**

- `def __init__(self, config: RedisConfigurationService, transport: RedisTransport, provider: RedisProvider, health: RedisHealthMonitor, diag: RedisDiagnostics, telemetry: RedisTelemetry, stats: RedisStatistics, validator: RedisValidator, report_gen: RedisReportGenerator) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_health(self) -> Dict[str, Any]`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def get_telemetry(self) -> Dict[str, Any]`
- `def get_statistics(self) -> Dict[str, Any]`
- `def get_recommendations(self) -> List[Dict[str, Any]]`
- `def format_key(self, workspace: str, project: str, subsystem: str, entity: str, purpose: str) -> str`
- `def get_learning_payload(self) -> Dict[str, Any]`
- `def generate_reports(self) -> None`

## Module: core/src/aios/services/persistence_impl_modules/redis/coordination.py

### class `DeadlockDetectorImpl`
- **Inherits from**: DeadlockDetector

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def register_wait(self, owner_id: str, lock_id: str, lock_type: str) -> None`
- `def unregister_wait(self, owner_id: str, lock_id: str) -> None`
- `def detect_deadlocks(self) -> List[Dict[str, Any]]`
- `def get_deadlock_recommendations(self) -> List[Dict[str, Any]]`

### class `CoordinationStatisticsCollectorImpl`
- **Inherits from**: CoordinationStatisticsCollector

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def record_acquisition(self, lock_type: str, policy: LockPolicy, success: bool, wait_time_ms: float) -> None`
- `def record_renewal(self, lock_type: str, success: bool) -> None`
- `def record_release(self, lock_type: str, success: bool) -> None`
- `def record_deadlock(self, cycle: List[str]) -> None`
- `def record_recovery(self, count: int) -> None`
- `def record_latency(self, op: str, latency_ms: float) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `CoordinationDiagnosticsImpl`
- **Inherits from**: CoordinationDiagnostics

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_diagnostics(self) -> Dict[str, Any]`
- `def log_error(self, message: str, severity: str, remediation: str) -> None`

### class `CoordinationHealthMonitorImpl`
- **Inherits from**: CoordinationHealthMonitor

**Methods:**

- `def __init__(self, provider: RedisProvider) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def check_health(self) -> Dict[str, Any]`

### class `CoordinationRecommendationEngineImpl`
- **Inherits from**: CoordinationRecommendationEngine

**Methods:**

- `def __init__(self, stats: CoordinationStatisticsCollector, diag: CoordinationDiagnostics) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_recommendations(self) -> List[Dict[str, Any]]`

### class `RedisCoordinationServiceImpl`
- **Inherits from**: RedisCoordinationService

**Methods:**

- `def __init__(self, provider: RedisProvider, registry: LockRegistry, lease_manager: LockLeaseManager, lock_manager: DistributedLockManager) -> None`
- `def initialize(self) -> None`
- `def start(self) -> None`
- `def stop(self) -> None`
- `def get_lock_manager(self) -> DistributedLockManager`
- `def get_registry(self) -> LockRegistry`
- `def get_lease_manager(self) -> LockLeaseManager`

## Module: core/src/aios/services/task/planner.py

### class `TaskPlanner`

**Methods:**

- `def __init__(self, registry: CommandRegistry, model_service: Optional[ModelService]) -> None`
- `def plan(self, objective: str) -> List[TaskStep]`

## Module: core/src/aios/services/task/models.py

### class `TaskStep`

**Methods:**

- `def __init__(self, command: str, optional: bool) -> None`
- `def to_dict(self) -> Dict[str, Any]`
- `def from_dict(cls, data: Dict[str, Any]) -> 'TaskStep'`

### class `Task`

**Methods:**

- `def __init__(self, objective: str, title: Optional[str], id: Optional[str], status: str, created_at: Optional[float], updated_at: Optional[float], steps: Optional[List[TaskStep]], execution_log: Optional[List[str]]) -> None`
- `def to_dict(self) -> Dict[str, Any]`
- `def from_dict(cls, data: Dict[str, Any]) -> 'Task'`

## Module: core/src/aios/services/task/progress.py

### class `ProgressTracker`

**Methods:**

- `def __init__(self) -> None`
- `def start_task(self, task: Task) -> None`
- `def start_step(self, idx: int, step: TaskStep) -> None`
- `def complete_step(self, idx: int, step: TaskStep) -> None`
- `def fail_step(self, idx: int, step: TaskStep) -> None`
- `def _print_step_result(self, idx: int, step: TaskStep, marker: str) -> None`
- `def print_progress(self, task: Task) -> None`

## Module: core/src/aios/services/task/executor.py

### class `TaskExecutor`

**Methods:**

- `def __init__(self, registry: Any, progress_tracker: ProgressTracker) -> None`
- `def execute_step(self, step: TaskStep) -> bool`
- `def execute_task(self, task: Task) -> None`

## Module: core/src/aios/services/task/history.py

### class `TaskHistory`

**Methods:**

- `def __init__(self, storage_dir: Path) -> None`
- `def _get_path(self, task_id: str) -> Path`
- `def save_task(self, task: Task) -> None`
- `def load_task(self, task_id: str) -> Optional[Task]`
- `def list_tasks(self) -> List[Task]`
- `def delete_task(self, task_id: str) -> bool`

## Module: core/src/aios/services/command/metadata.py

### class `CommandCategory`
- **Inherits from**: Enum
- **Type**: Enum

### class `CommandMetadata`

**Methods:**

- `def __init__(self, name: str, description: str, category: CommandCategory, required_agent: str, required_tools: List[str], example_usage: str) -> None`

## Module: core/src/aios/services/command/doc_gen.py

### class `DocumentationGenerator`

**Methods:**

- `def __init__(self, registry: CommandRegistry) -> None`
- `def generate_markdown(self, output_path: Path) -> None`

## Module: core/src/aios/services/command/discovery.py

### def `execute_agent_intent`
- `def execute_agent_intent(kernel: Any, intent_type: IntentType, action: str, params: dict) -> None`

### def `execute_tailor_resume`
- `def execute_tailor_resume(kernel: Any, args: str) -> None`

### def `execute_ats_score`
- `def execute_ats_score(kernel: Any, args: str) -> None`

### def `execute_cover_letter`
- `def execute_cover_letter(kernel: Any, args: str) -> None`

### def `execute_system_status`
- `def execute_system_status(kernel: Any) -> None`

### def `handle_new_conversation`
- `def handle_new_conversation(conv_manager: Any, args: str) -> None`

### def `handle_list_conversations`
- `def handle_list_conversations(conv_manager: Any) -> None`

### def `handle_resume_conversation`
- `def handle_resume_conversation(conv_manager: Any, args: str) -> None`

### def `handle_rename_conversation`
- `def handle_rename_conversation(conv_manager: Any) -> None`

### def `handle_delete_conversation`
- `def handle_delete_conversation(conv_manager: Any, args: str) -> None`

### def `handle_current_conversation`
- `def handle_current_conversation(conv_manager: Any) -> None`

### def `handle_show_history`
- `def handle_show_history(conv_manager: Any) -> None`

### def `handle_action_plan`
- `def handle_action_plan(kernel: Any, action_history: Any, args: str) -> None`

### def `handle_action_approve`
- `def handle_action_approve(action_history: Any) -> None`

### def `handle_action_reject`
- `def handle_action_reject(action_history: Any) -> None`

### def `handle_action_execute`
- `def handle_action_execute(kernel: Any, action_history: Any) -> None`

### def `handle_action_rollback`
- `def handle_action_rollback(kernel: Any, action_history: Any, args: str) -> None`

### def `handle_action_history`
- `def handle_action_history(action_history: Any) -> None`

### def `handle_run_task`
- `def handle_run_task(registry: CommandRegistry, kernel: Any, task_history: Any, progress_tracker: Any, args: str) -> None`

### def `handle_task_status`
- `def handle_task_status(task_history: Any) -> None`

### def `handle_task_history`
- `def handle_task_history(task_history: Any) -> None`

### def `handle_task_resume`
- `def handle_task_resume(registry: CommandRegistry, kernel: Any, task_history: Any, progress_tracker: Any, args: str) -> None`

### def `handle_help`
- `def handle_help(registry: CommandRegistry, args: str) -> None`

### def `handle_commands`
- `def handle_commands(registry: CommandRegistry, args: str) -> None`

### def `handle_search_command`
- `def handle_search_command(registry: CommandRegistry, args: str) -> None`

### def `handle_skills_list`
- `def handle_skills_list(registry: Any) -> None`

### def `handle_skills_inspect`
- `def handle_skills_inspect(registry: Any, args: str) -> None`

### def `handle_skills_enable`
- `def handle_skills_enable(manager: Any, registry: Any, kernel: Any, conv_manager: Any, args: str) -> None`

### def `handle_skills_disable`
- `def handle_skills_disable(manager: Any, registry: Any, args: str) -> None`

### def `handle_skills_reload`
- `def handle_skills_reload(manager: Any, registry: Any, kernel: Any, conv_manager: Any, args: str) -> None`

### def `match_command`
- `def match_command(user_input: str, registry: CommandRegistry) -> Optional[tuple[CommandMetadata, str]]`

### def `register_default_commands`
- `def register_default_commands(registry: CommandRegistry, kernel: Any, conv_manager: Any) -> None`

## Module: core/src/aios/services/command/registry.py

### class `CommandRegistry`
- **Inherits from**: ServiceLifecycle

**Methods:**

- `def __init__(self) -> None`
- `def initialize(self) -> None`
- `def register_command(self, metadata: CommandMetadata, handler: Callable[[Any], Any]) -> None`
- `def unregister_command(self, name: str) -> None`
- `def get_command(self, name: str) -> Optional[CommandMetadata]`
- `def get_handler(self, name: str) -> Optional[Callable[[Any], Any]]`
- `def list_commands(self, category: Optional[CommandCategory]) -> List[CommandMetadata]`
- `def search_commands(self, keyword: str) -> List[CommandMetadata]`

## Module: core/src/aios/services/conversation/store.py

### class `ConversationStore`

**Methods:**

- `def __init__(self, storage_dir: Path) -> None`
- `def _get_path(self, conversation_id: str) -> Path`
- `def save(self, conversation: Dict[str, Any]) -> None`
- `def load(self, conversation_id: str) -> Optional[Dict[str, Any]]`
- `def list_all(self) -> List[Dict[str, Any]]`
- `def delete(self, conversation_id: str) -> bool`

## Module: core/src/aios/services/conversation/models.py

### class `ConversationMessage`

**Methods:**

- `def __init__(self, role: str, content: str, timestamp: Optional[float]) -> None`
- `def to_dict(self) -> Dict[str, Any]`
- `def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage'`

### class `ConversationSummary`

**Methods:**

- `def __init__(self, summary: str, decisions: List[str], action_items: List[str], unresolved_questions: List[str], timestamp: Optional[float]) -> None`
- `def to_dict(self) -> Dict[str, Any]`
- `def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSummary'`

### class `Conversation`

**Methods:**

- `def __init__(self, id: Optional[str], title: Optional[str], created_time: Optional[float], updated_time: Optional[float], active_agent: Optional[str], messages: Optional[List[ConversationMessage]], summary: Optional[ConversationSummary], archived: bool) -> None`
- `def to_dict(self) -> Dict[str, Any]`
- `def from_dict(cls, data: Dict[str, Any]) -> 'Conversation'`

### class `ConversationContext`

**Methods:**

- `def __init__(self, conversation: Conversation, workspace_root: str) -> None`

## Module: core/src/aios/services/conversation/manager.py

### class `ConversationManager`

**Methods:**

- `def __init__(self, store: ConversationStore) -> None`
- `def _load_active_id(self) -> None`
- `def _save_active_id(self) -> None`
- `def create_conversation(self, title: Optional[str], agent_name: Optional[str]) -> Conversation`
- `def resume_conversation(self, conversation_id: str) -> Optional[Conversation]`
- `def get_current_conversation(self) -> Optional[Conversation]`
- `def list_conversations(self) -> List[Dict[str, Any]]`
- `def rename_conversation(self, conversation_id: str, new_title: str) -> bool`
- `def archive_conversation(self, conversation_id: str) -> bool`
- `def delete_conversation(self, conversation_id: str) -> bool`
- `def add_message(self, conversation_id: str, role: str, content: str) -> None`
- `def summarize_if_needed(self, conversation: Conversation, model_service: ModelService, max_messages: int) -> None`

### def `parse_summary_response`
- `def parse_summary_response(text: str) -> Dict[str, Any]`

## Module: core/src/aios/source_control/service.py

### class `SourceControlProvider`
- **Inherits from**: DIInitializeMixin

> Abstract interface defining required methods for source control host providers.

**Methods:**

- `def __init__(self, name: str) -> None`
- `def get_repository_metadata(self, repo_name: str) -> RepositoryMetadata`
- `def create_repository(self, name: str, is_private: bool, description: Optional[str]) -> RepositoryMetadata`
- `def fork_repository(self, repo_name: str) -> RepositoryMetadata`
- `def delete_repository(self, repo_name: str) -> bool`
- `def create_pull_request(self, repo_name: str, title: str, head: str, base: str, body: Optional[str], is_draft: bool) -> PullRequestInfo`
- `def inspect_pull_request(self, repo_name: str, pr_number: int) -> PullRequestInfo`
- `def update_pull_request(self, repo_name: str, pr_number: int, payload: Dict[str, Any]) -> PullRequestInfo`
- `def merge_pull_request(self, repo_name: str, pr_number: int, commit_message: Optional[str]) -> bool`
- `def create_issue(self, repo_name: str, title: str, body: Optional[str], assignees: List[str], labels: List[str]) -> IssueInfo`
- `def inspect_issue(self, repo_name: str, issue_number: int) -> IssueInfo`
- `def create_release(self, repo_name: str, tag_name: str, name: str, body: Optional[str], draft: bool, prerelease: bool) -> ReleaseInfo`
- `def create_webhook(self, repo_name: str, url: str, events: List[str]) -> WebhookInfo`
- `def list_workflows(self, repo_name: str) -> List[WorkflowInfo]`

### class `SourceControlRegistry`
- **Inherits from**: DIInitializeMixin

> Registry container saving registered providers.

**Methods:**

- `def __init__(self) -> None`
- `def register_provider(self, provider: SourceControlProvider) -> None`
- `def get_provider(self, name: str) -> SourceControlProvider`
- `def list_providers(self) -> List[str]`

### class `ProviderConfigurationService`
- **Inherits from**: DIInitializeMixin

> Manages active configuration properties and engineering profile strategies.

**Methods:**

- `def __init__(self) -> None`

### class `ProviderDiscovery`
- **Inherits from**: DIInitializeMixin

> Discovers local environment configurations and external hosts.

**Methods:**

- `def __init__(self, registry: SourceControlRegistry) -> None`
- `def discover_and_register(self) -> None`

### class `ProviderHealthMonitor`
- **Inherits from**: DIInitializeMixin

> Polls provider host latency, rate limits, and failure tracking metrics.

**Methods:**

- `def __init__(self, registry: SourceControlRegistry) -> None`
- `def record_call(self, provider_name: str, latency: float, success: bool) -> None`
- `def get_health_status(self, provider_name: str) -> Dict[str, Any]`

### class `ProviderDiagnostics`
- **Inherits from**: DIInitializeMixin

> Detects Git install versions, GitHub CLI auth states, and rate limits.

**Methods:**

- `def run_diagnostics(self) -> Dict[str, Any]`

### class `ProviderValidator`
- **Inherits from**: DIInitializeMixin

> Validates configuration parameters and repo urls.

**Methods:**

- `def validate_repository_name(self, name: str) -> bool`

### class `SourceControlService`
- **Inherits from**: DIInitializeMixin

> Central manager delegating queries to the active provider and tracking call metrics.

**Methods:**

- `def __init__(self, registry: SourceControlRegistry, config_service: ProviderConfigurationService, health_monitor: ProviderHealthMonitor, diagnostics: ProviderDiagnostics, validator: ProviderValidator) -> None`
- `def get_active_provider(self) -> SourceControlProvider`

## Module: core/src/aios/source_control/github_provider.py

### class `GitHubProvider`
- **Inherits from**: SourceControlProvider

> Production provider adapter for GitHub, executing native HTTP REST and GitHub CLI commands.

**Methods:**

- `def __init__(self, base_url: str, token: Optional[str]) -> None`
- `def _get_headers(self) -> Dict[str, str]`
- `def _request(self, method: str, path: str) -> httpx.Response`
- `def get_repository_metadata(self, repo_name: str) -> RepositoryMetadata`
- `def create_repository(self, name: str, is_private: bool, description: Optional[str]) -> RepositoryMetadata`
- `def fork_repository(self, repo_name: str) -> RepositoryMetadata`
- `def delete_repository(self, repo_name: str) -> bool`
- `def create_pull_request(self, repo_name: str, title: str, head: str, base: str, body: Optional[str], is_draft: bool) -> PullRequestInfo`
- `def inspect_pull_request(self, repo_name: str, pr_number: int) -> PullRequestInfo`
- `def update_pull_request(self, repo_name: str, pr_number: int, payload: Dict[str, Any]) -> PullRequestInfo`
- `def merge_pull_request(self, repo_name: str, pr_number: int, commit_message: Optional[str]) -> bool`
- `def create_issue(self, repo_name: str, title: str, body: Optional[str], assignees: List[str], labels: List[str]) -> IssueInfo`
- `def inspect_issue(self, repo_name: str, issue_number: int) -> IssueInfo`
- `def create_release(self, repo_name: str, tag_name: str, name: str, body: Optional[str], draft: bool, prerelease: bool) -> ReleaseInfo`
- `def create_webhook(self, repo_name: str, url: str, events: List[str]) -> WebhookInfo`
- `def list_workflows(self, repo_name: str) -> List[WorkflowInfo]`

## Module: core/src/aios/source_control/models.py

### class `RepositoryMetadata`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `BranchInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `CommitInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `PullRequestInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `IssueInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `ReleaseInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `WorkflowInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `WebhookInfo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

## Module: core/src/aios/source_control/git_local.py

### class `LocalGitExecutor`
- **Inherits from**: DIInitializeMixin

> Wrapper executing native git CLI shell subprocess commands inside target working directories.

**Methods:**

- `def __init__(self, workspace_root: Optional[str]) -> None`
- `def run_git(self, args: List[str], cwd: Optional[str]) -> str`
- `def clone(self, url: str, path: str) -> str`
- `def init(self, path: str) -> str`
- `def status(self, cwd: Optional[str]) -> str`
- `def fetch(self, remote: str, cwd: Optional[str]) -> str`
- `def pull(self, remote: str, branch: str, cwd: Optional[str]) -> str`
- `def push(self, remote: str, branch: str, cwd: Optional[str]) -> str`
- `def checkout(self, target: str, cwd: Optional[str]) -> str`
- `def switch(self, branch_name: str, cwd: Optional[str]) -> str`
- `def create_branch(self, branch_name: str, cwd: Optional[str]) -> str`
- `def delete_branch(self, branch_name: str, force: bool, cwd: Optional[str]) -> str`
- `def merge(self, source_branch: str, cwd: Optional[str]) -> str`
- `def rebase(self, upstream: str, cwd: Optional[str]) -> str`
- `def cherry_pick(self, sha: str, cwd: Optional[str]) -> str`
- `def stash_push(self, message: Optional[str], cwd: Optional[str]) -> str`
- `def stash_pop(self, cwd: Optional[str]) -> str`
- `def restore(self, path: str, cwd: Optional[str]) -> str`
- `def reset(self, target: str, mode: str, cwd: Optional[str]) -> str`
- `def tag(self, name: str, message: Optional[str], cwd: Optional[str]) -> str`
- `def stage(self, path: str, cwd: Optional[str]) -> str`
- `def unstage(self, path: str, cwd: Optional[str]) -> str`
- `def commit(self, message: str, amend: bool, cwd: Optional[str]) -> str`
- `def diff(self, base: Optional[str], head: Optional[str], cwd: Optional[str]) -> str`
- `def log(self, max_count: int, cwd: Optional[str]) -> str`
- `def detect_conflicts(self, cwd: Optional[str]) -> List[str]`
  * Scans workspace for conflict marker tags.

## Module: core/src/aios/source_control/telemetry.py

### class `SourceControlTelemetry`
- **Inherits from**: DIInitializeMixin

> Tracks latency profiles, execution counts, success/failure ratios, and rates.

**Methods:**

- `def __init__(self) -> None`
- `def record_call(self, latency: float, success: bool) -> None`
- `def get_metrics(self) -> Dict[str, Any]`

### class `SourceControlStatistics`
- **Inherits from**: DIInitializeMixin

> Aggregates PR counts, issue counts, and tags totals.

**Methods:**

- `def __init__(self) -> None`
- `def get_statistics(self) -> Dict[str, int]`

## Module: core/src/aios/source_control/report.py

### class `SourceControlReportGenerator`
- **Inherits from**: DIInitializeMixin

> Generates source control markdown reports inside the workspace directory.

**Methods:**

- `def __init__(self, workspace_root: str, diagnostics: ProviderDiagnostics, health_monitor: ProviderHealthMonitor, statistics: SourceControlStatistics) -> None`
- `def generate_reports(self) -> None`

## Module: core/src/aios/source_control/managers.py

### class `RepositoryManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, service: SourceControlService) -> None`
- `def get_metadata(self, repo_name: str) -> RepositoryMetadata`
- `def create(self, name: str, is_private: bool, description: Optional[str]) -> RepositoryMetadata`
- `def fork(self, repo_name: str) -> RepositoryMetadata`
- `def delete(self, repo_name: str) -> bool`

### class `BranchManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, git_executor: LocalGitExecutor) -> None`
- `def create(self, branch_name: str, cwd: Optional[str]) -> str`
- `def delete(self, branch_name: str, force: bool, cwd: Optional[str]) -> str`

### class `CommitManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, git_executor: LocalGitExecutor) -> None`
- `def commit(self, message: str, amend: bool, cwd: Optional[str]) -> str`
- `def log(self, max_count: int, cwd: Optional[str]) -> str`

### class `TagManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, git_executor: LocalGitExecutor) -> None`
- `def create_tag(self, name: str, message: Optional[str], cwd: Optional[str]) -> str`

### class `MergeManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, git_executor: LocalGitExecutor) -> None`
- `def merge(self, source_branch: str, cwd: Optional[str]) -> str`
- `def rebase(self, upstream: str, cwd: Optional[str]) -> str`
- `def cherry_pick(self, sha: str, cwd: Optional[str]) -> str`

### class `DiffManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, git_executor: LocalGitExecutor) -> None`
- `def diff(self, base: Optional[str], head: Optional[str], cwd: Optional[str]) -> str`

### class `WorkspaceRepositoryManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, git_executor: LocalGitExecutor) -> None`
- `def init_repo(self, path: str) -> str`
- `def clone_repo(self, url: str, path: str) -> str`
- `def stage_file(self, path: str, cwd: Optional[str]) -> str`
- `def unstage_file(self, path: str, cwd: Optional[str]) -> str`
- `def fetch_repo(self, remote: str, cwd: Optional[str]) -> str`
- `def pull_repo(self, remote: str, branch: str, cwd: Optional[str]) -> str`
- `def push_repo(self, remote: str, branch: str, cwd: Optional[str]) -> str`
- `def reset_repo(self, target: str, mode: str, cwd: Optional[str]) -> str`
- `def check_conflicts(self, cwd: Optional[str]) -> List[str]`

### class `PullRequestManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, service: SourceControlService) -> None`
- `def create(self, repo_name: str, title: str, head: str, base: str, body: Optional[str], is_draft: bool) -> PullRequestInfo`
- `def inspect(self, repo_name: str, pr_number: int) -> PullRequestInfo`
- `def update(self, repo_name: str, pr_number: int, payload: Dict[str, Any]) -> PullRequestInfo`
- `def merge(self, repo_name: str, pr_number: int, commit_message: Optional[str]) -> bool`

### class `IssueManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, service: SourceControlService) -> None`
- `def create(self, repo_name: str, title: str, body: Optional[str], assignees: List[str], labels: List[str]) -> IssueInfo`
- `def inspect(self, repo_name: str, issue_number: int) -> IssueInfo`

### class `ReleaseManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, service: SourceControlService) -> None`
- `def create(self, repo_name: str, tag_name: str, name: str, body: Optional[str], draft: bool, prerelease: bool) -> ReleaseInfo`

### class `WorkflowManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, service: SourceControlService) -> None`
- `def list_workflows(self, repo_name: str) -> List[WorkflowInfo]`

### class `WebhookManager`
- **Inherits from**: DIInitializeMixin

**Methods:**

- `def __init__(self, service: SourceControlService) -> None`
- `def create(self, repo_name: str, url: str, events: List[str]) -> WebhookInfo`

## Module: skills/research/commands.py

### def `execute_research_topic`
- `def execute_research_topic(args: str, kernel, conv_manager) -> None`

### def `execute_search_web`
- `def execute_search_web(args: str, kernel, conv_manager) -> None`

### def `execute_generate_research_report`
- `def execute_generate_research_report(args: str, kernel, conv_manager) -> None`

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/personal/commands.py

### def `execute_profile_show`
- `def execute_profile_show(args: str, kernel, conv_manager) -> None`

### def `execute_profile_list`
- `def execute_profile_list(args: str, kernel, conv_manager) -> None`

### def `execute_profile_create`
- `def execute_profile_create(args: str, kernel, conv_manager) -> None`

### def `execute_profile_switch`
- `def execute_profile_switch(args: str, kernel, conv_manager) -> None`

### def `execute_profile_update`
- `def execute_profile_update(args: str, kernel, conv_manager) -> None`

### def `execute_profile_delete`
- `def execute_profile_delete(args: str, kernel, conv_manager) -> None`

### def `execute_resume_create`
- `def execute_resume_create(args: str, kernel, conv_manager) -> None`

### def `execute_resume_optimize`
- `def execute_resume_optimize(args: str, kernel, conv_manager) -> None`

### def `execute_resume_versions`
- `def execute_resume_versions(args: str, kernel, conv_manager) -> None`

### def `execute_resume_compare`
- `def execute_resume_compare(args: str, kernel, conv_manager) -> None`

### def `execute_portfolio_list`
- `def execute_portfolio_list(args: str, kernel, conv_manager) -> None`

### def `execute_portfolio_add`
- `def execute_portfolio_add(args: str, kernel, conv_manager) -> None`

### def `execute_goal_add`
- `def execute_goal_add(args: str, kernel, conv_manager) -> None`

### def `execute_goal_update`
- `def execute_goal_update(args: str, kernel, conv_manager) -> None`

### def `execute_goal_list`
- `def execute_goal_list(args: str, kernel, conv_manager) -> None`

### def `execute_learning_add`
- `def execute_learning_add(args: str, kernel, conv_manager) -> None`

### def `execute_learning_progress`
- `def execute_learning_progress(args: str, kernel, conv_manager) -> None`

### def `execute_knowledge_add`
- `def execute_knowledge_add(args: str, kernel, conv_manager) -> None`

### def `execute_knowledge_search`
- `def execute_knowledge_search(args: str, kernel, conv_manager) -> None`

### def `execute_preferences_show`
- `def execute_preferences_show(args: str, kernel, conv_manager) -> None`

### def `execute_preferences_update`
- `def execute_preferences_update(args: str, kernel, conv_manager) -> None`

### def `execute_template_create`
- `def execute_template_create(args: str, kernel, conv_manager) -> None`

### def `execute_template_list`
- `def execute_template_list(args: str, kernel, conv_manager) -> None`

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/career/commands.py

### def `get_compiled_career_context`
- `def get_compiled_career_context(kernel) -> str`

### def `execute_career_analyze`
- `def execute_career_analyze(args: str, kernel, conv_manager) -> None`

### def `execute_career_jobs`
- `def execute_career_jobs(args: str, kernel, conv_manager) -> None`

### def `execute_career_resume`
- `def execute_career_resume(args: str, kernel, conv_manager) -> None`

### def `execute_career_optimize`
- `def execute_career_optimize(args: str, kernel, conv_manager) -> None`

### def `execute_career_cover_letter`
- `def execute_career_cover_letter(args: str, kernel, conv_manager) -> None`

### def `execute_career_score`
- `def execute_career_score(args: str, kernel, conv_manager) -> None`

### def `execute_career_interview`
- `def execute_career_interview(args: str, kernel, conv_manager) -> None`

### def `execute_career_roadmap`
- `def execute_career_roadmap(args: str, kernel, conv_manager) -> None`

### def `execute_career_applications`
- `def execute_career_applications(args: str, kernel, conv_manager) -> None`

### def `execute_career_workflow`
- `def execute_career_workflow(args: str, kernel, conv_manager) -> None`

### def `execute_career_report`
- `def execute_career_report(args: str, kernel, conv_manager) -> None`

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/developer/commands.py

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/memory/commands.py

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/runtime/commands.py

### def `execute_runtime_start`
- `def execute_runtime_start(args: str, kernel, conv_manager) -> None`

### def `execute_runtime_stop`
- `def execute_runtime_stop(args: str, kernel, conv_manager) -> None`

### def `execute_runtime_restart`
- `def execute_runtime_restart(args: str, kernel, conv_manager) -> None`

### def `execute_runtime_status`
- `def execute_runtime_status(args: str, kernel, conv_manager) -> None`

### def `execute_runtime_health`
- `def execute_runtime_health(args: str, kernel, conv_manager) -> None`

### def `execute_runtime_events`
- `def execute_runtime_events(args: str, kernel, conv_manager) -> None`

### def `execute_runtime_watchers`
- `def execute_runtime_watchers(args: str, kernel, conv_manager) -> None`

### def `execute_runtime_tasks`
- `def execute_runtime_tasks(args: str, kernel, conv_manager) -> None`

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/n8n/commands.py

### def `execute_workflow_create`
- `def execute_workflow_create(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_edit`
- `def execute_workflow_edit(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_validate`
- `def execute_workflow_validate(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_execute`
- `def execute_workflow_execute(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_stop`
- `def execute_workflow_stop(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_list`
- `def execute_workflow_list(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_search`
- `def execute_workflow_search(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_delete`
- `def execute_workflow_delete(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_export`
- `def execute_workflow_export(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_import`
- `def execute_workflow_import(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_clone`
- `def execute_workflow_clone(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_explain`
- `def execute_workflow_explain(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_optimize`
- `def execute_workflow_optimize(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_monitor`
- `def execute_workflow_monitor(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_logs`
- `def execute_workflow_logs(args: str, kernel, conv_manager) -> None`

### def `execute_workflow_health`
- `def execute_workflow_health(args: str, kernel, conv_manager) -> None`

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/system/commands.py

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/github/models.py

### class `GitHubRepo`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubBranch`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubPR`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubIssue`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubRelease`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubWorkflow`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubCommit`
- **Decorators**: `dataclass`
- **Type**: Dataclass

### class `GitHubTag`
- **Decorators**: `dataclass`
- **Type**: Dataclass

## Module: skills/github/agent.py

### class `GitHubAgent`
- **Inherits from**: Agent

**Methods:**

- `def __init__(self, memory_service, context_service, tool_service, model_service) -> None`
- `def name(self) -> str`
- `def description(self) -> str`
- `def execute(self, agent_context: AgentContext) -> AgentResult`

### def `render_template`
- `def render_template(template_path: Path, context: Dict[str, Any]) -> str`

## Module: skills/github/github_client.py

### class `EncryptedConfig`

**Methods:**

- `def __init__(self, filepath: Optional[str]) -> None`
- `def _xor_crypt(self, data: bytes) -> bytes`
- `def save_token(self, token: str) -> None`
- `def load_token(self) -> Optional[str]`

### class `GitHubClient`

**Methods:**

- `def __init__(self, token: Optional[str]) -> None`
- `def _get_headers(self) -> Dict[str, str]`
- `def list_repositories(self) -> List[GitHubRepo]`
- `def list_branches(self, owner: str, repo: str) -> List[GitHubBranch]`
- `def get_pr(self, owner: str, repo: str, number: int) -> Optional[GitHubPR]`
- `def get_pr_diff(self, owner: str, repo: str, number: int) -> str`
- `def get_issue(self, owner: str, repo: str, number: int) -> Optional[GitHubIssue]`
- `def list_workflows(self, owner: str, repo: str) -> List[GitHubWorkflow]`
- `def get_workflow_runs(self, owner: str, repo: str) -> List[dict]`
- `def get_latest_failed_job_log(self, owner: str, repo: str) -> tuple[Optional[str], Optional[str], Optional[str]]`
- `def get_latest_release(self, owner: str, repo: str) -> Optional[GitHubRelease]`
- `def create_issue(self, owner: str, repo: str, title: str, body: str) -> Optional[GitHubIssue]`
- `def create_pr(self, owner: str, repo: str, title: str, head: str, base: str, body: str) -> Optional[GitHubPR]`
- `def compare_branches(self, owner: str, repo: str, base: str, head: str) -> str`
- `def list_commits(self, owner: str, repo: str, sha: Optional[str]) -> List[GitHubCommit]`
- `def list_tags(self, owner: str, repo: str) -> List[GitHubTag]`

## Module: skills/github/commands.py

### def `get_local_repo_info`
- `def get_local_repo_info() -> Tuple[Optional[str], Optional[str]]`
> Helper to detect owner and repo from local git configuration or remote url.

### def `parse_repo_and_args`
- `def parse_repo_and_args(args: str) -> Tuple[Optional[str], Optional[str], List[str]]`
> Parses repository owner/repo and any extra positional arguments from command args.
If owner/repo is omitted, attempts to auto-detect it from local git configuration.

### def `require_action_engine_approval`
- `def require_action_engine_approval(objective: str, steps: List[str]) -> bool`
> Enforces approval for write actions.

### def `get_github_agent`
- `def get_github_agent(kernel) -> GitHubAgent`

### def `execute_github_login`
- `def execute_github_login(args: str) -> None`

### def `execute_github_status`
- `def execute_github_status(args: str) -> None`

### def `execute_list_repositories`
- `def execute_list_repositories(args: str) -> None`

### def `execute_clone_repository`
- `def execute_clone_repository(args: str) -> None`

### def `execute_review_pr`
- `def execute_review_pr(kernel, args: str) -> None`

### def `execute_review_issue`
- `def execute_review_issue(kernel, args: str) -> None`

### def `execute_summarize_repository`
- `def execute_summarize_repository(kernel, args: str) -> None`

### def `execute_compare_branches`
- `def execute_compare_branches(kernel, args: str) -> None`

### def `execute_generate_release_notes`
- `def execute_generate_release_notes(kernel, args: str) -> None`

### def `execute_create_issue`
- `def execute_create_issue(args: str) -> None`

### def `execute_create_pr`
- `def execute_create_pr(args: str) -> None`

### def `execute_list_workflows`
- `def execute_list_workflows(args: str) -> None`

### def `execute_workflow_status`
- `def execute_workflow_status(kernel, args: str) -> None`

### def `execute_latest_release`
- `def execute_latest_release(args: str) -> None`

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

## Module: skills/conversation/commands.py

### def `register_commands`
- `def register_commands(registry, kernel, conv_manager) -> None`

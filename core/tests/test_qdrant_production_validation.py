from core.tests.run_qdrant_production_validation import main


def test_qdrant_production_validation_run():
    # Execute the live Qdrant production validation suite against the real local server
    main()

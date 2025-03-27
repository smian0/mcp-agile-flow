---
description: Apply vertical slicing with hybrid testing when developing modular features to balance independence and integration
globs: **/modules/**/*.py
alwaysApply: false
---

# Vertical Slicing with Hybrid Testing

## Context
- When developing modular features that can operate independently
- When organizing code and tests for complex applications
- When balancing component independence with system integration needs
- When enabling faster development cycles for individual modules

## Requirements
- Structure modules as self-contained vertical slices with their own tests
- Implement a hybrid testing approach matching test scope to test location
- Place unit and module-integration tests within their module directory
- Keep cross-module integration tests at the application level
- Include a standalone mode for modules when applicable
- Provide service mode toggles to switch between direct and API access
- Document the test organization clearly with READMEs

## Examples
<example>
✅ **Good Module Structure**:
```
modules/feature/
  ├── app/            # Application code
  │   ├── components/ # UI components
  │   ├── pages/      # Page definitions
  │   └── utils/      # Utilities like API clients
  ├── service.py      # Service layer 
  ├── standalone.py   # Standalone runner
  ├── tests/          # Test directory
  │   ├── unit/       # Unit tests for isolated components
  │   ├── integration/ # Tests within the module boundary
  │   ├── conftest.py # Module-specific test fixtures
  │   └── README.md   # Documents test organization
  └── README.md       # Module documentation
```

✅ **Good Test Organization**:
```python
# In modules/feature/tests/unit/test_parser.py - Unit test
def test_parser_handles_empty_input():
    """Test parser handles empty input gracefully."""
    assert parse_input("") == []

# In modules/feature/tests/integration/test_service.py - Module integration
def test_service_stores_parsed_data(db_session):
    """Test service stores parsed data in the database."""
    service = FeatureService(session=db_session)
    result = service.process_and_store("raw data")
    assert db_session.query(DataModel).count() == 1

# In tests/modules/feature/test_api.py - Cross-module integration
def test_feature_api_requires_authentication(client):
    """Test feature API endpoints require authentication."""
    response = client.get("/api/feature/data")
    assert response.status_code == 401  # Unauthorized
```
</example>

<example type="invalid">
❌ **Bad Module Structure**:
```
modules/feature/
  ├── components.py   # UI components with no organization
  ├── service.py      # Service with direct imports from other modules
  └── utils.py        # Mixed utilities 

tests/
  └── test_feature.py # All tests mixed together
```

❌ **Bad Test Organization**:
```python
# All tests at the application level regardless of scope
def test_parser():
    # Unit test in wrong location
    pass

def test_database_integration():
    # Module test in wrong location
    pass
```

❌ **Bad Service Access**:
```python
# Hardcoded service type with no toggle
def get_service():
    return DirectService()  # No way to switch to API mode for testing
```
</example>

## Critical Rules
  - Make modules self-contained with clear boundaries
  - Keep unit and module integration tests with their module
  - Move cross-module tests to application-level test directories
  - Implement service mode toggles for API vs. direct service access
  - Create standalone mode for independent module usage
  - Document test organization with READMEs
  - Follow standard naming conventions for test files
  - Ensure test fixtures are available at the appropriate levels

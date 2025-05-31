# Context Module

This module handles context switching functionality for organizations and teams in the FastAPI auth service. It follows the established pattern of other modules (teams, organizations) with a clear separation of concerns.

## Structure

```
context/
├── __init__.py          # Module initialization
├── schemas.py           # Pydantic schemas for requests/responses
├── dao.py              # Data Access Object for database operations
├── services.py         # Business logic layer
├── views.py            # View functions for endpoints
├── routes.py           # Route definitions
└── README.md           # This documentation
```

## Components

### Schemas (`schemas.py`)
Defines the request and response models:
- `SwitchOrganizationRequest` - Request to switch active organization
- `SwitchTeamRequest` - Request to switch active team  
- `SwitchContextRequest` - Request to switch both organization and team
- `TokenResponse` - Response containing new token with context
- `CurrentContextResponse` - Response showing current active context
- `AvailableContextsResponse` - Response listing available contexts

### DAO (`dao.py`)
Handles all database operations:
- User validation and retrieval
- Organization and team context retrieval
- Permission fetching from roles
- Access validation for organizations and teams

### Services (`services.py`)
Contains business logic:
- `ContextService` - Main service class for context operations
- Token payload enrichment with context
- Context validation and switching logic
- Helper functions for token manipulation

### Views (`views.py`)
Endpoint implementations:
- `switch_organization()` - Switch to a different organization
- `switch_team()` - Switch to a different team
- `switch_context()` - Switch both organization and team
- `get_current_context()` - Get current active context
- `get_available_contexts()` - Get all available contexts for user

### Routes (`routes.py`)
API route definitions:
- `POST /rbac/context/switch-organization`
- `POST /rbac/context/switch-team`
- `POST /rbac/context/switch-context`
- `GET /rbac/context/current`
- `GET /rbac/context/available`

## Key Features

### Context Enriched Tokens
Tokens include:
- Active organization information
- Active team information
- Context-specific permissions
- Available organizations and teams list

### Access Validation
- Validates user access to requested organizations/teams
- Ensures teams belong to specified organizations
- Proper error handling for unauthorized access

### Permission Aggregation
- Combines permissions from organization roles
- Adds permissions from team roles
- Supports permission inheritance and overrides

## Usage

### Switching Organization
```python
POST /rbac/context/switch-organization
{
    "organization_id": 123
}
```

### Switching Team
```python
POST /rbac/context/switch-team
{
    "team_id": 456
}
```

### Switching Both
```python
POST /rbac/context/switch-context
{
    "organization_id": 123,
    "team_id": 456
}
```

### Getting Current Context
```python
GET /rbac/context/current
```

### Getting Available Contexts
```python
GET /rbac/context/available
```

## Integration

The context module integrates with:
- **Auth Module**: For token creation and validation
- **Organizations Module**: For organization data
- **Teams Module**: For team data
- **Roles/Permissions Module**: For permission management

## Migration from Auth Module

This module replaces the context functionality that was previously in the auth module:
- `auth/context_endpoints.py` → `context/views.py` + `context/routes.py`
- `auth/context_service.py` → `context/services.py` + `context/dao.py`
- Context schemas moved from `auth/schemas.py` → `context/schemas.py`

The functionality remains the same, but is now properly structured following the established module pattern. 
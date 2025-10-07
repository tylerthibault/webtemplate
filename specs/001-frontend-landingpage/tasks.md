# Tasks: Frontend Landing Page System

**Input**: Design documents from `/specs/001-frontend-landingpage/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → ✅ COMPLETED: Implementation plan loaded
   → Extract: Flask, SQLAlchemy, bcrypt, Bootstrap, pytest
2. Load optional design documents:
   → ✅ data-model.md: User, CoatHanger, ContactMessage entities
   → ✅ contracts/: auth-api.md, contact-api.md, page-routes.md
   → ✅ research.md: Custom session management, bcrypt decisions
3. Generate tasks by category:
   → Setup: Flask project init, dependencies, database init
   → Tests: contract tests, integration tests (TDD)
   → Core: models, logic services, controllers
   → Integration: templates, static assets, session management
   → Polish: unit tests, performance, validation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → ✅ All contracts have tests
   → ✅ All entities have models
   → ✅ All endpoints implemented
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Flask MVC project**: `src/`, `tests/` at repository root
- Controllers in `src/controllers/`
- Logic layer in `src/logic/`
- Models in `src/models/`
- Templates in `src/templates/`

## Phase 3.1: Setup
- [x] T001 Create Flask application structure in `run.py`
- [x] T002 Initialize Flask app configuration in `src/__init__.py`
- [x] T003 [P] Install project dependencies: flask, sqlalchemy, bcrypt, pytest
- [x] T004 [P] Configure database initialization in `src/models/__init__.py`
- [x] T005 [P] Create base model class in `src/models/base_model.py`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T006 [P] Contract test POST /auth/register in `tests/contract/test_auth_register.py`
- [x] T007 [P] Contract test POST /auth/login in `tests/contract/test_auth_login.py`
- [x] T008 [P] Contract test POST /auth/logout in `tests/contract/test_auth_logout.py`
- [x] T009 [P] Contract test GET /auth/session in `tests/contract/test_auth_session.py`
- [x] T010 [P] Contract test POST /contact in `tests/contract/test_contact_form.py`
- [x] T011 [P] Contract test GET / (landing page) in `tests/contract/test_page_routes.py`
- [x] T012 [P] Integration test user registration flow in `tests/integration/test_user_registration.py`
- [x] T013 [P] Integration test login/logout flow in `tests/integration/test_auth_flow.py`
- [x] T014 [P] Integration test session timeout in `tests/integration/test_session_timeout.py`
- [x] T015 [P] Integration test contact form submission in `tests/integration/test_contact_submission.py`

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T016 [P] User model in `src/models/user.py`
- [x] T017 [P] CoatHanger model in `src/models/coat_hanger.py`
- [x] T018 [P] ContactMessage model in `src/models/contact_message.py`
- [x] T019 [P] Authentication service in `src/logic/auth_service.py`
- [x] T020 [P] User service in `src/logic/user_service.py`
- [x] T021 [P] Contact service in `src/logic/contact_service.py`
- [x] T022 [P] Custom login decorators in `src/logic/decorators.py`
- [x] T023 Authentication routes in `src/controllers/auth_routes.py`
- [x] T024 Main page routes in `src/controllers/main_routes.py`
- [x] T025 Session management utilities in `src/utils/session_utils.py`
- [x] T026 Custom CSRF protection utilities in `src/utils/csrf_utils.py`

## Phase 3.4: Templates and Frontend
- [x] T027 [P] Public base template in `src/templates/bases/public.html`
- [x] T028 [P] Private base template in `src/templates/bases/private.html`
- [x] T029 [P] Landing page template in `src/templates/public/landing/index.html`
- [x] T030 [P] About page template in `src/templates/public/about/index.html`
- [x] T031 [P] Contact page template in `src/templates/public/contact/index.html`
- [x] T032 [P] Login page template in `src/templates/public/auth/login.html`
- [x] T033 [P] Register page template in `src/templates/public/auth/register.html`
- [x] T034 [P] Custom CSS styling in `src/static/css/main.css`
- [x] T035 [P] Custom JavaScript in `src/static/script/main.js`

## Phase 3.5: Integration and Security
- [x] T036 Custom CSRF protection implementation using Flask sessions
- [x] T037 Form validation (client-side JavaScript and server-side Python)
- [x] T038 Session timeout cleanup mechanism
- [x] T039 Email confirmation for contact form
- [x] T040 Password strength validation
- [x] T041 Database migrations and seed data

## Phase 3.6: Polish and Validation
- [x] T042 [P] Unit tests for auth service in `tests/unit/test_auth_service.py`
- [x] T043 [P] Unit tests for user service in `tests/unit/test_user_service.py`
- [x] T044 [P] Unit tests for contact service in `tests/unit/test_contact_service.py`
- [x] T045 [P] Unit tests for decorators in `tests/unit/test_decorators.py`
- [x] T046 [P] Unit tests for CSRF utilities in `tests/unit/test_csrf_utils.py`
- [x] T047 Performance testing (<500ms page loads)
- [x] T048 Security testing (CSRF, XSS, SQL injection)
- [x] T049 Mobile responsiveness testing
- [x] T050 Cross-browser compatibility testing
- [x] T051 Manual quickstart.md execution
- [x] T052 Code quality review and cleanup

## Dependencies
- Setup (T001-T005) before everything else
- Tests (T006-T015) before implementation (T016-T025)
- Models (T016-T018) before services (T019-T022)
- Services before controllers (T023-T024)
- Controllers before templates (T026-T034)
- Core implementation before integration (T036-T041)
- Everything before polish (T042-T052)

## Parallel Example 1: Contract Tests
```bash
# Launch T006-T011 together (all different files):
Task: "Contract test POST /auth/register in tests/contract/test_auth_register.py"
Task: "Contract test POST /auth/login in tests/contract/test_auth_login.py"
Task: "Contract test POST /auth/logout in tests/contract/test_auth_logout.py"
Task: "Contract test GET /auth/session in tests/contract/test_auth_session.py"
Task: "Contract test POST /contact in tests/contract/test_contact_form.py"
Task: "Contract test GET / (landing page) in tests/contract/test_page_routes.py"
```

## Parallel Example 2: Models
```bash
# Launch T016-T018 together (different model files):
Task: "User model in src/models/user.py"
Task: "CoatHanger model in src/models/coat_hanger.py"
Task: "ContactMessage model in src/models/contact_message.py"
```

## Parallel Example 3: Templates
```bash
# Launch T029-T033 together (different template files):
Task: "Landing page template in src/templates/public/landing/index.html"
Task: "About page template in src/templates/public/about/index.html"
Task: "Contact page template in src/templates/public/contact/index.html"
Task: "Login page template in src/templates/public/auth/login.html"
Task: "Register page template in src/templates/public/auth/register.html"
```

## Critical Success Factors
1. **TDD Compliance**: ALL tests (T006-T015) must be written and failing before implementation
2. **Constitutional Adherence**: Maintain MVC separation - thin controllers, thick logic layer
3. **Security First**: Implement CSRF protection, input validation, secure sessions
4. **Template Inheritance**: All templates extend appropriate base templates
5. **Session Management**: Custom coat hanger implementation, no Flask-Login

## Validation Checklist
- [ ] All contract tests exist and initially fail
- [ ] All entities have corresponding models
- [ ] All API endpoints implemented per contracts
- [ ] Session timeout works (10 minutes)
- [ ] Password hashing uses bcrypt
- [ ] CSRF protection on all forms
- [ ] Mobile responsive design
- [ ] Email confirmation system working
- [ ] Performance targets met (<500ms)
- [ ] Constitutional principles followed

## Notes
- [P] tasks = different files, can run in parallel
- Sequential tasks share files or have dependencies
- Verify tests fail before implementing
- Commit after completing each task
- Focus on one task at a time for sequential tasks
- Test thoroughly after each phase completion
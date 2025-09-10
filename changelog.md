# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-9-10

### Added

- Initialize Alembic migrations and create initial database schema
- Set up database migration infrastructure with Alembic
- Create initial tables structure for application core entities
- Configure migration environment and version control

### Changed

- Update requirements.txt for alembic
- Fix table arggs in models


## [0.1.0] - 2025-9-9

### Added

- **Initial Database Schema:** Established the core database models (tables) for a test management system.
  - `Organization` - Represents a company or project entity.
  - `Release` - Represents a product version or release cycle.
  - `TestPlan` - Represents a collection of test cases for a specific goal.
  - `TestCase` - Represents an individual test scenario.
  - `TestStep` - Represents a step within a test case.
  - `Status` - Represents the possible states of a test result (e.g., 'Passed', 'Failed', 'Blocked').
  - `ResultTestCase` - Represents the result of executing a test case against a release.
  - `ResultTestStep` - Represents the result of executing a test step against a release.

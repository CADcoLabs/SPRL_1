# Project Requirements Document (PRD)
## Modular Spiral Stair Creator System

### Executive Summary

This document outlines the requirements for transforming the existing VBA-based spiral stair creator into a modular Python system that provides complete spiral staircase generation including all missing components (pickets, handrails, posts) while maintaining IBC compliance.

### Current State Analysis

**Existing VBA System (`Module1.bas` + `UserForm1.frm`):**
- Creates center pole, treads, mid-landing (if needed), and top landing
- Enforces basic IBC compliance (walkline width ≥ 6.75", walk space ≥ 26")
- Limited to 4 input parameters: center pole diameter, overall height, outside diameter, total rotation
- Missing critical components: vertical/horizontal pickets, posts, handrail
- No capability to add/remove individual treads after generation
- Single monolithic codebase with limited extensibility

**Key Limitations:**
- Manual addition of missing spiral stair components required
- No modular architecture for independent component development
- Limited error recovery and component isolation
- No configuration persistence or reusability

### Project Objectives

#### Primary Goals
1. **Complete Spiral Stair System**: Generate all components including missing pickets, handrails, and posts
2. **Modular Architecture**: Independent component modules with failure isolation
3. **Enhanced Functionality**: Add/remove treads, modify individual components
4. **Improved User Experience**: Modern UI with tabbed interface and real-time validation
5. **Configuration Management**: Save/load stair configurations for reuse

#### Secondary Goals
1. **IBC Compliance Enhancement**: Comprehensive code checking with regional variants
2. **Performance Optimization**: Reduced AutoCAD COM calls through batching
3. **Error Recovery**: Graceful handling of component failures
4. **Documentation**: Complete technical documentation and user guides

### System Architecture Overview

#### Master Orchestrator Pattern
```
User Interface (tkinter) 
    ↓
Configuration Manager (JSON)
    ↓
Orchestrator Engine
    ↓
Individual Component Modules → AutoCAD 2025
```

#### Core Components

**1. Master Orchestrator UI (`main_ui.py`)**
- Modern tkinter interface replacing VBA UserForm1
- Tabbed design for different component categories
- Real-time parameter validation and preview
- Progress tracking and status reporting

**2. Configuration System (`config_manager.py`)**
- JSON-based configuration with schema validation
- Default values and parameter ranges
- Version compatibility and migration support
- Export/import capabilities for configuration sharing

**3. Component Modules (Individual Python files)**
- `center_pole_module.py` - Migrated from VBA
- `tread_module.py` - Enhanced with add/remove capability
- `landing_module.py` - Migrated from VBA
- `picket_module.py` - NEW: Vertical/horizontal balusters
- `handrail_module.py` - NEW: Continuous spiral handrail
- `post_module.py` - NEW: Structural posts at landings

**4. Utilities and Support**
- `ibc_compliance.py` - Enhanced code checking functions
- `autocad_interface.py` - Robust AutoCAD COM wrapper
- `geometry_utils.py` - Mathematical calculations and validations
- `error_handler.py` - Centralized error management and logging

### Functional Requirements

#### FR-1: User Interface Requirements
- **FR-1.1**: Tabbed interface with sections for Basic Parameters, Pickets, Hanrails, Posts, and Advanced Options
- **FR-1.2**: Real-time parameter validation with immediate feedback
- **FR-1.3**: Progress tracking during stair generation with module status
- **FR-1.4**: Configuration save/load functionality with .json format
- **FR-1.5**: Preview capability showing parameter summary before generation

#### FR-2: Component Generation Requirements
- **FR-2.1**: Generate complete spiral staircase with all components
- **FR-2.2**: Maintain existing VBA functionality for center pole, treads, and landings
- **FR-2.3**: Add vertical pickets with IBC-compliant spacing (≤ 4" gaps)
- **FR-2.4**: Generate continuous spiral handrail following stair geometry
- **FR-2.5**: Create structural posts at landings and intermediate points
- **FR-2.6**: Support both clockwise and counterclockwise rotation

#### FR-3: Enhanced Functionality Requirements
- **FR-3.1**: Add individual treads at specified indices with automatic angle recalculation
  - **Edge Case 3.1.1**: Adding treads that would violate IBC walkline width must display warning and suggest alternatives
  - **Edge Case 3.1.2**: Adding treads beyond practical limit (>100) must be rejected with clear explanation
  - **Edge Case 3.1.3**: Adding treads that create non-uniform riser heights must prompt user confirmation
- **FR-3.2**: Remove individual treads with automatic adjustment
  - **Edge Case 3.2.1**: Removing treads that would result in <2 total treads must be rejected
  - **Edge Case 3.2.2**: Removing treads that affect mid-landing requirements must recalculate compliance
  - **Edge Case 3.2.3**: Removing last tread (landing) must be prevented with informative error
- **FR-3.3**: Modify existing treads without full regeneration
  - **Edge Case 3.3.1**: Modifications that break geometric constraints must revert to last valid state
  - **Edge Case 3.3.2**: Conflicting custom tread modifications must prioritize most recent changes
- **FR-3.4**: Batch operations for multiple tread modifications
  - **Edge Case 3.4.1**: Batch operations that exceed memory limits must process in chunks
  - **Edge Case 3.4.2**: Partial batch failures must allow user to continue with successful operations
- **FR-3.5**: Component-level regeneration without affecting other parts
  - **Edge Case 3.5.1**: Component dependencies must be validated before regeneration (e.g., pickets depend on treads)
  - **Edge Case 3.5.2**: Regeneration failures must not corrupt existing geometry

#### FR-4: IBC Compliance Requirements
- **FR-4.1**: Maintain existing walkline width validation (≥ 6.75")
- **FR-4.2**: Maintain existing walk space validation (≥ 26")
- **FR-4.3**: Add picket spacing validation (≤ 4" sphere rule)
- **FR-4.4**: Add handrail height validation (34"-38" above tread nosing)
- **FR-4.5**: Provide override capabilities with explicit warnings
- **FR-4.6**: Support regional code variants (IBC, IRC, local amendments)

#### FR-5: Configuration Management Requirements
- **FR-5.1**: JSON schema validation for all configuration parameters
- **FR-5.2**: Default configuration with reasonable starting values
- **FR-5.3**: Configuration export for sharing and documentation
- **FR-5.4**: Configuration import with validation and migration
- **FR-5.5**: Configuration versioning for backward compatibility

### Non-Functional Requirements

#### NFR-1: Performance Requirements
- **NFR-1.1**: Complete stair generation within 30 seconds for typical configurations (≤20 treads)
- **NFR-1.2**: Individual component generation within 5 seconds
- **NFR-1.3**: UI responsiveness with progress feedback for long operations
- **NFR-1.4**: Optimized AutoCAD COM calls through batching
- **NFR-1.5**: Support complex stairs (≤100 treads, 720° rotation) within 2 minutes
- **NFR-1.6**: Memory usage kept under 500MB during operation
- **NFR-1.7**: Concurrent generation of multiple stairs must not degrade performance >50%

#### NFR-2: Scalability Requirements
- **NFR-2.1**: Support generation of stairs with up to 100 treads without memory issues
- **NFR-2.2**: Handle drawing files with up to 50 existing spiral stairs
- **NFR-2.3**: Configuration files must support up to 1000 custom tread modifications
- **NFR-2.4**: System must scale to support multiple AutoCAD sessions simultaneously

#### NFR-3: Security Requirements
- **NFR-3.1**: JSON configuration input must be sanitized to prevent code injection
- **NFR-3.2**: COM interface calls must be validated to prevent AutoCAD crashes
- **NFR-3.3**: File system access must be restricted to designated configuration directories
- **NFR-3.4**: Configuration files must be validated against malicious payloads (max file size: 10MB)
- **NFR-3.5**: Input validation must prevent buffer overflow attacks via parameter injection

#### NFR-4: Reliability Requirements
- **NFR-4.1**: Component failure isolation - other modules continue execution
- **NFR-4.2**: Graceful error handling with informative messages
- **NFR-4.3**: Automatic recovery from AutoCAD connection issues
- **NFR-4.4**: Rollback capability for failed operations
- **NFR-4.5**: System uptime must exceed 99.5% during normal operation
- **NFR-4.6**: Data corruption recovery mechanisms must restore last valid state

#### NFR-5: Maintainability Requirements
- **NFR-5.1**: Modular architecture with clear separation of concerns
- **NFR-5.2**: Comprehensive unit tests with ≥90% code coverage
- **NFR-5.3**: Clear API interfaces and documentation
- **NFR-5.4**: Consistent coding standards (PEP 8) and patterns
- **NFR-5.5**: Automated dependency vulnerability scanning
- **NFR-5.6**: Configuration schema changes must include automated migration tools

#### NFR-6: Usability Requirements
- **NFR-6.1**: Intuitive interface requiring minimal training (≤5 minutes for basic operation)
- **NFR-6.2**: Clear error messages with suggested corrections
- **NFR-6.3**: Contextual help and tooltips
- **NFR-6.4**: Keyboard shortcuts for common operations
- **NFR-6.5**: Interface must comply with WCAG 2.1 AA accessibility standards
- **NFR-6.6**: Color schemes must maintain 4.5:1 contrast ratio minimum
- **NFR-6.7**: Undo/redo functionality for all parameter changes

#### NFR-7: Internationalization Requirements
- **NFR-7.1**: Support imperial (inches/feet) and metric (mm/cm/m) units with real-time conversion
- **NFR-7.2**: Support multiple building codes (IBC, IRC, Eurocode EN 1991) through plugins
- **NFR-7.3**: Text labels must support Unicode for international character sets
- **NFR-7.4**: Number formats must respect regional settings (decimal separators, digit grouping)

#### NFR-8: Compatibility Requirements
- **NFR-8.1**: Support AutoCAD versions 2020-2025 with version-specific COM handling
- **NFR-8.2**: Maintain backward compatibility for configuration files (3 versions back)
- **NFR-8.3**: Support Windows 10/11 64-bit with Python 3.8-3.11
- **NFR-8.4**: Graceful degradation when optional dependencies are unavailable
- **NFR-8.5**: Fallback mechanisms for development without AutoCAD (mock COM interface)

### Technical Constraints

#### TC-1: Platform Requirements
- **TC-1.1**: Windows 11 operating system
- **TC-1.2**: AutoCAD 2025 with COM interface enabled
- **TC-1.3**: Python 3.8+ with tkinter support
- **TC-1.4**: Windows COM support (pywin32)

#### TC-2: Integration Requirements
- **TC-2.1**: Seamless AutoCAD COM integration using pyautocad
- **TC-2.2**: Maintain compatibility with existing AutoCAD drawings
- **TC-2.3**: Support for AutoCAD units in decimal inches
- **TC-2.4**: Entity creation in AutoCAD ModelSpace

#### TC-3: Data Requirements
- **TC-3.1**: JSON configuration format for human readability
- **TC-3.2**: Schema validation using jsonschema library
- **TC-3.3**: Configuration file size limit: 1MB maximum
- **TC-3.4**: UTF-8 encoding for all text data

### Requirements Traceability Matrix

| Requirement | User Story Reference | Test Coverage | Implementation Module | Risk Level |
|-------------|---------------------|---------------|----------------------|------------|
| FR-1.1 | Fabricator Story: "tabbed interface" | UI Integration Tests | main_ui.py | Low |
| FR-2.3 | Fabricator Story: "vertical pickets" | Unit + IBC Tests | picket_module.py | Medium |
| FR-3.1 | Fabricator Story: "add treads" | Geometry Tests | tread_module.py | High |
| FR-4.3 | IBC Compliance: "4-inch sphere rule" | Compliance Tests | ibc_compliance.py | High |
| NFR-1.1 | Performance: "30 second generation" | Performance Tests | All Modules | Medium |
| NFR-3.1 | Security: "input sanitization" | Security Tests | config_manager.py | High |

### Success Criteria

#### Phase 1 Success Criteria (Foundation) - Quantifiable Metrics
- [ ] Complete project structure with all directories and base files (100% directory structure match to specification)
- [ ] Master orchestrator UI with basic parameter input (5 tabs functional, all inputs validated)
- [ ] JSON configuration system with schema validation (100% schema compliance, <1ms validation time)
- [ ] Base module pattern implemented and tested (≥90% code coverage, all abstract methods implemented)
- **Acceptance Test**: Generate minimal stair using UI → JSON → Single module → AutoCAD
- **Performance Target**: UI responsiveness <100ms for parameter changes

#### Phase 2 Success Criteria (Core Migration) - Quantifiable Metrics
- [ ] Center pole, tread, and landing modules functional (100% VBA feature parity)
- [ ] IBC compliance checking migrated and enhanced (100% rule coverage, <5ms validation time)
- [ ] AutoCAD interface wrapper operational (≥99% COM call success rate, <3 retry attempts)
- [ ] Basic stair generation matching VBA output (pixel-perfect drawing comparison using diff tools)
- **Acceptance Test**: Generate identical stair to VBA system using same parameters
- **Performance Target**: Generation time ≤30 seconds for 20-tread stair

#### Phase 3 Success Criteria (Missing Components) - Quantifiable Metrics
- [ ] Picket module generating IBC-compliant vertical balusters (4-inch spacing validation, ≤100ms per picket)
- [ ] Handrail module creating continuous spiral handrail (smooth spline curves, proper height maintenance)
- [ ] Post module adding structural posts at appropriate locations (load-bearing positioning validation)
- [ ] Complete spiral stair generation with all components (6 modules integrated, <5% failure rate)
- **Acceptance Test**: Generate complete stair passing IBC compliance checks
- **Performance Target**: Full stair generation ≤45 seconds

#### Phase 4 Success Criteria (Enhancement) - Quantifiable Metrics
- [ ] Tread addition/removal functionality operational (≥95% success rate, geometry recalculation <2 seconds)
- [ ] Enhanced error handling and module isolation (zero cascade failures, 100% error recovery)
- [ ] Configuration save/load working reliably (100% roundtrip fidelity, <500ms file operations)
- [ ] Comprehensive testing and validation complete (≥90% code coverage, ≥95% test pass rate)
- **Acceptance Test**: Stress test with 50 tread modifications and recovery scenarios
- **Performance Target**: Individual tread operations ≤5 seconds

### Stakeholder Validation Requirements

#### Primary Stakeholder: Fabricator Engineers
- **Validation Method**: Alpha testing with 3 fabricator scenarios
- **Success Metrics**: Task completion rate ≥90%, user satisfaction ≥4/5
- **Key Workflows**: Standard stair generation, custom modifications, IBC compliance checking

#### Secondary Stakeholders: Architects & Installers
- **Validation Method**: Beta testing with configuration sharing workflows
- **Success Metrics**: Configuration reuse rate ≥80%, installation accuracy improvement ≥20%
- **Key Workflows**: Configuration export/import, documentation generation, field modifications

### Risk Assessment Matrix

| Risk Factor | Probability | Impact | Risk Score | Mitigation Strategy | Contingency Plan |
|-------------|-------------|---------|------------|-------------------|------------------|
| **AutoCAD COM Interface Instability** | High (70%) | High (9) | 6.3 | Robust error handling, connection pooling, retry logic | Fallback to DXF export/import |
| **Complex Geometry Performance Issues** | Medium (40%) | High (8) | 3.2 | Batching, progress feedback, algorithmic optimization | Simplified geometry modes |
| **IBC Compliance Rule Accuracy** | Medium (30%) | High (9) | 2.7 | Expert validation, comprehensive test cases | Override capabilities with warnings |
| **Tread Modification Edge Cases** | High (60%) | Medium (6) | 3.6 | Extensive unit testing, state validation | Revert to last known good state |
| **User Interface Complexity** | Medium (50%) | Medium (5) | 2.5 | Iterative design, user testing | Simplified "Basic" vs "Advanced" modes |
| **Configuration Schema Evolution** | Low (20%) | Medium (6) | 1.2 | Versioning, automated migration tools | Manual configuration recreation |
| **Third-party Dependency Failures** | Low (15%) | Medium (4) | 0.6 | Dependency pinning, alternative libraries | Graceful degradation of features |

#### Risk Monitoring and Response

**Weekly Risk Review Process:**
1. **Performance Metrics Tracking**: Monitor generation times, memory usage, COM call success rates
2. **Error Rate Analysis**: Track module failure rates, cascade failures, recovery success
3. **User Feedback Integration**: Collect usability metrics, task completion rates
4. **Technical Debt Assessment**: Code coverage trends, complexity metrics, documentation gaps

**Escalation Triggers:**
- Generation time exceeds 45 seconds for standard configurations
- Module failure rate exceeds 5%
- User task completion rate drops below 85%
- Security vulnerability discovered in dependencies

**Risk Response Strategies:**
- **Accept**: Low-impact, low-probability risks (dependency minor version changes)
- **Avoid**: High-impact risks through design changes (eliminate complex geometry features)
- **Mitigate**: Most risks through preventive measures (testing, validation, error handling)
- **Transfer**: Consider third-party solutions for high-complexity components (3D geometry libraries)

### Future Enhancements

#### Short-term (Next 6 months)
- Material and weight estimation capabilities
- Bill of Materials (BOM) generation
- Real-time 3D preview integration
- Advanced picket patterns and styles

#### Long-term (6-12 months)
- Web-based interface for remote access
- Database integration for project management
- Collaboration features for team workflows
- Integration with CAD libraries and standards

### Conclusion

This modular Python-based spiral stair creator will provide a complete, extensible solution that addresses all limitations of the current VBA system while adding significant new capabilities. The phased approach ensures manageable development with clear milestones and success criteria.
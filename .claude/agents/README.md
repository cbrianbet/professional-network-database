# Claude Code Agents for Professional Software Engineering Teams

This directory contains specialized agent definitions for use with Claude Code. Each agent encapsulates a specific role in the software development lifecycle, promoting separation of concerns and efficient collaboration.

## How to Use These Agents

To invoke an agent, use the `Agent` tool with the `subagent_type` parameter set to the agent's name:

```
Agent(subagent_type="architect", prompt="Design a REST API for user management")
```

You can also reference agents in your prompts: "@architect please design the database schema"

Each agent operates within its defined responsibilities and will delegate to other agents when appropriate.

## Agent Handoff Rules

Effective collaboration follows these handoff patterns:

1. **Architect → Developer**: 
   - Architect provides technical specifications, API contracts, and database designs
   - Developer implements based on these specifications
   - Developer raises implementation questions back to Architect

2. **Developer → Reviewer**:
   - Developer submits code for review
   - Reviewer provides feedback on quality, bugs, and maintainability
   - Developer addresses feedback and may re-submit

3. **Developer → Tester**:
   - Developer provides implementation details for test creation
   - Tester writes tests to validate functionality
   - Developer ensures code is testable

4. **Any Agent → Security-Reviewer**:
   - Any agent can request security review for their work products
   - Security-Reviewer focuses specifically on security aspects
   - Findings are returned to the requesting agent for remediation

5. **Architect/Developer → DevOps**:
   - Architect defines deployment architecture needs
   - Developer provides deployable artifacts
   - DevOps creates deployment pipelines and infrastructure
   - DevOps provides environment details back to developers

6. **Architect/Developer → Data-Engineer**:
   - Architect defines data model requirements
   - Developer implements data access layers
   - Data-Engineer optimizes data storage and provides ETL pipelines
   - Data-Engineer ensures data accessibility for applications

7. **Bidirectional Communication**:
   - Agents should ask clarifying questions when specifications are unclear
   - Implementation feedback should flow back to design agents
   - Cross-cutting concerns (security, performance) involve multiple agents

## Recommended Orchestration Workflow

For a typical feature implementation:

1. **Planning Phase**
   - @architect: Design feature specifications, API contracts, data models
   - @data-engineer: Design data storage and access patterns (if data-heavy)
   - @devops: Plan deployment and infrastructure requirements

2. **Implementation Phase**
   - @developer: Implement feature based on specifications
   - @tester: Create test plan and test cases (can start early)
   - @security-reviewer: Review security aspects of design and implementation

3. **Validation Phase**
   - @reviewer: Review code quality and maintainability
   - @tester: Execute tests and identify gaps
   - @devops: Validate deployment and configuration
   - @security-reviewer: Perform security testing

4. **Deployment Phase**
   - @devops: Deploy to staging/production
   - @developer: Address deployment issues
   - @monitoring: (External) Monitor production metrics

## Best Practices for Technology Stack

### React/Next.js Frontend
- **Architect**: Design component hierarchy, state management approach, API boundaries
- **Developer**: Follow Next.js conventions, implement components with proper TypeScript typing
- **Reviewer**: Check for accessibility, performance (bundle size, re-renders), correct hooks usage
- **Tester**: Write unit tests with Jest/React Testing Library, integration tests with Cypress/Playwright
- **DevOps**: Configure static asset optimization, CDN setup, edge deployment settings
- **Security-Reviewer**: Check for XSS vulnerabilities, proper auth token handling, CORS configuration

### Node.js/FastAPI/Python Backend
- **Architect**: Design API REST/GraphQL boundaries, microservice boundaries, database contracts
- **Developer**: Follow framework-specific patterns (FastAPI dependency injection, Django MVT)
- **Reviewer**: Check for proper error handling, input validation, efficient database queries
- **Tester**: Write unit tests (pytest/Jest), integration tests (TestClient/API testing), contract tests
- **DevOps**: Configure containerization, orchestration (Kubernetes), database migration strategies
- **Security-Reviewer**: Review authentication (JWT/sessions), authorization, SQL injection risks, API rate limiting

### Database (PostgreSQL)
- **Architect**: Design normalized schema, indexing strategy, relationship constraints
- **Developer**: Write efficient queries, use ORM appropriately, handle transactions
- **Data-Engineer**: Optimize complex queries, design partitioning strategies, create materialized views
- **Reviewer**: Check for N+1 query problems, missing indexes, proper connection handling
- **Tester**: Write database unit tests, test migration scripts, test edge cases in queries
- **DevOps**: Configure backup strategies, replication, connection pooling, performance monitoring

### Docker & Kubernetes
- **DevOps**: Create multi-stage Dockerfiles, Helm charts/Kubernetes manifests, health checks
- **Architect**: Design service boundaries for containerization, inter-service communication
- **Developer**: Ensure applications are cloud-native (stateless, configurable via env)
- **Security-Reviewer**: Scan images for vulnerabilities, check runtime privileges, network policies
- **Tester**: Test container builds, test Kubernetes deployments in kind/minikube

## General Best Practices

1. **Clear Specifications**: Architects should provide unambiguous specifications before development begins
2. **Incremental Feedback**: Use reviewers and testers early and often, not just at the end
3. **Security Shift Left**: Involve security-reviewer from design phase through deployment
4. **Observability Planning**: DevOps should plan monitoring and logging alongside feature development
5. **Data Considerations**: Data-engineer should be involved when features significantly impact data flows
6. **Documentation**: All agents should document their work appropriately for knowledge sharing
7. **Version Control**: Treat all agent outputs (specifications, code, configs) as version-controlled artifacts
8. **Continuous Learning**: Agents should stay updated on best practices for their domain
9. **Blameless Culture**: Focus on improving systems, not assigning blame when issues arise
10. **Regular Retrospectives**: Periodically review agent effectiveness and adjust handoff processes

## Customizing Agents

These agent definitions can be customized for your team's specific needs:
- Adjust tool permissions based on your project's security policies
- Modify model preferences (sonnet/opus) based on task complexity and cost considerations
- Add domain-specific examples relevant to your project
- Adjust guardrails based on team maturity and processes

Remember: Agents are assistants that augment human developers—they don't replace the need for human judgment, creativity, and responsibility.
# Professional Network Database Enhancement Project - Tracking

## Project Overview
- **Project Lead:** Claude Code (PM)
- **Team:** Dev1, Dev2, Dev3 (Developers), QA (QA Engineer)
- **Methodology:** Agile Scrum (2-week sprints)
- **Current Sprint:** Sprint 1 (Weeks 1-2)
- **Sprint Goal:** Foundation & Core Auth - National ID uniqueness and employment status
- **Start Date:** 2026-06-18
- **End Date:** 2026-07-02

## SPRINT 1 BACKLOG COMMITMENT
*Committed Story Points: 13 (Dev1: 7, Dev2: 8, Dev3: 5)*

### Sprint 1 Tickets In Progress

| Ticket ID | Owner | Status | Story Points | Description | Notes |
|-----------|-------|--------|--------------|-------------|-------|
| **EMP-01** | Dev1 | in_progress | 3 | As a user, I can select "On Contract terms" as employment status | - Updated Member model STATUS_CHOICES<br>- Modified dashboard.html filter dropdown<br>- Updated statusOptions() JS function<br>- **Next:** Update shortStatus() helper and cohort logic |
| **EMP-02** | Dev1 | in_progress | 2 | As a user, I can select "On Casual terms" as employment status | - Same tasks as EMP-01<br>- **Next:** Unit test creation |
| **EMP-03** | Dev1 | in_progress | 2 | As a user (teacher), I can select "TSC Transfer Request" as employment status | - Same tasks as EMP-01<br>- **Next:** Integration testing with charts/KPIs |
| **NAT-01** | Dev2 | in_progress | 5 | As a user, I can log in/register using my National ID as an alternative to email | - Added unique=True to national_id field (pending migration)<br>- Modified auth views to accept email OR national_id (in progress)<br>- **Next:** Data migration script creation |
| **NAT-02** | Dev2 | in_progress | 3 | As a system, National ID is enforced as unique across all users | - Created data migration backup plan<br>- **Next:** Implement uniqueness validation API endpoint |
| **FIL-01** | Dev3 | in_progress | 5 | As an admin, I can upload PDF/JPEG/PNG files to share resources | - Created FileResource model<br>- Configured media storage settings<br>- **Next:** Implement file upload view and basic template |

### Sprint 1 Definition of Done Checks
- [ ] Code written and self-reviewed
- [ ] Unit tests created and passing (min. 80% coverage for new code)
- [ ] Code reviewed by at least one other developer
- [ ] Changes merged to main branch
- [ ] Deployment to staging environment successful
- [ ] QA has executed test cases and passed
- [ ] Documentation updated
- [ ] No critical or high severity defects outstanding

## PRODUCT BACKLOG (Prioritized)

### Sprint 2 Candidates (Weeks 3-4)
| Ticket ID | Story Points | Component | Dependencies |
|-----------|--------------|-----------|--------------|
| FIL-02 | 3 | Backend/Frontend | FIL-01 |
| FIL-03 | 2 | Backend | FIL-01 |
| ADM-01 | 3 | Backend | NAT-02 |
| ADM-02 | 2 | Backend/Frontend | ADM-01 |
| ADM-03 | 5 | Backend/Frontend | NAT-01, NAT-02 |

### Sprint 3 Candidates (Weeks 5-6)
| Ticket ID | Story Points | Component | Dependencies |
|-----------|--------------|-----------|--------------|
| ADM-04 | 5 | Backend/Frontend | ADM-03 |
| Integration & Perf | 5 | Backend | All Sprint 1-2 tickets |
| UAT Prep & Bug Fixing | 5 | All | All tickets |
| UAT Coordination | 5 | QA | All tickets |

### Future Considerations (Post-MVP)
| Idea | Estimate | Notes |
|------|----------|-------|
| File type preview thumbnails | 3 | For JPEG/PNG in file management |
| Bulk file operations | 5 | Delete/multiple download |
| Advanced file filtering | 3 | By uploader, date range, custom tags |
| Approval workflow notifications (email) | 5 | Integrate with email service |
| Admin activity dashboard | 5 | Real-time metrics |

## DAILY PROGRESS LOG

### Day 1: 2026-06-18
- **Project Kickoff:** Sprint planning completed
- **Environment Setup:** 
  - All developers pulled latest main branch
  - Created feature branches: `sprint1/emp-status`, `sprint1/national-id`, `sprint1/file-upload`
  - QA set up test environment with copy of production data
- **Initial Findings:**
  - National_id field currently allows null/empty values - will need data cleanup before adding unique constraint
  - Employment status is currently free-text TextField - adding CHOICES will require migration strategy
  - Media storage not configured for production - need to set up AWS S3 or similar
- **Blockers Identified:**
  - None yet - awaiting data analysis from Dev2 on national_id field contents
- **Today's Accomplishments:**
  - Created PROJECT_TRACKING.md
  - Set up branch naming convention: `sprint1/<feature>`, `sprint2/<feature>`, etc.
  - Established Definition of Done checklist
  - Dev1 began researching statusOptions() function location
  - Dev2 started examining auth views for login/register modification points
  - Dev3 reviewed FileField documentation and media storage options

### Day 2: 2026-06-19 (Planned)
- Dev1: Complete EMP-01-03 model and filter updates
- Dev2: Analyze national_id data quality and create migration plan
- Dev3: Implement basic FileResource model and upload view skeleton
- QA: Write test cases for EMP-01-03 and create test data
- **Standup Focus:** Blockers, today's plan, yesterday's accomplishments

## BURNDOWN CHART (Estimated)
*Sprint 1: 13 story points committed*

| Day | Ideal Remaining | Actual Remaining | Notes |
|-----|-----------------|------------------|-------|
| Day 1 | 13 | 13 | Sprint start |
| Day 2 | 11.5 | TBD | After Day 1 work |
| Day 3 | 10 | TBD |  |
| Day 4 | 8.5 | TBD |  |
| Day 5 | 7 | TBD |  |
| Day 6 | 5.5 | TBD |  |
| Day 7 | 4 | TBD |  |
| Day 8 | 2.5 | TBD |  |
| Day 9 | 1 | TBD |  |
| Day 10 | 0 | TBD | Sprint end |

## RISKS & ISSUES LOG
| ID | Description | Impact | Probability | Status | Owner | Mitigation |
|----|-------------|--------|-------------|--------|-------|------------|
| RISK-01 | National ID data contains duplicates or nulls | High | Medium | Open | Dev2 | Data cleanup script; allow temporary non-unique during migration |
| RISK-02 | File upload exceeds storage limits | Medium | Low | Open | Dev3 | Implement size limits; monitor usage |
| RISK-03 | Approval workflow complexity underestimated | Medium | Medium | Future | Dev2/Dav3 | Start simple; iterate |
| ISSUE-01 | None | - | - | - | - | - |

## DECISION LOG
| Date | Decision | Rationale | Owner |
|------|----------|-----------|-------|
| 2026-06-18 | Use Django's built-in SuperUser system instead of custom is_super_admin field | Leverages existing auth framework; reduces custom code | Dev2 |
| 2026-06-18 | Status choices will be added to Member model via STATUS_CHOICES tuple | Ensures data integrity; provides validation | Dev1 |
| 2026-06-18 | File uploads will use Django's default FileSystemStorage for staging, configurable for production | Simplicity for initial implementation | Dev3 |

## NEXT STEPS
1. **Today (2026-06-18) EOD:** 
   - Dev1: Push initial EMP-01-03 changes to branch for review
   - Dev2: Share national_id data analysis findings
   - Dev3: Push FileResource model skeleton
   - QA: Share test case outline for EMP tickets
2. **Tomorrow Standup:** Review progress, identify any blockers, adjust plan if needed
3. **End of Day 2:** Aim to have EMP-01-03 model changes ready for code review

---
*Last Updated: 2026-06-18 15:45 GMT+3 by Claude Code (PM)*
*Next Update: Daily at standup or upon significant blocker/resolution*
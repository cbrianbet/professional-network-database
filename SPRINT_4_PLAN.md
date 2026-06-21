# Sprint 4 Plan: File Management Enhancements and System Monitoring

## 🎯 Sprint 4 Goal
Enhance the file management system with bulk operations and email notifications, while improving system monitoring and addressing technical debt.

## 📅 Sprint Timeline
- **Start Date:** 2026-07-18
- **End Date:** 2026-07-31 (2-week sprint)
- **Sprint Review:** 2026-07-31
- **Sprint Retrospective:** 2026-07-31

## 👥 Team Capacity & Commitment
Based on Sprint 2 velocity (21 points completed):
- Dev1: 8 points capacity
- Dev2: 7 points capacity  
- Dev3: 6 points capacity
- **Total Committed Story Points:** 21 points

## 📋 Selected Backlog Items for Sprint 4

| Ticket ID | Story Points | Component | Description |
|-----------|--------------|-----------|-------------|
| NOTIF-01 | 5 | Backend/Frontend | Approval workflow notifications (email) |
| DASH-02 | 5 | Backend/Frontend | Admin activity dashboard (real-time metrics) |
| FIL-06 | 3 | Frontend | File type preview thumbnails (for JPEG/PNG) |
| TECH-03 | 3 | Backend | Storage limits and monitoring |
| TECH-04 | 2 | Frontend | Browser compatibility for file previews |
| ENCRYPT-01 | 3 | Backend | Encrypt admin CSV exports (members/users) |

**Total Committed:** 21 points

## 🎯 Sprint 4 Definition of Done
- [ ] Code written and self-reviewed
- [ ] Unit tests created and passing (min. 80% coverage for new code)
- [ ] Code reviewed by at least one other developer
- [ ] Changes merged to main branch
- [ ] Deployment to staging environment successful
- [ ] QA has executed test cases and passed
- [ ] Documentation updated (API docs, user guides if needed)
- [ ] No critical or high severity defects outstanding
- [ ] Performance benchmarks meet acceptable thresholds (<2s for admin endpoints)
- [ ] Security review completed for new endpoints
- [ ] Accessibility compliance verified (WCAG 2.1 AA for new UI components)
- [ ] Cross-browser testing completed for UI enhancements (Chrome, Firefox, Safari, Edge)
- [ ] Encryption key management procedures documented

## 🔧 Technical Architecture & Dependencies

### Dependencies
- NOTIF-01 depends on the approval workflow from Sprint 2 (ADM-03)
- DASH-02 depends on the admin stats endpoint from Sprint 2 (ADM-02) and Sprint 3 (ADM-04 for storage analytics)
- FIL-06 depends on the file upload system from Sprint 1 (FIL-01) and Sprint 2 (FIL-02, FIL-03)
- TECH-03 depends on the file upload system and storage configuration
- TECH-04 depends on the file preview functionality
- ENCRYPT-01 depends on the admin export endpoints from Sprint 2 (ADM-05 for admin exports)

### Key Files to Modify
- `api/views.py` - New endpoints for email notifications, admin dashboard, storage limits, encrypted exports
- `api/serializers.py` - New serializers for dashboard metrics, storage info, activity logs
- `api/urls.py` - New URL patterns for new endpoints
- `api/models.py` - Potential model enhancements (SiteSettings for storage limits, ActivityLog for dashboard)
- `api/notifications.py` - Email notification service using Django signals
- `api/dashboard.py` - Dedicated dashboard API endpoints and serializers
- `api/utils/encryption.py` - Encryption utilities for CSV exports
- `api/signals.py` - Consolidated signal handlers (storage tracking, activity logging, notifications)
- `static/shared-layout.js` - Potential UI enhancements for admin pages, file previews, dashboard widgets
- `templates/admin.html` - Admin interface enhancements (file preview thumbnail display)
- `templates/dashboard.html` - For dashboard widgets (if extending dashboard)
- `templates/email/` - Email templates for approval/reject notifications
- `static/js/` - New JavaScript for file previews, browser compatibility fixes, and dashboard interactions

### Integration Points
- Email service (for notifications)
- Storage system (for limits and monitoring)
- Browser compatibility testing (for previews)

## 🚨 Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Email service integration failure | Medium | Low | Use a reliable email service provider; implement fallback logging and retry mechanism |
| Dashboard performance impact | Medium | Low | Optimize queries; use caching; limit real-time updates; monitor API load |
| Inaccurate storage monitoring | Low | Medium | Regularly test storage monitoring scripts; implement automated alerts for discrepancies |
| Browser-specific issues | Low | Medium | Test across major browsers; provide fallbacks; use feature detection |
| Encryption key loss or mismanagement | High | Low | Implement key backup procedures; use environment variables with clear documentation; warn about key rotation considerations |
| Signal-based tracking complexity | Low | Low | Consolidate signals in dedicated file; implement proper error handling in signal handlers |

## 📊 Sprint Backlog & Tasks

### NOTIF-01: Approval Workflow Notifications (5 points)
**Description:** Implement email notifications for user approval/reject events in the admin approval workflow.

**Acceptance Criteria:**
- [ ] When an admin approves a user, an email notification is sent to the user
- [ ] When an admin rejects a user, an email notification is sent to the user
- [ ] Email templates are professional and include relevant details
- [ ] Email sending is asynchronous to avoid blocking the API response
- [ ] Unit tests cover email notification triggers (>80% coverage)
- [ ] Configuration for email service is environment-based (using environment variables)
- [ ] Notification logic is decoupled from views using Django signals
- [ ] Email templates are maintained in Django template system for easy updates

**Tasks:**
1. Design email notification service using Django signals and create NotificationService class (Dev1) - 1 pt
2. Create email templates in templates/email/ directory using Django template system (Dev1) - 0.5 pt
3. Implement email sending functionality with async capability and error logging (Dev2) - 1 pt
4. Integrate notifications via post_save signals on User model for status changes (Dev2) - 0.5 pt
5. Create unit tests for email notifications covering trigger conditions and content (Dev3) - 1 pt
6. Review and integrate changes (Full team) - 0.5 pt
7. Update documentation (Dev3) - 0.5 pt

### DASH-02: Admin Activity Dashboard (5 points)
**Description:** Create a real-time admin activity dashboard showing key metrics and recent activities.

**Acceptance Criteria:**
- [ ] Dashboard shows real-time metrics: active users, pending approvals, file uploads today, etc.
- [ ] Dashboard shows recent activities: recent user signups, file uploads, approvals
- [ ] Data refreshes automatically every 30 seconds without full page reload
- [ ] Dashboard is accessible only to admin users
- [ ] Unit tests cover dashboard API endpoints (>80% coverage)
- [ ] Dashboard UI is responsive and fits within the shared layout
- [ ] Dashboard includes accessibility features: aria-live regions, pause/resume toggle, loading states
- [ ] Performance is optimized with caching and efficient queries

**Tasks:**
1. Design dashboard API endpoints and data structure, considering ActivityLog model for tracking events (Dev1) - 1 pt
2. Implement dashboard endpoints in views.py with proper admin permissions and caching (Dev2) - 1 pt
3. Create serializers for dashboard data and activity logs (Dev2) - 0.5 pt
4. Implement frontend dashboard widget using shared layout with responsive design (Dev3) - 1 pt
5. Add auto-refresh mechanism with pause/resume toggle and loading states (Dev3) - 0.5 pt
6. Implement accessibility features: aria-live regions, proper focus management, error handling (Dev3) - 0.5 pt
7. Create unit tests for dashboard endpoints covering metrics and activity data (Dev3) - 1 pt
8. Review and integrate changes (Full team) - 0.5 pt

### FIL-06: File Type Preview Thumbnails (3 points)
**Description:** Generate and display thumbnails for JPEG and PNG file previews in the file management interface.

**Acceptance Criteria:**
- [ ] Thumbnails are generated for JPEG and PNG files upon upload
- [ ] Thumbnails are displayed in the file resource list and detail views
- [ ] Thumbnails are optimized for fast loading (appropriate size and quality)
- [ ] Existing functionality for PDF thumbnails remains unaffected
- [ ] Unit tests cover thumbnail generation for JPEG/PNG (>80% coverage)
- [ ] Thumbnails include proper accessibility attributes (alt text, consistent sizing)
- [ ] Thumbnails implement lazy loading and fallback mechanisms for failed loads

**Tasks:**
1. Verify and enhance thumbnail generation for JPEG/PNG in FileResource model, ensuring serializer includes thumbnail_path with absolute URLs (Dev1) - 1 pt
2. Update file resource list and detail views to display thumbnails with proper alt text, consistent sizing (120x120px), and object-fit: cover (Dev3) - 1 pt
3. Implement lazy loading (loading="lazy") and fallback to file-type icons when thumbnails fail to load (Dev3) - 0.5 pt
4. Add hover/focus states with visible outlines and ensure touch targets ≥44x44px if actionable (Dev3) - 0.25 pt
5. Create unit tests for thumbnail generation covering JPEG/PNG files and fallback scenarios (Dev2) - 0.5 pt
6. Review and integrate changes (Full team) - 0.25 pt

### TECH-03: Storage Limits and Monitoring (3 points)
**Description:** Implement storage usage limits and monitoring to prevent exceeding storage capacity.

**Acceptance Criteria:**
- [ ] System monitors total storage usage and warns when approaching limit (e.g., 80%)
- [ ] System prevents uploads that would exceed the storage limit
- [ ] Storage usage is visible in the admin dashboard or stats endpoint
- [ ] Limits are configurable via environment variables
- [ ] Unit tests cover storage limit checks (>80% coverage)
- [ ] Storage tracking uses efficient mechanism (signals or caching) to avoid performance impact
- [ ] Warning system includes 80% threshold alerts and critical threshold notifications

**Tasks:**
1. Define storage limit configuration and monitoring strategy using SiteSettings model with signals (Dev1) - 0.5 pt
2. Implement storage usage tracking via post_save/post_delete signals on FileResource model (Dev2) - 1 pt
3. Modify upload views to enforce storage limits by checking request.content_length + current_usage <= limit (Dev2) - 0.5 pt
4. Add storage usage and warning status to admin stats endpoint with 80% threshold alerts (Dev1) - 0.5 pt
5. Create unit tests for storage limits covering tracking, enforcement, and warning scenarios (Dev3) - 0.5 pt
6. Review and integrate changes (Full team) - 0.5 pt

### TECH-04: Browser Compatibility for File Previews (2 points)
**Description:** Ensure file previews (thumbnails) work across major browsers (Chrome, Firefox, Safari, Edge).

**Acceptance Criteria:**
- [ ] File previews display correctly in Chrome, Firefox, Safari, and Edge
- [ ] Fallback mechanisms are in place for browsers with limited support
- [ ] No console errors related to file previews in supported browsers
- [ ] Unit tests include cross-browser checks (if applicable) or manual test plan
- [ ] Feature detection is used for blob URLs with graceful degradation
- [ ] Thumbnails are served as widely supported formats (JPEG/PNG) with fallbacks
- [ ] Responsive image techniques are used for high-DPI screens

**Tasks:**
1. Test current file preview implementation in target browsers (Chrome ≥110, Firefox ≥108, Safari ≥16, Edge ≥110) (Dev3) - 0.5 pt
2. Identify and fix compatibility issues using feature detection (createObjectURL) and CSS fallbacks where needed (Dev3) - 0.75 pt
3. Implement fallback to file-type icons when thumbnail generation fails and add appropriate tooltips/aria-labels (Dev3) - 0.5 pt
4. Ensure thumbnails use srcset/sizes for responsive image serving and appropriate caching headers (Dev1) - 0.25 pt
5. Update documentation with tested browser matrix and any known limitations (Dev1) - 0.25 pt
6. Review and integrate changes (Full team) - 0.25 pt

### ENCRYPT-01: Encrypt Admin CSV Exports (3 points)
**Description:** Implement encryption for admin CSV export endpoints (members and users) to protect sensitive data during export.

**Acceptance Criteria:**
- [ ] Admin CSV exports (members and users) are encrypted before download
- [ ] Encryption uses a strong algorithm (e.g., AES-256-GCM) with a key stored in environment variables
- [ ] Exported files are downloadable as encrypted CSV or as a password-protected ZIP
- [ ] Decryption instructions are provided in the download response or documentation
- [ ] Unit tests cover encryption and decryption functionality (>80% coverage)
- [ ] Encryption key is configurable via environment variable and defaults to a secure random key in development
- [ ] Download experience includes clear labeling, loading state, and post-decryption guidance
- [ ] Encryption service is modular and reusable for other data protection needs

**Tasks:**
1. Design encryption service using AES-256-GCM with HKDF key derivation and create utility class (Dev1) - 0.5 pt
2. Implement encryption and decryption utilities handling byte streams with proper error handling (Dev2) - 1 pt
3. Modify admin export views to encrypt CSV output in memory and return as application/octet-stream with .enc extension (Dev2) - 0.5 pt
4. Update API documentation and add decryption instructions in response headers and POST-download guidance (Dev1) - 0.5 pt
5. Implement download UI enhancements: clear labeling ("Download Encrypted Members CSV"), encryption status indicator, loading state during encryption, and file-size transparency (Dev3) - 0.5 pt
6. Create unit tests for encryption utilities covering roundtrip integrity and various data sizes (Dev3) - 0.5 pt
7. Review and integrate changes (Full team) - 0.5 pt


## 📈 Progress Tracking
- **Daily Standups:** 9:45 AM GMT+3 (15 minutes)
- **Mid-Sprint Check-in:** 2026-07-24
- **Burndown Tracking:** Updated daily in PROJECT_TRACKING.md
- **Quality Gates:** Definition of Done checks before considering work complete

## 🔗 Key References
- **Main Tracking:** `PROJECT_TRACKING.md`
- **Architecture Guide:** `ARCHITECTURE.md`
- **Development Setup:** `CLAUDE.md`
- **API Endpoints:** `api/urls.py`
- **Previous Sprints:** `SPRINT_SUMMARY.md`

---
*Prepared by: Claude Code (Project Manager)*
*Date: 2026-06-21*
*Next Review: Sprint Planning for Sprint 5 (post-Sprint 4)*
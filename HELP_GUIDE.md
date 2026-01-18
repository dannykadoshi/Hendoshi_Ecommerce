Typical admin pages & features (ecommerce)

Dashboard: KPIs (revenue, orders, conversion), recent orders, alerts.
Orders: list, filters (status/date), order detail, change status (processing, shipped, refunded), print packing slips/invoices, refunds, partial fulfillments.
Fulfillment / Shipping: shipping labels, tracking numbers, carrier integration, shipments queue.
Products: CRUD, variants, images/media manager, bulk import/export (CSV), draft/preview, publish/archiving, SEO fields.
Catalog management: collections/categories, product types, tags, attributes.
Inventory: stock levels, low-stock alerts, stock adjustments, warehouses.
Pricing & Promotions: price rules, sale scheduling, coupon codes, BOGO/discount engines.
Customers: profiles, order history, segmentation, notes, account status.
Payments & Refunds: payment status, reconciliation, refunds, payout reporting.
Returns & RMA: returns processing, approvals, refunds.
Content/CMS: pages, banners, blog posts, static content editor.
Reports & Analytics: sales by date, top products, conversion funnels, margins.
Integrations: webhooks, API tokens, third-party apps (fulfillment, analytics).
Settings: tax, shipping zones/rules, payment gateways, store settings.
Users & Roles: staff accounts, granular permissions/roles, audit logs.
Logs & Monitoring: activity/audit trail, failed jobs, background task monitor.
Dev/Operations: data import/export, maintenance tasks (migrations, reindexing), backups.


Plan (phased, incremental)

Phase 0 — Audit (quick)
Inspect current models and any admin.py registrations.
Identify missing fields needed for merchant workflows (tracking, statuses, SKU, stock).
Phase 1 — Minimal merchant UI (fast win)
Scaffold a merchant app with server-rendered views and templates.
Implement Orders list + detail with quick actions: change status, add tracking, print invoice.
Implement Products list + detail with image/media manager and simple bulk CSV import/export.
Add Inventory adjustments + low-stock list.
Phase 2 — Improvements
Dashboard (KPIs), sales reports, and exports.
Add role-based permissions, audit logs (e.g., django-simple-history), and activity feed.
Integrate async tasks for emails/fulfillment (Celery/RQ).
Phase 3 — UX polish / performance
Replace Django admin for complex workflows, add pagination/filter UX, keyboard shortcuts, SPA components if needed.
Add monitoring and scheduled jobs (fulfillment, reconciliation).
Tech choices & integrations

Start with Django server-rendered templates (fast to build, secure, reuse existing code).
Use django-import-export for CSV bulk operations.
Use django-simple-history or django-auditlog for change history.
For background jobs use django-rq or Celery (depends on infra; Render supports background workers).
Use Django permissions & groups for staff roles; add custom decorators/mixins for merchant views.
Keep Django admin for simple CRUD (collections, product types) and build custom merchant views for workflows.
Scope & rough time estimate (per feature, small-team pace)

Audit + scaffold: 1 day
Orders UI (list + detail + quick actions): 2–4 days
Products UI + bulk import: 2–4 days
Inventory adjustments + alerts: 1–2 days
Dashboard & reports basic: 2–4 days
Roles, audits, tests: 2–3 days
Total MVP merchant UI: ~8–16 working days (depending on polish and edge cases)
Security & ops notes

Require staff login; use @user_passes_test(lambda u: u.is_staff) or custom merchant role.
Add CSRF protection and audit trail for write ops.
Limit destructive actions (deletes/price changes) to higher roles; require confirmation.
Add tests for order transitions and bulk imports.
Typical admin pages & features (ecommerce)

Dashboard: KPIs (revenue, orders, conversion), recent orders, alerts.
Orders: list, filters (status/date), order detail, change status (processing, shipped, refunded), print packing slips/invoices, refunds, partial fulfillments.
Fulfillment / Shipping: shipping labels, tracking numbers, carrier integration, shipments queue.
Products: CRUD, variants, images/media manager, bulk import/export (CSV), draft/preview, publish/archiving, SEO fields.
Catalog management: collections/categories, product types, tags, attributes.
Inventory: stock levels, low-stock alerts, stock adjustments, warehouses.
Pricing & Promotions: price rules, sale scheduling, coupon codes, BOGO/discount engines.
Customers: profiles, order history, segmentation, notes, account status.
Payments & Refunds: payment status, reconciliation, refunds, payout reporting.
Returns & RMA: returns processing, approvals, refunds.
Content/CMS: pages, banners, blog posts, static content editor.
Reports & Analytics: sales by date, top products, conversion funnels, margins.
Integrations: webhooks, API tokens, third-party apps (fulfillment, analytics).
Settings: tax, shipping zones/rules, payment gateways, store settings.
Users & Roles: staff accounts, granular permissions/roles, audit logs.
Logs & Monitoring: activity/audit trail, failed jobs, background task monitor.
Dev/Operations: data import/export, maintenance tasks (migrations, reindexing), backups.


Plan (phased, incremental)

Phase 0 — Audit (quick)
Inspect current models and any admin.py registrations.
Identify missing fields needed for merchant workflows (tracking, statuses, SKU, stock).
Phase 1 — Minimal merchant UI (fast win)
Scaffold a merchant app with server-rendered views and templates.
Implement Orders list + detail with quick actions: change status, add tracking, print invoice.
Implement Products list + detail with image/media manager and simple bulk CSV import/export.
Add Inventory adjustments + low-stock list.
Phase 2 — Improvements
Dashboard (KPIs), sales reports, and exports.
Add role-based permissions, audit logs (e.g., django-simple-history), and activity feed.
Integrate async tasks for emails/fulfillment (Celery/RQ).
Phase 3 — UX polish / performance
Replace Django admin for complex workflows, add pagination/filter UX, keyboard shortcuts, SPA components if needed.
Add monitoring and scheduled jobs (fulfillment, reconciliation).
Tech choices & integrations

Start with Django server-rendered templates (fast to build, secure, reuse existing code).
Use django-import-export for CSV bulk operations.
Use django-simple-history or django-auditlog for change history.
For background jobs use django-rq or Celery (depends on infra; Render supports background workers).
Use Django permissions & groups for staff roles; add custom decorators/mixins for merchant views.
Keep Django admin for simple CRUD (collections, product types) and build custom merchant views for workflows.
Scope & rough time estimate (per feature, small-team pace)

Audit + scaffold: 1 day
Orders UI (list + detail + quick actions): 2–4 days
Products UI + bulk import: 2–4 days
Inventory adjustments + alerts: 1–2 days
Dashboard & reports basic: 2–4 days
Roles, audits, tests: 2–3 days
Total MVP merchant UI: ~8–16 working days (depending on polish and edge cases)
Security & ops notes

Require staff login; use @user_passes_test(lambda u: u.is_staff) or custom merchant role.
Add CSRF protection and audit trail for write ops.
Limit destructive actions (deletes/price changes) to higher roles; require confirmation.
Add tests for order transitions and bulk imports.
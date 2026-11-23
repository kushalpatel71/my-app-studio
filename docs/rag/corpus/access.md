# Accounts and access

Visitors can browse Home, Car Builds, detail pages, About, the portfolio, and the Knowledge Assistant without signing up. Public questions do not require an account.

Signup creates a member account. Login opens the private dashboard for that signed-in user. Logout revokes the session on the server. The dashboard requires an active authenticated session.

Only the administrator role may access the administration page and import the approved assistant documents. Members are denied administration access even if they request its API directly. The server checks the current database role on every protected request; hiding a navigation link is not authorization.

The assistant does not index usernames, passwords, sessions, account records, or role-management instructions. Import requires administrator authorization and a valid CSRF token.

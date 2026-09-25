import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + frappe.request.path
		raise frappe.Redirect
	context.csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()  # persist CSRF token before page render
	context.boot = {
		"user": frappe.session.user,
		"full_name": frappe.utils.get_fullname(frappe.session.user),
		"site_name": frappe.local.site,
	}

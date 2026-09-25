import frappe
from frappe.model.document import Document


class LibrarySettings(Document):
	pass


def get_settings():
	settings = frappe.get_cached_doc("Library Settings")
	settings.loan_period_days = settings.loan_period_days or 14
	settings.max_articles_per_member = settings.max_articles_per_member or 3
	return settings

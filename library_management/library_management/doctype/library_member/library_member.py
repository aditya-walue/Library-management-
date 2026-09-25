import frappe
from frappe import _
from frappe.model.document import Document


class LibraryMember(Document):
	def validate(self):
		user = frappe.db.get_value(
			"User", self.user, ["enabled", "first_name", "last_name", "email"], as_dict=True
		)
		if not user:
			frappe.throw(_("User {0} does not exist").format(self.user))
		if not user.enabled and self.status == "Active":
			frappe.throw(_("User {0} is disabled").format(self.user))
		self.first_name = user.first_name
		self.last_name = user.last_name
		self.email = user.email
		self.full_name = " ".join(filter(None, [self.first_name, self.last_name]))

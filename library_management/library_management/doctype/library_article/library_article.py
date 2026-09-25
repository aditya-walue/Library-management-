import frappe
from frappe import _
from frappe.model.document import Document


class LibraryArticle(Document):
	def validate(self):
		issued = self.get_issued_count()
		if (self.total_copies or 0) < issued:
			frappe.throw(_("Total copies cannot be less than {0} currently issued").format(issued))
		self.available_copies = (self.total_copies or 0) - issued
		self.status = "Available" if self.available_copies > 0 else "Unavailable"

	def get_issued_count(self) -> int:
		if self.is_new():
			return 0
		return frappe.db.count("Library Transaction", {"article": self.name, "status": ["in", ["Issued", "Overdue"]]})

	def refresh_availability(self):
		self.validate()
		self.db_set({"available_copies": self.available_copies, "status": self.status})

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, date_diff, getdate, nowdate

from library_management.library_management.doctype.library_settings.library_settings import get_settings


class LibraryTransaction(Document):
	def validate(self):
		settings = get_settings()
		if not self.due_date:
			self.due_date = add_days(self.issue_date, settings.loan_period_days)
		if getdate(self.due_date) < getdate(self.issue_date):
			frappe.throw(_("Due date cannot be before issue date"))
		if self.is_new():
			self.validate_member(settings)
			self.validate_availability()

	def validate_member(self, settings):
		if frappe.db.get_value("Library Member", self.member, "status") != "Active":
			frappe.throw(_("Member {0} is not active").format(self.member))
		open_loans = frappe.db.count(
			"Library Transaction", {"member": self.member, "status": ["in", ["Issued", "Overdue"]]}
		)
		if open_loans >= settings.max_articles_per_member:
			frappe.throw(_("Member already holds the maximum of {0} articles").format(open_loans))
		if frappe.db.exists(
			"Library Transaction",
			{"member": self.member, "article": self.article, "status": ["in", ["Issued", "Overdue"]]},
		):
			frappe.throw(_("Member already holds a copy of this article"))

	def validate_availability(self):
		available = frappe.db.get_value("Library Article", self.article, "available_copies", for_update=True)
		if not available or available <= 0:
			frappe.throw(_("No copies of this article are available"))

	def on_update(self):
		frappe.get_doc("Library Article", self.article).refresh_availability()

	def on_trash(self):
		self.flags.article = self.article

	def after_delete(self):
		frappe.get_doc("Library Article", self.flags.article).refresh_availability()

	def mark_returned(self, return_date=None):
		if self.status == "Returned":
			frappe.throw(_("Article already returned"))
		self.return_date = getdate(return_date or nowdate())
		late_days = max(date_diff(self.return_date, self.due_date), 0)
		self.fine_amount = late_days * (get_settings().fine_per_day or 0)
		self.status = "Returned"
		self.save()

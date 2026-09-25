import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate


@frappe.whitelist()
def get_dashboard_stats():
	frappe.has_permission("Library Transaction", throw=True)
	open_loans = {"status": ["in", ["Issued", "Overdue"]]}
	return {
		"articles": frappe.db.count("Library Article"),
		"copies": frappe.utils.cint(frappe.db.sql("select coalesce(sum(total_copies), 0) from `tabLibrary Article`")[0][0]),
		"available": frappe.utils.cint(frappe.db.sql("select coalesce(sum(available_copies), 0) from `tabLibrary Article`")[0][0]),
		"members": frappe.db.count("Library Member", {"status": "Active"}),
		"issued": frappe.db.count("Library Transaction", open_loans),
		"overdue": frappe.db.count("Library Transaction", {"status": "Overdue"}),
		"due_soon": frappe.get_all(
			"Library Transaction",
			filters={**open_loans, "due_date": ["<=", add_days(nowdate(), 3)]},
			fields=["name", "member", "member_name", "article", "article_title", "due_date", "status", "fine_amount"],
			order_by="due_date asc",
			limit=8,
		),
		"recent": frappe.get_all(
			"Library Transaction",
			fields=["name", "member_name", "article_title", "issue_date", "return_date", "status", "modified"],
			order_by="modified desc",
			limit=8,
		),
		"by_category": frappe.get_all(
			"Library Article",
			fields=["category", {"COUNT": "*", "as": "count"}],
			group_by="category",
			order_by="count desc",
		),
	}


@frappe.whitelist()
def search_catalogue(query: str | None = None, category: str | None = None, available_only: bool = False, start: int = 0, page_length: int = 24):
	frappe.has_permission("Library Article", throw=True)
	filters = {}
	if category:
		filters["category"] = category
	if frappe.utils.cint(available_only):
		filters["available_copies"] = [">", 0]
	or_filters = None
	if query:
		like = f"%{query}%"
		or_filters = {"title": ["like", like], "author": ["like", like], "isbn": ["like", like], "publisher": ["like", like]}
	return frappe.get_all(
		"Library Article",
		filters=filters,
		or_filters=or_filters,
		fields=["name", "title", "author", "isbn", "category", "publisher", "published_year", "total_copies", "available_copies", "status", "cover_image"],
		order_by="title asc",
		start=frappe.utils.cint(start),
		page_length=frappe.utils.cint(page_length),
	)


@frappe.whitelist(methods=["POST"])
def issue_article(member: str, article: str, issue_date: str | None = None, due_date: str | None = None):
	doc = frappe.get_doc(
		{
			"doctype": "Library Transaction",
			"member": member,
			"article": article,
			"issue_date": issue_date or nowdate(),
			"due_date": due_date,
		}
	)
	doc.insert()
	return doc.as_dict()


@frappe.whitelist(methods=["POST"])
def return_article(transaction: str, return_date: str | None = None):
	doc = frappe.get_doc("Library Transaction", transaction)
	doc.check_permission("write")
	doc.mark_returned(return_date)
	return doc.as_dict()


def mark_overdue():
	"""Daily: flag open loans past their due date and update the fine accrued so far."""
	for name in frappe.get_all(
		"Library Transaction",
		filters={"status": ["in", ["Issued", "Overdue"]], "due_date": ["<", getdate(nowdate())]},
		pluck="name",
	):
		doc = frappe.get_doc("Library Transaction", name)
		doc.update_overdue()
		doc.db_set({"status": doc.status, "fine_amount": doc.fine_amount}, update_modified=False)


def after_install():
	if not frappe.db.exists("Role", "Librarian"):
		frappe.get_doc({"doctype": "Role", "role_name": "Librarian", "desk_access": 1}).insert(ignore_permissions=True)


@frappe.whitelist()
def get_unlinked_users(txt: str | None = None):
	"""Enabled users that are not yet library members, for the member picker."""
	frappe.has_permission("Library Member", "create", throw=True)
	User = frappe.qb.DocType("User")
	Member = frappe.qb.DocType("Library Member")
	query = (
		frappe.qb.from_(User)
		.left_join(Member)
		.on(Member.user == User.name)
		.select(User.name, User.full_name, User.email, User.user_type)
		.where((User.enabled == 1) & (User.name.notin(["Administrator", "Guest"])) & Member.name.isnull())
		.orderby(User.full_name)
		.limit(50)
	)
	if txt:
		like = f"%{txt}%"
		query = query.where((User.full_name.like(like)) | (User.name.like(like)))
	return query.run(as_dict=True)

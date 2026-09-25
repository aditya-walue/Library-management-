import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate


@frappe.whitelist()
def get_dashboard_stats():
	# library-wide numbers are for staff only
	frappe.has_permission("Library Transaction", "create", throw=True)
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
def get_my_loans():
	"""Membership and loans of the logged-in user (member ID is the user ID)."""
	user = frappe.session.user
	member = frappe.db.get_value(
		"Library Member", user, ["name", "full_name", "membership_type", "status", "joined_on"], as_dict=True
	)
	if not member:
		return {"member": None, "loans": []}
	loans = frappe.get_all(
		"Library Transaction",
		filters={"member": user},
		fields=["name", "article", "article_title", "issue_date", "due_date", "return_date", "status", "fine_amount"],
		order_by="issue_date desc",
		limit=100,
	)
	return {"member": member, "loans": loans}


@frappe.whitelist()
def search_catalogue(
	query: str | None = None,
	category: str | None = None,
	available_only: bool = False,
	start: int = 0,
	page_length: int = 24,
	article: str | None = None,
):
	frappe.has_permission("Library Article", throw=True)
	filters = {}
	if article:
		filters["name"] = article
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


@frappe.whitelist()
def resolve_article_code(code: str):
	"""Find the article for a scanned QR code (library link or article ID) or ISBN barcode."""
	frappe.has_permission("Library Article", throw=True)
	code = (code or "").strip()
	if not code:
		return None

	# QR labels encode /library/catalogue?article=<name>
	if "article=" in code:
		from urllib.parse import parse_qs, urlparse

		code = (parse_qs(urlparse(code).query).get("article") or [code])[0]

	name = code if frappe.db.exists("Library Article", code) else None
	if not name:
		# ISBN-10/13 or any product barcode (UPC-A, EAN-8...); scanners may add a leading 0
		digits = "".join(ch for ch in code if ch.isdigit() or ch in "Xx").upper().lstrip("0")
		if len(digits) >= 6:
			match = frappe.db.sql(
				"""select name from `tabLibrary Article`
				where trim(leading '0' from replace(replace(upper(isbn), '-', ''), ' ', '')) = %s limit 1""",
				(digits,),
			)
			name = match[0][0] if match else None
	if not name:
		return None
	return frappe.db.get_value(
		"Library Article",
		name,
		["name", "title", "author", "isbn", "category", "available_copies", "total_copies"],
		as_dict=True,
	)


def _normalize_code(value: str) -> str:
	"""Card numbers compare case-insensitively, ignoring dashes, spaces and slashes (matches the SQL below)."""
	return "".join(ch for ch in (value or "") if ch not in "- /").upper()


@frappe.whitelist()
def resolve_member_code(code: str):
	"""Find the member for a scanned ID card (card number), library card QR, or user ID."""
	frappe.has_permission("Library Member", "create", throw=True)  # staff only
	code = (code or "").strip()
	if not code:
		return None

	# library cards encode /library/members?member=<user id>
	if "member=" in code:
		from urllib.parse import parse_qs, urlparse

		code = (parse_qs(urlparse(code).query).get("member") or [code])[0]

	name = code if frappe.db.exists("Library Member", code) else None
	normalized = _normalize_code(code)
	if not name and normalized:
		match = frappe.db.sql(
			"""select name from `tabLibrary Member`
			where upper(replace(replace(replace(card_id, '-', ''), ' ', ''), '/', '')) = %s limit 1""",
			(normalized,),
		)
		name = match[0][0] if match else None
	if not name:
		return None
	return frappe.db.get_value(
		"Library Member",
		name,
		["name", "full_name", "user", "card_id", "status", "membership_type", "joined_on", "phone", "email"],
		as_dict=True,
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
	add_lms_sidebar_link()


def add_lms_sidebar_link():
	"""Put a Library link in the Frappe Learning (LMS) sidebar so students find /library."""
	if "lms" not in frappe.get_installed_apps():
		return
	if not frappe.db.exists("Web Page", {"route": "library"}):
		# unpublished: only gives the LMS link a target; /library itself is served by www/library.py
		frappe.get_doc(
			{"doctype": "Web Page", "title": "Library", "route": "library", "published": 0}
		).insert(ignore_permissions=True)
	web_page = frappe.db.get_value("Web Page", {"route": "library"})
	settings = frappe.get_single("LMS Settings")
	if any(item.web_page == web_page for item in settings.sidebar_items):
		return
	settings.append("sidebar_items", {"web_page": web_page, "title": "Library", "icon": "Library", "route": "library"})
	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)

import frappe

STAFF_ROLES = {"Librarian", "System Manager"}


def is_staff(user: str | None = None) -> bool:
	user = user or frappe.session.user
	return user == "Administrator" or bool(STAFF_ROLES & set(frappe.get_roles(user)))


def _own_records_condition(doctype: str, field: str, user: str | None) -> str:
	user = user or frappe.session.user
	if is_staff(user):
		return ""
	return f"`tab{doctype}`.`{field}` = {frappe.db.escape(user)}"


def member_query_conditions(user: str | None = None) -> str:
	return _own_records_condition("Library Member", "user", user)


def transaction_query_conditions(user: str | None = None) -> str:
	return _own_records_condition("Library Transaction", "member", user)


def has_member_permission(doc, ptype: str | None = None, user: str | None = None) -> bool:
	user = user or frappe.session.user
	return is_staff(user) or doc.user == user


def has_transaction_permission(doc, ptype: str | None = None, user: str | None = None) -> bool:
	user = user or frappe.session.user
	return is_staff(user) or doc.member == user

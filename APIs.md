tsCloud API Guideline

Latest updated: 2013/09/04

=====================

Category Request API
--------------------

* URL: http://tool.thundersoft.com:8000/ad/category/
* Format: JSON
* Request method: GET
* Request:
`
{
	user_name: [USER NAME]
	token: [TOKEN],
}
`
* Returns Data:
`
{
	res: {BOOLEAN} - 0 Successful, 1 Failure,
	msg: 'Successful',
	data: [
		{
			'id': [ID],
			'name': [SUPPLIER NAME],
			'selected' {BOOLEAN} - 1 Selected, 0 Non-Selected.
		},
	]
}
`

Category Update API
--------------------

* URL: http://tool.thundersoft.com:8000/ad/category/update/
* Format: JSON
* Request method: POST
* Request:
`
{
	user_name: [USER NAME]
	token: [TOKEN],
	data: [
		{
			'id': [ID],
			'selected' {BOOLEAN} - 1 Selected, 0 Non-Selected.
		},
	]
}
`
* Returns Data:
`
{
	res: {BOOLEAN} - 0 Successful, 1 Failure,
	msg: 'Successful',
}
`

Supplier Request API
--------------------

* URL: http://tool.thundersoft.com:8000/ad/supplier/
* Format: JSON
* Request method: GET
* Request:
`
{
	user_name: [USER NAME]
	token: [TOKEN],
}
`
* Returns Data:
`
{
	res: {BOOLEAN} - 0 Successful, 1 Failure,
	msg: 'Successful',
	data: [
		{
			'id': [ID],
			'name': [SUPPLIER NAME],
			'selected': {BOOLEAN} - 1 Selected, 0 Non-Selected.
			'icon_url': [ICON URL]
		},
	]
}
`
Supplier Update API
--------------------

* URL: http://tool.thundersoft.com:8000/ad/supplier/update/
* Format: JSON
* Request method: POST
* Request:
`
{
	user_name: [USER NAME]
	token: [TOKEN],
	data: [
		{
			'id': [ID],
			'selected' {BOOLEAN} - 1 Selected, 0 Non-Selected.
		},
	]
}
`
* Returns Data:
`
{
	res: {BOOLEAN} - 0 Successful, 1 Failure,
	msg: 'Successful',
}
`

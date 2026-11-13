from odoo import api, fields, models


class OfficeAsset(models.Model):
    _name = 'office.asset'
    _description = 'Office Asset'

    name = fields.Char(string='Asset Name', required=True)
    code = fields.Char(string='Code', required=True)
    category = fields.Selection(
        [
            ('electronics', 'Electronics'),
            ('furniture', 'Furniture'),
            ('vehicle', 'Vehicle'),
            ('other', 'Other'),
        ],
        string='Category',
        default='electronics',
    )
    purchase_date = fields.Date(string='Purchase Date')
    condition = fields.Selection(
        [
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('damaged', 'Damaged'),
        ],
        string='Condition',
        default='good',
    )
    note = fields.Text(string='Note')
    active = fields.Boolean(default=True)
    loan_ids = fields.One2many('office.asset.loan', 'asset_id', string='Loans')
    is_available = fields.Boolean(string='Available', compute='_compute_is_available')
    loan_count = fields.Integer(string='Loan Count', compute='_compute_loan_count')

    @api.depends('loan_ids.state')
    def _compute_is_available(self):
        for asset in self:
            asset.is_available = not any(
                loan.state == 'borrowed' for loan in asset.loan_ids
            )

    @api.depends('loan_ids')
    def _compute_loan_count(self):
        for asset in self:
            asset.loan_count = len(asset.loan_ids)
from odoo import api, fields, models


class OfficeAssetLoan(models.Model):
    _name = 'office.asset.loan'
    _description = 'Office Asset Loan'
    _order = 'id desc'

    name = fields.Char(
        string='Loan Number', readonly=True, copy=False, default='New',
    )
    asset_id = fields.Many2one(
        'office.asset', string='Asset', required=True, ondelete='restrict',
    )
    borrower_id = fields.Many2one(
        'res.users', string='Borrower', required=True,
        default=lambda self: self.env.user,
    )
    loan_date = fields.Date(
        string='Loan Date', required=True, default=fields.Date.context_today,
    )
    due_date = fields.Date(string='Due Date', required=True)
    return_date = fields.Date(string='Return Date', readonly=True, copy=False)
    purpose = fields.Char(string='Purpose')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('borrowed', 'Borrowed'),
            ('returned', 'Returned'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        copy=False,
    )
    duration_days = fields.Integer(
        string='Duration (Days)', compute='_compute_duration_days',
    )
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_is_overdue')

    @api.depends('loan_date', 'due_date')
    def _compute_duration_days(self):
        for loan in self:
            if loan.loan_date and loan.due_date:
                loan.duration_days = (loan.due_date - loan.loan_date).days
            else:
                loan.duration_days = 0

    @api.depends('state', 'due_date')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for loan in self:
            loan.is_overdue = (
                loan.state == 'borrowed'
                and bool(loan.due_date)
                and loan.due_date < today
            )
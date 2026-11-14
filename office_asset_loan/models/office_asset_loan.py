from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


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
    is_overdue = fields.Boolean(
        string='Overdue', compute='_compute_is_overdue'
    )

    @api.constrains('loan_date', 'due_date')
    def _check_due_date(self):
        for loan in self:
            if (loan.loan_date and loan.due_date
                    and loan.due_date < loan.loan_date):
                raise ValidationError(
                    'Due date cannot be earlier than the loan date.'
                )

    @api.onchange('loan_date')
    def _onchange_loan_date(self):
        if self.loan_date and (
                not self.due_date or self.due_date < self.loan_date):
            self.due_date = self.loan_date + timedelta(days=7)

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('office.asset.loan')
                    or 'New'
                )
        return super().create(vals_list)

    def action_borrow(self):
        for loan in self:
            if loan.state != 'draft':
                raise UserError('Only loans in Draft status can be borrowed.')
            if loan.asset_id.condition == 'damaged':
                raise UserError(
                    f'Asset "{loan.asset_id.name}" is damaged '
                    'and cannot be borrowed.'
                )

            active_loan = self.sudo().search([
                ('asset_id', '=', loan.asset_id.id),
                ('state', '=', 'borrowed'),
                ('id', '!=', loan.id),
            ], limit=1)
            if active_loan:
                raise UserError(
                    f'Asset "{loan.asset_id.name}" is currently borrowed '
                    f'({active_loan.name}).'
                )
            loan.state = 'borrowed'

    def action_return(self):
        for loan in self:
            if loan.state != 'borrowed':
                raise UserError(
                    'Only loans in Borrowed status can be returned.'
                )
            loan.write({
                'state': 'returned',
                'return_date': fields.Date.context_today(loan),
            })

    def action_cancel(self):
        for loan in self:
            if loan.state != 'draft':
                raise UserError('Only loans in Draft status can be cancelled.')
            loan.state = 'cancelled'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_borrowed_or_returned(self):
        for loan in self:
            if loan.state in ('borrowed', 'returned'):
                raise UserError(
                    'Loans with status Borrowed or Returned cannot be deleted.'
                )

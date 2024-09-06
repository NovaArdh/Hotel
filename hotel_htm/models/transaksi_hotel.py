from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import date

class TransaksiHotel(models.Model):
    _name = 'transaksi.hotel'
    _description = 'Transaksi Hotel'
    _rec_name = 'partner_id'
    
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('finish', 'Finish'), ('cancel', 'Cancel')], string='Status', default='draft')
    partner_id = fields.Many2one('res.partner', string='Member', required=True)
    kamar_id = fields.Many2one('kamar.hotel', string='Kamar', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    duration = fields.Integer(string='Duration', compute='_compute_duration', store=True)
    note = fields.Text(string='Note')

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                record.duration = (record.end_date - record.start_date).days

    def confirm_transaction(self):
        self.state = 'active'
        self.kamar_id.update_room_status()

    def cancel_transaction(self):
        self.state = 'cancel'
        self.kamar_id.update_room_status()

    @api.constrains('kamar_id', 'start_date', 'end_date')
    def check_room_availability(self):
        for record in self:
            # Cek apakah ada transaksi aktif yang bertabrakan dengan transaksi yang dibuat
            overlapping_transactions = self.env['transaksi.hotel'].search([
                ('id', '!=', record.id),
                ('kamar_id', '=', record.kamar_id.id),
                ('state', '=', 'active'),
                ('start_date', '<=', record.end_date),
                ('end_date', '>=', record.start_date),
            ])
            if overlapping_transactions:
                raise ValidationError(
                    _('Kamar "%s" sudah dipesan dari %s sampai %s. Silakan pilih tanggal atau ruangan lain.') %
                    (record.kamar_id.name, overlapping_transactions[0].start_date, overlapping_transactions[0].end_date)
                )
            
    @api.model
    def auto_update_transaction_status(self):
        """ Automatically update the transaction status from 'active' to 'finish' 
        when the end_date is passed. """
        today = date.today()
        transactions = self.search([('state', '=', 'active'), ('end_date', '<', today)])
        for transaction in transactions:
            transaction.state = 'finish'
            transaction.kamar_id.update_room_status()

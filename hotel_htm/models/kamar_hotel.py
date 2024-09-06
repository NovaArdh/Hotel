from odoo import models, fields, api

class KamarHotel(models.Model):
    _name = 'kamar.hotel'
    _description = 'Kamar Hotel'
    
    name = fields.Char(string='Nama kamar', required=True)
    floor = fields.Integer(string='Lantai')
    length = fields.Float(string='Panjang', required=True)
    width = fields.Float(string='lebar', required=True)
    area = fields.Float(string='luas kamar', compute='_compute_area', store=True)
    state = fields.Selection([('available', 'Available'), ('booked', 'Booked')], string='Status', default='available')
    price_per_night = fields.Float(string='Price per malam', required=True)
    facilities_ids = fields.Many2many('fasilitas.hotel', string='Fasilitas kamar')
    transaction_ids = fields.One2many('transaksi.hotel', 'kamar_id', string='Transaksi booking')
    
    @api.depends('length', 'width')
    def _compute_area(self):
        for record in self:
            record.area = record.length * record.width

    @api.model
    def update_room_status(self):
        today = fields.Date.today()
        for room in self.search([]):
            transactions = room.transaction_ids.filtered(lambda t: t.state == 'active' and t.start_date <= today <= t.end_date)
            room.state = 'booked' if transactions else 'available'

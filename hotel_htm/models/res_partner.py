from odoo import _, api, fields, models

class HotelMember(models.Model):
    _inherit = 'res.partner'
    
    booking_transaction_ids = fields.One2many('transaksi.hotel', 'partner_id', string='Booking Transaksi')
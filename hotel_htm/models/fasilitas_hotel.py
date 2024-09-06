from odoo import _, api, fields, models

class FasilitasHotel(models.Model):
    _name = 'fasilitas.hotel'
    _description = 'Fasilitas Hotel'
    
    name = fields.Char(string='Nama', required=True)
    code = fields.Char(string='Code', required=True)
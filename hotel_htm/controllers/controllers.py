from odoo import http
from odoo.http import request
import json
import logging

class RoomAPIController(http.Controller):
    @http.route('/hotel/rooms', type='http', auth='public', methods=['GET'], csrf=False)
    def get_rooms(self):
        try:
            rooms = request.env['kamar.hotel'].sudo().search_read([], [
                'name', 'floor', 'length', 'width', 'state', 'price_per_night', 'facilities_ids', 'transaction_ids'
            ])

            data = []
            for room in rooms:
                room_data = {
                    'nama_kamar': room['name'],
                    'lantai': room['floor'],
                    'panjang': room['length'],
                    'lebar': room['width'],
                    'luas_kamar': room['length'] * room['width'],
                    'status': room['state'],
                    'price_per_malam': room['price_per_night'],
                    'fasilitas_kamar': [],
                    'transaksi_booking': []
                }

                facility_ids = room.get('facilities_ids', [])
                if facility_ids:
                    facilities = request.env['fasilitas.hotel'].sudo().search_read([('id', 'in', facility_ids)], ['name'])
                    room_data['fasilitas_kamar'] = [facility['name'] for facility in facilities]

                transaction_ids = room.get('transaction_ids', [])
                if transaction_ids:
                    transactions = request.env['transaksi.hotel'].sudo().search_read([('id', 'in', transaction_ids)], 
                                                                                ['partner_id', 'start_date', 'end_date', 'state'])
                    room_data['transaksi_booking'] = [{
                        'member': transaction['partner_id'][1] if transaction['partner_id'] else '',
                        'start_date': transaction['start_date'].strftime('%Y-%m-%d') if transaction['start_date'] else None,
                        'end_date': transaction['end_date'].strftime('%Y-%m-%d') if transaction['end_date'] else None,
                        'status': transaction['state']
                    } for transaction in transactions]

                data.append(room_data)

            return request.make_response(json.dumps(data), [('Content-Type', 'application/json')])

        except Exception as e:
            return request.make_response(json.dumps({'error': str(e)}), [('Content-Type', 'application/json')])
        
    @http.route('/hotel/rooms/create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_room(self, **kwargs):
        try:
            data = request.jsonrequest

            if not data:
                return {'error': "No data received. Please check the JSON payload."}

            required_fields = ['nama_kamar', 'lantai', 'panjang', 'lebar', 'status', 'price_per_malam', 'fasilitas_kamar']
            for field in required_fields:
                if field not in data:
                    return {'error': f"Field '{field}' is required."}

            new_room = request.env['kamar.hotel'].sudo().create({
                'name': data.get('nama_kamar'),
                'floor': data.get('lantai'),
                'length': data.get('panjang'),
                'width': data.get('lebar'),
                'state': data.get('status'),
                'price_per_night': data.get('price_per_malam'),
                'facilities_ids': [(6, 0, data.get('fasilitas_kamar', []))]
            })

            return {'success': True, 'kamar_id': new_room.id}

        except Exception as e:
            return {'error': str(e)}
        
    @http.route('/hotel/rooms/delete/<int:kamar_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_room(self, kamar_id, **kwargs):
        try:
            room = request.env['kamar.hotel'].sudo().search([('id', '=', kamar_id)], limit=1)

            if room:
                room_name = room.name
                room.unlink()
                return request.make_response(json.dumps({'success': True, 'message': f"Room with ID {kamar_id} deleted successfully."}), headers={'Content-Type': 'application/json'})
            else:
                return request.make_response(json.dumps({'error': f"Room with ID {kamar_id} not found."}), headers={'Content-Type': 'application/json'})

        except Exception as e:
            return request.make_response(json.dumps({'error': str(e)}), headers={'Content-Type': 'application/json'})
        
    @http.route('/hotel/rooms/update/<int:kamar_id>', type='json', auth='public', methods=['PUT', 'PATCH'], csrf=False)
    def update_room(self, kamar_id):
        try:
            data = request.jsonrequest

            room = request.env['kamar.hotel'].sudo().search([('id', '=', kamar_id)], limit=1)

            if room:
                room.write(data)
                return {'success': True, 'message': f"Room with ID {kamar_id} updated successfully."}
            else:
                return {'error': f"Room with ID {kamar_id} not found."}

        except Exception as e:
            return {'error': str(e)}
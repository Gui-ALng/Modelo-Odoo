from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FuelTank(models.Model):
    _name = 'fuel.tank'
    _description = 'Tanque de Combustível'
    _rec_name = 'name'

    name = fields.Char(string='Identificação do Tanque', required=True, default='Tanque Principal')
    capacity = fields.Float(string='Capacidade Máxima (L)', default=6000.0)
    current_stock = fields.Float(string='Estoque Atual (L)', compute='_compute_stock', store=True)

    # Relacionamento inverso para calcular estoque
    log_ids = fields.One2many('fuel.log', 'tank_id', string='Histórico')

    @api.depends('log_ids.liters', 'log_ids.operation_type')
    def _compute_stock(self):
        for tank in self:
            in_sum = sum(tank.log_ids.filtered(lambda log: log.operation_type == 'in').mapped('liters'))
            out_sum = sum(tank.log_ids.filtered(lambda log: log.operation_type == 'out').mapped('liters'))
            tank.current_stock = in_sum - out_sum


class FuelLog(models.Model):
    _name = 'fuel.log'
    _description = 'Registro de Combustível'
    _order = 'date desc'

    name = fields.Char(string='Referência', required=True, copy=False, readonly=True, default='Novo')
    date = fields.Datetime(string='Data e Hora', default=fields.Datetime.now, required=True)
    operation_type = fields.Selection([
        ('out', 'Abastecimento (Saída)'),
        ('in', 'Reabastecimento do Tanque (Entrada)')
    ], string='Tipo', default='out', required=True)

    tank_id = fields.Many2one('fuel.tank', string='Tanque', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Veículo/Placa') 
    driver_id = fields.Many2one('res.partner', string='Motorista')
    user_id = fields.Many2one('res.users', string='Responsável', default=lambda self: self.env.user, readonly=True)

    odometer = fields.Float(string='Odômetro/Horímetro Atual')
    liters = fields.Float(string='Litros', required=True)
    price_per_liter = fields.Float(string='Valor por Litro')
    total_amount = fields.Monetary(string='Valor Total', compute='_compute_total', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.depends('liters', 'price_per_liter')
    def _compute_total(self):
        for record in self:
            record.total_amount = record.liters * record.price_per_liter

    # Sequencia automatica para o nome
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Novo') == 'Novo':
                vals['name'] = self.env['ir.sequence'].next_by_code('fuel.log') or 'LOG-000'
        return super().create(vals_list)

    # Validação de Estoque Negativo
    @api.constrains('liters', 'operation_type', 'tank_id')
    def _check_stock(self):
        for record in self:
            if record.operation_type == 'out':
                if record.liters > record.tank_id.current_stock:
                    raise ValidationError(f"Estoque insuficiente no tanque '{record.tank_id.name}'. Estoque atual: {record.tank_id.current_stock} L.")


# --- Integração com Compras ---
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Campo para dizer pra qual tanque vai
    fuel_tank_id = fields.Many2one('fuel.tank', string='Destino: Tanque de Combustível')

    def button_confirm(self):
        # Executa o comportamento padrão do botão "Confirmar" (muda status, cria picking, etc)
        res = super(PurchaseOrder, self).button_confirm()

        for order in self:
            if order.fuel_tank_id:
                # Soma a quantidade de todos os itens do pedido
                total_liters = sum(line.product_qty for line in order.order_line)

                if total_liters > 0:
                    # Cria o registro no histórico de combustível
                    self.env['fuel.log'].create({
                        'name': f"Compra: {order.name}",  # Ex: Compra: P00001
                        'tank_id': order.fuel_tank_id.id,
                        'operation_type': 'in',  # Tipo Entrada
                        'liters': total_liters,
                        'price_per_liter': order.amount_total / total_liters,  # Preço médio
                        'date': fields.Datetime.now(),
                        'user_id': self.env.user.id,
                    })

        return res
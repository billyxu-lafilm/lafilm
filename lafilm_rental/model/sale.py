# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return super(SaleOrderLine, self).product_id_change()
        partner_set = False
        for grp in self.product_id.group_ids:
            for user in grp.users:
                if user.partner_id.id == self.order_id.partner_id.id:
                    partner_set = True
        if not partner_set:
            raise UserError(_('%s is not allowed to rent this %s ') % (
                    self.order_id.partner_id.name, self.product_id.name))
        domain = super(SaleOrderLine, self).product_id_change()
        return domain
    

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import uuid
from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    appointment_type_id = fields.Many2one('calendar.appointment.type', 'Online Appointment', readonly=False)


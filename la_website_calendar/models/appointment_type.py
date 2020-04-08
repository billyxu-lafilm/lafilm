from odoo import api, fields, models, _


class CalendarAppointmentType(models.Model):
    _inherit = "calendar.appointment.type"

    html_color = fields.Char('Color', default="#5FCEC7", help="Here you can set a specific HTML color index (e.g. #ff0000) to display the color if the attribute type is 'Color'. ")
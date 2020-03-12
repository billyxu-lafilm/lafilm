# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Website Appointment Calendar",
    'summary': "Web",
    'description': """
Website Appointment Calendar.
==========================================
-- Website Appointment Calendar
""",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': [
        'website_calendar','web'
    ],
    'data': [
        'views/event_templates.xml',
        # 'data/website_event_data.xml',
    ],
}

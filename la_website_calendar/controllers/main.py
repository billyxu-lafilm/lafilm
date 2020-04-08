from datetime import datetime, timedelta
from odoo import fields, http, _
from odoo.http import request
from dateutil.relativedelta import relativedelta
import werkzeug
import pytz
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools import html2plaintext, DEFAULT_SERVER_DATETIME_FORMAT as dtf

from odoo.addons.website_calendar.controllers.main import WebsiteCalendar


class WebsiteCalendar(WebsiteCalendar):

    @http.route(['/slot_ids'], type='json', auth="public", website=True)
    def slot_ids(self,  **searches):
        print ("============================================", searches)
        appointment_type_obj = request.env['calendar.appointment.type']
        appointment_type_ids = appointment_type_obj.search([])
        values = {}
        slot_lists = []
        for appointment_type_id in appointment_type_ids:
            timezone = appointment_type_id.appointment_tz
            slots = appointment_type_id.sudo()._get_appointment_slots(timezone)
            for slot in slots:
                if slot.get('weeks'):
                    weeks = slot.get('weeks')
                    if weeks:
                        for week in weeks:
                            for day in week:
                                if day.get('slots'):
                                    day_slots = day.get('slots')
                                    for day_slot in day_slots:
                                        time = appointment_type_id.appointment_duration
                                        sec = time*60*60
                                        start_datetime = datetime.strptime(day_slot.get('datetime'), "%Y-%m-%d %H:%M:%S")
                                        date_end = start_datetime + timedelta(seconds=sec)
                                        date_begin = start_datetime.isoformat()
                                        date_end = date_end.isoformat()
                                        url = "/website/calendar/%s/info?employee_id=%s&date_time=%s"  % (slug(appointment_type_id),day_slot.get('employee_id'), day_slot.get('datetime'))
                                        slot_lists.append({'start': date_begin,'end': date_end,'color': appointment_type_id.html_color, 'title': appointment_type_id.name, 'url':url})
        values.update({'slot_lists': slot_lists})
        print ("-------------------------------------------", values['slot_lists'])
        return values

    @http.route(['/website/calendar/<model("calendar.appointment.type"):appointment_type>/submit'], type='http', auth="public", website=True, method=["POST"])
    def calendar_appointment_submit(self, appointment_type, datetime_str, employee_id, name, phone, email, country_id=False, **kwargs):
        timezone = appointment_type.appointment_tz
        tz_session = pytz.timezone(timezone)
        date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc)
        date_end = date_start + relativedelta(hours=appointment_type.appointment_duration)

        # check availability of the employee again (in case someone else booked while the client was entering the form)
        Employee = request.env['hr.employee'].sudo().browse(int(employee_id))
        if Employee.user_id and Employee.user_id.partner_id:
            if not Employee.user_id.partner_id.calendar_verify_availability(date_start, date_end):
                return request.redirect('/website/calendar/%s/appointment?failed=employee' % appointment_type.id)

        country_id = int(country_id) if country_id else None
        country_name = country_id and request.env['res.country'].browse(country_id).name or ''
        Partner = request.env['res.partner'].sudo().search([('email', '=like', email)], limit=1)
        if Partner:
            if not Partner.calendar_verify_availability(date_start, date_end):
                return request.redirect('/website/calendar/%s/appointment?failed=partner' % appointment_type.id)
            if not Partner.mobile or len(Partner.mobile) <= 5 and len(phone) > 5:
                Partner.write({'mobile': phone})
            if not Partner.country_id:
                Partner.country_id = country_id
        else:
            Partner = Partner.create({
                'name': name,
                'country_id': country_id,
                'mobile': phone,
                'email': email,
            })

        description = ('Country: %s\n'
                       'Mobile: %s\n'
                       'Email: %s\n' % (country_name, phone, email))
        for question in appointment_type.question_ids:
            key = 'question_' + str(question.id)
            if question.question_type == 'checkbox':
                answers = question.answer_ids.filtered(lambda x: (key + '_answer_' + str(x.id)) in kwargs)
                description += question.name + ': ' + ', '.join(answers.mapped('name')) + '\n'
            elif kwargs.get(key):
                if question.question_type == 'text':
                    description += '\n* ' + question.name + ' *\n' + kwargs.get(key, False) + '\n\n'
                else:
                    description += question.name + ': ' + kwargs.get(key) + '\n'

        categ_id = request.env.ref('website_calendar.calendar_event_type_data_online_appointment')
        alarm_ids = appointment_type.reminder_ids and [(6, 0, appointment_type.reminder_ids.ids)] or []
        partner_ids = list(set([Employee.user_id.partner_id.id] + [Partner.id]))
        event = request.env['calendar.event'].sudo().create({
            'state': 'draft',
            'name': _('%s with %s') % (appointment_type.name, name),
            'start': date_start.strftime(dtf),
            # FIXME master
            # we override here start_date(time) value because they are not properly
            # recomputed due to ugly overrides in event.calendar (reccurrencies suck!)
            #     (fixing them in stable is a pita as it requires a good rewrite of the
            #      calendar engine)
            'start_date': date_start.strftime(dtf),
            'start_datetime': date_start.strftime(dtf),
            'stop': date_end.strftime(dtf),
            'stop_datetime': date_end.strftime(dtf),
            'allday': False,
            'duration': appointment_type.appointment_duration,
            'description': description,
            'alarm_ids': alarm_ids,
            'location': appointment_type.location,
            'partner_ids': [(4, pid, False) for pid in partner_ids],
            'categ_ids': [(4, categ_id.id, False)],
            'appointment_type_id': appointment_type.id,
            'user_id': Employee.user_id.id,
        })
        event.attendee_ids.write({'state': 'accepted'})
        return request.redirect('/website/calendar/view/' + event.access_token + '?message=new')

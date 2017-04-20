# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import time
import pytz
from openerp import fields, models, api, _
from functools import reduce


class TimesheetReport(models.TransientModel):
    _name = "timesheet.manager.remind"
    _description = "Timesheet Manager Remind Service"
    _inherit = ['mail.thread']

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    WEEKEND = [5, 6]

    @api.model
    def _start_remind(
            self,
            count_days=7,
            workstart='9:00:00',
            workend='18:00:00',
            resethours=1
    ):
        manager_remind_list = []
        employ_list = self.env['hr.employee'].search([])
        hrholidaypublicobj = self.env['hr.holidays.public']
        hranalytictmobj = self.env['hr.analytic.timesheet']
        for employee in employ_list:
            count = 0
            selected_date = datetime.date.today()
            date_one_day = datetime.timedelta(days=1)
            manager_remind_list.append({
                'employee_id': employee.id,
                'date': [],
            })
            while count < count_days:
                selected_date = selected_date - date_one_day
                if not hrholidaypublicobj.is_public_holiday(
                        selected_date,
                        employee.id
                ) \
                        and not self.is_weekend(
                            selected_date
                ):
                    allhours_should = self._get_all_hour(
                        selected_date,
                        employee.id,
                        workstart,
                        workend,
                        resethours
                    )
                    if not allhours_should:
                        continue
                    hrworklist = hranalytictmobj.search([
                        ('date',
                         '=',
                         str(selected_date)),
                        ('user_id',
                         '=',
                         employee.user_id.id)
                    ])
                    if hrworklist:
                        workhours_real = 0
                        for hrwork in hrworklist:
                            workhours_real += hrwork.unit_amount
                        allhours_real = workhours_real + resethours
                        if allhours_should <= allhours_real:
                            pass
                        else:
                            manager_remind_list[
                                len(manager_remind_list) - 1
                            ]['date'].append(str(selected_date))
                            if employee.parent_id:
                                manager_remind_list[
                                    len(manager_remind_list) - 1
                                ]['manager_id'] = employee.parent_id.id
                    else:
                        manager_remind_list[
                            len(manager_remind_list) - 1
                        ]['date'].append(str(selected_date))
                        if employee.parent_id:
                            manager_remind_list[
                                len(manager_remind_list) - 1
                            ]['manager_id'] = employee.parent_id.id
                    count += 1
        manager_remind_list = filter(
            lambda employee: 'manager_id' in employee,
            manager_remind_list
        )
        self.send_email_manager(manager_remind_list)

    @api.multi
    def send_email_manager(self, manager_remind_list=False):
        hremployeeobj = self.env['hr.employee']
        mail_obj = self.env['mail.mail']
        manager_list = set([employee['manager_id'] for employee in
                            manager_remind_list])
        if manager_list:
            for manager_id in list(manager_list):
                employee_date_list = filter(
                    lambda employee: employee['manager_id'] == manager_id,
                    manager_remind_list
                )
                manager = hremployeeobj.browse(manager_id)
                subject = _("Dear %s <br clear=left>") % manager.name
                body_html = "Follow employees would need to input timesheet: "
                for employee_date in employee_date_list:
                    employee = hremployeeobj.browse(
                        employee_date['employee_id']
                    )
                    body_html += _('%s Date: %s <br clear=left>') % (
                        employee.name,
                        employee_date['date']
                    )
                mail = mail_obj.create(
                    {'subject': subject,
                     'email_to': manager.work_email,
                     'body_html': body_html}
                )
                mail_obj.send([mail.id])

    def is_weekend(self, selected_date):
        if selected_date.weekday() not in self.WEEKEND:
            return False
        else:
            return True

    @api.multi
    def _get_all_hour(self, selected_date, employee_id, workstart,
                      workend, resethours):
        no_work = 0
        employee = self.env['hr.employee'].browse(employee_id)
        employee_tz_str = employee.user_id.tz
        if employee_tz_str:
            employee_tz = standard_tz = pytz.timezone(employee_tz_str)
        else:
            employee_tz = standard_tz = pytz.utc
        selected_date_start = self._str_to_datetime(
            str(selected_date) + ' ' + str(workstart), standard_tz)
        selected_date_end = self._str_to_datetime(
            str(selected_date) + ' ' + str(workend), standard_tz)
        workhours = selected_date_end.hour - selected_date_start.hour
        hrholidayobj = self.env['hr.holidays']
        leaves = hrholidayobj.search(
            [
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('state', 'not in', ('cancel', 'refuse'))
            ]
        )
        if not leaves:
            return workhours + resethours
        for leave in leaves:
            leave_date_from = self._tz_offset(
                leave.date_from, employee_tz
            )
            leave_date_to = self._tz_offset(
                leave.date_to, employee_tz
            )
            if leave_date_from >= selected_date_start \
                    and leave_date_from < selected_date_end <= leave_date_to:
                return leave_date_from.hour - selected_date_start.hour
            elif leave_date_from >= selected_date_start \
                    and selected_date_end >= leave_date_to:
                return leave_date_from.hour - selected_date_start.hour + \
                    selected_date_end.hour - leave_date_to.hour
            elif leave_date_to <= selected_date_end \
                    and leave_date_to > selected_date_start >= leave_date_from:
                return selected_date_end.hour - leave_date_to.hour
            elif leave_date_from < selected_date_start \
                    and selected_date_end < leave_date_to:
                return no_work
        return workhours + resethours

    def _str_to_datetime(self, str=False, standard_tz=False):
        return datetime.datetime.strptime(
            time.strftime(str),
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=standard_tz)

    def _tz_offset(self, str=False, employee_tz=False):
        utc_date = datetime.datetime.strptime(
            time.strftime(str),
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=pytz.utc)
        return utc_date.astimezone(employee_tz)

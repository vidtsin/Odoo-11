# -*- coding: utf-8 -*-
from __future__ import division
from odoo import models, fields, _, api
from odoo.exceptions import Warning
import time
from lxml.html.builder import INS


class ir_sequence(models.Model):
    _inherit = "ir.sequence"

    @api.depends('min_value')
    def display_min_value(self):
        for rec in self:
            if rec.prefix:
                start_number_filled = str(rec.min_value)
                for relleno in range(len(str(rec.min_value)), rec.padding):
                    start_number_filled = '0'+ start_number_filled
                rec.dis_min_value = rec.prefix + str(start_number_filled)

    @api.depends('max_value')
    def display_max_value(self):
        for rec in self:
            if rec.prefix:
                final_number = rec.max_value
                final_number_filled = str(rec.max_value)
                for relleno in range(len(str(final_number)),rec.padding):
                    final_number_filled = '0'+ final_number_filled
                rec.dis_max_value = rec.prefix + str(final_number_filled)

    fiscal_regime = fields.One2many('dei.fiscal_regime', 'sequence')
    start_date = fields.Date('Start Date')
    expiration_date = fields.Date('Expiration Date', compute="get_expiration_date")
    min_value = fields.Integer("Min Value", compute='get_min_value')
    max_value = fields.Integer("Max Value", compute='get_max_value')
    dis_min_value = fields.Char('min number',readonly=True, compute="display_min_value")
    dis_max_value = fields.Char('max number',readonly=True, compute="display_max_value")
    percentage_alert = fields.Float('percentage alert', default=80)
    # percentage         = fields.Float('percentage' )
    percentage = fields.Float('percentage', compute='compute_percentage')
    l_prefix = fields.Char('prefix', related='prefix')
    l_padding = fields.Integer('Number padding', related='padding')
    l_number_next_actual = fields.Integer('Next Number', related='number_next_actual')

    @api.model
    def create(self, values):
        new_id = super(ir_sequence, self).create(values)
        self.validar()
        return new_id

    @api.multi
    def write(self, values):
        write_id = super(ir_sequence, self).write(values)
        self.validar()
        return write_id

    @api.depends('fiscal_regime')
    @api.one
    def get_expiration_date(self):
        if self.fiscal_regime:
            for regime in self.fiscal_regime:
                if regime.selected:
                    self.expiration_date = regime.cai.expiration_date

    @api.depends('fiscal_regime')
    @api.one
    def get_min_value(self):
        if self.fiscal_regime:
            for regime in self.fiscal_regime:
                if regime.selected:
                    self.min_value= regime.desde
        else:
            self.min_value=0

    @api.depends('fiscal_regime')
    @api.one
    def get_max_value(self):
        if self.fiscal_regime:
            for regime in self.fiscal_regime:
                if regime.selected:
                    self.max_value = regime.hasta
        else:
            self.max_value = 0


    @api.depends('number_next_actual')
    def compute_percentage(self):
        numerator = self.number_next_actual - self.min_value
        denominator = self.max_value - self.min_value
        if denominator > 0:
            difference = (self.number_next_actual - self.min_value) / (self.max_value - self.min_value)
            self.percentage = (difference * 100) - 1
        else:
            self.percentage = 0

    def validar(self):
        already_in_list = []
        for fiscal_line in self.fiscal_regime:
            if fiscal_line.cai.name in already_in_list:
                raise Warning(_(' %s this cai is already in use ') % (fiscal_line.cai.name))
            already_in_list.append(fiscal_line.cai.name)

        for fiscal_line in self.fiscal_regime:
            for fiscal_line_compare in self.fiscal_regime:
                if fiscal_line.desde > fiscal_line_compare.desde and fiscal_line.desde < fiscal_line_compare.hasta:
                    raise Warning(_('%s to %s fiscal line overlaps ' ) %(fiscal_line.desde,fiscal_line.hasta))
                if fiscal_line.hasta > fiscal_line_compare.desde and fiscal_line.hasta < fiscal_line_compare.hasta:
                    raise Warning(_('%s to %s fiscal line overlaps ' ) %(fiscal_line.desde,fiscal_line.hasta))

        for fiscal_line in self.fiscal_regime:
            if fiscal_line.desde > fiscal_line.hasta:
                raise Warning(_('min_value %s to max_value %s' ) %(fiscal_line.desde,fiscal_line.hasta))


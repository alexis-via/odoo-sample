# -*- coding: utf-8 -*-
##############################################################################
#
#    Report * module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# NOTE : pas besoin de mettre ce fichier dans __init__.py

from openerp.report import report_sxw
from openerp import _
from openerp.exceptions import Warning


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'report_order_line': self._get_report_order_line,
        })
    # appel dans rapport : for each="entry in report_order_line(o)"

    def _get_report_order_line(self, order, context=None):
        res = {}
        # {categ_obj1 : {'subtotal': 123.12, 'lines': [line1, line2, line3]}}
        for line in order.order_line:
            if not line.product_id:
                raise Warning(
                    'Missing product on sale order line with description %s' % line.name)
            product_categ = line.product_id.categ_id
            if product_categ.parent_id and product_categ.parent_id.parent_id:
                while product_categ.parent_id.parent_id:
                    product_categ = product_categ.parent_id
            if product_categ in res:
                res[product_categ]['subtotal'] += line.price_subtotal
                res[product_categ]['lines'].append(line)
            else:
                res[product_categ] = {
                    'subtotal': line.price_subtotal,
                    'lines': [line],
                }
        print "res=", res
        result = []
        # [{'categ': categ1, 'subtotal': 123.12, 'lines': [line1, line2, line9]},
        # {'categ': categ2, 'subtotal': 223.42, 'lines': [line5, line3, line3]]
        for categ, struct in res.items():
            new_struct = {'categ': categ}
            new_struct.update(struct)
            print "new_struct=", new_struct
            result.append((categ.report_seq, new_struct))
        print "BEFORE SORT result=", result
        sorted_result = sorted(result, key=lambda to_sort: to_sort[0])
        print "AFTER SORT =", sorted_result
        return sorted_result

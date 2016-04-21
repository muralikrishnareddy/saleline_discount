# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


{
    'name': 'Sale Discount based on Role',
    'category': 'Sales', 
    'version': '1.0',
    'description': """
Control Discount based on User Sales Role
====================

Sale Order line wise user shall not be allowed to give more than configured Discount.

    """,
    'author': 'Murali Krishna Reddy',
    'website': 'http://www.credativ.in',
    'sequence':1,
    'depends': ['base','sale'],
    'data': [          
        'security/ir.model.access.csv',
        'sale_view.xml',
    ],
    "images": ["images/sale1.png",
               "images/sale2.png",
               "images/sale3.png"],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import os
import re
import openerp
from openerp import SUPERUSER_ID, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools import image_resize_image
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
import locale
from lxml import etree

from openerp.tools.safe_eval import safe_eval as eval
  

class sale_order(osv.osv):
    _inherit = "sale.order" 
    

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"         
    
    def check_discount_permitted(self, cr, uid, ids,product_id, linediscount, context=None):     
        if linediscount:   
            category_id=self.pool.get('ir.module.category').search(cr,uid,[('name','=','Sales'),('sequence','!=',0)],order='id',context=context)
            #group_ids=self.pool.get('res.groups').search(cr,uid,[('category_id','=',category_id[0])],context=context)
            user = self.pool.get('res.users').browse(cr, uid, uid)
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            if category_id and len(category_id)>0:
                for group in user.groups_id:
                    if group.category_id.id == category_id[0]:
                        if group.name=='Manager':
                            for line in product.product_tmpl_id.sale_role_discount_lines:
                                if line.group_id.id==group.id:
                                    discount = line.discount
                                    if discount and linediscount>discount:
                                        raise osv.except_osv(_('ERROR!'),_('you are not allowed to give more than %s %% discount for this product.' % discount) )
                            return True 
                        if group.name=='See all Leads':
                            for line in product.product_tmpl_id.sale_role_discount_lines:
                                if line.group_id.id==group.id:
                                    discount = line.discount
                                    if discount and linediscount>discount:
                                        raise osv.except_osv(_('ERROR!'),_('you are not allowed to give more than %s %% discount for this product.' % discount) )
                            return True 
                        if group.name=='See Own Leads':
                            for line in product.product_tmpl_id.sale_role_discount_lines:
                                if line.group_id.id==group.id:
                                    discount = line.discount
                                    if discount and linediscount>discount:
                                        raise osv.except_osv(_('ERROR!'),_('you are not allowed to give more than %s %% discount for this product.' % discount) )
                            return True         
                  
        return True
        
        
        
    def _check_discount(self, cr, uid, ids, context=None):
        line_obj = self.browse(cr, uid, ids[0], context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        self.check_discount_permitted(cr, uid, ids,line_obj.product_id.id, line_obj.discount, context=context)
        product = line_obj.product_id
        for group in user.groups_id:
            discount = (line.discount for line in product.sale_role_discount_lines if line.group_id.id==group.id)
            if discount and discount>line_obj.discount:
                return False
        return True
        
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = {}
        ret = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if 'value' in ret:
            ret['value']['discount']=False            
        return ret

    
   
class res_company(osv.osv):
    _inherit = "res.company"
    
    def _get_sales_roles(self, cr, uid, context=None):
        ret = []
        category_id=self.pool.get('ir.module.category').search(cr,uid,[('name','=','Sales')],context=context)
        group_ids=self.pool.get('res.groups').search(cr,uid,[('category_id','=',category_id[0])],context=context)
        for obj in self.pool.get('res.groups').browse(cr, uid,group_ids,context=context):
            ret.append((0,0,{'group_id':obj.id}))
        return ret
            
            
    _columns ={        
        'sale_role_discount_lines': fields.one2many('res.groups.discount.line', 'company_id', string='Discount Allowed per Role'),
    } 
    
class groups_discount_line(osv.osv):
    _name = 'res.groups.discount.line'
    _columns = {
        'company_id':fields.many2one('res.company','Company'),
        'group_id':fields.many2one('res.groups', 'Sales Role'),
        'discount':fields.float('Max Discount (%) can give'),
    }
    
    def create(self, cr, uid, vals, context=None):
        cnt = self.search_count(cr, uid, [('group_id','=',vals['group_id']),('company_id','=',vals['company_id'])])
        if cnt and cnt>0:
            raise osv.except_osv(_('ERROR!'),_('Discount entered more than once for same Role.'))
        ret = super(groups_discount_line, self).create(cr, uid, vals, context=context)
        return ret
        
        
class product_template(osv.osv):
    _inherit = "product.template"
    
    def _get_data_from_company(self, cr, uid, context=None):
        company = self.pool.get('res.company').browse(cr, uid, self.pool.get('res.company').search(cr, uid, [])[0])
        ret = []
        for line in company.sale_role_discount_lines:
            ret.append((0,0,{'group_id':line.group_id.id, 'discount':line.discount}))
        return ret
        
    _columns = {
        'sale_role_discount_lines': fields.one2many('sale.groups.discount.line', 'product_id', string='Discount Allowed per Role'),
    }
    _defaults = {
        'sale_role_discount_lines':_get_data_from_company,
    }
    
class sale_groups_discount_line(osv.osv):
    _name = 'sale.groups.discount.line'
    
    _columns = {
        'product_id':fields.many2one('product.template','Product'),
        'group_id':fields.many2one('res.groups', 'Sales Role'),
        'discount':fields.float('Max Discount (%) can give'),
    }    
    
    def create(self, cr, uid, vals, context=None):
        cnt = self.search_count(cr, uid, [('group_id','=',vals['group_id']),('product_id','=',vals['product_id'])])
        if cnt and cnt>0:
            raise osv.except_osv(_('ERROR!'),_('Discount entered more than once for same Role.'))
        ret = super(sale_groups_discount_line, self).create(cr, uid, vals, context=context)
        return ret
        
    

    
    
        

    
    
    
    
    
    
        
        

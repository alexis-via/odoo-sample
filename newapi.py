# -*- encoding: utf-8 -*-
##############################################################################
#
#    MODULENAME module for Odoo
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError, RedirectWarning
import openerp.addons.decimal_precision as dp
from openerp import workflow  # ex-netsvc  => on peut faire workflow.trg_validate()

from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class ProductCode(models.Model):
# wizard : models.TransientModel ; rien: models.AbstractModel
    _name = "product.code"
    _description = "Product code"
    _rec_name = "display_name"  # Nom du champ qui fait office de champ name
    _order = "name, id desc"
    # C'est ascendant par défaut, donc pas besoin de préciser "asc"
    _table = "prod_code"  # Nom de la table ds la DB
    _inherit = ['mail.thread']    # OU ['mail.thread', 'ir.needaction_mixin'] ?? ds quel cas ?
    _track = {
        'state': {
            'l10n_fr_intrastat_service.declaration_done':
            lambda self, cr, uid, obj, ctx=None: obj.state == 'done',
            }
        }

    def __init__(self, pool, cr):
        # Executed each time a registry is initialized, it can happen
        # for instance when you have several processes and one of them
        # invalidates the registry cache (after creation of a
        # ir.model.fields for instance).
        init_res = super(account_journal, self).__init__(pool, cr)
        cr.execute("UPDATE account_journal SET allow_date=True")
        return init_res

    # Pour hériter juste une propriété d'un champ :
    def __init__(self, pool, cr):
        super(crm_claim, self).__init__(pool, cr)
        self._columns['user_id'].string = 'Employee in charge'

    def init(self, cr):
        # Exécuté à chaque installation du module
        cr.execute(
            "UPDATE account_journal SET allow_date=true "
            "WHERE allow_date <> true")

    # DEPRECATED ? Apparemment, il faut ajouter un champ fonction "display_name"
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, u'%s (%s-%s)' % (record.name, record.date_start, record.date_end)))
        return res
        # when called with a single ID :
        # record.name_get()[0][1]

    # Hériter la recherche textuelle dans les champs many2one
    # name : object name to search for
    # operator : operator for name criteria
    @api.model
    def name_search(
            self, name='', args=None, operator='ilike', limit=80):
        if args is None:
            args = []
        if name:
            refs = self.search(
                [('code', '=', name)] + args, limit=limit)
            if refs:
                return refs.name_get()
        return super(StayRefectory, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

    @api.model
    def default_get(self, fields):
        res = super(OvhInvoiceGet, self).default_get(fields)
        accounts = []
        ovh_accounts = self.env['ovh.account'].search(
            [('company_id', '=', self.env.user.company_id.id)])
        for account in ovh_accounts:
            accounts.append({
                'ovh_account_id': account.id,
                'password': account.password,
            })
        # to set the value for a O2M fields, you need to return:
        # res = [
        #   {'o2m_field': [
        #       {'field1': field1val1, 'field2': field2val1},
        #       {'field1': field1val2, 'field2': field2val2}]
        #   }]
        res.update(account_ids=accounts)
        return res


    # Fonction on_change NON déclarée dans la vue form/tree
    # ATTENTION : apparemment, on ne peut pas avoir à la fois un
    # on_change='' dans la vue XML et un api.onchange pour le même champ
    # car dans ce cas seul le on_change='' est joué
    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.delivery_id = self.partner_id  # MAJ d'un autre champ
            # M2M : liste d'IDs (pas besoin de (6, 0, [])
            # On utilise un autre M2M pour le mettre à jour, on peut faire
            # self.champ_M2M_ids.ids -> ça donne la liste des IDs
            # M2O : recordset (ou ID)
            # O2M : ??
            # là, Odoo va jouer automatiquement le @api.onchange du champ delivery_id
            # pas besoin d'appeler le onchange de delivery_id dans notre code
        # Here, all form values are set on self
        # assigned values are not written to DB, but returned to the client
        # It is not possible to output a warning
        # It is not possible to put a raise Warning()
        # in this function (it will crash odoo)
        res = {'warning':
            {'title': _('Be careful'),
            {'message': _('here is the msg')}}
        # pour un domaine
        res = {'domain': {
            'champ1': "[('product_id', '=', product_id)]",
            'champ2': "[]"},
            }
        return res
        # si je n'ai ni warning ni domain, je n'ai pas besoin de faire un return

    # Fonction on_change déclarée dans la vue form/tree
    @api.multi
    def product_id_change(self, cr, uid, ids, champ1, champ2, context):
        # ATTENTION : a priori, on ne doit pas utiliser ids dans le code de la
        # fonction, car quand on fait un on_change avant le save, ids = []
        # Dans la vue XML :
        # <field name="product_id"
        #        on_change="product_id_change(champ1, champ2, context)" />
        # Piège : quand un champ float est passé dans un on_change,
        # si la personne avait tapé un entier, il va être passé en argument en
        # tant que integer et non en tant que float!

        raise orm.except_orm()
        # => il ne remet PAS l'ancienne valeur qui a déclanché le on_change

        # Pour mettre à jour des valeurs :
        return {'value': {'champ1': updated_value1, 'champ2': updated_value2}}
        # => à savoir : les onchange de 'champ1' et 'champ2' sont joués à
        # leur tour car leur valeur a été changée
        # si ces nouveaux on_change changent le product_id,
        # le product_id_change ne sera pas rejoué

        # Pour mettre un domaine :
        return {'domain': {
            'champ1': "[('product_id', '=', product_id)]",
            'champ2': "[]"},
            }
        # l'intégralité du domaine est dans une string

        # Pour retourner un message de warning :
        return {'warning': {
            'title': _('Le titre du msg de warn'),
            'message': _("Ce que j'ai à te dire %s") % (text)}}
        # Pour ne rien faire
        return False  # return True, ça marche en 7.0 mais ça bug en 6.1

    # La fonction de calcul du champ function price_subtotal
    @api.one  # auto-loop decorator
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    # @api.depends est utilisé pour: invalidation cache, recalcul, onchange
    # donc, maintenant, le fait d'avoir un champ calculé fait qu'il est
    # automatiquement mis à jour dans la vue quand un de ses champs 'depends'
    # est modifié ! COOOOOL !
    # ATTENTION : si chgt de @api.depends, faire -u module !
    # Pour un one2many : ne PAS juste indiquer le nom du champ o2m, sinon il ne fait rien
    # il faut aussi indiquer un champ sur le O2M. Exemple : 'line_ids.request_id'
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']  # calcul et stockage de la valeur
        self.second_field = 'iuit'  # calcul et stockage d'un 2e champ
                                    # equivalent de multi='pouet'
        # Pour un champ O2M, envoyer une liste d'IDS
        # pour un champ M2O, donner l'ID (ou le recordset ?)
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
        # Pas besoin de return !
        # on ne peut PAS faire un self.write({}) dans la fonction de calcul d'un champ fonction

    # Pour un champ fonction, on peut aussi faire @api.multi:
    # untaxed = fields.Float(compute='_amounts')
    # taxes = fields.Float(compute='_amounts')
    # total = fields.Float(compute='_amounts')
    @api.multi
    @api.depends('lines.amount', 'lines.taxes')
    def _amounts(self):
        for order in self:
            order.untaxed = sum(line.amount for line in order.lines)
            order.taxes = sum(line.taxes for line in order.lines)
            order.total = order.untaxed + order + taxes

    # Champ fonction inverse='_inverse_price'
    @api.one
    def _inverse_loud(self):
        self.name = (self.loud or '').lower()  # MAJ du ou des autres champs

    # Champ fonction search='_search_price'
    def _search_loud(self, operator, value):
        if value is not False:
            value = value.lower()
        return [('name', operator, value)]  # recherche sur les autres champs

    # Fonction default=_default_account
    @api.model
    def _default_account(self):
        return valeur_par_defaut
        # M2O : retourne un recordset (ne PAS retourner False !)
        # O2M : retourne une liste de dict contenant la valeur des champs
        # date : string ou objet datetime

    # Fonction pour fields.selection
    @api.model
    def _type_list_get(self):
        return [('key1', _('String1')), ('key2', _('String2'))]

    ### CHAMPS
    # id, create_uid, write_uid, create_date et write_date
    # sont déjà utilisable dans le code python sans re-définition
    active = fields.Boolean(default=True)
    # Par défaut, string = nom du champ avec majuscule pour chaque début de mot
    login = fields.Char(
        string='Login', size=16, translate=True, required=True,
        help="My help message")
    display_name = fields.Char(
        string='Display Name', compute='_compute_display_name',
        readonly=True, store=True)
    comment = fields.Text(string='Comment', translate=True)
    html = fields.Html(string='report', translate=True)
    code_digits = fields.Integer(
        string='# of Digits', track_visibility='always', default=12,
        groups='base.group_user')
    # OU groups=['base.group_user', 'base.group_hr_manager']
    # groups = XMLID : restriction du read/write et invisible ds les vues
    sequence = fields.Integer(default=10)
    # track_visibility = always ou onchange
    amount_untaxed = fields.Float(
        'Amount untaxed', digits=dp.get_precision('Account'))
    # digits=(precision, scale)
    # Scale est le nombre de chiffres après la virgule
    # quand le float est un fields.float ou un fields.function,
    # on met l'option : digits=dp.get_precision('Account')
    # Autres valeurs possibles pour get_precision : product/product_data.xml
    # Product Price, Discount, Stock Weight, Product Unit of Measure,
    # Product UoS
    start_date = fields.Date(
        string='Start Date', copy=False, default=fields.Date.context_today)
    # similaire : fields.Datetime and fields.Time
    type = fields.Selection([
        ('import', 'Import'),
        ('export', 'Export'),
        ], string="Type",
        default=lambda self: self._context.get('type', 'export'))
    # FIELDS.SELECTION ac selection dynamique :
    # type = fields.Selection('_type_list_get', string='Type', help='Pouet'),
    # Plus besoin de la double fonction pour que la 2e soit héritable
    # Pour ajouter des champs à un fields.Selection existant:
    # fields.Selection(
    #    selection_add=[('new_key1', 'My new key1'), ('new_key2', 'My New Key2')])
    picture = fields.Binary(string='Picture')
    # Pour fields.binary, il existe une option filters='*.png, *.gif',
    # qui restreint les formats de fichiers sélectionnables dans
    # la boite de dialogue, mais ça ne marche pas en GTK (on
    # ne peut rien sélectionner) et c'est pas supporté en Web, cf
    # https://bugs.launchpad.net/openobject-server/+bug/1076895

    # Exemple de champ fonction stocké
    price_subtotal = fields.Float(
        string='Amount', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price')
    # Exemple de champ function non stocké
    loud = fields.Char(
        store=False, compute='_compute_loud', inverse='_inverse_loud',
        search='_search_loud')
    account_id = fields.Many2one('account.account', string='Account',
        required=True, domain=[('type', 'not in', ['view', 'closed'])],
        default=_default_account)
    company_id = fields.Many2one(
        'res.company', string='Company',
        ondelete='cascade',
        default=lambda self: self.env['res.company']._company_default_get(
            'product.code'))
        # si on veut que tous les args soient nommés : comodel_name='res.company'
    user_id = fields.Many2one(
        'res.users', string='Salesman', default=lambda self: self.env.user ou self._uid ??) ## NON TESTE
    # ATTENTION : si j'ai déjà un domaine sur la vue,
    # c'est le domaine sur la vue qui prime !
    # ondelete='cascade' :
    # le fait de supprimer la company va supprimer l'objet courant !
    # ondelete='set null' (default)
    # si on supprime la company, le champ company_id est mis à 0
    # ondelete='restrict' :
    # si on supprime la company, ça déclanche une erreur d'intégrité !

    # Champ Relation
    company_currency_id = fields.Many2one(
        'res.currency', string='Currency', related='company_id.currency_id',
        store=True)
    # ATTENTION, en nouvelle API, on ne peut PAS faire un fields.Char qui
    # soit un related d'un fields.Selection (bloque le démarrage d'Odoo
    # sans message d'erreur !)

    line_ids = fields.One2many(
        'product.code.line', 'parent_id', string='Product lines',
        states={'done': [('readonly', True)]}, copy=True)
        # OU comodel_name='product.code.line', inverse_name='parent_id'
    # 2e arg = nom du champ sur l'objet destination qui est le M20 inverse
    # en v8 :
    # copy=True pour que les lignes soient copiées lors d'un duplicate
    # sinon, mettre copy=False (ça ne peut être qu'un booléen)
    # Valeur par défaut du paramètre "copy": True for normal fields, False for
    # one2many and computed fields, including property fields and related fields
    # ATTENTION : pour que states={} marche sur le champ A et que le
    # champ A est dans la vue tree, alors il faut que le champ "state"
    # soit aussi dans la vue tree.

    partner_ids = fields.Many2many(
        'res.partner', 'product_code_partner_rel', 'code_id', 'partner_id',
        'Related Partners')
    # 2e arg = nom de la table relation
    # 3e arg ou id1 = nom de la colonne dans la table relation
    # pour stocker l'ID du product.code
    # 4e arg ou id2 = nom de la colonne dans la table relation
    # pour stocker l'ID du res.partner
    # OU
    partner_ids = fields.Many2many(
        'res.partner', column1='code_id', column2='partner_id',
        string='Related Partners')
    # OU
    partner_ids = fields.Many2many(
        'res.partner', string='Related Partners')
    # Pour les 2 dernières définitions du M2M, il ne faut pas avoir
    # plusieurs champs M2M qui pointent du même obj vers le même obj

    # Champ property: il suffit de définit le champ comme un champ normal
    # et d'ajouter un argument company_dependent=True
    # Quand on veut lire la valeur d'un champ property dans une société
    # qui n'est pas celle de l'utilisateur, il faut passer dans le context
    # 'force_company': 8  (8 = ID de la company)
    }


        # 2. si il n'en existe pas pour cet objet, elle retourne le
        # "company_id" de l'utilisateur uid
        # http://openerp-expert-framework.71550.n3.nabble.com/Bug-925361-Re-6-1-date-values-that-are-initialized-as-defaults-may-appear-as-quot-off-by-one-day-quoe-td3741270.html

        # Ca permet d'avoir dans le champ date la date locale de
        # l'utilisateur qui créé l'objet, et non la date UTC du serveur, qui
        # peut être une date différente compte tenu du fuseau horaire.

        # Si on veut l'utiliser dans du code :
        # fields.Date.context_today(self)
        # ça renvoie la date du jour sous forme de STR

        # Pour convertir une datetime UTC en datetime de la timezone du
        # context (clé 'tz'), ou, si elle n'est pas présente, dans la timezone
        # de l'utilisateur:
        # datetime_in_tz = fields.datetime.context_timestamp(
        #    cr, uid, timestamp, context=context)
    }

    # APPEL A CREATE
    # apparemment, ça reste à l'ancienne, et on doit passer des IDs pour les M2O ???
    # on récupère un recordset en sortie

    @api.model  # equivalent de (self, cr, uid, vals, context=None)
    @api.returns('self')  # quand une fonction renvoi un recordset, on doit dire ici quel est le model de ce recordset
    def create(self, vals=None):
        if vals is None:
            vals = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.expense.expense')
        return super(ObjClass, self).create(vals)

    # Qd on appelle un write, pour un champ M2O, on met l'ID et non le recordset
    @api.multi  # équivalent de (self, cr, uid, ids, values, context=None)
    def write(self, values):
        values.update({'tutu': toto})
        return super(ObjClass, self).write(values)

    @api.multi
    def unlink(self):
        for donation in self:
            if donation.state == 'done':
                raise Warning(
                    _("The donation '%s' is in Done state, so you must "
                        "set it back to draft before deleting it.")
                    % donation.number)
        return super(DonationDonation, self).unlink()

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        # Si on a une séquence sur le champ name
        default['name'] = '/'  # comme ça, l'inherit du create va incrémenter la séq
        default['name'] = _('%s (copy)') % self.name
        return super(res_partner, self).copy(default)

    # CONTRAINTE PYTHON
    @api.one
    @api.constrains('lines', 'max_lines')  # SANS T à la fin pour constrains !
    def _check_size(self):
        if len(self.lines) > self.max_lines:
            raise ValidationError(_("Too many lines in %s") % self.name)
        # Pas besoin de return

    # PARFOIS, quand on supprime une contrainte SQL, il faut aussi la
    # supprimer dans postgres : ALTER TABLE res_partner DROP CONSTRAINT ...
    _sql_constraints = [
        (
            'date_uniq',
            'unique(start_date, company_id, type)',
            'A DEB of the same type already exists for this month !'),
        # selon cette page : https://www.pgrs.net/2008/01/11/postgresql-allows-duplicate-nulls-in-unique-columns/
        # c'est en fait "unique or null"
        (
            'currency_rate_max_delta_positive',
            'CHECK (currency_rate_max_delta >= 0)',
            "The value of the field '...' must be positive or 0."),
    ]

    @api.multi
    def my_button(self):
        # dans la vue: type="object"
        # cas particulier : on veut @api.multi pour ne pas boucler, mais
        # la fonction n'est prévue que pour 1 recordset:
        self.ensure_one()
        # Et, quand self ne contient qu'un seul record, on peut utiliser self.field_name
        # même en @api.multi
        return

    # pour un bouton qui ne renvoie pas d'action, on peut aussi faire
    @api.one
    def my_button(self):
    # il va alors boucler sur la fonction, mais comme le bouton est dans une vue form
    # il ne bouclera qu'une fois. Par contre, le résultat sera mis dans une séquence
    # donc ça marche pas si on renvoie une action

### EXEMPLES de code
partners = self.env['res.partner'].search([])
for partner in partners:
    print partner.name
    print partner['name']
    print partner.parent_id.company_id.name
    partner.name = 'Agrolait'   # Ecrit dans la DB

partners.name  # name of the first partner => BOF, confusion
partners.name = 'Agrolait'  # Assign first partner  => dangereux !
partners[0].name

if len(partners) >= 5:
    fifth = partners[4]  # Fifth partner

ajout = partners1 + partners2  # permet par exemple de transformer 2 recordset unitaire en 1 multi-recordset, pour appeler une fonction @api.multi dessus
union = partners1 | partners2
intersection = partners1 & partners2
difference = partners1 - partners2

# search retourne des objets
domain = [('id', 'in', self.ids), ('parent_id', '=', False)]
roots = self.search(domain)

roots.write({'modified': True})

@api.one
def cancel(self):
    self.state = 'cancel'

roots.cancel()  # appelle cancel sur chaque record de roots = [rec.cancel() for rec in roots]

@api.multi
@api.returns('res.partner')  # returns a recordset instead of ids
def root_partner(self):
    p = self.partner_id
    while p.parent_id:
        p = p.parent_id
    return p

# appel new api:
roots = recs.root_partner()
### Appel New API depuis ancienne API
root_ids = self.pool['res.partner'].root_partner(cr, uid, ids, context=context)

### Appel Ancienne API depuis nouvelle API
# déf en ancienne API:
def _get_picking_in(self, cr, uid, context=None)
# appel depuis new API:
self.env['purchase.order']._get_picking_in()

# définition en ancienne API
def onchange_partner_id(self, cr, uid, ids, partner_id, context=None)
# appel depuis new API
self.onchange_partner_id(partner_id)
# dans le cas d'un onchange, on ne peut généralement PAS passer d'IDs
nullrec = self.env['purchase.order'].browse(False)
nullrec.onchange_partner_id(partner_id)
# OU
self.pool['purchase.order'].onchange_partner_id(self._cr, self._uid, [], partner_id, context=recs.env.context)

self.env.cr  # shortcut : recs._cr
self.env.uid # shortcut : recs._uid
self.env.context # shortcut: recs._context

self.env.user  # current user as a record
self.env.ref('base.group_user')   # resolve XML ID, renvoie un recordset (pas un ID)
self.env['res.partner']  # equivalent de self.pool['res.partner']

# rebrowse recs with different parameters
env2 = self.env(cr2, uid2, context2)
recs2 = self.with_env(env2)

# special case: change/extend context
recs2 = self.with_context(context2)  # change context by context2
#ou
self = self.with_context(lang='fr')  # extend current context
self.env['res.currency'].with_context(date=signature_date).compute()

# special case: change the uid
recs2 = self.sudo(user)
recs2 = self.sudo()  # uid = SUPERUSER_ID

# RedirectWarning
action = self.env.ref('account.action_account_config')
msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))


### INHERIT
class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line():
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        return res

# si la classe hérite de mail.thread: on peut écrire un msg dans le chatter par cette simple ligne:
picking.message_post(_("The picking has been re-opened and set to draft state"))
# proto complet
def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification', subtype=None, parent_id=False, attachments=None, context=None, content_subtype='html', **kwargs)


# conversion datetime / string
>>> fields.Date.from_string('2014-06-15')
datetime.datetime(2014, 6, 15, ...)
>>> fields.Date.to_string(datetime.datetime.today())
’2014-06-15’
# idem avec fields.Datetime.to/from_string
# A NOTER : on peut mettre un objet datetime dans un self.search([('start_date', '=', start_date_dt)])

# QUESTIONS
#Apparemment, qd une fonction a un décorateur @api.cr_uid_id_context (exemple : send_mail dans le modulle email_template), on ne peut l'appeler qu'avec l'ancienne API)
#aussi @api.cr_uid_ids_context et @api.cr_uid_context

@api.cr_uid_ids_context
def machin(cr, uid, ids, context=None):

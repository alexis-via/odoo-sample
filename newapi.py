# -*- coding: utf-8 -*-
# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
# v8
from openerp.exceptions import Warning as UserError

import odoo.addons.decimal_precision as dp
from odoo.tools.misc import format_date, format_datetime, format_amount
from odoo.tools import float_compare, float_is_zero, float_round
from odoo.tools import file_open
from odoo import workflow  # ex-netsvc  => on peut faire workflow.trg_validate()

from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict   # a = defaultdict(list)

import logging
logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError:
    logger.debug('Cannot import phonenumbers')


class ProductCode(models.Model):
# wizard : models.TransientModel ; rien: models.AbstractModel
    _name = "product.code"
    _description = "Product code"
    _rec_name = "display_name"  # Nom du champ qui fait office de champ name
    _order = "name, id desc"
    _check_company_auto = True
    # C'est ascendant par défaut, donc pas besoin de préciser "asc"
    _table = "prod_code"  # Nom de la table ds la DB
    _inherit = ['mail.thread']    # OU ['mail.thread', 'ir.needaction_mixin'] ?? ds quel cas ?
    _inherit = ['mail.thread', 'mail.activity.mixin']  # V12
    # v10 only
     _name = 'purchase.order'
     _inherit = ['purchase.order', 'base.ubl']

    _track = {  # V7 and V8 / in v9+, replaced by _track_subtype(self, init_values)
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

    @api.model_cr  # Don't put api.model_cr on v14
    def init(self):
        # Exécuté à chaque installation et reload du module
        self._cr.execute(
            "UPDATE account_journal SET allow_date=true "
            "WHERE allow_date <> true")
        # Contrainte d'unicité restreinte à une certaine valeur
        self._cr.execute(
            '''
            CREATE UNIQUE INDEX IF NOT EXISTS single_email_primary ON res_partner_phone (partner_id, type) WHERE (type='8_email_primary')
            ''')

    @api.model_cr  # v10 v12 (not v8)
    def init(self):
    tools.drop_view_if_exists(self._cr, self._table)
    self._cr.execute("""CREATE or REPLACE VIEW %s as (SELECT ...""")


    # DEPRECATED ? Apparemment, il faut ajouter un champ fonction "display_name"
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, u'%s (%s-%s)' % (record.name, record.date_start, record.date_end)))
        return res
        # when called with a single ID :
        # record.name_get()[0][1]

    # Hériter la recherche textuelle dans les champs many2one (et aussi dans les vues de recherche qui ont <field name="partner_id" filter_domain="[('partner_id','child_of',self)]"/>
    # name : object name to search for
    # operator : operator for name criteria
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):  # 80 in v13-
        if args is None:
            args = []
        if name and operator == 'ilike':
            recs = self.search([('code', '=', name)] + args, limit=limit)
            if recs:
                return recs.name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.model
    def default_get(self, fields_list):
        res = super(OvhInvoiceGet, self).default_get(fields_list)
        accounts = []
        ovh_accounts = self.env['ovh.account'].search(
            [('company_id', '=', self.env.user.company_id.id)])
        for account in ovh_accounts:
            # en v8 et v10:
            accounts.append((0, 0, {'ovh_account_id': account.id, 'password': account.password,}))
            # en v8, ça marche aussi sans [(0, 0, {})] en donnant directement [{}]
        # return date as string (not datetime)
        # M2M : v10 : list of IDs ou [(6, 0, IDs)]
        # O2M : ID
        # to set the value for a O2M fields, you need to return:
        # v8 :
        # res = {'o2m_field': [
        #       {'field1': field1val1, 'field2': field2val1},
        #       {'field1': field1val2, 'field2': field2val2}]
        #   }
        # v10:
        # res = {'o2m_field': [
        #         (0, 0, {'field1': field1val1, 'field2': field2val1},
        #         (0, 0, {'field1': field1vaxx, 'field2': field2vayy},
        #         ]
        #       }
        res.update(account_ids=accounts)
        return res


    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.delivery_id = self.partner_id  # MAJ d'un autre champ
            # OU
            vals = {'delivery_id': self.partner_id.id}
            self.update(vals)
            # M2M : 2 possibilités :
            # - liste d'IDs, mais ça va AJOUTER les ids, comme (4, [IDs])
            # - [(6, 0, [IDs])], ce qui va remplacer les ids
            # (cf module product_category_tax dans akretion/odoo-usability)
            # On utilise un autre M2M pour le mettre à jour, on peut faire
            # self.champ_M2M_ids.ids -> ça donne la liste des IDs
            # M2O : recordset (ou ID)
            # O2M : exemple v10 dans purchase/models/account_invoice.py
            # méthode purchase_order_change()
            # là, Odoo va jouer automatiquement le @api.onchange du champ delivery_id
            # pas besoin d'appeler le onchange de delivery_id dans notre code
        # Here, all form values are set on self
        # assigned values are not written to DB, but returned to the client
        # It is not possible to output a warning
        # It is not possible to put a raise UserError()
        # in this function (it will crash odoo)
        res = {'warning':
            {'title': _('Be careful'),
            {'message': _('here is the msg')}}
        # pour un domaine
        res = {'domain': {
            'champ1': "[('product_id', '=', product_id)]",
            'champ2': "[]"},
            }
        # si on a besoin de changer le contexte (astuce qui peut être utile
        # pour ne pas déclancher en cascade les autres api.onchange qui filtreraient
        # sur le contexte
        self.env.context = self.with_context(olive_onchange=True).env.context
        # astuce trouvée sur https://github.com/odoo/odoo/issues/7472
        return res
        # si je n'ai ni warning ni domain, je n'ai pas besoin de faire un return

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
    # Apparemment, on peut mettre dans @api.depends un champ fonction stocké et ça va bien
    # faire le recalcul en cascade
    # (ça n'a pas l'air de marcher qd on met un api.depends sur un champ non stocké)
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']  # calcul et stockage de la valeur
        self.second_field = 'iuit'  # calcul et stockage d'un 2e champ
                                    # equivalent de multi='pouet'
        # Pour un champ O2M ou M2M, envoyer un recordset multiple ou une liste d'IDS
        # pour un champ M2O, donner le recordset ou l'ID
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
    @api.onchange('name')  # add @api.onchange on an inverse method to have it apply immediately and not upon save
    def _inverse_loud(self):
        for rec in self:
            rec.name = (rec.loud or '').lower()  # MAJ du ou des autres champs

    # Champ fonction search='_search_price'
    def _search_loud(self, operator, value):
        if value is not False:
            value = value.lower()
        today = fields.Date.context_today(self)
        self._cr.execute('SELECT id FROM [cur_obj] WHERE (fortress_type <> %s OR (fortress_type = %s AND effectivity_date is not null)) AND (end_date is null OR end_date > %s)', (today, ))
        res_ids = [x[0] for x in self._cr.fetchall()]
        res = [('id', 'in', res_ids)] # recherche sur les autres champs
        return res

    # Fonction default=_default_account
    @api.model
    def _default_account(self):
        return valeur_par_defaut
        # M2O : retourne un recordset ou un ID (ou False)
        # (NOTE: apparemment, en v8, il veut un ID)
        # OUTDATED (?) : ATTENTION, si on veut un M2O à False, il ne pas que la fonction
        #       _default_account retourne False mais self.env['..'].browse(False)
        # O2M : retourne une liste de dict contenant la valeur des champs
        # M2M : retourne un recordset multiple ?
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
        string='# of Digits', track_visibility='onchange', default=12,
        groups='base.group_user')
    # OU groups=['base.group_user', 'base.group_hr_manager']
    # groups = XMLID : restriction du read/write et invisible ds les vues ET EXPORT
    # v13: track_visibility='onchange' => tracking=X
    sequence = fields.Integer(default=10)
    # track_visibility = always ou onchange
    amount_untaxed = fields.Float(
        'Amount untaxed', digits='Product Unit of Measure',
        group_operator="avg")  # Utile pour un pourcentage par exemple
    # v13 : digits='Product Unit of Measure'
    # v12- : digits=dp.get_precision('Account')
    # digits=(precision, scale)   exemple (16, 2)
    # Scale est le nombre de chiffres après la virgule
    # quand le float est un fields.float ou un fields.function,
    # on met l'option : digits=dp.get_precision('Account')
    # Autres valeurs possibles pour get_precision : product/product_data.xml
    # Product Price, Discount, Stock Weight, Product Unit of Measure,
    # Product UoS (v8 only)
    # fields.Monetary is only in version >= 9.0
    debit = fields.Monetary(default=0.0, currency_field='company_currency_id')
    start_date = fields.Date(
        string='Start Date', copy=False, default=fields.Date.context_today,
        index=True)
    # similaire : fields.Datetime and fields.Time
    start_datetime = fields.Datetime(
        string='Start Date and Time', default=fields.Datetime.now)
    # index=True => the field will be indexed in the database
    # (much faster when you search on that field)
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
    # v14 : ondelete={"new_key1": "set default"}
    # other possible options for ondelete: set null, cascade (delete the records !)
    picture = fields.Binary(string='Picture', attachment=True)
    # Pour fields.binary, il existe une option filters='*.png, *.gif',
    # qui restreint les formats de fichiers sélectionnables dans
    # la boite de dialogue, mais ça ne marche pas en GTK (on
    # ne peut rien sélectionner) et c'est pas supporté en Web, cf
    # https://bugs.launchpad.net/openobject-server/+bug/1076895
    picture_filename = fields.Char(string='Filename')
    # Les champs "picture" et "picture_filename" sont liés ensemble dans la vue
    # via la balise filename="picture_filename" sur le champ 'picture'
    # Il faut que le champ 'picture_filename' soit présent dans la vue
    # (il peut être invisible)
    # Pour un fichier à télécharger d'Odoo, le nom du fichier aura la valeur de
    # picture_filename
    # Pour un fichier à uploader dans Odoo, 'picture_filename' vaudra le nom
    # du fichier uploadé par l'utilisateur

    # Exemple de champ fonction stocké
    price_subtotal = fields.Float(
        string='Amount', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price')
    # Exemple de champ function non stocké avec fonction inverse
    loud = fields.Char(
        store=False, compute='_compute_loud', inverse='_inverse_loud',
        search='_search_loud')
    account_id = fields.Many2one('account.account', string='Account',
        required=True, domain=[('type', 'not in', ['view', 'closed'])],
        default=lambda self: self._default_account(),
        check_company=True)
        # L'utilisation de lambda permet d'hériter la fonction _default_account() sans
        # hériter le champ. Sinon, on peut aussi utiliser default=_default_account
        # Possibilité d'hériter un domaine:
        # domain=lambda self: [('reconcile', '=', True), ('user_type_id.id', '=', self.env.ref('account.data_account_type_current_assets').id), ('deprecated', '=', False)]
    company_id = fields.Many2one(
        'res.company', string='Company',
        ondelete='cascade', required=True,
        default=lambda self: self.env['res.company']._company_default_get()
        default=lambda self: self.env.company)  # v13
        # si on veut que tous les args soient nommés : comodel_name='res.company'
    user_id = fields.Many2one(
        'res.users', string='Salesman', default=lambda self: self.env.user)
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
        store=True)  # option related_sudo=True by default
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
    # 3e arg ou column1 = nom de la colonne dans la table relation
    # pour stocker l'ID du product.code
    # 4e arg ou column2 = nom de la colonne dans la table relation
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
        # -> v8 à v11 ça renvoie la date du jour sous forme de STR dans la TZ de l'utilisateur
        # -> v12 : ça renvoie la date du jour sous forme d'obj datetime dans la TZ du user
        # fields.Date.today()
        # -> ça renvoie la date du jour en GMT ??
        # v12 : conversion datetime en date
        # fields.Date.to_date(line.datetime_order)
        # v12 : conversion date en datetime
        # fields.Datetime.to_datetime(line.end_date)

        # Pour avoir la date et l'heure LOCALE de l'utilisateur en datetime:
        # fields.Datetime.context_timestamp(self, datetime.now())
        # Pour convertir une datetime UTC en datetime de la timezone du
        # context (clé 'tz'), ou, si elle n'est pas présente, dans la timezone
        # de l'utilisateur:
        # datetime_in_tz_dt = fields.Datetime.context_timestamp(self, date_time_dt)
        # Datetime en UTC en string : fields.Datetime.now()
    }

    # APPEL A CREATE
    # apparemment, ça reste à l'ancienne, et on doit passer des IDs pour les M2O ???
    # on récupère un recordset en sortie

    @api.model  # equivalent de (self, cr, uid, vals, context=None)
    def create(self, vals):
        if 'company_id' in vals:  # v14
            self = self.with_company(vals['company_id'])
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hr.expense.expense')
        return super(ObjClass, self).create(vals)

    # Starting from v12, we can also use that:
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

    # Qd on appelle un write, pour un champ M2O, on met l'ID et non le recordset
    @api.multi  # équivalent de (self, cr, uid, ids, values, context=None)
    def write(self, vals):
        vals.update({'tutu': toto})
        return super(ObjClass, self).write(vals)

    @api.multi
    def unlink(self):
        for donation in self:
            if donation.state == 'done':
                raise UserError(
                    _("The donation '%s' is in Done state, so you must "
                        "set it back to draft before deleting it.")
                    % donation.number)
        return super(DonationDonation, self).unlink()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):

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
                                           # Ne mettre que des noms de champs de l'objet, sans suivre de liens (pas de 'lines.quantity')
    def _check_size(self):
        # Au niveau des contraines, les champs related ont déjà leur valeur
        if len(self.lines) > self.max_lines:
            raise ValidationError(_("Too many lines in %s") % self.name)
        # Pas besoin de return

    # PARFOIS, quand on supprime une contrainte SQL, il faut aussi la
    # supprimer dans postgres : ALTER TABLE res_partner DROP CONSTRAINT ...
    # On peut hériter une contrainte d'un module dont on dépend en lui
    # donnant le même nom (1er arg du tuple)
    _sql_constraints = [
        (
            'date_uniq',
            'unique(start_date, company_id, type)',
            'A DEB of the same type already exists for this month !'),
        # selon cette page : https://www.pgrs.net/2008/01/11/postgresql-allows-duplicate-nulls-in-unique-columns/
        # c'est en fait "unique or null"
        (
            'currency_rate_max_delta_positive',
            'CHECK(currency_rate_max_delta >= 0)',
            # check an interval: CHECK(probability >= 0 and probability <= 100)
            "The value of the field '...' must be positive or null."),
        # Exemple de neutralisation de la contrainte check_name native :
        (
            'check_name',
            "CHECK( 1=1 )",
            'Contacts require a name.'),
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

    # in v9+
    # Link between mail.message.subtype and the state of the recordset
    # mail.message.subtype is used for subscription
    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'paid' and self.type in ('out_invoice', 'out_refund'):
            return 'account.mt_invoice_paid'
        elif 'state' in init_values and self.state == 'open' and self.type in ('out_invoice', 'out_refund'):
            return 'account.mt_invoice_validated'
        elif 'state' in init_values and self.state == 'draft' and self.type in ('out_invoice', 'out_refund'):
            return 'account.mt_invoice_created'
        return super(AccountInvoice, self)._track_subtype(init_values)

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

# search sur active=True ET active=False
self.with_context(active_test=False).search(domain)

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
self.env.ref('base.group_user', raise_if_not_found=True)   # resolve XML ID, renvoie un recordset (pas un ID) ; raise_if_not_found=True par défaut
self.env['res.partner']  # equivalent de self.pool['res.partner']

# rebrowse recs with different parameters
env2 = self.env(cr2, uid2, context2)
recs2 = self.with_env(env2)

# special case: change/extend context
recs2 = self.with_context(context2)  # change context by context2
#ou
self = self.with_context(lang='fr')  # extend current context
self.env['res.currency'].with_context(date=signature_date).compute()
super(ProductPriceList, self.with_context(fiscal_position_id=self.fiscal_position_id.id)).print_report()

# special case: change the uid
recs2 = self.sudo(user.id)
recs2 = self.sudo()  # uid = SUPERUSER_ID

# RedirectWarning
action = self.env.ref('account.action_account_config')  # ok v14
msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

# Récupérer une action sous forme de dico
action = self.env['ir.actions.act_window'].for_xml_id('stock', 'action_package_view')
action = self.env.ref('stock.action_package_view').read()[0]
ex:
action = self.env.ref('account.action_invoice_tree1').read()[0]
action.update({
    'views': [(self.env.ref('account.invoice_form').id, 'form')],
    'view_mode': 'form,tree,kanban,calendar',
    'res_id': out_invoice.id,
    })

# v14+
action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_rules_report")

# Récupérer un action pour affichage d'un rapport (qweb ou py3o ou autre)
# en v10
action = self.env['report'].get_action(self, 'report_name')  # 1er arg = recordset, ID ou liste d'IDs
# en v12
action = self.env.ref('sale.action_report_saleorder')\
            .with_context({'discard_logo_check': True}).report_action(self)
# en v14+, on éditer un rapport directement depuis un bouton, pas besoin de code:
<button name="%(stock.action_report_delivery)d" string="Print" type="action"/>


# To get a report file as binary :
# v12, taken from mail/models/mail_template.py, method generate_email()
if report.report_type in ['qweb-html', 'qweb-pdf']:
    result, format = report.render_qweb_pdf([res_id])
else:
    res = report.render([res_id])
    if not res:
        raise UserError(_('Unsupported report type %s found.') % report.report_type)
    result, format = res

# Action pour récupérer un fichier qui a été généré par Odoo sur un objet (exemple : wizard FEC) :
# v8

action = action = {
    'name': u'Export ComptaFirst',
    'type': 'ir.actions.act_url',
    'url': "web/binary/saveas/?model=account.move.export.comptafirst&id=%d&filename_field=filename&field=file_data&download=true&filename=%s" % (self.id, self.filename),
    'target': 'self',
    }
# en v9+
action = {
    'name': 'FEC',
    'type': 'ir.actions.act_url',
    'url': "web/content/?model=account.fr.fec&id=%d&filename_field=filename&field=fec_data&download=true&filename=%s" % (self.id, self.filename),
    'target': 'self',
    }


### INHERIT
class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line():
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        return res

# si la classe hérite de mail.thread: on peut écrire un msg dans le chatter par cette simple ligne:
picking.message_post(_("The picking has been re-opened and set to draft state"))
# v10
message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
return_picking.message_post(body=message)
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

# Génération d'un mail à partir d'un mail.template
self.env.ref('mail_template_xmlid').send_mail(res_id)

@api.cr_uid_ids_context
def machin(cr, uid, ids, context=None):

# Conversion de devises
from_currency.with_context(date=date).compute(amount_to_convert, to_currency, round=True)
# a partir v12
from_currency._convert(from_amount, to_currency, company, date, round=True)
# Conversion d'UoM v10
In class product.uom
@api.multi
def _compute_quantity(self, qty, to_unit, round=True, rounding_method='UP'):

@api.multi
def _compute_price(self, price, to_unit):



# FLOAT
float_compare(value1, value2, precision_digits=None, precision_rounding=None)

value1 < value2 : returns -1
value1 > value2 : returns 1
value1 == value2 : returns 0

exemple:
prec = self.env['decimal.precision'].precision_get('Product Unit of Measure')
# Other avail decimal prec in v10:
# Product Price
# Discount
# Stock Weight
float_compare(credit_sum, debit_sum, precision_digits=prec)
# Currency / Monetary fields
float_compare(amount, 12, precision_rounding=currency.rounding)

float_is_zero(value, precision_digits=None, precision_rounding=None)

Returns true if ``value`` is small enough to be treated as
       zero at the given precision (smaller than the corresponding *epsilon*)

float_round(value, precision_digits=None, precision_rounding=None, rounding_method='HALF-UP')
rounding_method = 'UP' ou 'HALF-UP'

exemple : float_round(1.3298, precision_digits=precision)

## Méthodes sur l'objet currency (v10+)
is_zero()
compare_amounts()
round()

# Tools
from openerp.tools import file_open
f = file_open(
            'account_invoice_import_invoice2data/tests/pdf/'
            'invoice_free_fiber_201507.pdf',
            'rb')
pdf_file = f.read()
wiz = self.env['account.invoice.import'].create({
    'invoice_file': base64.b64encode(pdf_file),
    'invoice_filename': 'invoice_free_fiber_201507.pdf',
    })
f.close()

# fields.Binary
# READ
# Quand on a un recodset d'un object qui a un fields.Binary:
wizard.picture => fichier en base64
# WRITE
object.write({'picture': contenu_en_base64 ?})

# Attachments
# Read attachment
attachments = self.env['ir.attachment'].search([
    ('res_id', '=', des.id),
    ('res_model', '=', 'l10n.fr.intrastat.service.declaration'),
    ('type', '=', 'binary'),
    ])
attachment = attachments[0]
filename = attachment.datas_fname
file_itself = attachment.datas.decode('base64')
# Create attachment
import base64
attach = self.env['ir.attachment'].create({
    'name': filename,
    'res_id': self.id,
    'res_model': self._name,
    'datas': base64.encodestring(xml_bytes),
    OU 'raw': xml_bytes,
    # 'datas_fname': filename,  # dropped in v14
    })

# To know if a user is part of a group :
self.create_uid.has_group('account.group_account_manager')
return True or False

# Check ir.model.access
self.env['pos.config'].check_access_rights('read', raise_exception=True)

# Check ir.rules
my_partner.check_access_rule('read')

# Lire une entrée du fichier de config du serveur Odoo
idir = tools.config.get('invoice2data_templates_dir', False)

# Pour avoir la string d'un champ sélection
self._fields['state'].convert_to_export(self.state, self.env)

# force client-side reload (update user menu and current view)
return {
    'type': 'ir.actions.client',
    'tag': 'reload',
    }

# Sequence : si la séquence utilise range_year, on peut forcer une date qui ne soit pas la date du jour :

## v12-
self.env['ir.sequence'].with_context(ir_sequence_date='2015-10-09').next_by_code('sale.orde')
## v13+
self.env['ir.sequence'].next_by_code('sale.orde', sequence_date='2015-10-09')
# en v10, la création automatique des ir.sequence.date_range ne se fait que sur des périodes annuelles ; si on veut autre chose, il faut les créer à la main. Pour avoir la création automatique, il suffit que "use_date_range" soit coché.
# On peut utiliser %(current_year)s si on veut toujours l'année du jour et pas l'année de la facture (quand elle est != date du jour)
# On peut utiliser %(range_year)s si on veut l'année du début du range dans lequel se trouve notre date et lieu de l'année de la date.

self.env['account.analytic.account'].search_read([('type', '=', 'contract')], ['code'])
result: [{'code': u'113966', 'id': 14}, {'code': u'1485427485', 'id': 16}, {'code': u'AA001', 'id': 2}, {'code': u'AA002', 'id': 3}]

Ca renvoie comme un read:
Pour un M2O : 'account_id': (508, u'627100 Frais sur titres (achat, vente, garde)'

for move in self.filtered(lambda move: move.product_id.cost_method != 'real' and not move.origin_returned_move_id):

quant a un champ M2O package_id
quants est un recordset de plusieurs quants
quants.mapped('package_id') est un recordset de tous les packages liés à ces quants
# => plus nécessaire en v14: on peut utiliser quants.package_id
# exemple en v14 : https://github.com/odoo/odoo/blob/14.0/addons/sale_mrp/models/sale.py#L18

for inv in invoices.sorted(key='date_invoice'):
for inv in invoices.sorted(reverse=True):

self.read_group(domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True)

le(s) champ(s) présent dans groupby doit aussi être présent dans fields
lazy: if true, the results are only grouped by the first groupby and the
remaining groupbys are put in the __context key. If false, all the groupbys are
done in one call

Exemple:
line_ids = fields.One2many(
    'account.invoice.line', 'result_id', 'Commission Lines',
    readonly=True)

@api.depends('line_ids.commission_amount')
def _compute_amount_total(self):
    rg_res = self.env['account.invoice.line'].read_group([('result_id', 'in', self.ids)], ['result_id', 'commission_amount'], ['result_id'])
    mapped_data = dict([(x['result_id'][0], x['commission_amount']) for x in rg_res])
    for rec in self:
        rec.amount_total = mapped_data.get(rec.id, 0)

def _compute_sale_count(self):
    rg_res = self.env['sale.order'].read_group(
            [('agreement_id', 'in', self.ids)],
            ['agreement_id'], ['agreement_id'])
    mapped_data = dict(
        [(x['agreement_id'][0], x['agreement_id_count']) for x in rg_res])
    for agreement in self:
       agreement.sale_count = mapped_data.get(agreement.id, 0)

from odoo.tools.misc import formatLang
# CAUTION: it is not the same method as in the report ! It is only for numbers, not dates.
Proto: formatLang(env, value, digits=None, grouping=True, monetary=False, dp=False, currency_obj=False)
price_unit_formatted = formatLang(
    self.with_context(lang=lang).env, self.price_unit, currency_obj=self.company_id.currency_id)

Proto: format_date(env, value, lang_code=False, date_format=False)
'%s' % format_date(self.env, self.date)
# format_datetime is v13+ only
format_datetime(env, value, tz=False, dt_format='medium', lang_code=False)
'%s' % format_datetime(self.env, self.datetime_field)
format_amount(env, amount, currency, lang_code=False)
'%s' % format_amount(self.env, 12.42, invoice.currency_id)


self.env['ir.config_parameter'].sudo().get_param('webkit_path', default='default_path')

account_recordset = self.env['ir.property'].get('property_account_payable_id', 'res.partner')


# v14+ test intrastat country :
if country in self.env.ref('base.europe').country_ids

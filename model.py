# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
# DEFAULT_SERVER_DATETIME_FORMAT = %Y-%m-%d %H:%M:%S
from openerp import netsvc

from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class ProductCode(orm.Model):
# wizard : orm.TransientModel ; rien: orm.AbstractModel
    _name = "product.code"
    _description = "Product code"
    _rec_name = "login"  # Nom du champ qui fait office de champ name
    _order = "name, id desc"
    # C'est ascendant par défaut, donc pas besoin de préciser "asc"
    _table = "prod_code"  # Nom de la table ds la DB
    _inherit = ['mail.thread']
    _track = {
        'state': {
            'l10n_fr_intrastat_service.declaration_done':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
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

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record.id, u'[%s] %s' % (record.number, record.name)))
        return res
        # when called with a single ID :
        # self.name_get(cr, uid, [12], context=context)[0][1]

    # Hériter la recherche textuelle dans les champs many2one
    # name : object name to search for
    # operator : operator for name criteria
    # v8 old API
    def name_search(
            self, cr, uid, name='', args=None, operator='ilike', context=None,
            limit=100):
        if args is None:
            args = []
        if name and name.isdigit():
            ids = self.search(
                cr, uid, [('ref', '=', name)] + args,
                limit=limit, context=context)
            return self.name_get(cr, uid, ids, context=context)
            if not ids:
                ids = self.search(
                    cr, uid, [('prospect_ref', '=', name)] + args,
                    limit=limit, context=context)
                return self.name_get(cr, uid, ids, context=context)
        return super(res_partner, self).name_search(
            cr, uid, name=name, args=args, operator=operator, context=context,
            limit=limit)

    # Quand on fait un create dans du code, les valeurs de
    # default_get sont bien prises en compte
    def default_get(self, cr, uid, fields_list, context=None):
        # Note : on nomme l'arg 'fields_list' et non 'fields' pour éviter les
        # confusions avec le 'fields' de openerp.osv
        res = super(res_partner, self).default_get(
            cr, uid, fields_list, context=context)
        # Note : il faut toujours faire appel à super() même si on
        # n'hérite pas d'une classe pré-existante, sinon la mise aux
        # valeurs par défaut via 'default_champ' ne marche pas par
        # exemple et le _defaults = {} n'est pas pris en compte
        if not res:
            res = {}
        res.update({'champ1': valeur1, 'champ2': valeur2})
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        # arg "id" = ID de l'objet initial, pas de l'objet dupliqué,
        # vu qu'il n'est pas encore créé
        if default is None:
            default = {}
        # default should always be empty when we enter the fonction
        obj = self.browse(cr, uid, id, context=context)
        default.update({
            'state': 'draft',
            'description': _("%s (copy)") % (obj.description or ''),
            })
        # default = dict of field values to modify in the copied values
        # when creating the duplicated object
        return super(product_code, self).copy(
            cr, uid, id, default=default, context=context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        # Intérêt d'utiliser un copy_data() plutôt que copy() :
        # Quand on fait un copy() sur une sale order, Odoo ne va pas passer
        # dans la méthode copy() des sale.order.line, mais seulement dans la
        # fonction copy_data() des sale.order.line !
        if not default:
            default = {}
        default.update({
            'customer_wish_date': False,
        })
        return super(sale_order_line, self).copy_data(
            cr, uid, id, default=default, context=context)

    # FONCTION ON_CHANGE déclarée dans la vue form/tree
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

    # La fonction de calcul du fields.function
    def _compute_numbers(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for code in self.browse(cr, uid, ids, context=context):
            # PAS de MULTI
            result[code.id] = value
            # AVEC MULTI
            result[code.id] = {'field1': value1, 'field2': value2}
        return result
        # Si le champ fonction est un many2one :
        return {8: 12, 9: 13}
        # Si le champ fonction est un many2many ou one2many :
        return {8: [12, 13], 9: [7, 42]}

    # fields.function fnct_inv=_inv_numbers
    def _inv_numbers(
            self, cr, uid, ids, name, value, fnct_inv_arg, context=None):
        # value : contient la valeur entrée dans le champ
        # On fait un write de la bonne valeur et on return True ?
        return self.write(cr, uid, .., {}, context=context)

    def _search_numbers(self, cr, uid, obj, name, args, context=None):
        # obj = self
        # dans args, on trouve la liste des tuples qui définissent
        # la recherche à réaliser -> toute l'info intéressante est dedans !
        if not args:
            return []
        return [('id', 'in', [1, 2, 3])]
        # si on n'a rien trouvé, on retourne :
        return [('id', '=', '0')]

    # FONCTION d'INVALIDATION
    # - ATTENTION, self vaut l'objet qui trigger la fonction l'invalidation,
    # et non l'objet qui a le champ fields.function en question.
    # - les IDs passés en 3ème argument sont ceux de l'object qui trigger
    # la fonction d'invalidation
    # - les IDs renvoyés par la fonction d'invalidation doivent être ceux
    # de l'objet qui a la champ fields.function à recalculer
    # (la fonction renvoie une séquence d'IDs)

    # Fonction d'invalidation pour un champ situé sur un objet par lequel
    # on est lié en one2many
    # (idem pour le fields.related d'un M2O -> M2O)
    def _get_intrastat_from_product_line(self, cr, uid, ids, context=None):
        return self.pool['report.intrastat.product'].search(
            cr, uid, [('intrastat_line_ids', 'in', ids)], context=context)

    # Fonction pour fields.selection
    def _type_list_get(self, cr, uid, context=None):
        return [('key1', _('String1')), ('key2', _('String2'))]

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'create_uid': fields.many2one(
            'res.users', 'Created By', readonly=True),
        'write_uid': fields.many2one(
            'res.users', 'Last Modified By', readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'write_date': fields.datetime('Last Modification Date', readonly=True),
        'active': fields.boolean('Active'),
        'login': fields.char(
            'Login', size=16, translate=True, required=True,
            help="My help message"),
        'comment': fields.text('Comment', translate=True),
        'code_digits': fields.integer(
            '# of Digits', track_visibility='always',
            groups='base.group_user'),
        # OU groups='base.group_user,base.group_hr_manager'
        # groups = XMLID : restriction du read/write et invisible ds les vues
        # cf https://doc.odoo.com/trunk/server/04_security#access-rights
        'sequence': fields.integer('Sequence'),
        # track_visibility = always ou onchange
        'amount_untaxed': fields.float('Amount untaxed', digits=(16, 2)),
        # digits=(precision, scale)
        # Scale est le nombre de chiffres après la virgule
        # quand le float est un fields.float ou un fields.function,
        # on met l'option : digits_compute=dp.get_precision('Account')
        'start_date': fields.date('Start date'),
        # similaire : fields.datetime and fields.time
        'type': fields.selection([
            ('import', 'Import'),
            ('export', 'Export')
            ], 'Type', help="Pouet"),
        # FIELDS.SELECTION ac selection dynamique :
        'type': fields.selection(_type_list_get, 'Type', help='Pouet'),
        'picture': fields.binary('Picture'),
        # Pour fields.binary, il existe une option filters='*.png, *.gif',
        # qui restreint les formats de fichiers sélectionnables dans
        # la boite de dialogue, mais ça ne marche pas en GTK (on
        # ne peut rien sélectionner) et c'est pas supporté en Web, cf
        # https://bugs.launchpad.net/openobject-server/+bug/1076895
        'num_lines': fields.function(
            _compute_numbers, arg=None,
            fnct_inv=_inv_numbers, fnct_inv_arg=None,
            fnct_search=_search_numbers,
            type='integer',
            # if type='many2one', 'one2many' or 'many2many' :
            #   ADD: relation='account.journal',
            # if type='char' :
            #   ADD: size=512
            # if type='selection',
            #   ADD: selection=[('none','None'), ('all', 'All')]
            # if type='float':
            #   ADD: digits_compute=dp.get_precision('Account')
            multi='numbers', string='Number of lines',
            readonly=True, store={
                'product.code': (
                    lambda self, cr, uid, ids, c={}: ids, ['start_date'], 10),
                'report.intrastat.product.line': (
                    _get_intrastat_from_product_line, ['parent_id'], 20),
            }, help="Pouet"),
        'company_id': fields.many2one(
            'res.company', 'Company', ondelete='cascade'),
        # ATTENTION : si j'ai déjà un domaine sur la vue,
        # c'est le domaine sur la vue qui prime !
        # ondelete='cascade' :
        # le fait de supprimer la company va supprimer l'objet courant !
        # ondelete='set null' :
        # si on supprime la company, le champ company_id est mis à 0 (défaut)
        # ondelete='restrict' :
        # si on supprime la company, ça déclanche une erreur d'intégrité !
        'company_currency_id': fields.related(
            'company_id', 'currency_id',
            readonly=True, type='many2one', relation='res.currency',
            string='Currency'),
        # on peut aller chercher des champs avec plus d'un rebond ;
        # par exemple, on peut aller chercher un champ avec 2 rebonds
        # en mettant 3 arguments au début du fields.related
        # Attention, si on met store=, il faut une fonction d'invalidation
        # si c'est un field.related d'un champ selection, il faut mettre:
        # type='selection',
        # selection=[('absent', 'Absent'), ('present', 'Present')]

        # ATTENTION ONE2MANY : qd on ajoute un O2M sur un objet,
        # il faut probablement hériter le copy pour ce champ avec
        # default.update({'champ_one2many': False})
        'line_ids': fields.one2many(
            'product.code.line', 'parent_id', 'Product lines',
            states={'done': [('readonly', True)]}, copy=True),
        # 2e arg = nom du champ sur l'objet destination qui est le M20 inverse
        # en v8 :
        # copy=True pour que les lignes soient copiées lors d'un duplicate
        # ATTENTION : pour que states={} marche sur le champ A et que le
        # champ A est dans la vue tree, alors il faut que le champ "state"
        # soit aussi dans la vue tree.

        'partner_ids': fields.many2many(
            'res.partner', 'product_code_partner_rel', 'code_id', 'partner_id',
            'Related Partners'),
        # 2e arg = nom de la table relation
        # 3e arg ou id1 = nom de la colonne dans la table relation
        # pour stocker l'ID du product.code
        # 4e arg ou id2 = nom de la colonne dans la table relation
        # pour stocker l'ID du res.partner
        # OU
        'partner_ids': fields.many2many(
            'res.partner', id1='code_id', id2='partner_id',
            string='Related Partners'),
        # OU
        'partner_ids': fields.many2many(
            'res.partner', string='Related Partners'),
        # Pour les 2 dernières définitions du M2M, il ne faut pas avoir
        # plusieurs champs M2M qui pointent du même obj vers le même obj

        'partner_bank_id': fields.property(
            # EN V7 :
            'res.partner.bank', type="many2one", relation="res.partner.bank",
            string='Bank Account', view_load=True, help="Tutu"
            # EN V8 :
            type="many2one", relation="res.partner.bank",
            string='Bank Account', help="Tutu"),
    }

    def _default_code_digit(self, cr, uid, context=None):
        return default_value
        # Champ date : retourner la date en string (ne marche pas si on retourne en datetime)

    # Note : quand on fait un create() dans du code, les valeurs
    # de _defaults = {} sont prises en compte (ainsi que le default_get()
    _defaults = {
        'active': True,
        'login': 'Alexis',
        'code_digit': _default_code_digit,
        # ATTENTION, la fonction doit se trouver AVANT dans le fichier
        'user_id': lambda self, cr, uid, ctx: uid,
        'company_id': lambda self, cr, uid, context:
        self.pool['res.company']._company_default_get(
            cr, uid, 'asterisk.server', context=context),
        # La fonction _company_default_get retourne :
        # 1. la valeur de la company mise par la règle multi_company.default
        # pour cet objet et ce champ si il en existe une, cf
        # Settings > Technical > Multi-Companies > Default company per object
        # 2. si il n'en existe pas pour cet objet, elle retourne le
        # "company_id" de l'utilisateur uid
        'date_generation': fields.date.context_today,
        'datetime_gen': fields.datetime.now,
        # http://openerp-expert-framework.71550.n3.nabble.com/Bug-925361-Re-6-1-date-values-that-are-initialized-as-defaults-may-appear-as-quot-off-by-one-day-quoe-td3741270.html

        # Ca permet d'avoir dans le champ date la date locale de
        # l'utilisateur qui créé l'objet, et non la date UTC du serveur, qui
        # peut être une date différente compte tenu du fuseau horaire.

        # Si on veut l'utiliser dans du code :
        # fields.date.context_today(self, cr, uid, context=context)
        # ça renvoie la date du jour sous forme de STR

        # Pour convertir une datetime UTC en datetime de la timezone du
        # context (clé 'tz'), ou, si elle n'est pas présente, dans la timezone
        # de l'utilisateur:
        # datetime_in_tz = fields.datetime.context_timestamp(
        #    cr, uid, timestamp, context=context)

        'incident_ref': '/',
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('incident_ref', '/') == '/':
            vals['incident_ref'] = self.pool['ir.sequence'].next_by_code(
                cr, uid, 'crm.rma', context=context)
        return super(obj_class, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals.update({'tutu': toto})
        return super(obj_class, self).write(
            cr, uid, ids, vals, context=context)

    def _check_start_date(self, cr, uid, ids):
        for machin in ids:
            raise orm.except_orm(
                _('Error:'),
                _("My error message with %s and %s.") % (tutu, titi))
        return True

    _constraints = [
        (
            _check_start_date,
            "Start date must be the first day of a month",
            ['start_date']),
    ]

    # PARFOIS, quand on supprime une contrainte SQL, il faut aussi la
    # supprimer dans postgres : ALTER TABLE res_partner DROP CONSTRAINT ...
    _sql_constraints = [
        (
            'date_uniq',
            'unique(start_date, company_id, type)',
            'A DEB of the same type already exists for this month !'),
        (
            'currency_rate_max_delta_positive',
            'CHECK (currency_rate_max_delta >= 0)',
            "The value of the field '...' must be positive or 0."),
    ]

    def my_button(self, cr, uid, ids, context=None):
        # dans la vue: type="object"
        assert len(ids) == 1, 'Only 1 ID'
        return


### INHERIT
class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line():
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        return res

#### DOMAINES : odoo/openerp/osv/expression.py
TERM_OPERATORS = ('=', '!=', '<=', '<', '>', '>=', '=?', '=like', '=ilike',
                  'like', 'not like', 'ilike', 'not ilike', 'in', 'not in',
                  'child_of')
# like et ilike => openerp ajoute automatiquement les '%' avant ET après : %terme%
# quand on utilise =like et =ilike, c'est à nous de mettre les %, donc on peut être
# plus précis
# starts with AB is [('field','=like','AB%')]
# ends with AB is [('field','=like','%AB')]
# 'child_of', 'ID') => matche sur les enfants ET l'ID

# Récupérer une clé du fichier de config du serveur Odoo
from openerp.tools.config import config
config.get('email_from', False)

#### Accès direct à la DB
# Note : ça by-passe les droits d'accès de l'utilisateur !
# cr.execute()
cr.execute('''SELECT ... %s ''', ())
# toujours un tuple en 2e arg, même si un seul %s dans la string du premier arg
# toujours %s, jamais autre chose
# quand WHERE id in %s -> %s doit être un tuple
cr.execute('UPDATE sale_order_line set tutu=True where id in %s', (tuple(ids), ))

# cr.fetchall() :
# séquence avec une entrée par ligne de résultat, contenant une liste avec une entrée par colonne
# cr.dictfetchall() :
# on récupère un dico avec clé = nom_du_champ, valeur = valeur du champ
cr.execute(
    'SELECT id, name, product_id from sale_order_line where id in %s',
    (tuple(ids), ))
for sol in cr.dictfetchall():
    print sol['product_id']


#### DATES
# STR -> TIME
datetime.strptime(start_date_str, DEFAULT_SERVER_DATE_FORMAT)
# TIME -> STR
my_datetime.strftime(DEFAULT_SERVER_DATE_FORMAT)
# Créer un datetime :
datetime(2014, 12, 25)  # Noël

# RELATIVEDELTA
# SANS "S" -> information absolue
# year, month, day, hour, minute, second, microsecond
relativedelta(day=1)  # 1er jour du mois
####
# AVEC "S" -> information relative ; peut être négatif
# years, months, weeks, days, hours, minutes, seconds, microseconds
relativedelta(days=1)  # +1 jour

# pour avoir le nombre de jours d'un objet relativedelta :
relativedelta(days=3).days  # renvoie: 3

# On a le droit de balancer une date au format datetime dans un write ou un create

#### RENVOI d'ACTIONS :
# Retourner une nouvelle vue form :
# 1) Retourner une nouvelle vue avec des données préremplies :
# Mettre dans le contexte les champs et leur valeur
# context['partner_id'] = partner_id
return {
    'name': _('Create phone call in CRM'),
    'type': 'ir.actions.act_window',
    'res_model': 'wizard.create.crm.phonecall',
    'view_mode': 'form',
    'nodestroy': True,
    'target': 'new',
    'context': context,
    }

#OU MIEUX :

act_model, act_id = self.pool['ir.model.data'].get_object_reference(
    cr, uid, 'mrp_repair', 'action_repair_order_tree')
assert act_model == 'ir.actions.act_window', 'Wrong model'
action = self.pool[act_model].read(
    cr, uid, act_id, context=context)
action.update({
    'target': 'new',
    'nodestroy': True,
    })

#en v8, encore mieux
action = self.pool['ir.actions.act_window'].for_xml_id(cr, uid, 'stock', 'action_package_view', context=context)
# ça fait à la fois le xmlid_to_res_id et le read

# ATTENTION: si on veut renvoyer une vue form, il faut faire:
action.update({
    'views': False,  # Important, sinon il continue de mettre le tree en premier (en particulier quand il y a des ir.actions.act_window.view)
    'view_mode': 'form,tree',
    })

# 2) Retourner une vue form d'un enregistrement existant :
return {
    'name': _('Create phone call in CRM'),  # self.pool['res.partner']._description,
    'type': 'ir.actions.act_window',
    'res_model': 'wizard.create.crm.phonecall',  # self.pool['res.partner']._name
    'view_mode': 'form,tree',  # L'élément en 1ère position est celui qui sera utilisé
    'nodestroy': False,  # Close the wizard pop-up (if returned by the function of the wizard)
    'target': 'current',
    'res_id': partner_id,
    'context': context,
    }

# TODO : tester la même chose ac get_object_reference => ça ne marche pas !!!, cf le module donation_stay

# Retourner la vue tree d'une liste de records :
# idem que précédemment avec mais SANS res_id et avec :
    'view_mode': 'tree,form',
    'domain': [('id', 'in', ids)],

# v8 only
action_id = self.pool['ir.model.data'].xmlid_to_res_id(
    cr, uid, 'donation.donation_action', raise_if_not_found=True)
action = self.pool['ir.actions.act_window'].read(
    cr, uid, action_id, context=context)
action.update({
    'view_mode': 'tree,form,graph',
    'domain': [('id', 'in', new_donation_ids)],
    'target': 'current'})

# Avoir un double group_by dans une vue tree:
    'context': {'group_by': ['employee_id', 'holiday_status_id']},

# fermer la vue form du wizard :
return {'type': 'ir.actions.act_window_close'}  # en fait, on n'en a plus besoin, car par défaut un return True sur un bouton type="object" va fermer le wizard

#### RENVOI d'UN RAPPORT :
return {
    'type': 'ir.actions.report.xml',
    'report_name': 'sale.order',
    # report_name = report_name de la définition du ir.actions.report.xml
    'datas': {
        'model': 'sale.order',
        'ids': [id1, id2, id3],
        'form': valeur,  # Facultatif. On peut y accéder dans le rapport via data['form']
        },
    'context': context,
    }

# Renvoi d'une entrée de menu (trouvé dans point_of_sale.py en v8)
return {
    'type': 'ir.actions.client',
    'name': 'Point of Sale Menu',
    'tag': 'reload',
    'params': {'menu_id': menu_id},
    }

# Renvoi d'une URL:
return {
    'type': 'ir.actions.act_url',
    'url': 'http://maps.google.com/',
    'target': 'new',
}

#### M2M/O2M
# MANY2MANY
# BROWSE : cur_production.move_lines => [browse_record(stock.move, 61), browse_record(stock.move, 63), browse_record(stock.move, 65)]
# READ : cur_production_read['move_lines'] => [61, 63, 65]
# Dans le dico, on a non seulement les clés correspondant aux champs demandés, avec en plus une clé 'id'

# ONE2MANY
# BROWSE : cur_production.move_created_ids => [browse_record(stock.move, 59), browse_record(stock.move, 60)]
# READ : cur_production_read['move_created_ids'] => [59, 60]

# MANY2ONE
# BROWSE : cur_production.picking_id.id => 7
# READ : cur_production_read['picking_id'] => (7, u'D120042')


# WRITE et CREATE MANY2MANY
[(0, 0,  { values })]    link to a new record that needs to be created with the given values dictionary
[(1, ID, { values })]    update the linked record with id = ID (write *values* on it)
[(2, ID)]                remove and delete the linked record with id = ID (calls unlink on ID, that will delete the object completely, and the link to it as well)
[(3, ID)]                cut the link to the linked record with id = ID (delete the relationship between the two objects but does not delete the target object itself)
[(4, ID)]                link to existing record with id = ID (adds a relationship)
[(5)    ]                unlink all (like using (3,ID) for all linked records)
[(6, 0, [IDs])]          replace the list of linked IDs (like using (5) then (4,ID) for each ID in the list of IDs)

# WRITE et CREATE ONE2MANY
(0, 0,  { values })    link to a new record that needs to be created with the given values dictionary
(1, ID, { values })    update the linked record with id = ID (write *values* on it)
(2, ID)                remove and delete the linked record with id = ID (calls unlink on ID, that will delete the object completely, and the link to it as well)
[(6, 0, [IDs])] => pas indiqué dans le code source du serveur, mais ça marche !

# Example :
[(0, 0, {'field_name':field_value_record1, ...}), (0, 0, {'field_name':field_value_record2, ...})]

# WRITE MANY2ONE
Simply use the ID of target record, which must already exist, or ``False`` to remove the link.

# SEARCH on MANY2MANY
# 'in', tuple ne marche pas

'|', ('route_ids', '=', ha_lib_route_id),
('route_ids', '=', ha_lib_et_vpc_route_id),
])
# -> ('route_ids', '=', 7) doit en fait se comprendre pour un M2M en route_ids.ids contient ha_lib_route_id (et ça peut contenir d'autres IDs)
# donc la recherche ci-dessous donne en fait tous les produits qui contiennent la route ha_lib_route_id ou ha_lib_et_vpc_route_id.

### Get an XMLID
# en v8
res_id = self.pool['ir.model.data'].xmlid_to_res_id(
    cr, uid, 'account.action_invoice_tree1', raise_if_not_found=False)

# en v7
get_object_reference(self, cr, uid, module, xml_id)

model, res_id = self.pool['ir.model.data'].get_object_reference(
    cr, uid, 'module', 'xml_id')
assert model == 'res.partner', 'Wrong model'
# model sera une string type 'product.product' et non self.pool['product.product']

browse_record = self.pool['ir.model.data'].get_object(
    cr, uid, 'module', 'xml_id', context=context)

# pour savoir si l'utilisateur uid se trouve dans un groupe dont le XMLID est donné en 3e arg :
self.pool['res.users'].has_group(
    cr, uid, 'l10n_fr_intrastat_product.group_detailed_intrastat_product')
# renvoie True ou False

#### Faire avancer le workflow via du code
from openerp import netsvc

wf_service = netsvc.LocalService("workflow")
wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_confirm', cr)

button_confirm correspond au champ "signal" sur la workflow.transition

#### Petits secrets de l'ORM :
# Quand on fait un search sur un champ traduisible, il ne cherche que sur la langue qu'on donne dans la clé 'lang' du contexte (si pas de context, il cherche sur l'anglais)
# Quand on fait un create sur un objet avec un champ traduisible :
# Quand on fait le create, il ne tient pas compte de l'éventuelle langue du contexte
#  et fait l'entrée dans la table principale et rien dans ir_translation
# Ensuite, on fait le write avec 'name' en français et context['lang'] = 'fr_FR'
# -> il créé une entrée dans la table ir_translation
# Conséquence de cela :
# Si je fais :
# 1) create({'name': 'Mon produit joli'})
# 2) with_context(lang='en_US').write({'name': 'My cute product'})
# => on a perdu le texte français !
## La solution qui marche :
# 1) create({'name': 'Mon produit joli'})
# 2) with_context(lang='fr_FR').write({'name': 'Mon produit joli'})
# 3) with_context(lang='en_US').write({'name': 'My cute product'})
# Evidemment, le plus simple et logique est de faire :
# 1) create({'name': 'My cute product'})
# 2) with_context(lang='fr_FR').write({'name': 'Mon produit joli'})

#### List comprehension :
# [x*2 for x in range(20) if x % 3]
# result : [2, 4, 8, 10, 14, 16, 20, 22, 26, 28, 32, 34, 38]

#### SAFE EVAL
from openerp.tools.safe_eval import safe_eval
# 1er arg : la string
# 2e arg : un dico avec pour chaque début de string, l'obj openerp correspondant
safe_eval('sepa_export.payment_order_ids[0].reference', {'sepa_export': gen_args['sepa_export']})

#### Polish notation
#Comment la lire :
#http://en.wikipedia.org/wiki/Polish_notation
# Tu vas de gauche à droite, et dès que tu rencontres un signe suivi de 2 (), tu exécutes la requête, et tu recommences tt à gauche

## ATTACHMENTS
# Création
attach_id = self.pool['ir.attachment'].create(
    cr, uid, {
        'name': filename,
        'res_id': 12,
        'res_model': 'sale.order',  # self._name
        'datas': xml_string.encode('base64'),
        'datas_fname': filename,
    },
    context=context)

# Recherche

# web_context_tunnel (dans server-tools)
# Dans __openerp__.py, ajouter à la clé 'depends': 'web_context_tunnel'
# ATTENTION, il faut reloader toute l'interface après l'installation du module (où après l'héritage de la vue ??)
<xpath expr="//field[@name='line_ids']/tree/field[@name='product_id']"
            position="attributes">
    <attribute name="context_private_car_product_id">{'private_car_product_id': parent.private_car_product_id}</attribute>
</xpath>
dans le code:
private_car_product_id = context.get('private_car_product_id')

# Pour avoir le libellé d'un fields.selection:
key_label_dict = dict(self.pool['sale.order'].fields_get(
    cr, uid, ['state'], context=context)['state']['selection'])
order_state_label = key_label_dict[order.state]

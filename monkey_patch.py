# -*- encoding: utf-8 -*-
# Sample monkey-patching
##############################################################################

from openerp.osv import orm, fields
from openerp.report import report_sxw



class base_formatlang_date_extension_installed(orm.AbstractModel):
    '''When you use monkey patching, the code is executed when the module
    is in the addons_path of the OpenERP server, even is the module is not
    installed ! In order to avoid the side-effects it can create,
    we create an AbstractModel inside the module and we test the
    availability of this Model in the code of the monkey patching below.
    At Akretion, we call this the "Guewen trick", in reference
    to a trick used by Guewen Baconnier in the "connector" module.
    '''
    _name = "base.formatlang.date.extension.installed"


_get_lang_dict_original = report_sxw.rml_parse._get_lang_dict


def _get_lang_dict(self):
    if self.pool.get('base.formatlang.date.extension.installed'):
        # This is the code which is executed when this module is installed
        pool_lang = self.pool.get('res.lang')
        lang = self.localcontext.get('lang', 'en_US') or 'en_US'
        lang_ids = pool_lang.search(
            self.cr, self.uid, [('code', '=', lang)])[0]
        lang_obj = pool_lang.browse(self.cr, self.uid, lang_ids)
        self.lang_dict.update({
            'lang_obj': lang_obj,
            # we use our field 'report_date_format' instead of the native
            # field 'date_format'
            'date_format': lang_obj.report_date_format,
            'time_format': lang_obj.time_format,
            })
        self.default_lang[lang] = self.lang_dict.copy()
    else:
        # If this module is not installed, we execute the old code
        _get_lang_dict_original(self)
    return True

report_sxw.rml_parse._get_lang_dict = _get_lang_dict

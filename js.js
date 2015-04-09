openerp.module_name = function (instance) {

    var _t = instance.web._t; // Pr la traduc

Pop-up de notif :
self.do_notify(_t("Titre"), _t('Message'));

Traduc :
this.do_warn(_t("E-mail Error"), _t("Can't send email to invalid e-mail address"));

Faire un read :

new instance.web.Model("res.users").get_func("read")(this.session.uid, ["company_id"]))

OU

new instance.web.Model("res.currency").query(["symbol", "position"])

}

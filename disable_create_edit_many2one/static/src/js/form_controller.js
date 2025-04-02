/** @odoo-module **/


const { onWillStart, useSubEnv } = owl;
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { user } from "@web/core/user";

patch(FormController.prototype, {
    setup() {
        onWillStart(async () => {
            this.can_create_edit = await user.hasGroup("disable_create_edit_many2one.create_edit_many2one_group");
        });

        useSubEnv({
            can_create_edit: () => this._can_create_edit(),
        });

        super.setup();
    },
    _can_create_edit() {
        return this.can_create_edit;
    },
});


/** @odoo-module */

import { registry } from "@web/core/registry"
import { formView } from "@web/views/form/form_view"
import { FormController } from "@web/views/form/form_controller"
const { useEffect } = owl
const { onWillStart, useSubEnv } = owl;
import { useService } from "@web/core/utils/hooks";
import { jsonrpc } from "@web/core/network/rpc_service";
import { patch } from "@web/core/utils/patch";

patch(FormController.prototype, {

    setup(){
        if (this.props.resModel == 'res.partner' || this.props.resModel == 'product.template' || this.props.resModel == 'product.product' ){
            onWillStart(async () => {
                this.can_create = await jsonrpc(`/web/dataset/call_kw/res.users/has_group`, {
                    model: "res.users",
                    method: "has_group",
                    args: ['disable_form.all_access_of_product'],
                    kwargs: {},
                });
            });
            super.setup()
            this.onNotebookPageChange = (notebookId, page) => {
                this.disableForm()
            };

        } else {
            super.setup()
        }

    },

    disableForm() {
        const inputElements = document.querySelectorAll(".o_form_sheet input")
        const fieldWidgets = document.querySelectorAll(".o_form_sheet .o_field_widget")
        console.log(this.model.root.data.active);
        if (!this.can_create && this.model.root.data.active == true){
            if (inputElements) inputElements.forEach(e => e.setAttribute("disabled", 1))
            if (fieldWidgets) fieldWidgets.forEach(e => e.classList.add("pe-none"))
            this.canEdit = false
        } else {
            if (inputElements) inputElements.forEach(e => e.removeAttribute("disabled"))
            if (fieldWidgets) fieldWidgets.forEach(e => e.classList.remove("pe-none"))
            this.canEdit = true
        }
    },

    async beforeLeave() {
//        if (this.model.root.data.state == 'draft') return
        if (!this.can_create) return
                super.beforeLeave()
            },

    async beforeUnload(ev) {
        if (this.can_create) return
//        if (this.model.root.data.state == 'draft') return
        super.beforeUnload(ev)
    },

});
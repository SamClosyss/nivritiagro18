/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { PropertyValue } from "@web/views/fields/properties/property_value";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";
import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";

const { onWillStart } = owl;

patch(Many2XAutocomplete.prototype, {
    setup() {
        super.setup();
        if (this.env.can_create_edit !== undefined && !this.env.can_create_edit()) {
            this.activeActions.createEdit = false;
            this.activeActions.create = false;
        }
    },

    async loadOptionsSource(request) {
        if (this.env.can_create_edit !== undefined && !this.env.can_create_edit()) {
            this.activeActions.createEdit = false;
            this.activeActions.create = false;
        }
        this.activeActions.open = false;
        return super.loadOptionsSource(...arguments);
    },
});

patch(Many2OneField.prototype, {
    setup() {

        if (this.env.can_create_edit !== undefined && !this.env.can_create_edit()) {
            this.props.canQuickCreate = false;
            this.props.canCreate = false;
            this.props.canCreateEdit = false;
        }
        this.props.canOpen = false;
        super.setup();
    },
});

patch(Many2ManyTagsField.prototype, {
    setup() {

        if (this.env.can_create_edit !== undefined && !this.env.can_create_edit()) {
            this.props.canQuickCreate = false;
            this.props.canCreate = false;
            this.props.canCreateEdit = false;
        }
        super.setup();
    },
});
